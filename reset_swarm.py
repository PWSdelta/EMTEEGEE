#!/usr/bin/env python3
"""
Reset Swarm State - Clear all pending tasks and workers for testing
"""

import os
import sys
import django
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from django.conf import settings
from pymongo import MongoClient

def reset_swarm():
    """Clear all swarm data for fresh testing"""
    
    # Connect to MongoDB
    mongodb_connection_string = os.getenv('MONGODB_CONNECTION_STRING')
    
    if mongodb_connection_string:
        mongo_client = MongoClient(mongodb_connection_string)
        db_name = settings.MONGODB_SETTINGS.get('db_name', 'emteegee_dev')
    else:
        mongo_client = MongoClient(settings.MONGODB_SETTINGS['host'])
        db_name = settings.MONGODB_SETTINGS.get('db_name', 'emteegee_dev')
    
    db = mongo_client[db_name]
    
    print("🧹 Clearing swarm state...")
    
    # Clear all workers
    workers_result = db.swarm_workers.delete_many({})
    print(f"✅ Removed {workers_result.deleted_count} workers")
    
    # Clear all pending tasks
    tasks_result = db.swarm_tasks.delete_many({'status': 'assigned'})
    print(f"✅ Removed {tasks_result.deleted_count} pending tasks")
    
    # Reset card analysis flags (keep existing analysis data)
    cards_result = db.cards.update_many(
        {},
        {'$unset': {'analysis.fully_analyzed': ''}}
    )
    print(f"✅ Reset analysis flags on {cards_result.modified_count} cards")
    
    print("🎉 Swarm state reset complete!")

if __name__ == "__main__":
    reset_swarm()
