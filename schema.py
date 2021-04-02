from bson import dbref, ObjectId
from distutils.util import strtobool
from graphene import Boolean, DateTime, Field, Int, List, Mutation, ObjectType, Schema, String, Union
from requests import delete_tag, insert_tag, retrieve_tags, retrieve_tags_with_batching, retrieve_news, retrieve_companies, retrieve_triplets, retrieve_tags
from loaders import NewsLoader, TagLoader
import os


if 'USE_DATALOADER' in os.environ and not os.getenv('USE_DATALOADER').casefold() in ['y', 'yes', 't', 'true', 'on', '1', 'n', 'no', 'f', 'false', 'off', '0']:
    raise ValueError('Environment variable USE_DATALOADER must be either y, yes, t, true, on, 1, n, no, f, false, off or 0')

USE_DATALOADER = strtobool(os.getenv('USE_DATALOADER', '1'))

news_loader = NewsLoader()
tag_loader = TagLoader()


class Tag(ObjectType):
    _id = String()
    name = String()
    tag = String()
    macroTag = String()
    subTag = String()
    reference = String()


class Company(ObjectType):
    _id = String()
    name = String()
    website = String()
    effectif = Int()
    collection = String()
    tags = List(Tag)

    def resolve_tags(root, info):
        _id = root['_id']
        return tag_loader.load((_id, 'companies')) if USE_DATALOADER else retrieve_tags(_id, 'companies')


class News(ObjectType):
    _id = String()
    text = String()
    date = DateTime()
    source = String()


class Triplet(ObjectType):
    _id = String()
    sujet = String()
    predicat = String()
    objet = String()
    newsId = String()
    collection = String()
    news = Field(News)
    tags = List(Tag)

    def resolve_news(root, info):
        newsId = root['newsId']
        return news_loader.load(newsId) if USE_DATALOADER else retrieve_news(newsId)

    def resolve_tags(root, info):
        _id = root['_id']
        return tag_loader.load((_id, 'triplets')) if USE_DATALOADER else retrieve_tags(_id, 'triplets')


class ReferenceUnion(Union):
    class Meta:
        types = (Company, Triplet)

    @classmethod
    def resolve_type(cls, instance, info):
        collection = instance['collection']
        if collection == 'companies':
            return Company
        elif collection == 'triplets':
            return Triplet
        raise Exception('Unsupported type')


class AddTag(Mutation):
    class Arguments:
        name = String()
        tag = String()
        subTag = String()
        macroTag = String()
        ref = String(required=True)
        refId = String(required=True)

    ok = Boolean()
    tag = Field(Tag)

    def mutate(root, info, **kwargs):
        kwargs['reference'] = dbref.DBRef(kwargs['ref'], ObjectId(kwargs['refId']))
        del kwargs['ref']
        del kwargs['refId']
        insert_tag(kwargs)

        return {'ok': True, 'tag': kwargs}


class DeleteTags(Mutation):
    class Arguments:
        _id = String()
        name = String()
        tag = String()
        subTag = String()
        macroTag = String()
        ref = String()
        refId = String()

    ok = Boolean()
    deletedDocuments = Int()

    def mutate(root, info, **kwargs):
        if '_id' in kwargs:
            kwargs['_id'] = ObjectId(kwargs['_id'])

        if 'ref' in kwargs and 'refId' in kwargs:
            kwargs['reference'] = dbref.DBRef(kwargs['ref'], ObjectId(kwargs['refId']))
            del kwargs['ref']
            del kwargs['refId']

        deleted_tags = delete_tag(kwargs).deleted_count
        return {'ok': deleted_tags > 0, 'deletedDocuments': deleted_tags}


class Query(ObjectType):
    get_tags = List(ReferenceUnion, _id=String(), tag=String(), subTag=String(), macroTag=String(), name=String(), ref=String(), refId=String())
    get_companies = List(Company, _id=String(), name=String(), website=String(), effectif=Int())
    get_triplets = List(Triplet, _id=String(), sujet=String(), predicat=String(), objet=String(), newsId=String(), source=String())

    def resolve_get_tags(root, info, **kwargs):
        if '_id' in kwargs:
            kwargs['_id'] = ObjectId(kwargs['_id'])
        if 'ref' in kwargs:
            kwargs['reference.$ref'] = kwargs['ref']
            del kwargs['ref']
        if 'refId' in kwargs:
            kwargs['reference.$id'] = ObjectId(kwargs['refId'])
            del kwargs['refId']
        return retrieve_tags_with_batching(kwargs)

    def resolve_get_companies(root, info, **kwargs):
        if '_id' in kwargs:
            kwargs['_id'] = ObjectId(kwargs['_id'])
        return retrieve_companies(kwargs)

    def resolve_get_triplets(root, info, **kwargs):
        if '_id' in kwargs:
            kwargs['_id'] = ObjectId(kwargs['_id'])
        if 'newsId' in kwargs:
            kwargs['newsId'] = ObjectId(kwargs['newsId'])
        if 'source' in kwargs:
            kwargs['news.source'] = kwargs['source']
            del kwargs['source']
        return retrieve_triplets(kwargs)


class Mutations(ObjectType):
    add_tag = AddTag.Field()
    delete_tags = DeleteTags.Field()


schema = Schema(query=Query, mutation=Mutations)
