# EMTEEGEE Living Manual
## Complete Project Documentation & Development Guide

**Generated:** June 22, 2025  
**Purpose:** Comprehensive documentation for EMTEEGEE AI-powered MTG card analysis platform  
**For:** Future development, onboarding, and system understanding

---

## 🎯 Project Overview

**EMTEEGEE** is a sophisticated AI-powered Magic: The Gathering card analysis platform built with Django and MongoDB. It represents the evolution from a Flask-based system (MagicAI) to a production-ready Django platform with distributed AI analysis capabilities.

### Core Value Proposition
- **29,448 Magic cards** imported from MTGJson/Scryfall
- **82 fully analyzed cards** with comprehensive AI analysis (20 components each)
- **Distributed swarm system** for AI analysis across multiple machines
- **Production-ready infrastructure** with Django, MongoDB, and background processing

---

## 🏗️ Architecture Overview

### Technology Stack
```
Production Stack:
├── Django 5.2.3              # Web framework with admin interface
├── MongoDB                   # Primary database for card/analysis data
├── SQLite                    # Django admin/auth database
├── Redis                     # Background task queues (optional)
├── Ollama                    # Local AI model hosting
└── PyMongo                   # MongoDB Python driver

Development Tools:
├── django-allauth            # Social authentication (Google OAuth)
├── Django REST Framework     # API framework (configured, not implemented)
├── Celery                    # Background task processing
└── dotenv                    # Environment variable management
```

### Database Architecture

#### MongoDB Collections (Primary Data)
```javascript
// cards collection (29,448+ documents)
{
  "uuid": "string",           // MTGJson unique identifier
  "name": "string",
  "mana_cost": "{1}{U}",
  "mana_value": number,
  "colors": ["string"],
  "types": ["string"],
  "oracle_text": "string",
  "analysis": {               // AI analysis data
    "fully_analyzed": true,
    "component_count": 20,
    "analysis_started_at": ISODate,
    "analysis_completed_at": ISODate,
    "components": {
      "play_tips": {
        "content": "...",
        "model_used": "llama3.2:latest",
        "created_at": ISODate,
        "word_count": 290,
        "tokens_used": 374
      },
      // ... 19 more components
    }
  }
  // ... complete MTGJson structure preserved
}

// decks collection (1000+ documents)
{
  "code": "string",           // Unique deck identifier
  "name": "string",
  "mainBoard": [{"uuid": "string", "count": number}],
  "sideBoard": [{"uuid": "string", "count": number}],
  "totalCards": number,
  "releaseDate": ISODate
}
```

#### SQLite Tables (Django Admin)
- Standard Django auth tables
- User management
- Admin interface data

---

## 🤖 AI Analysis System

### The Four Ollama Models

The system uses 4 different AI models, each optimized for specific analysis types:

```python
OLLAMA_MODELS = {
    'llama3.2:latest': {
        'name': 'Efficient Model',
        'use_case': 'Quick analysis, play tips, rules clarifications',
        'components': ['play_tips', 'rules_clarifications', 'mulligan_considerations']
    },
    'llama3.1:latest': {
        'name': 'Balanced Model', 
        'use_case': 'General analysis, synergies, formats',
        'components': ['thematic_analysis', 'synergy_analysis', 'format_analysis', 
                      'deck_archetypes', 'sideboard_guide', 'art_flavor_analysis']
    },
    'llama3.3:70b': {
        'name': 'Premium Model',
        'use_case': 'Deep analysis, competitive play, complex interactions',
        'components': ['tactical_analysis', 'power_level_assessment', 'competitive_analysis',
                      'investment_outlook', 'meta_positioning', 'advanced_interactions']
    },
    'mistral:7b': {
        'name': 'Alternative Perspective',
        'use_case': 'Budget options, beginner content, historical context',
        'components': ['budget_alternatives', 'historical_context', 'new_player_guide',
                      'design_philosophy']
    }
}
```

