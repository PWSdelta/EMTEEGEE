"""
URL configuration for the cards app.
"""

from django.urls import path
from . import views

app_name = 'cards'

urlpatterns = [
    # Public views
    path('', views.home, name='home'),
    path('card/<str:card_uuid>/', views.card_detail, name='card_detail'),
    path('browse/', views.browse_cards, name='browse'),
    
    # Analysis features
    path('analysis/dashboard/', views.analysis_dashboard, name='analysis_dashboard'),
    path('api/analyze/<str:card_uuid>/', views.start_analysis, name='start_analysis'),
    
    # Admin views (legacy, keeping for compatibility)
    path('admin-cards/', views.admin_card_list, name='admin_card_list'),
    path('admin-cards/<str:card_uuid>/', views.admin_card_detail, name='admin_card_detail'),
]
