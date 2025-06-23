"""
Working Cards URLs
"""

from django.urls import path
from django.http import HttpResponse
from django.shortcuts import render
from . import views as real_views  # Import the real views

app_name = 'cards'

def home(request):
    """Simple home view with fully analyzed cards"""
    from django.shortcuts import render
    from cards.models import get_cards_collection
    
    try:
        cards_collection = get_cards_collection()
        
        # Get fully analyzed cards with exactly 20 components
        fully_analyzed_cards = list(cards_collection.aggregate([
            {
                '$match': {
                    'analysis.components': {'$exists': True}
                }
            },
            {
                '$addFields': {
                    'component_count': {
                        '$cond': {
                            'if': {'$eq': [{'$type': '$analysis.components'}, 'object']},
                            'then': {'$size': {'$objectToArray': '$analysis.components'}},
                            'else': 0
                        }
                    }
                }
            },
            {
                '$match': {
                    'component_count': {'$eq': 20}  # Exactly 20 components = fully analyzed
                }
            },
            {
                '$sort': {
                    'edhrecRank': 1  # Sort by popularity
                }
            },
            {'$limit': 20}  # Show up to 20 cards
        ]))
        
        # Calculate statistics
        total_cards = cards_collection.count_documents({})
        analyzed_cards_count = len(fully_analyzed_cards)
        total_components = analyzed_cards_count * 20
        avg_components = 20 if analyzed_cards_count > 0 else 0
        
        context = {
            'fully_analyzed_cards': fully_analyzed_cards,
            'statistics': {
                'total_cards': f"{total_cards:,}",
                'fully_analyzed': analyzed_cards_count,
                'total_components': f"{total_components:,}",
                'avg_components': avg_components,
            }
        }
        
    except Exception as e:
        print(f"Error in home view: {e}")
        context = {
            'fully_analyzed_cards': [],
            'statistics': {
                'total_cards': "Error",
                'fully_analyzed': 0,
                'total_components': "0",
                'avg_components': 0,
            }
        }
    
    return render(request, 'cards/home.html', context)

def card_detail(request, card_uuid):
    """Simple card detail page"""
    return render(request, 'cards/card_detail.html', {'card': {'uuid': card_uuid, 'name': 'Test Card'}})

def the_abyss(request):
    """Simple abyss page"""
    return render(request, 'cards/the_abyss.html', {'cards': []})

def art_gallery(request):
    """Simple art gallery page"""
    return render(request, 'cards/art_gallery.html', {'gallery_cards': []})

def analysis_dashboard(request):
    """Simple analysis dashboard"""
    return HttpResponse("Analysis Dashboard - Coming Soon!")

def start_analysis(request, card_uuid):
    """Simple analysis start"""
    return HttpResponse("Analysis Started")

def worker_control_panel(request):
    """Simple worker control"""
    return HttpResponse("Worker Control Panel")

def job_queue_status(request):
    """Simple queue status"""
    return HttpResponse("Queue Status")

def bulk_queue_cards(request):
    """Simple bulk queue"""
    return HttpResponse("Bulk Queue")

def retry_failed_job(request, job_id):
    """Simple retry job"""
    return HttpResponse("Retry Job")

def cleanup_old_jobs(request):
    """Simple cleanup"""
    return HttpResponse("Cleanup Jobs")

def reset_stuck_jobs(request):
    """Simple reset jobs"""
    return HttpResponse("Reset Jobs")

def admin_card_list(request):
    """Simple admin list"""
    return HttpResponse("Admin Card List")

def admin_card_detail(request, card_uuid):
    """Simple admin detail"""
    return HttpResponse("Admin Card Detail")

def browse_cards(request):
    """Simple browse redirect"""
    from django.shortcuts import redirect
    return redirect('cards:the_abyss')

urlpatterns = [
    # Public views
    path('', home, name='home'),
    path('card/<str:card_uuid>/', card_detail, name='card_detail'),
    path('browse/', browse_cards, name='browse'),
    path('abyss/', the_abyss, name='the_abyss'),
    path('card-list/', the_abyss, name='card_list'),  # Legacy compatibility
    
    # Art Gallery
    path('gallery/', art_gallery, name='art_gallery'),

    # Analysis features
    path('analysis/dashboard/', analysis_dashboard, name='analysis_dashboard'),
    path('api/analyze/<str:card_uuid>/', start_analysis, name='start_analysis'),

    # Job Queue Management
    path('queue/control/', worker_control_panel, name='worker_control_panel'),
    path('api/queue/status/', job_queue_status, name='job_queue_status'),
    path('api/queue/bulk-queue/', bulk_queue_cards, name='bulk_queue_cards'),
    path('api/queue/retry/<str:job_id>/', retry_failed_job, name='retry_failed_job'),
    path('api/queue/cleanup/', cleanup_old_jobs, name='cleanup_old_jobs'),
    path('api/queue/reset-stuck/', reset_stuck_jobs, name='reset_stuck_jobs'),

    # Admin views (legacy, keeping for compatibility)
    path('admin-cards/', admin_card_list, name='admin_card_list'),
    path('admin-cards/<str:card_uuid>/', admin_card_detail, name='admin_card_detail'),
]