### The 20 Analysis Components

Each analyzed card receives 20 distinct analysis components:

#### Strategic Components (6)
1. **tactical_analysis** - Deep mechanical breakdown (llama3.3:70b)
2. **power_level_assessment** - Overall power evaluation (llama3.3:70b)
3. **competitive_analysis** - Tournament viability (llama3.1:latest)
4. **synergy_analysis** - Card interactions (llama3.1:latest)
5. **meta_positioning** - Current metagame role (llama3.3:70b)
6. **advanced_interactions** - Complex rules scenarios (llama3.3:70b)

#### Practical Components (6)
7. **play_tips** - Practical usage advice (llama3.2:latest)
8. **combo_suggestions** - Synergistic cards (llama3.1:latest)
9. **format_analysis** - Performance across formats (llama3.1:latest)
10. **deck_archetypes** - Suitable deck types (llama3.1:latest)
11. **mulligan_considerations** - Keep/mulligan decisions (llama3.2:latest)
12. **sideboard_guide** - Sideboarding strategies (llama3.1:latest)

#### Educational Components (4)
13. **new_player_guide** - Beginner explanations (mistral:7b)
14. **rules_clarifications** - Common rules questions (llama3.2:latest)
15. **budget_alternatives** - Cheaper similar cards (mistral:7b)
16. **historical_context** - MTG history perspective (mistral:7b)

#### Thematic Components (4)
17. **thematic_analysis** - Lore and flavor (llama3.1:latest)
18. **art_flavor_analysis** - Artistic elements (llama3.1:latest)
19. **design_philosophy** - Design intent (mistral:7b)
20. **investment_outlook** - Financial/collectible value (llama3.3:70b)

### Analysis Quality
- **High-quality content**: 300-900 words per component
- **Multiple perspectives**: Different AI models for different analysis types
- **Structured data**: Consistent formatting and metadata
- **Rich insights**: Deep strategic and educational content

---

## 🐝 Swarm Distribution System

### Architecture
The swarm system distributes AI analysis work across multiple machines based on their capabilities:

#### Central Server (Manages work distribution)
- Django web interface
- MongoDB for card storage
- Redis for work queues
- RESTful API for worker communication

#### Worker Types
- **Desktop (RTX 3070, 64GB RAM)**: Fast GPU-accelerated components
  - Components: play_tips, rules_clarifications, combo_suggestions, format_analysis
- **Laptop (128GB RAM, Big CPU)**: Deep analysis with large models
  - Components: thematic_analysis, historical_context, design_philosophy, advanced_interactions

### Work Distribution Strategy
```python
GPU_COMPONENTS = [
    'play_tips', 'mulligan_considerations', 'rules_clarifications',
    'combo_suggestions', 'format_analysis', 'synergy_analysis',
    'competitive_analysis', 'tactical_analysis'
]

CPU_HEAVY_COMPONENTS = [
    'thematic_analysis', 'historical_context', 'art_flavor_analysis',
    'design_philosophy', 'advanced_interactions', 'meta_positioning'
]

BALANCED_COMPONENTS = [
    'budget_alternatives', 'deck_archetypes', 'new_player_guide',
    'sideboard_guide', 'power_level_assessment', 'investment_outlook'
]
```

---

## 📁 Project Structure

