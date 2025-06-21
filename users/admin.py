from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserFavorite, UserCollection, CollectionItem


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'cards_viewed', 'last_activity']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'date_joined', 'favorite_colors']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('MTG Profile', {
            'fields': ('bio', 'location', 'birth_date', 'favorite_colors', 'favorite_formats')
        }),
        ('Activity', {
            'fields': ('cards_viewed', 'last_activity')
        }),
    )


@admin.register(UserFavorite)
class UserFavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'card', 'added_at']
    list_filter = ['added_at']
    search_fields = ['user__username', 'card__name']
    autocomplete_fields = ['user', 'card']


class CollectionItemInline(admin.TabularInline):
    model = CollectionItem
    extra = 0
    autocomplete_fields = ['card']


@admin.register(UserCollection)
class UserCollectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'is_public', 'created_at', 'updated_at']
    list_filter = ['is_public', 'created_at']
    search_fields = ['name', 'description', 'user__username']
    autocomplete_fields = ['user']
    inlines = [CollectionItemInline]


@admin.register(CollectionItem)
class CollectionItemAdmin(admin.ModelAdmin):
    list_display = ['collection', 'card', 'quantity', 'added_at']
    list_filter = ['added_at']
    search_fields = ['collection__name', 'card__name']
    autocomplete_fields = ['collection', 'card']
