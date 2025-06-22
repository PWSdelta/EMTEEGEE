from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.

def index(request):
    """Simple index view for testing"""
    return JsonResponse({
        'message': 'Cards API is running',
        'swarm_status_url': '/cards/api/swarm/status'
    })
