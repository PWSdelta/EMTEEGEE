"""
Card and Deck models for the EMTEEGEE Django project.
These are used for Django admin interface but actual data is stored in MongoDB.
"""

from django.db import models
from datetime import datetime


class Card(models.Model):
    """
    Simplified Django model for admin interface.
    Actual card data is stored in MongoDB with full MTGJson structure.
    """
    uuid = models.CharField(max_length=36, unique=True)
    name = models.CharField(max_length=255)
    mana_cost = models.CharField(max_length=50, blank=True)
    mana_value = models.IntegerField(default=0)
    type_line = models.CharField(max_length=255, blank=True)
    colors = models.CharField(max_length=10, blank=True)  # Simplified as string
    rarity = models.CharField(max_length=20, blank=True)
    set_code = models.CharField(max_length=10, blank=True)
    
    # Analysis tracking
    fully_analyzed = models.BooleanField(default=False)
    analysis_completed_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    imported_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        
    def __str__(self):
        return f"{self.name} ({self.set_code})"


class Deck(models.Model):
    """
    Simplified Django model for admin interface.
    Actual deck data is stored in MongoDB with full MTGJson structure.
    """
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=50, blank=True)
    release_date = models.CharField(max_length=20, blank=True)
    total_cards = models.IntegerField(default=0)
    
    # Timestamps
    imported_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-release_date', 'name']
        
    def __str__(self):
        return f"{self.name} ({self.code})"


# MongoDB data access utilities
from pymongo import MongoClient
from django.conf import settings


def get_mongodb_collection(collection_name):
    """Get a MongoDB collection for direct access."""
    mongodb_settings = settings.MONGODB_SETTINGS
    
    # Create connection string
    if mongodb_settings['username'] and mongodb_settings['password']:
        client = MongoClient(
            host=mongodb_settings['host'],
            username=mongodb_settings['username'],
            password=mongodb_settings['password'],
            authSource=mongodb_settings['auth_source']
        )
    else:
        client = MongoClient(mongodb_settings['host'])
    
    db = client[mongodb_settings['db_name']]
    return db[collection_name]


def get_cards_collection():
    """Get the MongoDB cards collection."""
    return get_mongodb_collection('cards')


def get_decks_collection():
    """Get the MongoDB decks collection."""
    return get_mongodb_collection('decks')
    
    def __str__(self):
        return self.name


