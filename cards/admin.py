from django.contrib import admin
from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import render
from django.urls import path
from django.utils.html import format_html
from .models import get_cards_collection, get_decks_collection


class MongoCardAdmin:
    """Custom admin interface for MongoDB Card data."""
    
    def get_urls(self):
        urls = [
            path('cards/', self.card_list_view, name='cards-list'),
            path('cards/<str:card_uuid>/', self.card_detail_view, name='card-detail'),
        ]
        return urls
    
    def card_list_view(self, request):
        """Display a list of cards with search and pagination."""
        cards_collection = get_cards_collection()
        
        # Get search query
        search_query = request.GET.get('q', '')
        page = int(request.GET.get('page', 1))
        per_page = 20
        skip = (page - 1) * per_page
        
        # Build MongoDB query
        mongo_query = {}
        if search_query:
            mongo_query['name'] = {'$regex': search_query, '$options': 'i'}
        
        # Get cards with pagination
        cards = list(cards_collection.find(mongo_query).skip(skip).limit(per_page))
        total_cards = cards_collection.count_documents(mongo_query)
        
        # Calculate pagination info
        has_next = (skip + per_page) < total_cards
        has_previous = page > 1
        
        context = {
            'cards': cards,
            'search_query': search_query,
            'page': page,
            'has_next': has_next,
            'has_previous': has_previous,
            'next_page': page + 1 if has_next else None,
            'previous_page': page - 1 if has_previous else None,
            'total_cards': total_cards,
            'showing_from': skip + 1,
            'showing_to': min(skip + per_page, total_cards),
        }
        
        return render(request, 'admin/cards/card_list.html', context)
    
    def card_detail_view(self, request, card_uuid):
        """Display detailed view of a single card."""
        cards_collection = get_cards_collection()
        
        # Get card by UUID
        card = cards_collection.find_one({'uuid': card_uuid})
        if not card:
            raise Http404("Card not found")
        
        context = {
            'card': card,
            'card_uuid': card_uuid,
        }
        
        return render(request, 'admin/cards/card_detail.html', context)


# Register the custom admin
mongo_card_admin = MongoCardAdmin()


class DeckAdmin(admin.ModelAdmin):
    """Simple deck admin for now - we'll enhance this later."""
    list_display = ['code', 'name', 'type', 'release_date', 'total_cards']
    list_filter = ['type']
    search_fields = ['name', 'code']
    readonly_fields = ['imported_at', 'updated_at']


# We don't register Card with standard admin since we use MongoDB
# admin.site.register(Card, CardAdmin)
# admin.site.register(Deck, DeckAdmin)
