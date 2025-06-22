# MagicAI - Product Requirements Document
## Technical Architecture & Migration Guide

**Document Version:** 1.0  
**Date:** June 21, 2025  
**Target Migration:** Flask → Django  
**Author:** System Analysis for Claude 4.0 Implementation

---

## 1. Executive Summary

MagicAI is a comprehensive Magic: The Gathering card analysis platform that generates AI-powered reviews, tracks pricing data, and provides detailed card information. The current Flask implementation has grown complex and requires migration to Django for better scalability, maintainability, and development efficiency.

### Key Goals
- **Primary:** Provide comprehensive MTG card analysis with AI-generated reviews
- **Secondary:** Track pricing trends, provide search/browse functionality
- **Tertiary:** Support user accounts, favorites, and personalized content

### Current State
- **Operational:** Core functionality works but performance issues exist
- **Database:** MongoDB with 201+ fully analyzed cards, 35,000+ total cards
- **Architecture:** Flask-based with complex component system
- **Issues:** Performance bottlenecks, routing problems, architectural debt

---

## 2. Technical Architecture Overview

### Current Flask Stack
```
Flask Application (app.py - 1,762 lines)
├── Routes (Blueprint-based)
│   ├── Main Routes (/routes/main_routes.py)
│   ├── Card Routes (/routes/card_routes.py) 
│   ├── Auth Routes (/routes/auth_routes.py)
│   ├── API Routes (/routes/api_routes.py)
│   └── Review Routes (/routes/review_routes.py)
├── Core Systems
│   ├── Component Workshop (AI generation)
│   ├── Card Mention Linker (performance issues)
│   ├── Price Analytics
│   ├── Job Management (Celery)
│   └── Multi-Color Review System
└── Data Layer
    ├── MongoDB (MagicAI database)
    ├── Collections: cards, review_components, users
    └── External APIs: Scryfall, MTGJson
```

### Database Schema (MongoDB → Django Models)

#### Cards Collection
```javascript
{
  "_id": ObjectId,
  "id": "scryfall_uuid",           // Primary identifier
  "name": "Card Name",
  "mana_cost": "{1}{R}",
  "cmc": 2,
  "type_line": "Creature — Human",
  "oracle_text": "Card text",
  "colors": ["R"],
  "color_identity": ["R"],
  "power": "2",
  "toughness": "1",
  "rarity": "common",
  "set": "set_code",
  "collector_number": "123",
  "image_uris": {},
  "prices": {},
  "legalities": {},
  "fully_analyzed": true,          // Key field for frontend
  "analysis_completed_at": Date,
  "component_count": 125
}
```

#### Review Components Collection
```javascript
{
  "_id": ObjectId,
  "card_id": ObjectId,             // References cards._id
  "component_type": "thematic_analysis",
  "content_markdown": "Review text",
  "content_html": "Processed HTML",
  "model_used": "llama3.2:latest",
  "created_at": Date,
  "is_active": true,
  "generation_metadata": {}
}
```

---

## 3. Core Features & User Stories

### Public Features (No Auth Required)
1. **Homepage** - Featured cards grid, stats, search
2. **Card Detail Pages** - Full card info + AI analysis
3. **Search & Browse** - Advanced filtering, pagination
4. **Price Tracking** - Historical price data, trends

### User Features (Auth Required)
1. **User Accounts** - Registration, login, profiles
2. **Favorites** - Save cards, create lists
3. **Personalized Content** - Recommendations based on activity

### Admin Features
1. **Content Generation** - Trigger AI review generation
2. **System Monitoring** - Job status, performance metrics
3. **Data Management** - Import/export, cleanup tools

---

## 4. Key Files & Components

### Critical Flask Files to Understand
```
app.py                          # Main Flask app (1,762 lines)
├── Core Configuration
├── Database connections
├── Blueprint registration
└── Route debugging

routes/
├── main_routes.py             # Homepage, browse, search
├── card_routes.py             # Card detail pages (BROKEN)
├── auth_routes.py             # User authentication
└── api_routes.py              # JSON API endpoints

Core Systems:
├── component_workshop.py      # AI review generation
├── card_mention_linker.py     # Cross-card linking (SLOW)
├── price_analytics.py         # Price tracking
├── celery_manager.py          # Background jobs
└── models.py                  # User management
```

### Templates (Jinja2 → Django Templates)
```
templates/
├── base.html                  # Bootstrap 5.3.2, responsive
├── index.html                 # Homepage with card grid
├── card_detail_v2.html        # Enhanced with Scrollspy
├── search.html                # Advanced search interface
└── browse.html                # Paginated card browser
```

### Static Assets
```
static/
├── css/enhanced-responsive.css
├── js/magic-ai-utils.js
├── js/search-widget.js
└── img/ (minimal usage)
```

---

## 5. Performance Issues & Solutions

