from django.contrib import admin
from .models import Card, Deck


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ['name', 'mana_cost', 'mana_value', 'type_line', 'rarity', 'set_code', 'fully_analyzed']
    list_filter = ['fully_analyzed', 'rarity', 'colors', 'set_code']
    search_fields = ['name', 'type_line']
    readonly_fields = ['uuid', 'imported_at', 'updated_at']
    ordering = ['name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('uuid', 'name', 'mana_cost', 'mana_value', 'type_line')
        }),
        ('Card Details', {
            'fields': ('colors', 'rarity', 'set_code')
        }),
        ('Analysis Status', {
            'fields': ('fully_analyzed', 'analysis_completed_at')
        }),
        ('Timestamps', {
            'fields': ('imported_at', 'updated_at'),
            'classes': ['collapse']
        }),
    )


@admin.register(Deck)
class DeckAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'code', 'release_date', 'total_cards']
    list_filter = ['type', 'code']
    search_fields = ['name', 'code']
    readonly_fields = ['imported_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'type', 'code', 'release_date')
        }),
        ('Deck Statistics', {
            'fields': ('total_cards',)
        }),
        ('Timestamps', {
            'fields': ('imported_at', 'updated_at'),
            'classes': ['collapse']
        }),
    )
        ('Deck Contents', {
            'fields': ('mainBoard', 'sideBoard', 'commander'),
            'classes': ['collapse']
        }),
        ('Analysis', {
            'fields': ('fully_analyzed', 'analysis_completed_at'),
        }),
        ('Timestamps', {
            'fields': ('imported_at', 'updated_at'),
            'classes': ['collapse']
        }),
    )
    
    def total_cards(self, obj):
        return obj.total_cards
    total_cards.short_description = 'Total Cards'
    
    def mainboard_count(self, obj):
        return obj.mainboard_count
    mainboard_count.short_description = 'Mainboard'
    
    def sideboard_count(self, obj):
        return obj.sideboard_count
    sideboard_count.short_description = 'Sideboard'
