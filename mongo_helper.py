import os
from pymongo import MongoClient

DB_NAME = 'dw_tags'

_subType = 'subTag'
_type = 'tag'
_name = 'name'
_macroType = 'macroTag'
_reference = 'reference'

MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017')

# client = MongoClient("mongodb+srv://user:user@python-mongo-graphql.37e9n.mongodb.net/social?retryWrites=true&w=majority")
client = MongoClient(MONGO_URI)

db = client[DB_NAME]

companies_collection = db['companies']
news_collection = db['news']
triplets_collection = db['triplets']
tags_collection = db['tags']