```
emteegee/
├── claude/                    # 📋 Documentation & context (this folder)
│   ├── EMTEEGEE_LIVING_MANUAL.md    # This comprehensive guide
│   ├── EMTEEGEE_PRD.md              # Product requirements document
│   ├── VPS_DEPLOYMENT_PLAN.md       # Production deployment guide
│   ├── scripts/                     # Deployment automation scripts
│   └── settings_production.py       # Production Django settings
├── cards/                     # 🃏 Core card management Django app
│   ├── models.py                     # MongoDB model wrappers
│   ├── views.py                      # Card display logic
│   ├── admin.py                      # Django admin customization
│   ├── urls.py                       # URL routing for cards
│   ├── swarm_api.py                  # Swarm system API
│   ├── analysis_manager.py           # Analysis operations
│   └── management/commands/          # Management commands
│       ├── import_atomic_cards.py    # MTGJson card import
│       └── import_mtgjson_decks.py   # Deck import
├── analyses/                  # 🔍 Analysis Django app (future expansion)
├── users/                     # 👤 User management Django app
├── emteegee/                  # ⚙️ Django project settings
│   ├── settings.py                   # Main configuration
│   ├── urls.py                       # URL routing
│   └── wsgi.py                       # WSGI application
├── templates/                 # 🎨 HTML templates
│   ├── base.html                     # Base template
│   ├── cards/                        # Card-specific templates
│   └── home_simple.html              # Homepage
├── static/                    # 🎨 CSS, JS, images
├── downloads/                 # 📥 MTGJson data (gitignored)
├── logs/                      # 📝 Application logs (gitignored)
├── swarm_*.py                 # 🐝 Swarm system components
├── desktop_worker*.py         # 💻 Desktop worker implementations
├── laptop_worker*.py          # 💻 Laptop worker implementations
├── requirements.txt           # 📦 Python dependencies
├── .env                       # 🔐 Environment variables
└── README.md                  # 📖 User-facing documentation
```

---

## 🔧 Environment Configuration

### Key Environment Variables (.env)
```properties
# MongoDB Connection
MONGODB_CONNECTION_STRING=mongodb+srv://user:pass@cluster.mongodb.net/emteegee_dev?retryWrites=true&w=majority

# Django Settings
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=False
DJANGO_API_BASE_URL=https://mtgabyss.com

# Ollama Configuration
OLLAMA_HOST=http://localhost:11434

# Swarm Configuration
SWARM_SERVER_URL=http://localhost:8001
```

### Database Configuration
- **MongoDB**: Primary database for cards and analysis data
- **SQLite**: Django admin and authentication
- **Connection String**: Supports both local MongoDB and MongoDB Atlas

---

## 🚀 Development Workflow

### Local Development Setup
1. **Clone Repository**
2. **Install Dependencies**: `pip install -r requirements.txt`
3. **Configure Environment**: Set up `.env` file
4. **Setup MongoDB**: Local or Atlas connection
5. **Run Migrations**: `python manage.py migrate`
6. **Import Data**: Run card import commands
7. **Start Server**: `python manage.py runserver`

### Key Management Commands
```bash
# Import MTGJson card data
python manage.py import_atomic_cards

# Import deck data
python manage.py import_mtgjson_decks

# Check analysis status
python check_current_analysis.py

# Start swarm manager
python swarm_manager.py

# Start workers
python desktop_worker.py
python laptop_worker.py
```

---

## 📊 Current Status & Metrics

### Data Status (June 2025)
- ✅ **29,448 Magic cards** imported from MTGJson
- ✅ **1000+ decks** imported with metadata
- ✅ **82 cards fully analyzed** (20 components each = 1,640 AI insights)
- ✅ **Core infrastructure complete** and operational
- ✅ **Swarm system functional** with multi-machine support

### Analysis Pipeline Status
- **Total Analysis Components Generated**: 1,640+ (82 cards × 20 components)
- **Analysis Success Rate**: High quality, 300-900 words per component
- **Models in Use**: 4 Ollama models with specialized assignments
- **Background Processing**: Functional with retry logic

---

## 🎯 Development Priorities

### Immediate Priorities (High Impact)
1. **Enhanced Card Analysis Interface** 
   - Improve `templates/cards/card_detail.html` to showcase AI analysis
   - Display all 20 analysis components in organized tabs/sections
   - Add model attribution and analysis timestamps

