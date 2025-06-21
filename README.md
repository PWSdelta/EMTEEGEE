# EMTEEGEE - Django Migration

A comprehensive Magic: The Gathering card analysis platform with AI-powered reviews, deck analysis, and pricing data. This Django application uses MongoDB and imports data directly from MTGJson.

## 🚀 Features

### Cards
- **AI-Powered Analysis**: Comprehensive card reviews using multiple AI models
- **Advanced Search**: Search by name, text, colors, mana cost, and more
- **Price Tracking**: Historical pricing data from multiple sources
- **Rich Card Display**: High-quality images, mana symbols, and detailed information

### Decks (MTGJson Import)
- **MTGJson Integration**: Direct import from MTGJson deck files
- **Comprehensive Deck Database**: Access to thousands of tournament and casual decks
- **Deck Analysis**: AI-powered strategy analysis, mana curve, and synergy analysis
- **Format Support**: All MTGJson supported formats

### User Features
- **User Accounts**: Registration, profiles, and preferences
- **Favorites**: Save favorite cards
- **Personalized Content**: Recommendations based on user activity

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.11+
- MongoDB 6.0+ (local or cloud)
- Redis 6+ (for caching and background tasks)
- Git

### 1. Clone and Setup Environment

```powershell
# Clone the repository
git clone <your-repo-url>
cd emteegee

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # On Windows
# source venv/bin/activate  # On macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

```powershell
# Copy environment template
copy .env.example .env

# Edit .env file with your MongoDB settings
notepad .env
```

Key environment variables:
- `SECRET_KEY`: Django secret key (generate a new one for production)
- `DEBUG`: Set to `False` in production
- `MONGODB_URI`: MongoDB connection string
- `DB_NAME`: Database name (default: `emteegee_dev`)

### 3. Database Setup

#### MongoDB Setup
```powershell
# Make sure MongoDB is running
# Local: mongod --dbpath /path/to/data/directory
# Or use MongoDB Atlas (cloud)

# Run Django setup (no migrations needed for MongoDB)
python manage.py collectstatic

# Create superuser
python manage.py createsuperuser
```

### 4. Import Data

#### Import MTGJson Card Data (AtomicCards)
```powershell
# Download and import AtomicCards directly from MTGJson
python manage.py import_atomic_cards --dry-run

# Import for real (this will take a while - ~200MB+ file)
python manage.py import_atomic_cards

# Import from local file (if already downloaded)
python manage.py import_atomic_cards --file AtomicCards.json

# Import with limit for testing
python manage.py import_atomic_cards --limit 1000

# Update existing cards
python manage.py import_atomic_cards --update-existing
```

#### Import MTGJson Deck Files
```powershell
# Download deck files from MTGJson
# https://mtgjson.com/downloads/all-decks/

# Import deck files (dry run first)
python manage.py import_mtgjson_decks --path /path/to/mtgjson/deck/files/ --dry-run

# Import for real
python manage.py import_mtgjson_decks --path /path/to/mtgjson/deck/files/ --limit 100

# Update existing decks
python manage.py import_mtgjson_decks --path /path/to/mtgjson/deck/files/ --update-existing
```

#### Import Cards from MongoDB (if migrating from Flask)
```powershell
# If you have existing card data in MongoDB
python manage.py migrate_from_mongodb --mongo-url mongodb://localhost:27017/ --database MagicAI --dry-run

# Remove --dry-run when ready to import
python manage.py migrate_from_mongodb --mongo-url mongodb://localhost:27017/ --database MagicAI
```

### 5. Run the Development Server

```powershell
# Start Django development server
python manage.py runserver

# Access the application
# http://localhost:8000/
```

### 6. Background Tasks (Optional)

```powershell
# Install and start Redis
# Download from: https://redis.io/download

# Start Celery worker (in separate terminal)
celery -A emteegee worker --loglevel=info

