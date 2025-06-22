from django.db import models
from django.conf import settings
import pymongo

# Create your models here.

def get_mongodb_collection(collection_name):
    """Get a MongoDB collection using Django settings."""
    mongodb_settings = settings.MONGODB_SETTINGS
    
    # Handle both connection string and legacy settings
    if 'connection_string' in mongodb_settings:
        # Use connection string method
        client = pymongo.MongoClient(mongodb_settings['connection_string'])
    else:
        # Use legacy host-based method
        if mongodb_settings.get('username') and mongodb_settings.get('password'):
            client = pymongo.MongoClient(
                host=mongodb_settings['host'],
                username=mongodb_settings['username'],
                password=mongodb_settings['password'],
                authSource=mongodb_settings.get('auth_source', 'admin')
            )
        else:
            client = pymongo.MongoClient(mongodb_settings['host'])
    
    db_name = mongodb_settings.get('db_name', 'emteegee_dev')
    db = client[db_name]
    return db[collection_name]


def get_cards_collection():
    """Get the MongoDB cards collection."""
    return get_mongodb_collection('cards')


def get_decks_collection():
    """Get the MongoDB decks collection."""
    return get_mongodb_collection('decks')
