"""
Views for the cards app with MongoDB integration and analysis features.
"""

from django.shortcuts import render, get_object_or_404
from django.http import Http404, JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
import logging

from .models import get_cards_collection
from .analysis_manager import analysis_manager
from .ollama_client import ALL_COMPONENT_TYPES
from .job_queue import job_queue

logger = logging.getLogger(__name__)

class HomeView(TemplateView):
    """Home page with recent cards and analysis stats."""
    template_name = 'cards/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            cards_collection = get_cards_collection()
            
            # Get some recent cards
            recent_cards = list(cards_collection.find().limit(12))
            
            # Get analysis progress
            progress = analysis_manager.get_analysis_progress()
            
            # Get some fully analyzed cards for featured section
            featured_cards = list(cards_collection.find({
                "analysis.fully_analyzed": True
            }).limit(6))
            
            context.update({
                'recent_cards': recent_cards,
                'featured_cards': featured_cards,
                'analysis_progress': progress,
                'card_count': f"{progress.get('total_cards', 0):,}"
            })
            
        except Exception as e:
            logger.error(f"Error in home view: {e}")
            messages.error(self.request, "Error loading home page")
            context.update({
                'recent_cards': [],
                'featured_cards': [],
                'analysis_progress': {},
                'card_count': "Error loading"
            })
        
        return context

# Function-based views for better control over analysis features
def home(request):
    """Home page function view."""
    view = HomeView.as_view()
    return view(request)

class CardDetailView(TemplateView):
    """Display detailed card information with analysis components."""
    template_name = 'cards/card_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get card UUID from URL
        card_uuid = kwargs.get('card_uuid')
        if not card_uuid:
            raise Http404("Card UUID required")
        
        try:
            card = analysis_manager.get_card_by_uuid(card_uuid)
            if not card:
                raise Http404("Card not found")
            
            # Get analysis data
            analysis = card.get('analysis', {})
            components = analysis.get('components', {})
            
            # Organize components by category for display
            component_categories = {
                'Strategic': ['tactical_analysis', 'power_level_assessment', 'competitive_analysis', 
                             'synergy_analysis', 'meta_positioning', 'advanced_interactions'],
                'Practical': ['play_tips', 'combo_suggestions', 'format_analysis', 
                             'deck_archetypes', 'mulligan_considerations', 'sideboard_guide'],
                'Educational': ['new_player_guide', 'rules_clarifications', 
                               'budget_alternatives', 'historical_context'],
                'Thematic': ['thematic_analysis', 'art_flavor_analysis', 
                            'design_philosophy', 'investment_outlook']
            }
            
            organized_components = {}
            for category, component_types in component_categories.items():
                organized_components[category] = {
                    comp_type: components.get(comp_type) 
                    for comp_type in component_types 
                    if comp_type in components
                }
            
            context.update({
                'card': card,
                'analysis': analysis,
                'components': components,
                'organized_components': organized_components,
                'all_component_types': ALL_COMPONENT_TYPES,
                'completion_percentage': (len(components) / 20) * 100 if components else 0
            })
            
        except Http404:
            raise
        except Exception as e:
            logger.error(f"Error in card_detail view for {card_uuid}: {e}")
            raise Http404("Card not found")
        
        return context

def card_detail(request, card_uuid):
    """Function-based card detail view."""
    view = CardDetailView.as_view()
    return view(request, card_uuid=card_uuid)

def browse_cards(request):
    """Redirect to The Abyss page - our enhanced search/discovery experience."""
    from django.shortcuts import redirect
    from django.urls import reverse
    
    # Preserve any query parameters
    query_params = request.GET.urlencode()
    abyss_url = reverse('cards:the_abyss')
    
    if query_params:
        return redirect(f"{abyss_url}?{query_params}")
    else:
        return redirect(abyss_url)

@require_http_methods(["POST"])
@csrf_exempt
def start_analysis(request, card_uuid):
    """Start analysis for a specific card (AJAX endpoint)."""
    try:
        card = analysis_manager.get_card_by_uuid(card_uuid)
        if not card:
            return JsonResponse({'error': 'Card not found'}, status=404)
        
        # Check if already fully analyzed
        analysis = card.get('analysis', {})
        if analysis.get('fully_analyzed'):
            return JsonResponse({
                'status': 'already_complete',
                'message': 'Card is already fully analyzed'
            })
        
        # Start analysis (in a real app, this would be queued with Celery)
        # For now, we'll generate one component as a demo
        component_type = request.POST.get('component_type', 'play_tips')
        
        if component_type not in ALL_COMPONENT_TYPES:
            return JsonResponse({'error': 'Invalid component type'}, status=400)
        
        success = analysis_manager.generate_component(card_uuid, component_type)
        
        if success:
            # Get updated analysis
            updated_card = analysis_manager.get_card_by_uuid(card_uuid)
            updated_analysis = updated_card.get('analysis', {})
            
            return JsonResponse({
                'status': 'success',
                'message': f'Generated {component_type}',
                'component_count': updated_analysis.get('component_count', 0),
                'fully_analyzed': updated_analysis.get('fully_analyzed', False)
            })
        else:
            return JsonResponse({
                'status': 'error', 
                'message': f'Failed to generate {component_type}'
            })
        
    except Exception as e:
        logger.error(f"Error starting analysis for {card_uuid}: {e}")
        return JsonResponse({'error': 'Internal server error'}, status=500)

