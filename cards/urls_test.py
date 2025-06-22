"""
URL configuration for Cards app - minimal version for testing
"""

from django.urls import path
from django.http import HttpResponse

app_name = 'cards'

def test_view(request):
    return HttpResponse("Test page working")

urlpatterns = [
    path('', test_view, name='test'),
]
