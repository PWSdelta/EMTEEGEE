# 🃏 Scryfall Data Integration for EMTEEGEE

This module enhances your MTG card analysis app with rich data from Scryfall, including pricing, high-resolution images, format legalities, and comprehensive metadata.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
python setup_scryfall.py
```

### 2. Import Scryfall Data
```bash
# Import default cards dataset (recommended - 483MB)
python manage.py import_scryfall_data

# Or choose a specific dataset
python manage.py import_scryfall_data --dataset=oracle_cards
```

### 3. Enhanced Features Available
- 💰 **Real-time pricing** (USD, EUR, TIX, Foil)
- 🖼️ **High-resolution images** (multiple sizes)
- ⚖️ **Format legalities** (Standard, Modern, Legacy, etc.)
- 🎨 **Artist information** and artwork details
- 🔗 **Direct Scryfall links** for more info
- 📊 **Rich metadata** (keywords, Oracle text, etc.)

## 📊 Available Datasets

| Dataset | Size | Description |
|---------|------|-------------|
| `oracle_cards` | 155 MB | One card per Oracle ID (recommended for analysis) |
| `default_cards` | 483 MB | Every card in English (recommended for UI) |
| `unique_artwork` | 219 MB | Cards with unique artwork |
| `all_cards` | 2.23 GB | Every card in every language |

## 🎨 Template Usage

### Basic Scryfall Data Check
```django
{% if card|has_scryfall %}
    <p>Enhanced with Scryfall data!</p>
{% endif %}
```

### Display Card Image
```django
<!-- High resolution image -->
<img src="{{ card|scryfall_image:'large' }}" alt="{{ card.name }}">

<!-- Available sizes: small, normal, large, png, art_crop, border_crop -->
<img src="{{ card|scryfall_image:'art_crop' }}" alt="{{ card.name }}">
```

### Show Pricing
```django
<!-- USD price -->
<span class="price">{{ card|scryfall_price:"usd" }}</span>

<!-- Available price types: usd, usd_foil, eur, tix -->
<span class="foil-price">{{ card|scryfall_price:"usd_foil" }}</span>
```

### Format Legalities
```django
{% with card|scryfall_legalities as legalities %}
    {% for format, status in legalities.items %}
        {% if status == "legal" %}
            <span class="badge bg-success">{{ format|title }}</span>
        {% endif %}
    {% endfor %}
{% endwith %}
```

### Artist and Links
```django
<p>Artist: {{ card|card_artist }}</p>
<a href="{{ card|scryfall_url }}" target="_blank">View on Scryfall</a>
```

## 🏗️ Data Structure

After import, each card in MongoDB will have a `scryfall` field containing:

```json
{
  "scryfall": {
    "scryfall_id": "uuid",
    "oracle_id": "uuid", 
    "name": "Card Name",
    "uri": "https://scryfall.com/card/...",
    "layout": "normal",
    "cmc": 3,
    "type_line": "Creature — Human Wizard",
    "oracle_text": "Card text...",
    "mana_cost": "{2}{U}",
    "colors": ["U"],
    "color_identity": ["U"],
    "keywords": ["Flying"],
    "legalities": {
      "standard": "legal",
      "modern": "legal",
      "legacy": "legal"
    },
    "rarity": "rare",
    "set_code": "ZNR",
    "set_name": "Zendikar Rising",
    "artist": "Artist Name",
    "released_at": "2020-09-25",
    "images": {
      "small": "https://cards.scryfall.io/small/...",
      "normal": "https://cards.scryfall.io/normal/...",
      "large": "https://cards.scryfall.io/large/...",
      "png": "https://cards.scryfall.io/png/...",
      "art_crop": "https://cards.scryfall.io/art_crop/...",
      "border_crop": "https://cards.scryfall.io/border_crop/..."
    },
    "prices": {
      "usd": "1.50",
      "usd_foil": "3.00",
      "eur": "1.25",
      "tix": "0.5"
    },
    "purchase_uris": {
      "tcgplayer": "https://...",
      "cardmarket": "https://...",
      "cardhoarder": "https://..."
    }
  }
}
```

## 🛠️ Python API Usage

```python
from cards.scryfall_utils import ScryfallDataHelper

# Get card image URL
image_url = ScryfallDataHelper.get_best_image_url(card, 'large')

# Get formatted price
price = ScryfallDataHelper.format_price(card['scryfall']['prices']['usd'])

# Check format legality
is_legal = ScryfallDataHelper.is_card_legal_in_format(card, 'modern')

# Get all pricing data
prices = ScryfallDataHelper.get_card_prices(card)
```

## 🔄 Updating Data

Scryfall data updates daily. To keep your data fresh:

```bash
# Re-run the import (it will update existing cards)
python manage.py import_scryfall_data

# Check the log for import statistics
cat scryfall_import.log
```

## 📈 Import Statistics

After running the import, you'll see:
- **Updated existing cards**: Cards that already existed and got Scryfall data
- **New cards added**: Cards imported from Scryfall that weren't in your database
- **Errors**: Any cards that failed to process

## 🎯 UI/UX Enhancements

The Scryfall integration enables:

1. **Better Card Browsing**: High-quality images and pricing at a glance
2. **Comprehensive Analysis**: Format legalities and competitive viability
3. **Market Intelligence**: Price tracking and investment insights
4. **Visual Appeal**: Professional-quality artwork and layouts
5. **Direct Integration**: Links to purchase and more information

## 🚨 Important Notes

- **Pricing Freshness**: Prices are updated daily but consider them estimates
- **Rate Limiting**: Scryfall bulk data respects their rate limits
- **Storage**: Enhanced data will increase your MongoDB storage usage
- **Updates**: Re-running import updates existing cards safely

## 🔧 Troubleshooting

### Import Fails
```bash
# Check if requests is installed
pip install requests

# Check MongoDB connection
python manage.py check

# View detailed logs
tail -f scryfall_import.log
```

### Template Errors
```bash
# Ensure filters are loaded
{% load card_filters %}

# Check if card has Scryfall data
{% if card|has_scryfall %}
    <!-- Scryfall features here -->
{% endif %}
```

## 📚 Further Reading

- [Scryfall API Documentation](https://scryfall.com/docs/api)
- [Scryfall Bulk Data](https://scryfall.com/docs/api/bulk-data)
- [Card Object Structure](https://scryfall.com/docs/api/cards)