### Current Problems
1. **Card Mention Linker** - Database query per card mention (O(n²) problem)
2. **Component Workshop** - Blocking AI generation calls
3. **Route Errors** - Cards redirecting to search page
4. **Memory Usage** - Large MongoDB queries not optimized

### Django Solutions
1. **ORM Optimization** - Use select_related(), prefetch_related()
2. **Caching** - Redis for frequent queries, template caching
3. **Background Tasks** - Celery integration with Django
4. **Database Indexing** - Proper indexes on search fields

---

## 6. Django Migration Strategy

### Phase 1: Data Model Migration
```python
# Django Models (approximate)
class Card(models.Model):
    scryfall_id = models.UUIDField(unique=True)  # From MongoDB.id
    name = models.CharField(max_length=200, db_index=True)
    mana_cost = models.CharField(max_length=100, blank=True)
    cmc = models.IntegerField(default=0)
    type_line = models.CharField(max_length=200)
    oracle_text = models.TextField(blank=True)
    colors = models.JSONField(default=list)
    power = models.CharField(max_length=10, blank=True)
    toughness = models.CharField(max_length=10, blank=True)
    rarity = models.CharField(max_length=20)
    fully_analyzed = models.BooleanField(default=False)
    analysis_completed_at = models.DateTimeField(null=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['fully_analyzed']),
            models.Index(fields=['colors']),
            models.Index(fields=['type_line']),
        ]

class ReviewComponent(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    component_type = models.CharField(max_length=50)
    content_markdown = models.TextField()
    content_html = models.TextField(blank=True)
    model_used = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['card', 'component_type']),
            models.Index(fields=['is_active']),
        ]
```

### Phase 2: View Migration
```python
# Django Views (class-based)
class CardDetailView(DetailView):
    model = Card
    template_name = 'cards/detail.html'
    context_object_name = 'card'
    slug_field = 'scryfall_id'
    slug_url_kwarg = 'card_id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['components'] = self.object.reviewcomponent_set.filter(
            is_active=True
        ).select_related('card')
        context['related_cards'] = Card.objects.filter(
            colors__overlap=self.object.colors
        ).exclude(id=self.object.id)[:5]
        return context

class CardSearchView(ListView):
    model = Card
    template_name = 'cards/search.html'
    context_object_name = 'cards'
    paginate_by = 24
    
    def get_queryset(self):
        qs = Card.objects.filter(fully_analyzed=True)
        query = self.request.GET.get('q')
        if query:
            qs = qs.filter(
                Q(name__icontains=query) |
                Q(oracle_text__icontains=query)
            )
        return qs
```

### Phase 3: URL Configuration
```python
# urls.py
urlpatterns = [
    path('', CardListView.as_view(), name='home'),
    path('card/<uuid:card_id>/', CardDetailView.as_view(), name='card_detail'),
    path('card/<uuid:card_id>/<slug:slug>/', CardDetailView.as_view(), name='card_detail_seo'),
    path('search/', CardSearchView.as_view(), name='search'),
    path('browse/', CardBrowseView.as_view(), name='browse'),
    path('api/cards/', include('cards.api_urls')),
]
```

---

## 7. Data Migration Plan

### MongoDB to PostgreSQL
```python
# Management command: migrate_cards.py
class Command(BaseCommand):
    def handle(self, *args, **options):
        mongo_client = MongoClient('mongodb://localhost:27017/')
        mongo_db = mongo_client['MagicAI']
        
        # Migrate cards
        for mongo_card in mongo_db.cards.find({}):
            Card.objects.update_or_create(
                scryfall_id=mongo_card['id'],
                defaults={
                    'name': mongo_card['name'],
                    'mana_cost': mongo_card.get('mana_cost', ''),
                    'fully_analyzed': mongo_card.get('fully_analyzed', False),
                    # ... other fields
                }
            )
        
        # Migrate components
        for component in mongo_db.review_components.find({}):
            card = Card.objects.get(scryfall_id=component['card_id'])
            ReviewComponent.objects.update_or_create(
                card=card,
                component_type=component['component_type'],
                defaults={
                    'content_markdown': component['content_markdown'],
                    'is_active': component.get('is_active', True),
                    # ... other fields
                }
            )
```

---

## 8. Configuration & Settings

### Django Settings
```python
# settings.py priorities
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'magicai_django',
        # ... connection details
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}

# Celery configuration
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

# External APIs
SCRYFALL_API_BASE = 'https://api.scryfall.com'
MTGJSON_API_BASE = 'https://mtgjson.com/api/v5'
```

---

## 9. UI/UX Considerations

### Current Frontend (Preserve These)
- **Bootstrap 5.3.2** - Recent version, good responsive design
- **Scrollspy Navigation** - Working well in card_detail_v2.html
- **Enhanced Search Widget** - Complex but functional
- **Card Grid Layout** - Responsive, works on mobile
- **Mana Symbol Support** - Uses Scryfall API for symbols

