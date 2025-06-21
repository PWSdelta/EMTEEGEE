"""
Card and Deck models for the EMTEEGEE Django project.
These are used for Django admin interface but actual data is stored in MongoDB.
"""

from django.db import models
from datetime import datetime


class Card(models.Model):
    """
    Simplified Django model for admin interface.
    Actual card data is stored in MongoDB with full MTGJson structure.
    """
    uuid = models.CharField(max_length=36, unique=True)
    name = models.CharField(max_length=255)
    mana_cost = models.CharField(max_length=50, blank=True)
    mana_value = models.IntegerField(default=0)
    type_line = models.CharField(max_length=255, blank=True)
    colors = models.CharField(max_length=10, blank=True)  # Simplified as string
    rarity = models.CharField(max_length=20, blank=True)
    set_code = models.CharField(max_length=10, blank=True)
    
    # Analysis tracking
    fully_analyzed = models.BooleanField(default=False)
    analysis_completed_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    imported_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        
    def __str__(self):
        return f"{self.name} ({self.set_code})"


class Deck(models.Model):
    """
    Simplified Django model for admin interface.
    Actual deck data is stored in MongoDB with full MTGJson structure.
    """
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=50, blank=True)
    release_date = models.CharField(max_length=20, blank=True)
    total_cards = models.IntegerField(default=0)
    
    # Timestamps
    imported_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-release_date', 'name']
        
    def __str__(self):
        return f"{self.name} ({self.code})"


# MongoDB data access utilities
from pymongo import MongoClient
from django.conf import settings


def get_mongodb_collection(collection_name):
    """Get a MongoDB collection for direct access."""
    mongodb_settings = settings.MONGODB_SETTINGS
    
    # Create connection string
    if mongodb_settings['username'] and mongodb_settings['password']:
        client = MongoClient(
            host=mongodb_settings['host'],
            username=mongodb_settings['username'],
            password=mongodb_settings['password'],
            authSource=mongodb_settings['auth_source']
        )
    else:
        client = MongoClient(mongodb_settings['host'])
    
    db = client[mongodb_settings['db_name']]
    return db[collection_name]


def get_cards_collection():
    """Get the MongoDB cards collection."""
    return get_mongodb_collection('cards')


def get_decks_collection():
    """Get the MongoDB decks collection."""
    return get_mongodb_collection('decks')
