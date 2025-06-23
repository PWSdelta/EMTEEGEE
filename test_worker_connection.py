#!/usr/bin/env python3
"""
Test Worker Connection to Remote Servers
Diagnose connection issues with swarm API endpoints
"""

import requests
import json
from datetime import datetime

def test_server_connection(server_url):
    """Test connection to a specific server"""
    print(f"\n🔍 Testing connection to: {server_url}")
    
    # Test basic connectivity
    try:
        response = requests.get(f"{server_url}/", timeout=10)
        print(f"✅ Basic connection: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Basic connection failed: {e}")
        return False
    
    # Test swarm status endpoint
    try:
        response = requests.get(f"{server_url}/api/swarm/status", timeout=10)
        if response.status_code == 200:
            print(f"✅ Swarm API accessible: {response.json()}")
        else:
            print(f"❌ Swarm API failed: HTTP {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            return False
    except Exception as e:
        print(f"❌ Swarm API error: {e}")
        return False
    
    # Test worker registration endpoint
    try:
        test_registration = {
            'worker_id': 'test-worker',
            'capabilities': {
                'hostname': 'test-host',
                'worker_type': 'desktop',
                'cpu_cores': 8,
                'ram_gb': 32,
                'gpu_available': True
            },
            'status': 'active',
            'registered_at': datetime.utcnow().isoformat()
        }
        
        response = requests.post(
            f"{server_url}/api/swarm/register",
            json=test_registration,
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"✅ Worker registration works: {response.json()}")
        else:
            print(f"❌ Worker registration failed: HTTP {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            return False
    except Exception as e:
        print(f"❌ Worker registration error: {e}")
        return False
    
    return True

def main():
    """Test all configured servers"""
    servers = [
        'http://localhost:8000',           # Local development
        'https://mtgabyss.com',            # Production domain
        'http://64.23.130.187:8000',       # DigitalOcean IP
    ]
    
    print("🤖 EMTeeGee Worker Connection Test")
    print("=" * 40)
    
    working_servers = []
    
    for server in servers:
        if test_server_connection(server):
            working_servers.append(server)
    
    print(f"\n📊 Summary:")
    print(f"✅ Working servers: {len(working_servers)}")
    print(f"❌ Failed servers: {len(servers) - len(working_servers)}")
    
    if working_servers:
        print(f"\n🎯 Recommended server for worker:")
        print(f"   {working_servers[0]}")
        
        # Test work availability
        try:
            response = requests.post(
                f"{working_servers[0]}/api/swarm/get_work",
                json={
                    'worker_id': 'test-worker',
                    'max_tasks': 1,
                    'worker_type': 'desktop',
                    'specialization': 'fast_gpu_analysis'
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                tasks = result.get('tasks', [])
                print(f"🔄 Available work: {len(tasks)} task(s)")
                if tasks:
                    print(f"   Sample task: {tasks[0].get('card_name', 'Unknown')}")
            else:
                print(f"⚠️  Work request failed: HTTP {response.status_code}")
        except Exception as e:
            print(f"⚠️  Work availability test failed: {e}")
    else:
        print("\n❌ No working servers found!")
        print("   - Check if Django server is running")
        print("   - Verify swarm API is configured")
        print("   - Check network connectivity")

if __name__ == "__main__":
    main()
