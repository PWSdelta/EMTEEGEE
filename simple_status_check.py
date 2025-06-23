"""
Simple production status checker using urllib (built-in Python)
"""
import urllib.request
import urllib.error
import json
from datetime import datetime

def check_url(url, name):
    """Check if a URL is responding"""
    try:
        print(f"🔍 Testing {name}: {url}")
        
        with urllib.request.urlopen(url, timeout=10) as response:
            if response.status == 200:
                content = response.read().decode('utf-8')
                
                # Try to parse as JSON
                try:
                    data = json.loads(content)
                    print(f"✅ {name}: OK (JSON response)")
                    return True, data
                except json.JSONDecodeError:
                    print(f"✅ {name}: OK (HTML response)")
                    return True, content[:100]
            else:
                print(f"❌ {name}: HTTP {response.status}")
                return False, None
                
    except urllib.error.HTTPError as e:
        if e.code == 502:
            print(f"❌ {name}: 502 Bad Gateway (Django not running)")
        else:
            print(f"❌ {name}: HTTP {e.code}")
        return False, None
    except urllib.error.URLError as e:
        print(f"❌ {name}: Connection failed - {e.reason}")
        return False, None
    except Exception as e:
        print(f"❌ {name}: Error - {str(e)}")
        return False, None

def main():
    print("=== EMTEEGEE PRODUCTION STATUS CHECK ===")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("")
    
    base_url = "https://mtgabyss.com"
    
    urls_to_test = [
        (f"{base_url}/", "Main Site"),
        (f"{base_url}/admin/", "Django Admin"),
        (f"{base_url}/api/enhanced_swarm/status", "Enhanced API Status"),
        (f"{base_url}/api/enhanced_swarm/workers", "Enhanced API Workers"),
    ]
    
    results = {}
    
    for url, name in urls_to_test:
        success, data = check_url(url, name)
        results[name] = success
        if success and isinstance(data, dict):
            print(f"   📄 Response: {json.dumps(data, indent=2)[:150]}...")
        print("")
    
    # Summary
    print("=== SUMMARY ===")
    working = sum(1 for success in results.values() if success)
    total = len(results)
    
    for name, success in results.items():
        status = "✅ WORKING" if success else "❌ FAILED"
        print(f"{status}: {name}")
    
    print(f"\n📊 Status: {working}/{total} endpoints working")
    
    if results.get("Enhanced API Status"):
        print("\n🚀 DJANGO IS RUNNING - READY FOR WORKERS!")
        print("Start workers with: python universal_worker_enhanced.py --server https://mtgabyss.com")
    else:
        print("\n⚠️  DJANGO IS NOT RUNNING")
        print("Solutions:")
        print("1. SSH to production server")
        print("2. cd /var/www/emteegee")
        print("3. bash deploy_production.sh")

if __name__ == "__main__":
    main()
