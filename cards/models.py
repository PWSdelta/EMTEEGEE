from django.db import models
from django.conf import settings
import pymongo

# Create your models here.

def get_mongodb_collection(collection_name):
    """Get a MongoDB collection using Django settings."""
    mongodb_settings = settings.MONGODB_SETTINGS
    
    # Create connection string
    if mongodb_settings['username'] and mongodb_settings['password']:
        client = pymongo.MongoClient(
            host=mongodb_settings['host'],
            username=mongodb_settings['username'],
            password=mongodb_settings['password'],
            authSource=mongodb_settings['auth_source']
        )
    else:
        client = pymongo.MongoClient(mongodb_settings['host'])
    
    db = client[mongodb_settings['db_name']]
    return db[collection_name]


def get_cards_collection():
    """Get the MongoDB cards collection."""
    return get_mongodb_collection('cards')


def get_decks_collection():
    """Get the MongoDB decks collection."""
    return get_mongodb_collection('decks')
