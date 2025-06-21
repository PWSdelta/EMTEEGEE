from django.db import models
from cards.models import Card


class AnalysisComponent(models.Model):
    """
    Analysis components for cards - reviews, lore, strategy, pricing analysis, etc.
    Migrated from MongoDB review_components collection.
    """
    
    COMPONENT_TYPES = [
        ('thematic_analysis', 'Thematic Analysis'),
        ('competitive_analysis', 'Competitive Analysis'),
        ('flavor_analysis', 'Flavor & Lore Analysis'),
        ('pricing_analysis', 'Pricing Analysis'),
        ('synergy_analysis', 'Synergy Analysis'),
        ('historical_analysis', 'Historical Analysis'),
        ('deck_building', 'Deck Building Notes'),
        ('art_analysis', 'Art & Design Analysis'),
    ]
    
    # Relationships
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='analysis_components')
    
    # Content
    component_type = models.CharField(max_length=50, choices=COMPONENT_TYPES, db_index=True)
    content_markdown = models.TextField(help_text="Original markdown content")
    content_html = models.TextField(blank=True, help_text="Processed HTML content")
    
    # AI metadata
    model_used = models.CharField(max_length=100, help_text="AI model used for generation")
    generation_metadata = models.JSONField(default=dict, help_text="Generation parameters and metadata")
    
    # Status
    is_active = models.BooleanField(default=True, db_index=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['card', 'component_type']),
            models.Index(fields=['is_active']),
            models.Index(fields=['created_at']),
            models.Index(fields=['component_type']),
        ]
        ordering = ['component_type', '-created_at']
        unique_together = ['card', 'component_type']  # One component per type per card
    
    def __str__(self):
        return f"{self.card.name} - {self.get_component_type_display()}"
    
    def save(self, *args, **kwargs):
        # Auto-generate HTML from markdown if not provided
        if self.content_markdown and not self.content_html:
            # TODO: Add markdown to HTML conversion
            self.content_html = self.content_markdown
        super().save(*args, **kwargs)


class PriceHistory(models.Model):
    """
    Historical price data for cards.
    """
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='price_history')
    
    # Price data
    usd = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    usd_foil = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    eur = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tix = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Source and timing
    source = models.CharField(max_length=50, default='scryfall')
    recorded_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['card', 'recorded_at']),
            models.Index(fields=['recorded_at']),
        ]
        ordering = ['-recorded_at']
    
    def __str__(self):
        return f"{self.card.name} - ${self.usd} ({self.recorded_at.date()})"
