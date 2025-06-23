# Quick check of analysis status and art images
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emteegee.settings')
django.setup()

from cards.models import get_cards_collection

cards = get_cards_collection()

print("Checking analyzed cards...")
analyzed_count = cards.count_documents({'analysis.fully_analyzed': True})
print(f"Cards with analysis.fully_analyzed=True: {analyzed_count}")

# Check specific cards with analysis
sample_analyzed = list(cards.find({'analysis.fully_analyzed': True}).limit(3))
print(f"\nSample analyzed cards ({len(sample_analyzed)}):")
for card in sample_analyzed:
    name = card.get('name', 'Unknown')
    has_art_crop = 'art_crop' in card.get('imageUris', {})
    print(f"  - {name}: art_crop={has_art_crop}")

# Check A Little Chat specifically
little_chat = cards.find_one({'name': 'A Little Chat'})
if little_chat:
    is_analyzed = little_chat.get('analysis', {}).get('fully_analyzed', False)
    has_art = 'art_crop' in little_chat.get('imageUris', {})
    print(f"\nA Little Chat:")
    print(f"  - Analysis fully_analyzed: {is_analyzed}")
    print(f"  - Has art_crop: {has_art}")
    if has_art:
        print(f"  - Art URL: {little_chat['imageUris']['art_crop'][:60]}...")

# Count analyzed cards with art images
analyzed_with_art = cards.count_documents({
    'analysis.fully_analyzed': True,
    'imageUris.art_crop': {'$exists': True, '$ne': None}
})
print(f"\nAnalyzed cards with art images: {analyzed_with_art}")
