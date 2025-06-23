#!/usr/bin/env python3

# Simple test without Django setup to avoid mtgdb errors
import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.getcwd())

def test_simple_gallery():
    print("=== SIMPLE GALLERY TEST ===")
    
    # Let's just test if we can access the gallery URL directly
    try:
        import requests
        
        # Test the gallery URL
        response = requests.get('http://127.0.0.1:8000/gallery/', timeout=10)
        print(f"Gallery URL Status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            
            if 'Gallery is currently empty' in content:
                print("❌ Gallery shows as empty")
            else:
                print("✅ Gallery has content")
                
            if 'carousel-item' in content:
                print("✅ Gallery has carousel items")
                
            carousel_count = content.count('carousel-item')
            print(f"Carousel items found: {carousel_count}")
            
        else:
            print(f"❌ Gallery returned status {response.status_code}")
            
    except ImportError:
        print("requests module not available, trying with urllib")
        try:
            import urllib.request
            
            response = urllib.request.urlopen('http://127.0.0.1:8000/gallery/')
            content = response.read().decode('utf-8')
            
            if 'Gallery is currently empty' in content:
                print("❌ Gallery shows as empty")
            else:
                print("✅ Gallery has content")
                
            if 'carousel-item' in content:
                print("✅ Gallery has carousel items")
                
            carousel_count = content.count('carousel-item')
            print(f"Carousel items found: {carousel_count}")
            
        except Exception as e:
            print(f"❌ Error testing gallery: {e}")
    
    except Exception as e:
        print(f"❌ Error testing gallery: {e}")

if __name__ == "__main__":
    test_simple_gallery()
