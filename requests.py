from bson import dbref
from mongo_helper import db, news_collection, tags_collection


# Retrieve tags in the database grouped by the related reference.
# If no tags are related to the reference it returns an empty array.
# ids must have a strict structure.
# For example : ids -> [(ObjectId('602bc867b537c341612e210f', 'companies'), (ObjectId('602bc867b537c341612e2115', 'triplets'))]
def retrieve_multiple_tags(ids):
    references = list(map(lambda x: dbref.DBRef(x[1], x[0]), ids))
    references_as_objects = list(map(lambda x: {'ref': x[1], 'refId': x[0]}, ids))

    results = list(tags_collection.aggregate([
        {
            '$match': {
                'reference': {'$in': references}
            }
        },
        {
            '$addFields': {
                '__ref': {
                    'ref': '$reference.$ref',
                    'refId': '$reference.$id'
                }
            }
        },
        {
            '$addFields': {
                '__order': {
                    '$indexOfArray': [references_as_objects, '$__ref']
                }
            }
        },
        {
            '$group': {
                '_id': '$reference',
                'items': {'$push': '$$ROOT'},
                '__order': {'$first': '$__order'}
            }
        },
        {
            '$sort': {'__order': 1}
        }
    ]))

    items = list(map(lambda x: x['items'], results))

    if len(items) == len(ids):
        return items

    """
    Handles the case when there is one id and no items have been found
    """
    if len(items) == 0:
        return [[]]

    """
    Adds programatically an empty array of tags when no tag is related to the reference.
    Because the MongoDB query does not return references when no tags are related to them.
    """
    for i in range(0, len(ids)):
        refId = ids[i][0]
        tagRefId = items[i][0]['__ref']['refId']

        if refId != tagRefId:
            items.insert(i, [])

    return items


# TODO: Change the name
def retrieve_tags_with_batching(match={}):
    """
    This request only retrieves references that are linked to specific tags.
    For example, it will gather companies and triplets for a given predicate of tag (e.g. macroTag: "Filiere" & tag: "Aeronautique").
    The data will look like this :
    [
        {
            'ref': 'companies',
            'refIds': [ObjectId('xxx'), ObjectId('yyy'), ObjectId('zzz')]
        }, {
            'ref': 'triplets',
            'refIds': [ObjectId('aaa'), ObjectId('bbb')]
        }
    ]
    """
    references_result = list(tags_collection.aggregate([
        {
            '$match': match
        }, {
            '$group': {
                '_id': {
                    'refId': '$reference.$id',
                    'ref': '$reference.$ref'
                }
            }
        }, {
            '$group': {
                '_id': '$_id.ref',
                'refIds': {'$push': '$_id.refId'}
            }
        }, {
            '$project': {
                '_id': False,
                'ref': '$_id',
                'refIds': True
            }
        }
    ]))

    references = []
    # For each requested reference type (companies, triplets, ...), tags are retrieved and pushed into the references array
    for reference_result in references_result:
        # Collection of the reference
        ref = reference_result['ref']
        # _id of the reference
        ref_ids = reference_result['refIds']

        """
        This request retrieves tags related to a given reference.
        For example, you wille have :
        [
            {
                'collection': 'triplets',
                'sujet': 'Airbus',
                'predicat': 'vend',
                'objet': '10 avions à AirFrance',
                # 'tags': [
                #     {
                #         'tag': 'Aeronautique',
                #         'macroTag': 'Filiere'
                #     }, {
                #         'name': 'Airbus',
                #         'tag': 'Commande',
                #         'macroTag': 'BE',
                #         'subTag': 'Vendeur'
                #     }
                # ]
            }
        ]
        """
        tags_results = list(db[ref].aggregate([
            {
                '$match': {'_id': {'$in': ref_ids}}
            },
            # {
            #     '$lookup': {
            #         'from': 'tags',
            #         'localField': '_id',
            #         'foreignField': 'reference.$id',
            #         'as': 'tags'
            #     }
            # },
            {
                '$addFields': {
                    'collection': ref
                }
            }
        ]))

        references.extend(tags_results)

    return references


# Finds 1 news in the database for a given _id.
def retrieve_news(_id):
    return news_collection.find_one({'_id': _id})


# Finds multiple news in the database for an array of _id.
def retrieve_multiple_news(_ids):
    return list(news_collection.find({'_id': {'$in': _ids}}))


# Finds tags related to a specific _id (refId) in a specific collection (ref).
def retrieve_tags(refId, ref):
    return list(tags_collection.aggregate([
        {
            '$match': {
                'reference.$id': refId,
                'reference.$ref': ref
            }
        }
    ]))


# Finds companies and their related tags.
def retrieve_companies(match={}):
    # companies_result = list(db['companies'].aggregate([
    #     {
    #         '$lookup': {
    #             'from': 'tags',
    #             'localField': '_id',
    #             'foreignField': 'reference.$id',
    #             'as': 'tags'
    #         }
    #     }, {
    #         '$match': match
    #     }
    # ]))
    companies_result = list(db['companies'].aggregate([
        {
            '$match': match
        },
        {
            '$addFields': {
                'collection': 'companies'
            }
        }
    ]))
    return companies_result


# Finds triplets and their related tags
def retrieve_triplets(match={}):
    triplets_result = list(db['triplets'].aggregate([
        # {
        #     '$lookup': {
        #         'from': 'tags',
        #         'localField': '_id',
        #         'foreignField': 'reference.$id',
        #         'as': 'tags'
        #     }
        # },
        {
            '$lookup': {
                'from': 'news',
                'localField': 'newsId',
                'foreignField': '_id',
                'as': 'news'
            }
        }, {
            '$addFields': {
                'news': {'$first': '$news'}
            }
        }, {
            '$match': match
        }
    ]))
    return triplets_result


# Inserts a tag into the database.
# For exemple, the company having the _id 602d3b4d73c9c71ee04fa954 will be tagged as a concurrent.
# {
#     'ref': 'companies',
#     'refId': '602d3b4d73c9c71ee04fa954',
#     'macroTag': 'Entite',
#     'tag': 'Concurrent'
# }
def insert_tag(document):
    return tags_collection.insert_one(document)


# Deletes tags in the database.
# For exemple the following predicate deletes ALL tags matching macroTag as 'Filiere' and 'tag' as 'Aeronautique'
# {
#     'macroTag': 'Filiere',
#     'tag': 'Aeronautique'
# }
def delete_tag(predicate):
    return tags_collection.delete_many(predicate)