def analysis_dashboard(request):
    """Dashboard for monitoring analysis progress."""
    try:
        # Get overall progress
        progress = analysis_manager.get_analysis_progress()
        
        # Get some recent activity
        cards_collection = get_cards_collection()
        recently_analyzed = list(cards_collection.find({
            'analysis.analysis_completed_at': {'$exists': True}
        }).sort([('analysis.analysis_completed_at', -1)]).limit(10))
        
        in_progress = list(cards_collection.find({
            'analysis.component_count': {'$gt': 0, '$lt': 20}
        }).limit(10))
        
        context = {
            'progress': progress,
            'recently_analyzed': recently_analyzed,
            'in_progress': in_progress,
            'component_types': ALL_COMPONENT_TYPES
        }
        
        return render(request, 'cards/analysis_dashboard.html', context)
        
    except Exception as e:
        logger.error(f"Error in analysis_dashboard: {e}")
        messages.error(request, "Error loading dashboard")
        return render(request, 'cards/analysis_dashboard.html', {})

# Legacy admin views (keeping for compatibility)
def admin_card_list(request):
    """Admin card browser."""
    try:
        cards_collection = get_cards_collection()
        
        # Get search query
        search_query = request.GET.get('q', '').strip()
        
        # Build MongoDB query
        if search_query:
            mongo_query = {
                '$or': [
                    {'name': {'$regex': search_query, '$options': 'i'}},
                    {'text': {'$regex': search_query, '$options': 'i'}},
                    {'type': {'$regex': search_query, '$options': 'i'}}
                ]
            }
        else:
            mongo_query = {}
        
        # Get total count for pagination info
        total_cards = cards_collection.count_documents(mongo_query)
        
        # Pagination
        page = request.GET.get('page', 1)
        per_page = 50
        skip = (int(page) - 1) * per_page
        
        # Get cards
        cards = list(cards_collection.find(mongo_query).skip(skip).limit(per_page))
        
        # Simple pagination context
        total_pages = (total_cards + per_page - 1) // per_page
        
        context = {
            'cards': cards,
            'search_query': search_query,
            'current_page': int(page),
            'total_pages': total_pages,
            'total_cards': total_cards,
            'has_previous': int(page) > 1,
            'has_next': int(page) < total_pages,
            'previous_page': int(page) - 1 if int(page) > 1 else None,
            'next_page': int(page) + 1 if int(page) < total_pages else None,
        }
        
        return render(request, 'admin/cards/card_list.html', context)
        
    except Exception as e:
        logger.error(f"Error in admin_card_list view: {e}")
        messages.error(request, "Error loading cards")
        return render(request, 'admin/cards/card_list.html', {'cards': []})

def admin_card_detail(request, card_uuid):
    """Admin interface for viewing card details."""
    try:
        card = analysis_manager.get_card_by_uuid(card_uuid)
        if not card:
            raise Http404("Card not found")
        
        # Get analysis status
        analysis = card.get('analysis', {})
        
        context = {
            'card': card,
            'analysis': analysis,
            'component_types': ALL_COMPONENT_TYPES
        }
        
        return render(request, 'admin/cards/card_detail.html', context)
        
    except Exception as e:
        logger.error(f"Error in admin_card_detail view: {e}")
        raise Http404("Card not found")

def bulk_queue_cards(request):
    """Bulk queue unanalyzed cards for analysis."""
    try:
        limit = int(request.POST.get('limit', 100))
        
        # Use the job queue's bulk enqueue method
        jobs_enqueued = job_queue.bulk_enqueue_unanalyzed_cards(limit=limit)
        
        return JsonResponse({
            'status': 'success',
            'message': f'Queued {jobs_enqueued} cards for analysis',
            'jobs_enqueued': jobs_enqueued
        })
        
    except Exception as e:
        logger.error(f"Error bulk queuing cards: {e}")
        return JsonResponse({'error': 'Failed to bulk queue cards'}, status=500)

