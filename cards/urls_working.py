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
    """Enhanced card detail page with real data"""
    from cards.analysis_manager import analysis_manager
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        card = analysis_manager.get_card_by_uuid(card_uuid)
        
        if not card:
            return render(request, 'cards/card_detail_test.html', {
                'error': "Card not found in database"
            })
        
        # Get analysis data
        analysis = card.get('analysis', {})
        components = analysis.get('components', {})
        
        context = {
            'card': card,
            'analysis': analysis,
            'components': components,
            'completion_percentage': (len(components) / 20) * 100 if components else 0
        }
        
        return render(request, 'cards/card_detail_test.html', context)
        
    except Exception as e:
        logger.error(f"Error in card_detail view for {card_uuid}: {e}")
        return render(request, 'cards/card_detail_test.html', {
            'error': f"Error loading card: {str(e)}"
        })

def the_abyss(request):
    """Import the real the_abyss function"""
    from . import views as real_views
    return real_views.the_abyss(request)

def art_gallery(request):
    """Import the real art_gallery function"""
    from . import views as real_views
    return real_views.art_gallery(request)

def autocomplete_api(request):
    """Import the real autocomplete API function"""
    from . import views as real_views
    return real_views.autocomplete_api(request)

def analysis_dashboard(request):
    """Import the real analysis dashboard function"""
    from . import views as real_views
    return real_views.analysis_dashboard(request)

def start_analysis(request, card_uuid):
    """Import the real start analysis function"""
    from . import views as real_views
    return real_views.start_analysis(request, card_uuid)

def worker_control_panel(request):
    """Import the real worker control panel function"""
    from . import views as real_views
    return real_views.worker_control_panel(request)

def job_queue_status(request):
    """Import the real job queue status function"""
    from . import views as real_views
    return real_views.job_queue_status(request)

def bulk_queue_cards(request):
    """Import the real bulk queue function"""
    from . import views as real_views
    return real_views.bulk_queue_cards(request)

def retry_failed_job(request, job_id):
    """Import the real retry job function"""
    from . import views as real_views
    return real_views.retry_failed_job(request, job_id)

def cleanup_old_jobs(request):
    """Import the real cleanup function"""
    from . import views as real_views
    return real_views.cleanup_old_jobs(request)

def reset_stuck_jobs(request):
    """Import the real reset stuck jobs function"""
    from . import views as real_views
    return real_views.reset_stuck_jobs(request)

def admin_card_list(request):
    """Import the real admin card list function"""
    from . import views as real_views
    return real_views.admin_card_list(request)

def admin_card_detail(request, card_uuid):
    """Import the real admin card detail function"""
    from . import views as real_views
    return real_views.admin_card_detail(request, card_uuid)

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
    
    # Search API
    path('api/autocomplete/', autocomplete_api, name='autocomplete_api'),

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
