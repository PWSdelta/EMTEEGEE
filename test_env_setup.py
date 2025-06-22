#!/usr/bin/env python3
"""
Test environment variable setup for remote MongoDB
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_env_vars():
    print("🧪 Testing Environment Variable Setup")
    print("="*50)
    
    # Check MongoDB connection string
    mongodb_connection = os.getenv('MONGODB_CONNECTION_STRING')
    if mongodb_connection:
        # Mask sensitive parts of the connection string for display
        masked_connection = mongodb_connection[:20] + "***" + mongodb_connection[-20:] if len(mongodb_connection) > 40 else "***"
        print(f"✅ MongoDB Connection String: {masked_connection}")
    else:
        print("❌ MONGODB_CONNECTION_STRING not set in .env file")
        print("   Please add your connection string to .env file")
    
    # Check other variables
    django_secret = os.getenv('DJANGO_SECRET_KEY')
    django_debug = os.getenv('DJANGO_DEBUG')
    ollama_host = os.getenv('OLLAMA_HOST')
    swarm_server = os.getenv('SWARM_SERVER_URL')
    
    print(f"✅ Django Secret Key: {'Set' if django_secret else 'Using default'}")
    print(f"✅ Django Debug: {django_debug or 'True'}")
    print(f"✅ Ollama Host: {ollama_host or 'http://localhost:11434'}")
    print(f"✅ Swarm Server: {swarm_server or 'http://localhost:8001'}")
    
    return bool(mongodb_connection)

def test_mongodb_connection():
    """Test connection to remote MongoDB"""
    print(f"\n🧪 Testing Remote MongoDB Connection")
    print("="*50)
    
    try:
        from pymongo import MongoClient
        
        mongodb_connection = os.getenv('MONGODB_CONNECTION_STRING')
        if not mongodb_connection:
            print("❌ No connection string available")
            return False
        
        print("   Connecting to remote MongoDB...")
        client = MongoClient(mongodb_connection)
        
        # Test connection
        db = client['emteegee_dev']
        cards = db.cards
        
        total_cards = cards.count_documents({})
        print(f"✅ Connected to remote MongoDB!")
        print(f"   Database: emteegee_dev")
        print(f"   Total cards: {total_cards:,}")
        
        # Test write access
        test_collection = db.connection_test
        test_doc = {'test': True, 'timestamp': 'test'}
        result = test_collection.insert_one(test_doc)
        
        if result.inserted_id:
            print("✅ Write access confirmed")
            # Clean up test document
            test_collection.delete_one({'_id': result.inserted_id})
            print("✅ Test document cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False

def main():
    print("🐝 Environment Variable Setup Test")
    print("="*60)
    
    if test_env_vars():
        if test_mongodb_connection():
            print(f"\n🎉 Environment setup complete!")
            print(f"\nBoth workers can now connect to the remote database.")
            print(f"Next steps:")
            print(f"1. Copy .env file to laptop (if different machine)")
            print(f"2. Run desktop worker: python desktop_worker_clean.py")
            print(f"3. Run laptop worker: python laptop_worker_real.py")
        else:
            print(f"\n❌ MongoDB connection issues")
    else:
        print(f"\n❌ Please set up MONGODB_CONNECTION_STRING in .env file")
        print(f"   Add this line to .env:")
        print(f"   MONGODB_CONNECTION_STRING=your_connection_string_here")

if __name__ == "__main__":
    main()
