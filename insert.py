from bson import ObjectId, dbref
import dateparser
from mongo_helper import client, DB_NAME, companies_collection, news_collection, triplets_collection, tags_collection, _type, _macroType, _subType, _name, _reference

client.drop_database(DB_NAME)

companies_ids = companies_collection.insert_many([
    {
        'name': 'Airbus',
        'website': 'www.airbus.com',
        'effectif': 134931
    },
    {
        'name': 'AirFrance',
        'website': 'www.airfrance.fr',
        'effectif': 44849
    },
    {
        'name': 'SNCF',
        'website': 'www.sncf.fr',
        'effectif': 275000
    }
]).inserted_ids

news_ids = news_collection.insert_many([
    {
        'text': 'Airbus vend 10 avions à AirFrance. Emirates achète 15 A350 à Airbus',
        'source': 'NouvelObs',
        'date': dateparser.parse('Novembre 2020')
    },
    {
        'text': 'AirFrance va licencier 200 employés dans les deux prochains mois',
        'source': "L'usine nouvelle",
        'date': dateparser.parse('Janvier 2021')
    },
    {
        'text': 'La SNCF commande 10 TGV',
        'source': 'Le Monde',
        'date': dateparser.parse('Décembre 2020')
    }
]).inserted_ids

triplets_ids = triplets_collection.insert_many([
    {
        'sujet': 'Airbus',
        'predicat': 'vend',
        'objet': '10 avions à AirFrance',
        'newsId': news_ids[0]
    },
    {
        'sujet': 'Emirates',
        'predicat': 'achète',
        'objet': '15 A350 à Airbus',
        'newsId': news_ids[0]
    },
    {
        'sujet': 'AirFrance',
        'predicat': 'va licencier',
        'objet': '200 employés dans les deux prochains mois',
        'newsId': news_ids[1]
    },
    {
        'sujet': 'La SNCF',
        'predicat': 'commande',
        'objet': '10 TGV',
        'newsId': news_ids[2]
    }
]).inserted_ids

tags_collection.insert_many([
    # ----------------------------------------
    # FILIERES
    # ----------------------------------------
    {
        _type: 'Aeronautique',
        _macroType: 'Filiere',
        _reference: dbref.DBRef('companies', companies_ids[0])
    },
    {
        _type: 'Aeronautique',
        _macroType: 'Filiere',
        _reference: dbref.DBRef('companies', companies_ids[1])
    },
    {
        _type: 'Ferroviaire',
        _macroType: 'Filiere',
        _reference: dbref.DBRef('companies', companies_ids[2])
    },
    {
        _type: 'Aeronautique',
        _macroType: 'Filiere',
        _reference: dbref.DBRef('triplets', triplets_ids[0])
    },
    {
        _type: 'Aeronautique',
        _macroType: 'Filiere',
        _reference: dbref.DBRef('triplets', triplets_ids[1])
    },
    {
        _type: 'Aeronautique',
        _macroType: 'Filiere',
        _reference: dbref.DBRef('triplets', triplets_ids[2])
    },
    {
        _type: 'Ferroviaire',
        _macroType: 'Filiere',
        _reference: dbref.DBRef('triplets', triplets_ids[3])
    },
    # ----------------------------------------
    # ENTITES
    # ----------------------------------------
    {
        _type: 'Client',
        _macroType: 'Entite',
        _reference: dbref.DBRef('companies', companies_ids[0])
    },
    {
        _type: 'Fournisseur',
        _macroType: 'Entite',
        _reference: dbref.DBRef('companies', companies_ids[1])
    },
    {
        _type: 'Partenaire',
        _macroType: 'Entite',
        _reference: dbref.DBRef('companies', companies_ids[2])
    },
    # ----------------------------------------
    # Airbus vend 10 avions à AirFrance
    # ----------------------------------------
    {
        _name: 'Airbus',
        _type: 'Commande',
        _macroType: 'BE',
        _subType: 'Vendeur',
        _reference: dbref.DBRef('triplets', triplets_ids[0])
    },
    {
        _name: '10',
        _type: 'Commande',
        _macroType: 'BE',
        _subType: 'Quantité',
        _reference: dbref.DBRef('triplets', triplets_ids[0])
    },
    {
        _name: 'avions',
        _type: 'Commande',
        _macroType: 'BE',
        _subType: 'Produit',
        _reference: dbref.DBRef('triplets', triplets_ids[0])
    },
    {
        _name: 'AirFrance',
        _type: 'Commande',
        _macroType: 'BE',
        _subType: 'Acheteur',
        _reference: dbref.DBRef('triplets', triplets_ids[0])
    },
    # ----------------------------------------
    # Emriates achète 15 A350 à Airbus
    # ----------------------------------------
    {
        _name: 'Airbus',
        _type: 'Commande',
        _macroType: 'BE',
        _subType: 'Vendeur',
        _reference: dbref.DBRef('triplets', triplets_ids[1])
    },
    {
        _name: '15',
        _type: 'Commande',
        _macroType: 'BE',
        _subType: 'Quantité',
        _reference: dbref.DBRef('triplets', triplets_ids[1])
    },
    {
        _name: 'A350',
        _type: 'Commande',
        _macroType: 'BE',
        _subType: 'Produit',
        _reference: dbref.DBRef('triplets', triplets_ids[1])
    },
    {
        _name: 'Emirates',
        _type: 'Commande',
        _macroType: 'BE',
        _subType: 'Acheteur',
        _reference: dbref.DBRef('triplets', triplets_ids[1])
    },
    # ----------------------------------------
    # AirFrance va licencier 200 employés dans les deux prochains mois
    # ----------------------------------------
    {
        _name: 'AirFrance',
        _type: 'Licenciement',
        _macroType: 'BE',
        _subType: 'Acteur',
        _reference: dbref.DBRef('triplets', triplets_ids[2])
    },
    {
        _name: '200',
        _type: 'Licenciement',
        _macroType: 'BE',
        _subType: 'Quantité',
        _reference: dbref.DBRef('triplets', triplets_ids[2])
    },
    # ----------------------------------------
    # La SNCF commande 10 TGV
    # ----------------------------------------
    {
        _name: 'SNCF',
        _type: 'Commande',
        _macroType: 'BE',
        _subType: 'Acheteur',
        _reference: dbref.DBRef('triplets', triplets_ids[3])
    },
    {
        _name: '10',
        _type: 'Commande',
        _macroType: 'BE',
        _subType: 'Quantité',
        _reference: dbref.DBRef('triplets', triplets_ids[3])
    },
    {
        _name: 'TGV',
        _type: 'Commande',
        _macroType: 'BE',
        _subType: 'Produit',
        _reference: dbref.DBRef('triplets', triplets_ids[3])
    }
])