@require_http_methods(["POST"])
@csrf_exempt
def retry_failed_job(request, job_id):
    """Retry a specific failed job."""
    try:
        success = job_queue.requeue_failed_job(job_id)
        
        if success:
            return JsonResponse({
                'status': 'success',
                'message': f'Job {job_id[:8]}... requeued for retry'
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Job not found or not in failed state'
            })
        
    except Exception as e:
        logger.error(f"Error retrying job {job_id}: {e}")
        return JsonResponse({'error': 'Failed to retry job'}, status=500)

@require_http_methods(["POST"])
@csrf_exempt
def cleanup_old_jobs(request):
    """Clean up old completed/failed jobs."""
    try:
        days_old = int(request.POST.get('days_old', 7))
        cleaned_count = job_queue.cleanup_old_jobs(days_old=days_old)
        
        return JsonResponse({
            'status': 'success',
            'message': f'Cleaned up {cleaned_count} old jobs',
            'cleaned_count': cleaned_count
        })
        
    except Exception as e:
        logger.error(f"Error cleaning up jobs: {e}")
        return JsonResponse({'error': 'Failed to cleanup jobs'}, status=500)

@require_http_methods(["POST"])
@csrf_exempt
def reset_stuck_jobs(request):
    """Reset jobs that have been stuck in processing state."""
    try:
        hours_old = int(request.POST.get('hours_old', 2))
        reset_count = job_queue.reset_stuck_jobs(hours_old=hours_old)
        
        return JsonResponse({
            'status': 'success',
            'message': f'Reset {reset_count} stuck jobs',
            'reset_count': reset_count
        })
        
    except Exception as e:
        logger.error(f"Error resetting stuck jobs: {e}")
        return JsonResponse({'error': 'Failed to reset stuck jobs'}, status=500)

def job_queue_status(request):
    """Get current job queue status (AJAX endpoint)."""
    try:
        stats = job_queue.get_queue_stats()
        recent_jobs = job_queue.get_recent_jobs(limit=10)
        
        return JsonResponse({
            'status': 'success',
            'stats': stats,
            'recent_jobs': [
                {
                    'job_id': job['job_id'][:8] + '...',
                    'card_uuid': job['card_uuid'][:8] + '...',
                    'job_type': job['job_type'],
                    'status': job['status'],
                    'created_at': job['created_at'].isoformat() if job.get('created_at') else None,
                    'attempts': job.get('attempts', 0),
                    'error_message': job.get('error_message', '')[:100] if job.get('error_message') else None
                }
                for job in recent_jobs
            ]
        })
        
    except Exception as e:
        logger.error(f"Error getting queue status: {e}")
        return JsonResponse({'error': 'Failed to get queue status'}, status=500)

def worker_control_panel(request):
    """Control panel for managing analysis workers."""
    try:
        # Get queue stats
        queue_stats = job_queue.get_queue_stats()
        
        # Get recent jobs for monitoring
        recent_jobs = job_queue.get_recent_jobs(limit=20)
        
        # Get failed jobs that can be retried
        failed_jobs = list(job_queue.jobs_collection.find({
            'status': 'failed',
            'attempts': {'$lt': 3}  # Only show jobs that can still be retried
        }).sort([('completed_at', -1)]).limit(15))
        
        context = {
            'queue_stats': queue_stats,
            'recent_jobs': recent_jobs,
            'failed_jobs': failed_jobs,
            'total_queue_size': sum(queue_stats.values())
        }
        
        return render(request, 'cards/worker_control_panel.html', context)
        
    except Exception as e:
        logger.error(f"Error in worker_control_panel: {e}")
        messages.error(request, "Error loading worker control panel")
        return render(request, 'cards/worker_control_panel.html', {})