2. **Analysis Browsing & Discovery**
   - Filter by analysis completeness (fully analyzed vs partial)
   - Search within analysis content (find cards mentioning "combo")
   - Sort by analysis quality, date, or popularity

3. **Analysis Queue Management**
   - Build interface to monitor analysis progress
   - Show cards in queue vs completed
   - Display analysis success/failure rates

4. **Content Enhancement**
   - Cross-reference system for card mentions in analyses
   - Parse card names like `[[Counterspell]]` and create links
   - Build "cards mentioned in this analysis" sections

### Medium-Term Development
5. **Advanced Analysis Features**
   - Analysis comparison tool (side-by-side card comparison)
   - Analysis export (PDF/markdown export)
   - User feedback system for analysis quality

6. **API Development**
   - RESTful endpoints for card and analysis data
   - Search API for programmatic access
   - Analysis API with filtering capabilities

7. **Educational Features**
   - Learning paths through card analyses for new players
   - Analysis tutorials and guides
   - Format-specific analysis aggregations

---

## 🔍 Key Files Reference

### Core Django Files
- `emteegee/settings.py` - Main Django configuration with MongoDB setup
- `cards/models.py` - MongoDB helper functions and collection access
- `cards/views.py` - Card display logic (needs analysis enhancement)
- `cards/urls.py` - URL routing for card views

### Analysis System Files
- `swarm_manager.py` - Central work distribution system
- `desktop_worker.py` - GPU-optimized worker for fast components
- `laptop_worker.py` - CPU-optimized worker for deep analysis
- `cards/analysis_manager.py` - Analysis operations and progress tracking

### Data Management Files
- `cards/management/commands/import_atomic_cards.py` - MTGJson import
- `check_current_analysis.py` - Analysis status verification
- `populate_work_queue.py` - Queue management for analysis jobs

### Templates & UI
- `templates/cards/card_detail.html` - Individual card display (needs enhancement)
- `templates/cards/home_simple.html` - Homepage with search
- `static/` - CSS, JavaScript, and images

---

## 🛠️ Technical Implementation Details

### MongoDB Integration Pattern
```python
def get_mongodb_collection(collection_name):
    """Get a MongoDB collection using Django settings."""
    mongodb_settings = settings.MONGODB_SETTINGS
    
    if 'connection_string' in mongodb_settings:
        client = pymongo.MongoClient(mongodb_settings['connection_string'])
    else:
        # Fallback to legacy host-based method
        client = pymongo.MongoClient(mongodb_settings['host'])
    
    db_name = mongodb_settings.get('db_name', 'emteegee_dev')
    db = client[db_name]
    return db[collection_name]
```

### Analysis Component Access
```python
# Access fully analyzed cards
cards_collection = get_cards_collection()
analyzed_cards = cards_collection.find({'analysis.fully_analyzed': True})

# Get specific analysis component
card = cards_collection.find_one({'name': 'Lightning Bolt'})
play_tips = card['analysis']['components']['play_tips']['content']
```

### Swarm Worker Registration
```python
# Worker capabilities detection
capabilities = {
    'hostname': socket.gethostname(),
    'cpu_cores': psutil.cpu_count(),
    'ram_gb': round(psutil.virtual_memory().total / (1024**3)),
    'gpu_available': check_gpu(),
    'worker_type': 'desktop',  # or 'laptop'
    'preferred_models': ['llama3.2:latest', 'llama3.1:latest']
}
```

---

## 📈 Business Value & Competitive Advantages

### Unique Value Propositions
1. **Comprehensive Coverage**: 20 analysis components vs typical 1-2
2. **Multi-Model AI**: Different AI models optimized for different analysis types
3. **Educational Focus**: Beginner-friendly with advanced strategic depth
4. **Strategic Depth**: Covers gameplay, deck building, meta analysis, and collecting
5. **Rich Metadata**: Detailed tracking of analysis quality and sources

