#!/usr/bin/env python3
"""
Standalone test of desktop worker Ollama integration
"""

import requests
import json
import time

def test_ollama_simple():
    """Simple Ollama test"""
    print("🧪 Testing Ollama...")
    
    try:
        # Simple generation test
        payload = {
            "model": "qwen2.5:7b",
            "prompt": "Magic: The Gathering is",
            "stream": False,
            "options": {"num_predict": 50}
        }
        
        print("   Sending request to Ollama...")
        response = requests.post('http://localhost:11434/api/generate', json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Ollama working!")
            print(f"   Response: {result.get('response', 'No response')}")
            return True
        else:
            print(f"❌ Status: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_card_analysis():
    """Test actual card analysis prompt"""
    print("\n🧪 Testing Card Analysis...")
    
    card_data = {
        'name': 'Lightning Bolt',
        'mana_cost': '{R}',
        'type_line': 'Instant',
        'oracle_text': 'Lightning Bolt deals 3 damage to any target.'
    }
    
    prompt = f"""Analyze the Magic: The Gathering card '{card_data['name']}' for play tips.

Card Details:
- Name: {card_data['name']}
- Mana Cost: {card_data['mana_cost']}
- Type: {card_data['type_line']}
- Text: {card_data['oracle_text']}

Provide practical gameplay tips for this card. Focus on:
- When to play it
- Best targets
- Timing considerations
- Strategic applications

Keep the analysis concise but informative."""

    try:
        payload = {
            "model": "qwen2.5:7b",
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": 200
            }
        }
        
        print("   Generating card analysis...")
        start_time = time.time()
        response = requests.post('http://localhost:11434/api/generate', json=payload, timeout=60)
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            analysis = result.get('response', 'No response')
            
            print("✅ Card analysis generated!")
            print(f"   Time: {end_time - start_time:.2f} seconds")
            print(f"   Analysis:\n{analysis}")
            return True
        else:
            print(f"❌ Analysis failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Analysis error: {e}")
        return False

def main():
    print("🐝 Desktop Worker Ollama Test")
    print("="*40)
    
    if test_ollama_simple():
        test_card_analysis()
        print("\n✅ Desktop worker ready for real analysis!")
    else:
        print("\n❌ Fix Ollama issues first")

if __name__ == "__main__":
    main()
