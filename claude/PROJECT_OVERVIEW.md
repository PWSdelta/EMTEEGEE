# EMTEEGEE Project Overview for Claude 4.0+

**Generated**: 2025-01-27  
**Purpose**: Claude context and development assistant reference  
**Project Status**: Core Infrastructure Complete - Ready for API Development

---

## 🎯 Project Summary

**EMTEEGEE** is a production-ready Django + MongoDB platform for Magic: The Gathering card analysis, built by migrating from a Flask-based system. The core infrastructure is complete with full MTGJson integration.

### ✅ What's Working (Tested & Verified)
- **Django 5.2.3** with dual database setup (MongoDB + SQLite)
- **Complete MTGJson Import Pipeline** (32,811+ cards, 1000+ decks)
- **Production-ready settings** with environment configuration
- **Django Admin Interface** with custom MongoDB model wrappers
- **Google OAuth Integration** via django-allauth
- **Comprehensive Management Commands** with Windows PowerShell support
- **Living Documentation** in `/claude` directory

### 🔄 Next Development Priorities
1. **REST API Endpoints** - Framework configured, ready to implement
2. **Card Analysis Features** - Models in place, algorithms needed
3. **User Interface** - Templates ready, need modern card browsing
4. **Background Tasks** - Celery/Redis configured, ready for use

---

## 📁 Project Structure

```
emteegee/
├── claude/                    # 📋 Claude documentation & context
│   ├── EMTEEGEE_LIVING_MANUAL.md    # Complete project manual
│   ├── EMTEEGEE_PRD.md              # Product requirements
│   ├── DEVELOPMENT_ROADMAP.md       # Next steps planning
│   └── PROJECT_OVERVIEW.md          # This file
├── cards/                     # 🃏 Core card management app
│   ├── models.py                     # MongoDB model wrappers
│   ├── admin.py                      # Django admin customization
│   ├── management/commands/          # MTGJson import commands
│   │   ├── import_atomic_cards.py    # Card import (32,811+ cards)
│   │   └── import_mtgjson_decks.py   # Deck import (1000+ decks)
├── emteegee/                  # ⚙️ Django project settings
│   ├── settings.py                   # Production-ready configuration
│   └── urls.py                       # URL routing
├── downloads/                 # 📥 MTGJson data (gitignored)
├── logs/                      # 📝 Application logs (gitignored)
├── templates/                 # 🎨 HTML templates
├── static/                    # 🎨 CSS, JS, images
├── users/                     # 👤 User management
├── analyses/                  # 🔍 Card analysis (future)
├── README.md                  # 📖 User-facing documentation
├── QUICK_START.md             # 🚀 Setup instructions
└── requirements.txt           # 📦 Python dependencies
```

---

## 🛠️ Core Technologies

### Production Stack
- **Django 5.2.3** - Web framework with admin interface
- **MongoDB** - Primary database for card/deck data via PyMongo
- **SQLite** - Django admin/auth database  
- **django-allauth** - Social authentication (Google OAuth)
- **Django REST Framework** - API framework (ready to use)
- **Celery + Redis** - Background tasks (configured)

### Import Pipeline
- **MTGJson Integration** - Complete AtomicCards.json import
- **Deck Metadata** - Batch download via decklist.json
- **Error Handling** - Comprehensive validation and logging
- **Progress Tracking** - Real-time import status

---

## 💾 Database Architecture

### MongoDB Collections (Primary Data)
```javascript
// cards collection (32,811+ documents)
{
  "uuid": "string",           // MTGJson unique identifier
  "name": "string", 
  "manaValue": number,
  "colors": ["string"],
  "types": ["string"],
  "text": "string",
  // ... complete MTGJson structure preserved
}

// decks collection (1000+ documents)
{
  "code": "string",           // Unique deck identifier
  "name": "string",
  "mainBoard": [{"uuid": "string", "count": number}],
  "sideBoard": [{"uuid": "string", "count": number}],
  "totalCards": number,
  "imported_at": "datetime"
}
```

### SQLite Tables (Django Admin)
- Standard Django auth tables (users, sessions, permissions)
- Admin logs and django-allauth tables

---

## 🔧 Management Commands (Production Ready)

### Card Import
```powershell
# Import complete MTGJson dataset
python manage.py import_atomic_cards --file downloads/AtomicCards.json

# Options: --dry-run, --limit, --update-existing, --verbosity
```

### Deck Import  
```powershell
# Batch download and import from MTGJson
python manage.py import_mtgjson_decks --download-from-decklist

# Options: --limit, --dry-run, --update-existing
```

### Status Checking
```powershell
# Test MongoDB connection and setup
python test_setup.py

# Check Django configuration
python manage.py check

# Quick data verification
python -c "from cards.models import Card, Deck; print(f'Cards: {Card.objects.count()}, Decks: {Deck.objects.count()}')"
```

---

## 🎯 Development Context for Claude

### When helping with EMTEEGEE:

1. **Reference the Living Manual** (`/claude/EMTEEGEE_LIVING_MANUAL.md`) for comprehensive details
2. **Use Windows PowerShell** commands (project developed on Windows 11)
3. **Preserve MTGJson structure** - don't modify the imported data format
4. **Follow Django best practices** - leverage built-in features
5. **Consider MongoDB patterns** - use PyMongo for complex queries
6. **Maintain dual database** - SQLite for Django, MongoDB for card data

### Common Development Tasks:
- **API Development**: REST endpoints for card/deck search
- **Analysis Features**: Mana curve, synergy detection, format checking
- **UI Enhancement**: Modern card browsing with Bootstrap 5
- **Performance**: MongoDB indexing, query optimization
- **Testing**: pytest-django for comprehensive coverage

### Key Files to Reference:
- **settings.py** - All configuration and database setup
- **models.py** - MongoDB model wrappers and query methods
- **import commands** - Data ingestion and validation patterns
- **Living Manual** - Complete troubleshooting and workflow guide

---

## 📊 Current State Metrics

- **Cards Imported**: 32,811 (complete MTGJson AtomicCards)
- **Decks Available**: 1,000+ (via decklist.json metadata)
- **Import Speed**: 1,000+ cards/second
- **Database Size**: ~150MB (complete dataset)
- **Memory Usage**: ~200-300MB (development)
- **Error Rate**: <0.1% (robust error handling)

---

## 🚀 Next Development Session

**Immediate Priority**: REST API implementation for card search
**Files to Create**: `cards/api_urls.py`, `cards/serializers.py`, `cards/views.py`
**Framework**: Django REST Framework (already configured)
**Testing**: Use existing card data for immediate validation

This project represents a solid foundation for a modern MTG analysis platform with all core infrastructure complete and ready for feature development.
