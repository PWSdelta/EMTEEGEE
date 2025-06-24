import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.models import get_cards_collection

cards = get_cards_collection()

print("🔍 Searching for Sol Ring and cards with many components...")

# Search for Sol Ring specifically
sol_ring = cards.find_one({'name': 'Sol Ring'})
if sol_ring:
    analysis = sol_ring.get('analysis', {})
    uuid = sol_ring.get('uuid', '')
    component_count = analysis.get('component_count', 0)
    components = analysis.get('components', {})
    
    print("\n🎯 Sol Ring Found!")
    print(f"   UUID: {uuid}")
    print(f"   Component Count: {component_count}")
    print(f"   Components Type: {type(components)}")
    if isinstance(components, dict):
        print(f"   Components Keys: {list(components.keys())[:5]}")
    print(f"   URL: http://127.0.0.1:8000/card/{uuid}/")
else:
    print("❌ Sol Ring not found")

# Find cards with most components
print("\n🏆 Cards with Most Components:")
high_cards = list(cards.find({
    'analysis.component_count': {'$gt': 10}
}).sort([('analysis.component_count', -1)]).limit(10))

for i, card in enumerate(high_cards, 1):
    name = card.get('name', 'Unknown')
    uuid = card.get('uuid', '')
    analysis = card.get('analysis', {})
    component_count = analysis.get('component_count', 0)
    components = analysis.get('components', {})
    
    print(f"\n{i}. {name}")
    print(f"   UUID: {uuid}")
    print(f"   Component Count: {component_count}")
    print(f"   Components: {len(components) if isinstance(components, dict) else 'Empty'} entries")
    print(f"   URL: http://127.0.0.1:8000/card/{uuid}/")
    
    # Check first component for content
    if isinstance(components, dict) and components:
        first_key = next(iter(components.keys()))
        first_component = components[first_key]
        if isinstance(first_component, dict) and 'content' in first_component:
            content_length = len(first_component['content'])
            print(f"   ✅ Sample content length: {content_length} chars")
        else:
            print(f"   ⚠️  Component structure: {type(first_component)}")

print("\n🚀 Use any of these URLs to test the improved card detail page!")
