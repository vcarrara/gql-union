from bson import ObjectId
from bson.dbref import DBRef
import dateparser
from faker import Faker
from mongo_helper import client, DB_NAME, companies_collection, news_collection, triplets_collection, tags_collection, _type, _macroType, _subType, _name, _reference
import random

fake = Faker()
client.drop_database(DB_NAME)

companies_number = 200
news_number = 200
triplets_number = 700
tags_number = 1500

companies_ids = companies_collection.insert_many([{
    'name': fake.company(),
    'website': fake.url(),
    'effectif': random.randint(10, 10000)
} for _ in range(companies_number)]).inserted_ids

news_ids = news_collection.insert_many([{
    'text': fake.text(),
    'source': random.choice(["L'usine nouvelle", 'NouvelObs', 'Le Monde', 'Le Figaro', 'BBC', 'The New-York Times', 'The Washington Post']),
    'date': dateparser.parse(fake.date())
} for _ in range(news_number)]).inserted_ids

triplets_ids = triplets_collection.insert_many([{
    'sujet': fake.word(),
    'predicat': fake.word(),
    'objet': fake.word(),
    'newsId': random.choice(news_ids)
} for _ in range(triplets_number)]).inserted_ids


def generate_random_tag():
    tag = {}

    tag[_macroType] = random.choice(['BE', 'Entite', 'Filiere'])
    if tag[_macroType] == 'BE':
        tag[_type] = random.choice([
            'Commande',
            'Annulation commande',
            'Recrutement',
            'Licenciement',
            'Fusion',
            'Investissement',
            'Rachat',
            'Levee de fonds',
            'Cession',
            'Changement de dirigeant'
        ])
        tag[_subType] = random.choice(['Vendeur', 'Acheteur', 'Produit'])
        tag[_name] = fake.word()
    elif tag[_macroType] == 'Entite':
        tag[_type] = random.choice(['Client', 'Concurrent', 'Prospect', 'Fournisseur', 'Partenaire', 'Autre'])
    elif tag[_macroType] == 'Filiere':
        tag[_type] = random.choice([
            'Agroalimentaire',
            'Automobile',
            'Chimie et materiaux',
            'Aeronautique',
            'Ferroviaire',
            'Defense',
            'Energie',
            'Nucleaire',
            'Numerique',
            'Packaging',
            'Sante',
            'Client',
            'Concurrent',
            'Prospect',
            'Fournisseur',
            'Partenaire',
            'Autre'
        ])

    collection = random.choice(['companies', 'triplets'])
    if collection == 'companies':
        tag[_reference] = DBRef('companies', random.choice(companies_ids))
    elif collection == 'triplets':
        tag[_reference] = DBRef('triplets', random.choice(triplets_ids))

    return tag


tags_collection.insert_many([generate_random_tag() for _ in range(tags_number)])
