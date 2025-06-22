"""
Simple test views to debug import issues.
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import TemplateView

def home(request):
    """Simple home view for testing."""
    context = {
        'recent_cards': [],
        'featured_cards': [],
        'analysis_progress': {'total_cards': 0},
        'card_count': '0'
    }
    return render(request, 'cards/home.html', context)

def card_detail(request, card_uuid):
    """Simple card detail view for testing."""
    context = {
        'card': {'uuid': card_uuid, 'name': 'Test Card'},
        'analysis': {},
        'organized_components': {}
    }
    return render(request, 'cards/card_detail.html', context)

def the_abyss(request):
    """Simple abyss view for testing."""
    context = {
        'cards': [],
        'card_count': 0,
        'query': '',
        'filters': {}
    }
    return render(request, 'cards/the_abyss.html', context)

def art_gallery(request):
    """Simple art gallery view for testing."""
    context = {
        'gallery_cards': [],
        'total_cards': 0
    }
    return render(request, 'cards/art_gallery.html', context)

# Stub functions for other views
def analysis_dashboard(request):
    return JsonResponse({'status': 'coming soon'})

def start_analysis(request, card_uuid):
    return JsonResponse({'status': 'analysis queued'})

def worker_control_panel(request):
    return JsonResponse({'status': 'worker panel'})

def job_queue_status(request):
    return JsonResponse({'status': 'queue status'})

def bulk_queue_cards(request):
    return JsonResponse({'status': 'bulk queue'})

def retry_failed_job(request, job_id):
    return JsonResponse({'status': 'retry job'})

def cleanup_old_jobs(request):
    return JsonResponse({'status': 'cleanup'})

def reset_stuck_jobs(request):
    return JsonResponse({'status': 'reset stuck'})

def admin_card_list(request):
    return JsonResponse({'status': 'admin card list'})

def admin_card_detail(request, card_uuid):
    return JsonResponse({'status': 'admin card detail'})

def browse_cards(request):
    return JsonResponse({'status': 'browse cards'})
