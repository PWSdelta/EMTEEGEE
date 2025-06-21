from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView
from django.db.models import Q, Count
from django.http import JsonResponse, Http404
from django.core.paginator import Paginator
from django.conf import settings
import random

from .models import Card, get_cards_collection


class HomeView(TemplateView):
    """
    Homepage displaying platform status.
    Shows card import status and authentication options.
    """
    template_name = 'cards/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
          # Get card count from MongoDB
        try:
            cards_collection = get_cards_collection()
            card_count = cards_collection.count_documents({})
            context['card_count'] = f"{card_count:,}"
        except Exception:
            context['card_count'] = "Error loading"
            
        return context


class CardDetailView(TemplateView):
    """
    Card detail page with full analysis using MongoDB data.
    """
    template_name = 'cards/card_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get card UUID from URL
        card_uuid = kwargs.get('card_uuid')
        if not card_uuid:
            raise Http404("Card UUID required")
        
        # Get card from MongoDB
        cards_collection = get_cards_collection()
        card = cards_collection.find_one({'uuid': card_uuid})
        
        if not card:
            raise Http404("Card not found")
        
        context['card'] = card
        context['card_uuid'] = card_uuid
        
        return context


class OldCardDetailView(DetailView):
    """
    OLD: Card detail page with full analysis.
    Supports both UUID-only and UUID+slug URLs for SEO.
    """
    model = Card
    template_name = 'cards/detail.html'
    context_object_name = 'card'
    slug_field = 'scryfall_id'
    slug_url_kwarg = 'card_id'
    
    def get_object(self, queryset=None):
        # Get card by scryfall_id (UUID)
        card_id = self.kwargs.get('card_id')
        return get_object_or_404(Card, scryfall_id=card_id)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        card = self.object
        
        # Get all analysis components
        context['components'] = card.analysis_components.filter(is_active=True)
        
        # Get related cards (same colors)
        if card.colors:
            related_cards = Card.objects.filter(
                colors__overlap=card.colors,
                fully_analyzed=True
            ).exclude(id=card.id)[:6]
            context['related_cards'] = related_cards
        
        # Price history
        context['price_history'] = card.price_history.all()[:30]  # Last 30 entries
        
        return context


class CardBrowseView(ListView):
    """
    Paginated card browser with filtering.
    """
    model = Card
    template_name = 'cards/browse.html'
    context_object_name = 'cards'
    paginate_by = settings.PAGINATE_BY
    
    def get_queryset(self):
        qs = Card.objects.filter(fully_analyzed=True)
        
        # Apply filters from query parameters
        color_filter = self.request.GET.get('colors')
        if color_filter:
            colors = color_filter.split(',')
            qs = qs.filter(colors__overlap=colors)
        
        rarity_filter = self.request.GET.get('rarity')
        if rarity_filter:
            qs = qs.filter(rarity=rarity_filter)
        
        cmc_filter = self.request.GET.get('cmc')
        if cmc_filter:
            qs = qs.filter(cmc=int(cmc_filter))
        
        type_filter = self.request.GET.get('type')
        if type_filter:
            qs = qs.filter(type_line__icontains=type_filter)
        
        # Sorting
        sort_by = self.request.GET.get('sort', 'name')
        if sort_by in ['name', '-name', 'cmc', '-cmc', '-created_at']:
            qs = qs.order_by(sort_by)
        
        return qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add filter options for the UI
        context['rarities'] = Card.objects.values_list('rarity', flat=True).distinct()
        context['all_colors'] = ['W', 'U', 'B', 'R', 'G']
        context['current_filters'] = dict(self.request.GET.items())
        
        return context


class CardSearchView(ListView):
    """
    Card search with text-based queries.
    """
    model = Card
    template_name = 'cards/search.html'
    context_object_name = 'cards'
    paginate_by = settings.PAGINATE_BY
    
    def get_queryset(self):
        query = self.request.GET.get('q', '').strip()
        
        if not query:
            return Card.objects.none()
        
        # Search in name and oracle text
        qs = Card.objects.filter(
            Q(name__icontains=query) |
            Q(oracle_text__icontains=query) |
            Q(type_line__icontains=query)
        ).filter(fully_analyzed=True)
        
        return qs.order_by('name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context


class RandomCardView(DetailView):
    """
    Redirect to a random card detail page.
    """
    model = Card
    
    def get_object(self, queryset=None):
        # Get a random fully analyzed card
        cards = Card.objects.filter(fully_analyzed=True)
        count = cards.count()
        if count == 0:
            return None
        
        random_index = random.randint(0, count - 1)
        return cards[random_index]
    
    def get(self, request, *args, **kwargs):
        card = self.get_object()
        if not card:
            return render(request, 'cards/no_cards.html')
        
        # Redirect to the card detail page
        from django.shortcuts import redirect
        return redirect('cards:card_detail', card_id=card.scryfall_id)