class Deck(models.Model):
    """
    MTG Deck model matching MTGJson deck structure exactly.
    No user creation - only imported from MTGJson.
    """
    # MTGJson deck structure
    _id = models.ObjectIdField()
    
    # Basic deck information (exact MTGJson format)
    name = models.CharField(max_length=200, db_index=True)
    type = models.CharField(max_length=50)  # "deck" 
    code = models.CharField(max_length=10, db_index=True)  # Set code
    releaseDate = models.DateField(null=True, blank=True)
    
    # Deck contents - stored as nested JSON (MTGJson format)
    mainBoard = models.JSONField(default=list)  # List of card objects with count, uuid, etc.
    sideBoard = models.JSONField(default=list)  # List of card objects
    commander = models.JSONField(default=list)  # For Commander decks
    
    # Metadata
    imported_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Analysis status
    fully_analyzed = models.BooleanField(default=False, db_index=True)
    analysis_completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        collection = 'decks'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['code']),
            models.Index(fields=['type']),
            models.Index(fields=['releaseDate']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    @property
    def total_cards(self):
        """Calculate total cards in deck."""
        total = 0
        for card in self.mainBoard:
            total += card.get('count', 1)
        for card in self.sideBoard:
            total += card.get('count', 1)
        for card in self.commander:
            total += card.get('count', 1)
        return total
    
    @property
    def mainboard_count(self):
        """Calculate mainboard card count."""
        return sum(card.get('count', 1) for card in self.mainBoard)
    
    @property
    def sideboard_count(self):
        """Calculate sideboard card count."""
        return sum(card.get('count', 1) for card in self.sideBoard)


class Deck(models.Model):
    """
    MTG Deck model for storing complete decklists.
    """
    FORMAT_CHOICES = [
        ('standard', 'Standard'),
        ('modern', 'Modern'),
        ('legacy', 'Legacy'),
        ('vintage', 'Vintage'),
        ('commander', 'Commander/EDH'),
        ('pioneer', 'Pioneer'),
        ('pauper', 'Pauper'),
        ('historic', 'Historic'),
        ('alchemy', 'Alchemy'),
        ('brawl', 'Brawl'),
        ('limited', 'Limited'),
        ('other', 'Other'),
    ]
    
    # Basic information
    name = models.CharField(max_length=200, help_text="Deck name")
    description = models.TextField(blank=True, help_text="Deck description or strategy")
    format = models.CharField(max_length=20, choices=FORMAT_CHOICES, db_index=True)
    
    # Deck colors (calculated from cards)
    colors = models.JSONField(default=list, help_text="Deck colors")
    color_identity = models.JSONField(default=list, help_text="Full color identity")
    
    # Stats
    total_cards = models.IntegerField(default=0, help_text="Total cards in deck")
    unique_cards = models.IntegerField(default=0, help_text="Number of unique cards")
    average_cmc = models.FloatField(default=0.0, help_text="Average converted mana cost")
    
    # Tournament/competitive data
    tournament_name = models.CharField(max_length=300, blank=True, help_text="Tournament name")
    tournament_date = models.DateField(null=True, blank=True, help_text="Tournament date")
    pilot_name = models.CharField(max_length=100, blank=True, help_text="Deck pilot name")
    placement = models.IntegerField(null=True, blank=True, help_text="Tournament placement")
    wins = models.IntegerField(default=0, help_text="Match wins")
    losses = models.IntegerField(default=0, help_text="Match losses")
    draws = models.IntegerField(default=0, help_text="Match draws")
    
    # Analysis status
    analyzed = models.BooleanField(default=False, help_text="Whether deck has been analyzed")
    analysis_completed_at = models.DateTimeField(null=True, blank=True)
    
    # Import metadata
    source_file = models.CharField(max_length=500, blank=True, help_text="Original file name")
    import_source = models.CharField(max_length=100, blank=True, help_text="Import source (mtgtop8, edhrec, etc.)")
    external_id = models.CharField(max_length=100, blank=True, help_text="External deck ID")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['format']),
            models.Index(fields=['analyzed']),
            models.Index(fields=['tournament_date']),
            models.Index(fields=['created_at']),
            models.Index(fields=['total_cards']),
            models.Index(fields=['pilot_name']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        if self.pilot_name:
            return f"{self.name} by {self.pilot_name}"
        return self.name
    
    @property
    def win_rate(self):
        total_matches = self.wins + self.losses + self.draws
        if total_matches == 0:
            return 0
        return (self.wins + (self.draws * 0.5)) / total_matches
    
    def calculate_stats(self):
        """Calculate deck statistics from decklist items."""
        items = self.decklist_items.all()
        
        self.total_cards = sum(item.quantity for item in items)
        self.unique_cards = items.count()
        
        # Calculate average CMC
        total_cmc = 0
        total_count = 0
        all_colors = set()
        
        for item in items:
            if item.card:
                # Include lands at CMC 0 in calculation
                cmc_contribution = item.card.cmc * item.quantity
                total_cmc += cmc_contribution
                total_count += item.quantity
                
                # Collect colors
                if item.card.colors:
                    all_colors.update(item.card.colors)
        
        self.average_cmc = total_cmc / total_count if total_count > 0 else 0
        self.colors = list(all_colors)
        
        # Calculate color identity (includes mana symbols in text)
        color_identity = set(all_colors)
        for item in items:
            if item.card and item.card.color_identity:
                color_identity.update(item.card.color_identity)
        
        self.color_identity = list(color_identity)
        self.save()


class DecklistItem(models.Model):
    """
    Individual cards in a deck with quantities.
    """
    BOARD_CHOICES = [
        ('main', 'Main Deck'),
        ('side', 'Sideboard'),
        ('maybe', 'Maybeboard'),
        ('command', 'Command Zone'),  # For Commander
    ]
    
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE, related_name='decklist_items')
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='deck_inclusions')
    quantity = models.PositiveIntegerField(default=1, help_text="Number of copies")
    board = models.CharField(max_length=10, choices=BOARD_CHOICES, default='main')
    
    # For cards that couldn't be matched during import
    card_name_raw = models.CharField(max_length=200, blank=True, 
                                   help_text="Original card name from import")
    
    class Meta:
        unique_together = ['deck', 'card', 'board']
        indexes = [
            models.Index(fields=['deck', 'board']),
            models.Index(fields=['card']),
        ]
    
    def __str__(self):
        board_suffix = f" ({self.board})" if self.board != 'main' else ""
        if self.card:
            return f"{self.quantity}x {self.card.name}{board_suffix}"
        return f"{self.quantity}x {self.card_name_raw}{board_suffix}"


class DeckAnalysis(models.Model):
    """
    AI-generated deck analysis similar to card analysis components.
    """
    
    ANALYSIS_TYPES = [
        ('overview', 'Deck Overview'),
        ('strategy', 'Strategy Analysis'),
        ('mana_curve', 'Mana Curve Analysis'),
        ('synergies', 'Card Synergies'),
        ('strengths', 'Deck Strengths'),
        ('weaknesses', 'Deck Weaknesses'),
        ('sideboard', 'Sideboard Guide'),
        ('meta_position', 'Meta Position'),
        ('upgrade_suggestions', 'Upgrade Suggestions'),
    ]
    
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE, related_name='analyses')
    analysis_type = models.CharField(max_length=30, choices=ANALYSIS_TYPES)
    
    # Content
    content_markdown = models.TextField(help_text="Analysis content in markdown")
    content_html = models.TextField(blank=True, help_text="Processed HTML content")
    
    # AI metadata
    model_used = models.CharField(max_length=100, help_text="AI model used")
    generation_metadata = models.JSONField(default=dict, help_text="Generation parameters")
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['deck', 'analysis_type']
        indexes = [
            models.Index(fields=['deck', 'analysis_type']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.deck.name} - {self.get_analysis_type_display()}"
