#!/usr/bin/env python3
"""
EMTEEGEE Production Status Checker
Quickly check if Django and the Enhanced Swarm API are running on production
"""

import requests
import json
from datetime import datetime

def check_endpoint(url, endpoint_name, expected_type="any"):
    """Check if an endpoint is responding correctly"""
    try:
        print(f"🔍 Testing {endpoint_name}: {url}")
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            # Try to parse as JSON for API endpoints
            if expected_type == "json":
                try:
                    data = response.json()
                    print(f"✅ {endpoint_name}: OK (JSON response)")
                    return True, data
                except json.JSONDecodeError:
                    print(f"⚠️  {endpoint_name}: Responding but not JSON")
                    return False, None
            else:
                print(f"✅ {endpoint_name}: OK (HTTP 200)")
                return True, response.text[:100]
        else:
            print(f"❌ {endpoint_name}: HTTP {response.status_code}")
            return False, None
            
    except requests.exceptions.ConnectTimeout:
        print(f"❌ {endpoint_name}: Connection timeout")
        return False, None
    except requests.exceptions.ConnectionError:
        print(f"❌ {endpoint_name}: Connection failed")
        return False, None
    except Exception as e:
        print(f"❌ {endpoint_name}: Error - {str(e)}")
        return False, None

def main():
    print("=== EMTEEGEE PRODUCTION STATUS CHECK ===")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("")
    
    base_url = "https://mtgabyss.com"
    
    endpoints_to_test = [
        (f"{base_url}/", "Main Site", "html"),
        (f"{base_url}/admin/", "Django Admin", "html"),
        (f"{base_url}/api/enhanced_swarm/status", "Enhanced API Status", "json"),
        (f"{base_url}/api/enhanced_swarm/workers", "Enhanced API Workers", "json"),
        (f"{base_url}/api/enhanced_swarm/metrics", "Enhanced API Metrics", "json"),
        (f"{base_url}/api/work/get-work", "Original API (if exists)", "json"),
    ]
    
    results = {}
    
    for url, name, expected_type in endpoints_to_test:
        success, data = check_endpoint(url, name, expected_type)
        results[name] = success
        if success and expected_type == "json" and data:
            print(f"   📄 Data preview: {json.dumps(data, indent=2)[:200]}...")
        print("")
    
    # Summary
    print("=== SUMMARY ===")
    working_count = sum(1 for success in results.values() if success)
    total_count = len(results)
    
    for name, success in results.items():
        status = "✅ WORKING" if success else "❌ FAILED"
        print(f"{status}: {name}")
    
    print(f"\n📊 Overall Status: {working_count}/{total_count} endpoints working")
    
    if results.get("Enhanced API Status"):
        print("\n🚀 READY FOR WORKERS: You can now start universal workers!")
        print("   Command: python universal_worker_enhanced.py --server https://mtgabyss.com")
    else:
        print("\n⚠️  NOT READY: Enhanced API is not responding. Django may not be running.")
        print("   Solution: Run deploy_production.sh on the production server")

if __name__ == "__main__":
    main()
