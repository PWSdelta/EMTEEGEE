from django.contrib import admin
from .models import AnalysisComponent, PriceHistory


@admin.register(AnalysisComponent)
class AnalysisComponentAdmin(admin.ModelAdmin):
    list_display = ['card', 'component_type', 'model_used', 'is_active', 'created_at']
    list_filter = ['component_type', 'model_used', 'is_active']
    search_fields = ['card__name', 'content_markdown']
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['card']
    
    fieldsets = (
        ('Component Information', {
            'fields': ('card', 'component_type', 'is_active')
        }),
        ('Content', {
            'fields': ('content_markdown', 'content_html')
        }),
        ('AI Metadata', {
            'fields': ('model_used', 'generation_metadata'),
            'classes': ['collapse']
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse']
        }),
    )


@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = ['card', 'usd', 'usd_foil', 'eur', 'source', 'recorded_at']
    list_filter = ['source', 'recorded_at']
    search_fields = ['card__name']
    readonly_fields = ['recorded_at']
    autocomplete_fields = ['card']
    date_hierarchy = 'recorded_at'
    ordering = ['-recorded_at']