# Start Celery beat (for scheduled tasks)
celery -A emteegee beat --loglevel=info
```

## 📁 Project Structure

```
emteegee/
├── cards/                  # Card and deck models, views
│   ├── models.py          # Card, Deck models (MongoDB/Djongo)
│   ├── views.py           # Card and deck views
│   ├── api_views.py       # REST API endpoints
│   ├── admin.py           # Django admin configuration
│   └── management/
│       └── commands/
│           └── import_mtgjson_decks.py
├── analyses/              # AI analysis components
│   ├── models.py          # AnalysisComponent, PriceHistory models
│   └── views.py           # Analysis management views
├── users/                 # User management
│   ├── models.py          # Custom User, UserFavorite models
│   └── views.py           # Authentication and profile views
├── templates/             # Django templates
│   ├── base.html          # Base template with Bootstrap 5.3.2
│   └── cards/             # Card-specific templates
├── static/                # Static files (CSS, JS, images)
├── emteegee/              # Django project settings
│   ├── settings.py        # Main settings file (MongoDB config)
│   ├── urls.py            # URL configuration
│   └── wsgi.py            # WSGI configuration
└── requirements.txt       # Python dependencies
```

## 🔧 MongoDB Configuration

### Database Models

#### Card Model (MTGJson Format)
- Uses MTGJson field names: `manaCost`, `manaValue`, `colorIdentity`
- Stored in `cards` collection
- Supports all MTGJson card attributes
- Includes analysis status tracking

#### Deck Model (MTGJson Format)
- Direct import from MTGJson deck files
- Stores `mainBoard`, `sideBoard`, `commander` as JSON arrays
- No user deck creation - import only
- Stored in `decks` collection

### MTGJson Deck Import

The system imports deck files directly from MTGJson format:

```json
{
  "data": {
    "Deck Name": {
      "code": "SET",
      "mainBoard": [
        {
          "count": 4,
          "uuid": "card-uuid",
          "name": "Card Name"
        }
      ],
      "sideBoard": [],
      "commander": []
    }
  }
}
```

## 🚀 Deployment

### Production Setup

1. **Environment Variables**
```bash
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
MONGODB_URI=mongodb://user:pass@host:port/database
DB_NAME=emteegee_prod
REDIS_URL=redis://localhost:6379/0
```

2. **Static Files**
```bash
python manage.py collectstatic
```

3. **Web Server**
```bash
# Using Gunicorn
gunicorn emteegee.wsgi:application --bind 0.0.0.0:8000
```

## 📊 MTGJson Integration

### Supported Deck Formats

The system is designed specifically for MTGJson deck files:

- **Tournament Decks**: Pro Tour, Grand Prix, etc.
- **Casual Decks**: Community submitted decks
- **Preconstructed Decks**: Official Wizards products
- **Commander Decks**: EDH format support

### Import Process

1. Download deck files from [MTGJson All Decks](https://mtgjson.com/downloads/all-decks/)
2. Extract JSON files
3. Run import command: `python manage.py import_mtgjson_decks --path /path/to/files/`
4. Decks are stored with full MTGJson structure preserved

## 🧪 Testing

```powershell
# Run tests
python manage.py test

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **MTGJson**: Comprehensive MTG data and deck files
- **Scryfall API**: Card data and images
- **Django Community**: Framework and ecosystem
- **Bootstrap**: UI framework

---

**Note**: This application is designed specifically for MTGJson deck import. Users cannot create decks through the UI - all deck data comes from MTGJson files. The focus is on analysis and browsing of existing tournament and casual deck data.

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.11+
- MongoDB 6.0+ (running locally or via Docker)
- Redis 6+ (for caching and background tasks)
- Git

### 1. Clone and Setup Environment

```powershell
# Clone the repository
git clone <your-repo-url>
cd emteegee

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # On Windows
# source venv/bin/activate  # On macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### 2. MongoDB Setup

```powershell
# Option 1: Install MongoDB locally
# Download from https://www.mongodb.com/try/download/community

# Option 2: Use Docker
docker run -d -p 27017:27017 --name mongodb mongo:6.0

# The application expects a database named 'emteegee_dev'
# MongoDB will create it automatically when first accessed
```

### 3. Environment Configuration

```powershell
# Copy the MongoDB environment template
cp .env.mongodb .env

# Edit .env with your MongoDB connection details
# The defaults should work for local MongoDB installation
```

### 4. Database Setup

```powershell
# Run Django migrations (these work with djongo/MongoDB)
python manage.py migrate

# Create a superuser account
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput
```
# Copy environment template
copy .env.example .env

# Edit .env file with your settings
notepad .env
```

Key environment variables:
- `SECRET_KEY`: Django secret key (generate a new one for production)
- `DEBUG`: Set to `False` in production
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `USE_SQLITE`: Set to `True` for SQLite development setup

### 3. Database Setup

#### Option A: PostgreSQL (Recommended)
```powershell
# Install PostgreSQL and create database
createdb magicai_django

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

#### Option B: SQLite (Development Only)
```powershell
# Set in .env file
USE_SQLITE=True

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 4. Import Data

#### Import Cards from MongoDB (if migrating from Flask)
```powershell
# Install pymongo if not already installed
pip install pymongo

# Run migration command
python manage.py migrate_from_mongodb --mongo-url mongodb://localhost:27017/ --database MagicAI --dry-run

# Remove --dry-run when ready to import
python manage.py migrate_from_mongodb --mongo-url mongodb://localhost:27017/ --database MagicAI
```

#### Import Deck Files
```powershell
# Import deck files from directory
python manage.py import_decks --path /path/to/deck/files/ --dry-run

# Import specific formats
python manage.py import_decks --path /path/to/deck/files/ --format mtga --limit 100

# Skip decks with missing cards
python manage.py import_decks --path /path/to/deck/files/ --skip-missing-cards
```

### 5. Run the Development Server

