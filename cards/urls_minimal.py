"""
URL configuration for Cards app - test version
"""

from django.urls import path
from django.http import HttpResponse

app_name = 'cards'

def test_home(request):
    return HttpResponse("Home page working")

urlpatterns = [
    path('', test_home, name='home'),
]
