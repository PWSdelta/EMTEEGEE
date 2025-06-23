#!/usr/bin/env python3
"""
Debug script to find the correct collection and examine structure
"""

import os
import sys
import django
from pprint import pprint

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from pymongo import MongoClient

def debug_collections():
    """Debug collections and find tasks"""
    print("🔍 Examining MongoDB collections...")
    
    # Connect to MongoDB
    client = MongoClient('mongodb://localhost:27017/')
    db = client['emteegee_dev']
    
    # List all collections
    collections = db.list_collection_names()
    print(f"📋 Available collections: {collections}")
    
    # Look for task-related collections
    task_collections = [c for c in collections if 'task' in c.lower() or 'swarm' in c.lower()]
    print(f"🎯 Task-related collections: {task_collections}")
    
    # Check each collection for documents
    for collection_name in collections:
        collection = db[collection_name]
        count = collection.count_documents({})
        print(f"📊 {collection_name}: {count} documents")
        
        if count > 0 and ('task' in collection_name.lower() or 'swarm' in collection_name.lower()):
            print(f"🔍 Sample document from {collection_name}:")
            sample = collection.find_one()
            if sample:
                print("Available fields:")
                for key in sample.keys():
                    print(f"  {key}: {type(sample[key])}")
                print()

if __name__ == "__main__":
    debug_collections()
