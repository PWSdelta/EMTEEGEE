import pymongo

# Connect directly to MongoDB
client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['emteegee_dev']
collection = db['cards']

print("Checking card collection...")

# Check if cards have analysis.components
cards_with_analysis = list(collection.find({
    "analysis.components": {"$exists": True, "$ne": {}}
}))

print(f"Found {len(cards_with_analysis)} cards with analysis.components")

if cards_with_analysis:
    for card in cards_with_analysis[:10]:
        name = card.get('name', 'Unknown')
        components = card.get('analysis', {}).get('components', {})
        count = len(components) if components else 0
        
        print(f"{name}: {count} components")
        print(f"  ID: {card.get('uuid')}")
        print(f"  URL: /cards/{card.get('uuid')}/")
        
        if count > 5:
            print(f"  ★ GOOD TEST CARD - {count} components!")
        print()
    
    # Find best card
    best = max(cards_with_analysis, key=lambda c: len(c.get('analysis', {}).get('components', {})))
    best_count = len(best.get('analysis', {}).get('components', {}))
    print(f"BEST: {best.get('name')} - {best_count} components")
    print(f"TEST URL: /cards/{best.get('_id')}/")
else:
    print("No cards found. Let me check what's actually in the database...")
    
    # Check total cards
    total = collection.count_documents({})
    print(f"Total cards: {total}")
    
    # Check structure
    sample = collection.find_one({})
    if sample:
        print(f"Sample card structure: {list(sample.keys())}")
        if 'analysis' in sample:
            print(f"Analysis structure: {list(sample['analysis'].keys())}")