```powershell
# Start Django development server
python manage.py runserver

# Access the application
# http://localhost:8000/
```

### 6. Background Tasks (Optional)

```powershell
# Install and start Redis
# Download from: https://redis.io/download

# Start Celery worker (in separate terminal)
celery -A emteegee worker --loglevel=info

# Start Celery beat (for scheduled tasks)
celery -A emteegee beat --loglevel=info
```

## 📁 Project Structure

```
emteegee/
├── cards/                  # Card models, views, and deck functionality
│   ├── models.py          # Card, Deck, DeckCard, DeckAnalysis models
│   ├── views.py           # Card and deck views
│   ├── api_views.py       # REST API endpoints
│   ├── admin.py           # Django admin configuration
│   └── management/
│       └── commands/
│           ├── migrate_from_mongodb.py
│           └── import_decks.py
├── analyses/              # AI analysis components
│   ├── models.py          # AnalysisComponent, PriceHistory models
│   └── views.py           # Analysis management views
├── users/                 # User management
│   ├── models.py          # Custom User, UserFavorite, UserCollection
│   └── views.py           # Authentication and profile views
├── templates/             # Django templates
│   ├── base.html          # Base template with Bootstrap 5.3.2
│   └── cards/             # Card-specific templates
├── static/                # Static files (CSS, JS, images)
├── emteegee/              # Django project settings
│   ├── settings.py        # Main settings file
│   ├── urls.py            # URL configuration
│   └── wsgi.py            # WSGI configuration
└── requirements.txt       # Python dependencies
```

## 🔧 Configuration

### Database Models

#### Card Model
- Migrated from MongoDB `cards` collection
- Supports all MTG card attributes
- Includes analysis status tracking
- Indexed for performance

#### Deck Models
- `Deck`: Main deck information
- `DeckCard`: Cards in decks with quantities
- `DeckAnalysis`: AI-powered deck analysis
- `DeckStats`: Calculated deck statistics

#### Analysis Models
- `AnalysisComponent`: AI-generated card analysis
- `PriceHistory`: Historical price tracking

### API Endpoints

#### Cards API
- `GET /api/cards/` - List cards with filtering
- `GET /api/cards/{id}/` - Card details
- `GET /api/cards/search/` - Search cards
- `GET /api/cards/random/` - Random card
- `GET /api/cards/stats/` - Database statistics

#### Decks API
- `GET /api/decks/` - List decks with filtering
- `GET /api/decks/{id}/` - Deck details
- `GET /api/decks/search/` - Search decks
- `GET /api/decks/{id}/mana-curve/` - Deck mana curve

### Deck File Formats Supported

- **MTGO**: Magic Online deck files (.dec)
- **MTGA**: Magic Arena deck files (.txt)
- **JSON**: Moxfield, Archidekt, and other JSON formats
- **Text**: Generic text-based formats

## 🚀 Deployment

### Production Setup

1. **Environment Variables**
```bash
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
DATABASE_URL=postgresql://user:pass@localhost/magicai_django
REDIS_URL=redis://localhost:6379/0
```

2. **Static Files**
```bash
python manage.py collectstatic
```

3. **Database**
```bash
python manage.py migrate
```

4. **Web Server**
```bash
# Using Gunicorn
gunicorn emteegee.wsgi:application --bind 0.0.0.0:8000

# Using Nginx (recommended for production)
# Configure Nginx to proxy to Gunicorn
```

### Docker Deployment (Optional)

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "emteegee.wsgi:application", "--bind", "0.0.0.0:8000"]
```

## 🧪 Testing

```powershell
# Run tests
python manage.py test

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

## 📊 Performance Optimization

### Database Optimization
- Proper indexing on search fields
- Use `select_related()` and `prefetch_related()` for joins
- Database connection pooling
- Query optimization with `django-debug-toolbar`

### Caching
- Redis caching for frequent queries
- Template fragment caching
- API response caching

### Background Tasks
- Celery for AI analysis generation
- Scheduled tasks for price updates
- Queue management for bulk operations

## 🔍 Monitoring and Debugging

### Development Tools
- Django Debug Toolbar: `pip install django-debug-toolbar`
- Django Extensions: `pip install django-extensions`
- IPython: `pip install ipython`

### Production Monitoring
- Sentry for error tracking
- Django logging configuration
- Performance monitoring with APM tools

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Scryfall API**: Card data and images
- **MTGJson**: Comprehensive MTG data
- **Django Community**: Framework and ecosystem
- **Bootstrap**: UI framework
- **Claude AI**: Documentation and migration assistance

## 📞 Support

For issues and questions:
1. Check the GitHub Issues
2. Review the documentation
3. Create a new issue with detailed information

---

**Note**: This is a migration from a Flask application. The original MongoDB data can be imported using the provided management commands. The deck import feature supports 3000+ deck files for comprehensive testing and analysis.