def the_abyss(request):
    """
    The Abyss - Simple, powerful card search.
    Just one search box with amazing full-text search across all card fields.
    """
    try:
        cards_collection = get_cards_collection()
        
        # Get search parameters (only search query matters)
        search_query = request.GET.get('q', '').strip()
        page = int(request.GET.get('page', 1))
        
        # Build MongoDB query
        query = {}
        sort_criteria = [('name', 1)]  # Default alphabetical sort
        
        # Full-text search across ALL fields - comprehensive and powerful
        if search_query:
            # Split search query into terms for better matching
            search_terms = search_query.split()
            search_conditions = []
            
            for term in search_terms:
                search_conditions.append({
                    '$or': [
                        {'name': {'$regex': term, '$options': 'i'}},
                        {'text': {'$regex': term, '$options': 'i'}},
                        {'type': {'$regex': term, '$options': 'i'}},
                        {'artist': {'$regex': term, '$options': 'i'}},
                        {'setName': {'$regex': term, '$options': 'i'}},
                        {'setCode': {'$regex': term, '$options': 'i'}},
                        {'keywords': {'$in': [term]}},
                        {'flavorText': {'$regex': term, '$options': 'i'}},
                        {'manaCost': {'$regex': term, '$options': 'i'}},
                        {'subtypes': {'$in': [term]}},
                        {'supertypes': {'$in': [term]}}
                    ]
                })
            
            if search_conditions:
                query['$and'] = search_conditions
                # Sort search results by relevance (name matches first, then EDHREC rank)
                sort_criteria = [
                    ('name', 1),  # Alphabetical within relevance groups
                    ('edhrecRank', 1)  # Popular cards higher
                ]
        
        # Get total count
        total_cards = cards_collection.count_documents(query)
        
        # Pagination
        per_page = 36  # More cards per page since we're focused on results
        skip = (page - 1) * per_page
        
        # Execute query with sorting
        cards_cursor = cards_collection.find(query).sort(sort_criteria).skip(skip).limit(per_page)
        cards = list(cards_cursor)
        
        # Add detail URLs
        for card in cards:
            card['detail_url'] = f"/card/{card['uuid']}/"
        
        # Calculate pagination info
        total_pages = (total_cards + per_page - 1) // per_page
        has_previous = page > 1
        has_next = page < total_pages
        
        context = {
            'cards': cards,
            'search_query': search_query,
            'total_cards': total_cards,
            'page': page,
            'total_pages': total_pages,
            'has_previous': has_previous,
            'has_next': has_next,
            'previous_page': page - 1 if has_previous else None,
            'next_page': page + 1 if has_next else None,
            'is_search': bool(search_query)
        }
        
        return render(request, 'cards/the_abyss.html', context)
        
    except Exception as e:
        logger.error(f"Error in the_abyss view: {e}")
        import traceback
        traceback.print_exc()
        return render(request, 'cards/the_abyss.html', {
            'cards': [],
            'total_cards': 0,
            'error_message': f'Error loading cards: {str(e)}'
        })

def art_gallery(request):
    """
    MTG Art Gallery - Beautiful carousel showcasing high-quality card art.
    Uses Scryfall's artCrop images for a stunning visual experience.
    Prioritizes cards with high-resolution scans and beautiful artwork.
    """
    try:
        cards_collection = get_cards_collection()        # Get 100 cards with exceptional art quality
        # Prioritize cards with highres_scan status and art_crop images
        query = {
            'imageUris.art_crop': {'$exists': True, '$ne': None},
            '$or': [
                # High-resolution scans with great art
                {'imageStatus': 'highres_scan'},
                # Mythic and rare cards often have stunning art
                {'rarity': {'$in': ['mythic', 'rare']}},
                # Planeswalkers have iconic artwork
                {'type': {'$regex': 'Planeswalker', '$options': 'i'}},
                # Popular cards often have memorable art
                {'edhrecRank': {'$lte': 2000}},
                # Include some legendary creatures (often have great art)
                {'$and': [
                    {'type': {'$regex': 'Legendary', '$options': 'i'}},
                    {'type': {'$regex': 'Creature', '$options': 'i'}}
                ]}
            ]
        }
          # Get a diverse selection of 120 cards (we'll shuffle and take 100)
        gallery_cards = list(cards_collection.find(
            query,
            {
                'uuid': 1,
                'name': 1,
                'imageUris': 1,
                'artist': 1,
                'setCode': 1,
                'setName': 1,
                'rarity': 1,
                'type': 1,
                'manaCost': 1,
                'colors': 1,
                'scryfallUri': 1,
                'edhrecRank': 1,
                'imageStatus': 1,
                'highresImage': 1,
                'releasedAt': 1
            }
        ).limit(120))
        
        # Shuffle for variety and take 100 for performance
        import random
        random.shuffle(gallery_cards)
        gallery_cards = gallery_cards[:100]
          # Add card detail URLs and enhance data
        for card in gallery_cards:
            card['detail_url'] = f"/card/{card['uuid']}/"
            # Ensure we have the art_crop URL
            if 'imageUris' in card and 'art_crop' in card['imageUris']:
                card['art_url'] = card['imageUris']['art_crop']
            else:
                # Fallback to normal image if art_crop not available
                card['art_url'] = card.get('imageUris', {}).get('normal', '')
            
        context = {
            'gallery_cards': gallery_cards,
            'total_cards': len(gallery_cards),
            'page_title': 'MTG Art Gallery'
        }
        
        return render(request, 'cards/art_gallery.html', context)
        
    except Exception as e:
        logger.error(f"Error in art_gallery: {e}")
        return render(request, 'cards/art_gallery.html', {
            'gallery_cards': [],
            'total_cards': 0,
            'error': str(e)
        })
