#!/usr/bin/env python3
"""
Test Ollama connectivity for the swarm workers
"""

import requests
import json

def test_ollama_connection():
    """Test if Ollama is accessible"""
    print("🧪 Testing Ollama Connection...")
    
    try:
        # Test Ollama API
        response = requests.get('http://localhost:11434/api/tags')
        if response.status_code == 200:
            models = response.json()
            print("✅ Ollama is running!")
            print(f"   Available models: {len(models.get('models', []))}")
            
            for model in models.get('models', []):
                print(f"   - {model['name']}")
            
            return True
        else:
            print(f"❌ Ollama API returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Cannot connect to Ollama: {e}")
        return False

def test_model_inference():
    """Test a simple model inference"""
    print("\n🧪 Testing Model Inference...")
    
    try:
        # Test with a simple prompt
        payload = {
            "model": "qwen2.5:7b",
            "prompt": "What is Magic: The Gathering? (Answer in one sentence)",
            "stream": False
        }
        
        response = requests.post('http://localhost:11434/api/generate', json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Model inference successful!")
            print(f"   Response: {result.get('response', 'No response')[:100]}...")
            return True
        else:
            print(f"❌ Model inference failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Model inference error: {e}")
        return False

def main():
    print("🐝 Ollama Swarm Integration Test")
    print("="*40)
    
    if test_ollama_connection():
        test_model_inference()
        print("\n✅ Ollama integration ready for swarm workers!")
        print("\nNext: Test the desktop_worker_real.py script")
    else:
        print("\n❌ Fix Ollama connection before proceeding")

if __name__ == "__main__":
    main()
