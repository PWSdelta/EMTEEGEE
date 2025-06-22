#!/usr/bin/env python3
"""
Direct MongoDB + Ollama Test
Test the swarm system with real MongoDB and Ollama
"""

import requests
import json
import time
from pymongo import MongoClient

def test_mongodb_connection():
    """Test MongoDB connection"""
    print("🧪 Testing MongoDB Connection...")
    
    try:
        # Load environment variables
        from dotenv import load_dotenv
        import os
        load_dotenv()
        
        # Use remote MongoDB if available, fallback to local
        mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/emteegee_dev')
        if mongo_uri.startswith('mongodb+srv://') or mongo_uri.startswith('mongodb://'):
            client = MongoClient(mongo_uri)
            db_name = mongo_uri.split('/')[-1] if '/' in mongo_uri else 'emteegee_dev'
            db = client[db_name]
        else:
            client = MongoClient('localhost:27017')
            db = client['emteegee_dev']
        
        cards = db.cards
        
        # Test connection
        total_cards = cards.count_documents({})
        print(f"✅ MongoDB connected!")
        print(f"   Total cards: {total_cards:,}")
        
        # Get a sample card for testing
        sample_card = cards.find_one({'name': {'$exists': True}})
        if sample_card:
            print(f"   Sample card: {sample_card.get('name', 'Unknown')}")
            return sample_card
        
        return None
        
    except Exception as e:
        print(f"❌ MongoDB error: {e}")
        return None

def test_ollama_analysis(card_data):
    """Test real Ollama analysis"""
    print(f"\n🧪 Testing Ollama Analysis for {card_data.get('name', 'Unknown')}...")
    
    prompt = f'''Analyze the Magic: The Gathering card "{card_data.get('name', 'Unknown')}" for practical play tips.

Card Details:
- Name: {card_data.get('name', 'Unknown')}
- Mana Cost: {card_data.get('mana_cost', 'N/A')}
- Type: {card_data.get('type_line', 'N/A')}
- Text: {card_data.get('oracle_text', 'N/A')}

Provide 3-4 practical gameplay tips for this card. Be concise and focus on:
1. When to play it
2. Best targets or situations
3. Timing considerations
4. Common synergies

Format as a clear, helpful guide for players.'''

    try:
        payload = {
            "model": "qwen2.5:7b",
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": 300
            }
        }
        
        print("   Sending to Ollama...")
        start_time = time.time()
        response = requests.post('http://localhost:11434/api/generate', json=payload, timeout=60)
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            analysis = result.get('response', 'No response')
            
            print(f"✅ Analysis generated in {end_time - start_time:.2f}s")
            print(f"   Length: {len(analysis)} characters")
            print(f"   Preview: {analysis[:150]}...")
            
            return analysis
        else:
            print(f"❌ Ollama error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Analysis error: {e}")
        return None

def test_mongodb_storage(card_data, analysis):
    """Test storing analysis back to MongoDB"""
    print(f"\n🧪 Testing MongoDB Storage...")
    
    try:
        client = MongoClient('localhost:27017')
        db = client['emteegee_dev']
        cards = db.cards
        
        # Update the card with analysis
        update_result = cards.update_one(
            {'_id': card_data['_id']},
            {
                '$set': {
                    'swarm_test_analysis': {
                        'play_tips': analysis,
                        'generated_at': time.time(),
                        'model': 'qwen2.5:7b',
                        'worker': 'test-desktop'
                    }
                }
            }
        )
        
        if update_result.modified_count > 0:
            print("✅ Analysis stored in MongoDB!")
            return True
        else:
            print("❌ Storage failed - no documents updated")
            return False
            
    except Exception as e:
        print(f"❌ Storage error: {e}")
        return False

def main():
    print("🐝 Real MongoDB + Ollama Integration Test")
    print("="*50)
    
    # Test MongoDB
    card_data = test_mongodb_connection()
    if not card_data:
        print("❌ Cannot proceed without MongoDB")
        return
    
    # Test Ollama analysis
    analysis = test_ollama_analysis(card_data)
    if not analysis:
        print("❌ Cannot proceed without Ollama")
        return
    
    # Test storage
    if test_mongodb_storage(card_data, analysis):
        print("\n🎉 Full integration working!")
        print("\nReady to run the real swarm workers:")
        print("1. Start Django server (optional for API)")
        print("2. Run: python desktop_worker_real.py")
        print("3. Run: python laptop_worker_real.py")
        print("4. Monitor: python swarm_dashboard.py")
    else:
        print("\n❌ Storage issues need to be resolved")

if __name__ == "__main__":
    main()