### Django Template Improvements
```django
<!-- Use Django's built-in features -->
{% load static %}
{% load card_extras %}  <!-- Custom template tags -->

<!-- Better URL handling -->
<a href="{% url 'card_detail' card.scryfall_id %}">{{ card.name }}</a>

<!-- Template inheritance -->
{% extends 'base.html' %}
{% block content %}
<!-- Card detail content -->
{% endblock %}
```

---

## 10. API Design (Django REST Framework)

### Current API Endpoints to Migrate
```
GET /api/cards/search
GET /api/cards/random  
GET /api/cards/filters
GET /api/cards/stats
GET /api/card/<id>
POST /api/parse-mana
```

### Django REST Framework Implementation
```python
# serializers.py
class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = '__all__'

class ComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewComponent
        fields = '__all__'

# views.py (DRF)
class CardViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Card.objects.filter(fully_analyzed=True)
    serializer_class = CardSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['name', 'oracle_text']
    filterset_fields = ['colors', 'rarity', 'cmc']
```

---

## 11. Performance Optimizations

### Database Optimizations
1. **Indexes** - All search fields, foreign keys
2. **Query Optimization** - Use select_related() for joins
3. **Pagination** - Built-in Django pagination
4. **Caching** - Template caching, query caching

### Code Optimizations
1. **Lazy Loading** - Only load data when needed
2. **Background Tasks** - Move AI generation to Celery
3. **Static Files** - Use CDN for assets
4. **Compression** - Gzip middleware

---

## 12. Testing Strategy

### Test Coverage Priorities
1. **Models** - Data integrity, relationships
2. **Views** - Response codes, context data
3. **APIs** - JSON responses, error handling
4. **Integration** - Full user flows

### Django Test Tools
```python
class CardModelTest(TestCase):
    def test_card_creation(self):
        card = Card.objects.create(
            scryfall_id=uuid4(),
            name="Test Card"
        )
        self.assertTrue(card.fully_analyzed)

class CardViewTest(TestCase):
    def test_card_detail_view(self):
        response = self.client.get(f'/card/{self.card.scryfall_id}/')
        self.assertEqual(response.status_code, 200)
```

---

## 13. Deployment Considerations

### Production Stack
- **Web Server:** Gunicorn + Nginx
- **Database:** PostgreSQL 15+
- **Cache:** Redis
- **Queue:** Celery with Redis broker
- **Static Files:** WhiteNoise or S3

### Environment Variables
```bash
DATABASE_URL=postgresql://user:pass@localhost/magicai
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
```

---

## 14. Migration Timeline

### Phase 1 (Week 1-2): Foundation
- [ ] Django project setup
- [ ] Database models definition
- [ ] Data migration scripts
- [ ] Basic views (homepage, card detail)

### Phase 2 (Week 3-4): Core Features  
- [ ] Search & browse functionality
- [ ] API endpoints (DRF)
- [ ] User authentication
- [ ] Admin interface

### Phase 3 (Week 5-6): Advanced Features
- [ ] Celery task migration
- [ ] Performance optimizations
- [ ] Testing suite
- [ ] Deployment setup

---

## 15. Known Issues to Address

### Critical Issues
1. **Card Routes Breaking** - Cards redirect to search page
2. **Performance Bottlenecks** - Card linker making too many DB queries
3. **Memory Usage** - Large result sets not paginated properly

### Flask-Specific Problems
1. **Blueprint Complexity** - Too many route files
2. **Template Inheritance** - Inconsistent base templates
3. **Error Handling** - Generic error pages

### Django Solutions
1. **Class-Based Views** - Better organization, built-in mixins
2. **Admin Interface** - Built-in admin for content management
3. **ORM Benefits** - Relationships, migrations, query optimization

---

## 16. Success Metrics

### Performance Goals
- [ ] Page load times < 2 seconds
- [ ] Search response < 500ms
- [ ] 99% uptime
- [ ] Handle 1000+ concurrent users

### Feature Goals
- [ ] All current functionality preserved
- [ ] Improved mobile experience
- [ ] Better admin tools
- [ ] Comprehensive test coverage (>80%)

---

## 17. Resources & References

### Django-Specific Resources
- Django Documentation: https://docs.djangoproject.com/
- Django REST Framework: https://www.django-rest-framework.org/
- Django-filter: https://django-filter.readthedocs.io/
- Celery with Django: https://docs.celeryproject.org/en/stable/django/

### MTG Data Sources
- Scryfall API: https://scryfall.com/docs/api
- MTGJson: https://mtgjson.com/
- Mana font: https://mana.andrewgioia.com/

### Current Production URLs (for reference)
- Homepage: `/` (32 featured cards)
- Card Detail: `/card/<scryfall_uuid>/<slug>`
- Search: `/search`
- Browse: `/browse`
- API: `/api/cards/*`

---

**This document should provide Claude 4.0 with everything needed to start the Django migration from scratch while preserving the core functionality and improving upon the current architecture.**
