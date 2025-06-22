#!/usr/bin/env python3
"""
Quick Working Desktop Worker for Testing
"""

import requests
import time
import socket
import platform
import psutil
import logging
import ollama

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_worker_registration(server_url):
    """Test worker registration with correct API endpoints"""
    
    worker_id = f"desktop-{socket.gethostname()}"
    
    capabilities = {
        'hostname': socket.gethostname(),
        'platform': platform.platform(),
        'cpu_cores': psutil.cpu_count(),
        'ram_gb': round(psutil.virtual_memory().total / (1024**3)),
        'gpu_available': True,
        'worker_type': 'desktop',
        'preferred_models': ['qwen2.5:7b', 'llama3.1:latest', 'mistral:7b'],
        'specialization': 'fast_gpu_inference'
    }
    
    print(f"🤖 Testing registration for {worker_id}")
    print(f"   Server: {server_url}")
    print(f"   Capabilities: {capabilities}")
    
    try:
        # Test registration
        response = requests.post(
            f"{server_url}/cards/api/swarm/register",
            json={
                'worker_id': worker_id,
                'capabilities': capabilities
            },
            timeout=30
        )
        
        print(f"   Registration response: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Registration successful!")
            print(f"   Assigned components: {len(result.get('assigned_components', []))}")
            return True
        else:
            print(f"❌ Registration failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return False

def test_get_work(server_url, worker_id):
    """Test getting work from server"""
    
    try:
        response = requests.post(
            f"{server_url}/cards/api/swarm/get_work",
            json={
                'worker_id': worker_id,
                'max_tasks': 1
            },
            timeout=30
        )
        
        print(f"   Get work response: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            tasks = result.get('tasks', [])
            print(f"✅ Got {len(tasks)} tasks")
            
            if tasks:
                task = tasks[0]
                print(f"   Task: {task['card_name']} - {task['components']}")
                return task
            
            return None
        else:
            print(f"❌ Get work failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Get work error: {e}")
        return None

def main():
    server_url = "http://localhost:8001"
    worker_id = f"desktop-{socket.gethostname()}"
    
    print("🐝 Quick Desktop Worker Test")
    print("="*40)
    
    # Test registration
    if test_worker_registration(server_url):
        print(f"\n🎯 Testing work assignment...")
        task = test_get_work(server_url, worker_id)
        
        if task:
            print(f"\n✅ Worker cycle successful!")
            print(f"Ready to process: {task['card_name']}")
        else:
            print(f"\n⚠️  No work available yet")
    else:
        print(f"\n❌ Registration failed - check Django server and API endpoints")

if __name__ == "__main__":
    main()