### Target Users
- **New Magic Players**: Comprehensive beginner guides and explanations
- **Competitive Players**: Deep strategic analysis and meta positioning
- **Deck Builders**: Synergy analysis and archetype recommendations
- **Collectors**: Investment outlook and historical context
- **Content Creators**: Rich analysis content for articles and videos

---

## 🚨 Known Issues & Technical Debt

### Current Limitations
1. **UI/UX**: Analysis display needs significant enhancement
2. **Search**: Analysis content not yet searchable
3. **Performance**: Large MongoDB queries not optimized
4. **API**: REST endpoints configured but not implemented
5. **Documentation**: Some analysis quality metrics missing

### Migration Legacy (Flask → Django)
- Original system: MagicAI (Flask-based, 1,762 lines in app.py)
- Performance issues: Card mention linker, component workshop blocking
- Route errors: Cards redirecting to search page
- Memory usage: Large MongoDB queries not optimized

---

## 🔗 External Integrations

### Data Sources
- **MTGJson**: Primary card data source (AtomicCards.json)
- **Scryfall**: Secondary data source and imagery
- **EDHREC**: Deck popularity and meta analysis data

### AI Infrastructure
- **Ollama**: Local AI model hosting (http://localhost:11434)
- **Models**: llama3.2, llama3.1, llama3.3:70b, mistral:7b
- **GPU Support**: NVIDIA GPU acceleration for compatible models

### Production Services
- **MongoDB Atlas**: Cloud database hosting
- **Domain**: mtgabyss.com (primary), tcgplex.com (legacy)
- **Deployment**: VPS deployment with Nginx and SSL

---

## 📝 Development Notes

### Recent Insights (June 2025)
- Analysis system is the core competitive advantage
- Focus should be on showcasing the 1,640+ existing AI insights
- UI enhancement will have immediate user impact
- Cross-referencing system will create powerful content discovery
- Analysis search functionality will differentiate from competitors

### Architecture Decisions
- MongoDB chosen for flexible schema and large dataset handling
- Django chosen for rapid development and admin interface
- Swarm system enables cost-effective distributed AI processing
- Multiple AI models provide diverse analysis perspectives

### Future Considerations
- Consider caching layer (Redis) for performance
- Implement comprehensive testing suite
- Add monitoring and alerting for production
- Develop mobile-responsive interface
- Consider GraphQL API for flexible data access

---

## 🎓 Learning Resources

### Magic: The Gathering Knowledge
- Understanding of MTG rules, formats, and competitive play
- Knowledge of deck archetypes and meta game concepts
- Familiarity with card evaluation and strategic analysis

### Technical Skills
- Django web development and MongoDB integration
- AI/ML concepts and local model deployment (Ollama)
- Background task processing (Celery/Redis)
- Full-stack web development (HTML, CSS, JavaScript)

---

## 📞 Quick Reference

### Useful Commands
```bash
# Check analysis status
python check_current_analysis.py

# View specific card analysis
python check_specific_card.py "Lightning Bolt"

# Monitor analysis progress
python check_analysis_status.py

# Start swarm components
python swarm_manager.py        # Central coordinator
python desktop_worker.py      # GPU worker
python laptop_worker.py       # CPU worker

# Django management
python manage.py runserver     # Start development server
python manage.py shell         # Django shell with MongoDB access
python manage.py collectstatic # Collect static files
```

### Database Queries
```javascript
// MongoDB shell queries
db.cards.countDocuments({'analysis.fully_analyzed': true})  // Count analyzed cards
db.cards.findOne({'name': 'Lightning Bolt'})               // Get specific card
db.cards.find({'analysis.fully_analyzed': true}).limit(10) // Sample analyzed cards
```

---

**Last Updated:** June 22, 2025  
**Version:** 1.0  
**Author:** AI Assistant (Claude) with project analysis

This living manual should be updated as the project evolves. It serves as the single source of truth for understanding EMTEEGEE's architecture, capabilities, and development direction.
