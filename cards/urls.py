from django.urls import path
from . import views

app_name = 'cards'

urlpatterns = [
    # Homepage
    path('', views.HomeView.as_view(), name='home'),
    
    # Card pages
    path('browse/', views.CardBrowseView.as_view(), name='browse'),
    path('search/', views.CardSearchView.as_view(), name='search'),
    path('card/<str:card_uuid>/', views.CardDetailView.as_view(), name='card_detail'),
]
