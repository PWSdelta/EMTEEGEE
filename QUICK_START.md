# 🎯 Quick Start Guide - MagicAI Django + MongoDB

## Ready to Import MTGJson Data!

Your Django + MongoDB setup is complete and ready to import MTGJson data. Here's how to get started:

### 🚀 Step 1: Install Dependencies
```powershell
pip install -r requirements.txt
```

### ⚙️ Step 2: Configure Environment
```powershell
# Copy and edit environment file
copy .env.example .env
# Edit .env with your MongoDB settings
```

### 📦 Step 3: Import MTGJson Card Data
```powershell
# Import all MTG cards (AtomicCards.json from MTGJson)
# This downloads ~200MB+ and imports 50,000+ cards
python manage.py import_atomic_cards --dry-run  # Test first
python manage.py import_atomic_cards             # Import for real

# Or download file first, then import
python manage.py import_atomic_cards --download-only
python manage.py import_atomic_cards --file AtomicCards.json
```

### 🃏 Step 4: Import MTGJson Deck Data
```powershell
# Download deck files from: https://mtgjson.com/downloads/all-decks/
# Extract the JSON files, then:

python manage.py import_mtgjson_decks --path /path/to/deck/files/ --dry-run
python manage.py import_mtgjson_decks --path /path/to/deck/files/
```

### ✅ Step 5: Test & Run
```powershell
# Test your setup
python test_setup.py

# Create admin user
python manage.py createsuperuser

# Start the server
python manage.py runserver
```

## 📊 What You'll Get

### Cards Database
- **Source**: MTGJson AtomicCards.json
- **Format**: Exact MTGJson structure preserved
- **Fields**: `manaCost`, `manaValue`, `colorIdentity`, etc.
- **Count**: 50,000+ unique cards

### Decks Database  
- **Source**: MTGJson deck files
- **Format**: `mainBoard`, `sideBoard`, `commander` as JSON arrays
- **Types**: Tournament decks, precons, casual decks
- **Count**: Thousands of deck lists

### API Endpoints
- `/api/cards/` - Card listings with filtering
- `/api/decks/` - Deck listings  
- `/admin/` - Django admin interface

## 🗂️ Data Structure

### Card Document (MongoDB)
```json
{
  "uuid": "card-uuid",
  "name": "Lightning Bolt",
  "manaCost": "{R}",
  "manaValue": 1,
  "type": "Instant",
  "text": "Lightning Bolt deals 3 damage to any target.",
  "colors": ["R"],
  "colorIdentity": ["R"],
  "rarity": "common",
  "setCode": "LEA",
  "fully_analyzed": false
}
```

### Deck Document (MongoDB)
```json
{
  "name": "Red Deck Wins",
  "type": "deck", 
  "code": "SET",
  "mainBoard": [
    {
      "count": 4,
      "uuid": "card-uuid",
      "name": "Lightning Bolt"
    }
  ],
  "sideBoard": [],
  "commander": []
}
```

## 🎯 Import Commands Summary

| Command | Purpose | Source |
|---------|---------|---------|
| `import_atomic_cards` | Import all MTG cards | https://mtgjson.com/api/v5/AtomicCards.json |
| `import_mtgjson_decks` | Import deck lists | https://mtgjson.com/downloads/all-decks/ |

## 🔧 Development Commands

```powershell
# Test connection
python test_setup.py

# Import cards (full database)
python manage.py import_atomic_cards

# Import cards (testing - first 1000)
python manage.py import_atomic_cards --limit 1000

# Import decks
python manage.py import_mtgjson_decks --path ./deck_files/

# Run development server
python manage.py runserver

# Access admin
# http://localhost:8000/admin/
```

That's it! You're ready to build a comprehensive MTG database with Django + MongoDB! 🎉
