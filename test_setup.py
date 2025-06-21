#!/usr/bin/env python
"""
Test script to verify MongoDB connection and Django setup.
Run this after setting up your environment to ensure everything works.
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(project_dir))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

def test_mongodb_connection():
    """Test MongoDB connection using Django settings."""
    try:
        from django.conf import settings
        from pymongo import MongoClient
        
        db_config = settings.DATABASES['default']
        
        if 'CLIENT' in db_config:
            client_config = db_config['CLIENT']
            client = MongoClient(
                host=client_config.get('host'),
                username=client_config.get('username'),
                password=client_config.get('password'),
                authSource=client_config.get('authSource', 'admin')
            )
        else:
            client = MongoClient('mongodb://localhost:27017/')
        
        # Test connection
        db = client[db_config['NAME']]
        
        # Try to get server info
        server_info = client.server_info()
        print(f"✅ MongoDB connection successful!")
        print(f"   Server version: {server_info.get('version', 'Unknown')}")
        print(f"   Database: {db_config['NAME']}")
          # Check collections
        collections = db.list_collection_names()
        print(f"   Collections found: {len(collections)}")
        
        if 'cards' in collections:
            card_count = db.cards.count_documents({})
            analyzed_count = db.cards.count_documents({'fully_analyzed': True})
            print(f"   Cards in database: {card_count:,}")
            print(f"   Analyzed cards: {analyzed_count:,}")
        
        if 'decks' in collections:
            deck_count = db.decks.count_documents({})
            print(f"   Decks in database: {deck_count:,}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False

def test_django_setup():
    """Test Django setup and model imports."""
    try:
        from cards.models import Card, Deck
        from analyses.models import AnalysisComponent
        from users.models import User
        
        print("✅ Django models imported successfully!")
        print("   Available models: Card, Deck, AnalysisComponent, User")
        return True
        
    except Exception as e:
        print(f"❌ Django setup failed: {e}")
        return False

def test_environment_variables():
    """Test required environment variables."""
    try:
        from django.conf import settings
        
        print("✅ Environment variables:")
        print(f"   DEBUG: {settings.DEBUG}")
        print(f"   SECRET_KEY: {'Set' if settings.SECRET_KEY else 'Not set'}")
        print(f"   ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
        
        db_config = settings.DATABASES['default']
        print(f"   Database Engine: {db_config['ENGINE']}")
        print(f"   Database Name: {db_config['NAME']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Environment check failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🔍 Testing EMTEEGEE Django Setup")
    print("=" * 40)
    
    tests = [
        ("Environment Variables", test_environment_variables),
        ("Django Setup", test_django_setup),
        ("MongoDB Connection", test_mongodb_connection),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Testing {test_name}...")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 40)
    print("📊 Test Results:")
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed! Your setup is ready.")
        print("\nNext steps:")
        print("1. Start the Django server: python manage.py runserver")
        print("2. Import MTGJson deck files: python manage.py import_mtgjson_decks --path /path/to/files/")
        print("3. Visit http://localhost:8000/ to see your application")
    else:
        print("\n⚠️  Some tests failed. Please check your configuration.")
        print("\nTroubleshooting:")
        print("1. Make sure MongoDB is running")
        print("2. Check your .env file configuration")
        print("3. Verify all dependencies are installed: pip install -r requirements.txt")

if __name__ == "__main__":
    main()
