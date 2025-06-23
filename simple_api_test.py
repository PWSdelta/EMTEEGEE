import json
import urllib.request
import urllib.error

def test_api():
    base_url = "http://localhost:8001"
    endpoints = [
        ("/", "Main Page"),
        ("/api/swarm/status/", "Swarm Status"),
        ("/api/swarm/register/", "Swarm Register (GET)"),
    ]
    
    for endpoint, description in endpoints:
        url = base_url + endpoint
        print(f"\n=== Testing {description} ===")
        print(f"URL: {url}")
        
        try:
            with urllib.request.urlopen(url) as response:
                status = response.getcode()
                content_type = response.headers.get('Content-Type', 'Unknown')
                
                print(f"Status: {status}")
                print(f"Content-Type: {content_type}")
                
                if status == 200:
                    data = response.read().decode('utf-8')
                    if 'application/json' in content_type:
                        try:
                            json_data = json.loads(data)
                            print(f"JSON Response: {json.dumps(json_data, indent=2)}")
                        except:
                            print(f"Invalid JSON: {data[:200]}...")
                    else:
                        print(f"HTML/Text Response: {data[:200]}...")
                else:
                    print(f"HTTP Error: {status}")
                    
        except urllib.error.HTTPError as e:
            print(f"HTTP Error {e.code}: {e.reason}")
        except Exception as e:
            print(f"Connection Error: {e}")

if __name__ == "__main__":
    test_api()
