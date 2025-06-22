"""
API views for card analysis requests and other AJAX endpoints.
"""

import json
from datetime import datetime, timezone
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.db.models import Q
from cards.models import get_cards_collection
import logging
import re

logger = logging.getLogger(__name__)

# Constants for MongoDB field paths
ANALYSIS_REQUEST_COUNT = 'analysis.request_count'
ANALYSIS_LAST_REQUESTED = 'analysis.last_requested_at'
ANALYSIS_IN_QUEUE = 'analysis.in_queue'
ANALYSIS_FULLY_ANALYZED = 'analysis.fully_analyzed'
ANALYSIS_COMPONENT_COUNT = 'analysis.component_count'
ERROR_INTERNAL_SERVER = 'Internal server error'


@method_decorator(csrf_exempt, name='dispatch')
class RequestAnalysisView(View):
    """Handle analysis requests for cards."""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            card_uuid = data.get('card_uuid')
            
            if not card_uuid:
                return JsonResponse({'error': 'Card UUID is required'}, status=400)
            
            cards_collection = get_cards_collection()
            
            # Check if card exists
            card = cards_collection.find_one({'uuid': card_uuid})
            if not card:
                return JsonResponse({'error': 'Card not found'}, status=404)
              # Check if already fully analyzed
            analysis = card.get('analysis', {})
            if analysis.get('fully_analyzed'):
                return JsonResponse({
                    'status': 'already_complete',
                    'message': 'This card has already been fully analyzed!'
                })
            
            # Add or increment analysis request
            now = datetime.now(timezone.utc)
            update_doc = {
                '$inc': {ANALYSIS_REQUEST_COUNT: 1},
                '$set': {
                    ANALYSIS_LAST_REQUESTED: now,
                    ANALYSIS_IN_QUEUE: True
                },
                '$push': {
                    'analysis.request_history': {
                        'requested_at': now,
                        'ip_address': self.get_client_ip(request)
                    }
                }
            }
            
            # Initialize analysis object if it doesn't exist
            if not analysis:
                update_doc['$setOnInsert'] = {
                    'analysis.created_at': now,
                    ANALYSIS_COMPONENT_COUNT: 0,
                    ANALYSIS_FULLY_ANALYZED: False
                }
            
            cards_collection.update_one(
                {'uuid': card_uuid},
                update_doc,
                upsert=True
            )
              # Get updated request count
            updated_card = cards_collection.find_one({'uuid': card_uuid})
            request_count = updated_card.get('analysis', {}).get('request_count', 1)
            
            logger.info(f"Analysis requested for {card['name']} (UUID: {card_uuid[:8]}...) - Total requests: {request_count}")
            
            return JsonResponse({
                'status': 'success',
                'message': f'Analysis requested! This card now has {request_count} request(s).',
                'request_count': request_count,
                'in_queue': True
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            logger.error(f"Error requesting analysis: {e}")
            return JsonResponse({'error': ERROR_INTERNAL_SERVER}, status=500)
    
    def get_client_ip(self, request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


@require_http_methods(["GET"])
def analysis_queue_status(request):
    """Get current analysis queue status."""
    try:
        cards_collection = get_cards_collection()
          # Count cards in queue (requested but not fully analyzed)
        queue_count = cards_collection.count_documents({
            ANALYSIS_IN_QUEUE: True,
            ANALYSIS_FULLY_ANALYZED: {'$ne': True}
        })
        
        # Count fully analyzed cards
        completed_count = cards_collection.count_documents({
            ANALYSIS_FULLY_ANALYZED: True
        })
        
        # Get top requested cards (not yet analyzed)
        top_requested = list(cards_collection.find(
            {
                ANALYSIS_REQUEST_COUNT: {'$exists': True, '$gt': 0},
                ANALYSIS_FULLY_ANALYZED: {'$ne': True}
            },
            {
                'name': 1,
                'uuid': 1,
                ANALYSIS_REQUEST_COUNT: 1,
                ANALYSIS_LAST_REQUESTED: 1
            }
        ).sort(ANALYSIS_REQUEST_COUNT, -1).limit(10))
        
        return JsonResponse({
            'queue_count': queue_count,
            'completed_count': completed_count,
            'top_requested': [
                {
                    'name': card['name'],
                    'uuid': card['uuid'],
                    'request_count': card.get('analysis', {}).get('request_count', 0),
                    'last_requested': card.get('analysis', {}).get('last_requested_at')
                }                for card in top_requested
            ]
        })
        
    except Exception as e:
        logger.error(f"Error getting queue status: {e}")
        return JsonResponse({'error': ERROR_INTERNAL_SERVER}, status=500)


@require_http_methods(["GET"])
def card_analysis_status(request, card_uuid):
    """Get analysis status for a specific card."""
    try:
        cards_collection = get_cards_collection()
        
        card = cards_collection.find_one(
            {'uuid': card_uuid},
            {
                'name': 1,
                ANALYSIS_FULLY_ANALYZED: 1,
                ANALYSIS_COMPONENT_COUNT: 1,
                ANALYSIS_REQUEST_COUNT: 1,
                ANALYSIS_IN_QUEUE: 1,
                ANALYSIS_LAST_REQUESTED: 1
            }
        )
        
        if not card:
            return JsonResponse({'error': 'Card not found'}, status=404)
        
        analysis = card.get('analysis', {})
        
        return JsonResponse({
            'name': card['name'],
            'uuid': card_uuid,
            'fully_analyzed': analysis.get('fully_analyzed', False),
            'component_count': analysis.get('component_count', 0),
            'request_count': analysis.get('request_count', 0),
            'in_queue': analysis.get('in_queue', False),
            'last_requested': analysis.get('last_requested_at')
        })
        
    except Exception as e:
        logger.error(f"Error getting card analysis status: {e}")
        return JsonResponse({'error': ERROR_INTERNAL_SERVER}, status=500)


@require_http_methods(["GET"])
def autocomplete_suggestions(request):
    """
    Provide autocomplete suggestions for card search.
    Returns a mix of card names, types, keywords, artists, and sets.
    """
    query = request.GET.get('q', '').strip()
    
    if not query or len(query) < 2:
        return JsonResponse({'suggestions': []})
    
    try:
        cards_collection = get_cards_collection()
        suggestions = []
        
        # Escape special regex characters but preserve the query structure
        escaped_query = re.escape(query)
        regex_pattern = {'$regex': escaped_query, '$options': 'i'}
        
        # MongoDB aggregation constants
        MATCH_OP = '$match'
        GROUP_OP = '$group'
        LIMIT_OP = '$limit'
        
        # Get suggestions from different sources
        suggestions.extend(_get_card_name_suggestions(cards_collection, regex_pattern))
        
        if len(suggestions) < 15:
            suggestions.extend(_get_type_suggestions(cards_collection, regex_pattern, suggestions, MATCH_OP, GROUP_OP, LIMIT_OP))
        
        if len(suggestions) < 15:
            suggestions.extend(_get_artist_suggestions(cards_collection, regex_pattern, suggestions, MATCH_OP, GROUP_OP, LIMIT_OP))
        
        if len(suggestions) < 15:
            suggestions.extend(_get_set_suggestions(cards_collection, regex_pattern, suggestions, MATCH_OP, GROUP_OP, LIMIT_OP))
        
        # Limit total suggestions
        suggestions = suggestions[:15]
        
        return JsonResponse({'suggestions': suggestions})
        
    except Exception as e:
        logger.error(f"Autocomplete error: {str(e)}")
        return JsonResponse({'suggestions': []})


def _get_card_name_suggestions(cards_collection, regex_pattern):
    """Get card name suggestions."""
    name_matches = cards_collection.find(
        {'name': regex_pattern},
        {'name': 1, 'uuid': 1, '_id': 0}
    ).limit(8)
    
    suggestions = []
    for doc in name_matches:
        suggestions.append({
            'text': doc['name'],
            'type': 'card',
            'icon': 'bi-diamond',
            'category': 'Cards',
            'uuid': doc.get('uuid')  # Include UUID for direct navigation
        })
    return suggestions


def _get_type_suggestions(cards_collection, regex_pattern, existing_suggestions, match_op, group_op, limit_op):
    """Get card type suggestions."""
    existing_texts = [s['text'] for s in existing_suggestions]
    type_pipeline = [
        {match_op: {'type': regex_pattern}},
        {group_op: {'_id': '$type'}},
        {limit_op: 5}
    ]
    type_matches = cards_collection.aggregate(type_pipeline)
    
    suggestions = []
    for doc in type_matches:
        type_name = doc['_id']
        if type_name and type_name not in existing_texts:
            suggestions.append({
                'text': type_name,
                'type': 'type',
                'icon': 'bi-tags',
                'category': 'Types'
            })
    return suggestions


def _get_artist_suggestions(cards_collection, regex_pattern, existing_suggestions, match_op, group_op, limit_op):
    """Get artist suggestions."""
    existing_texts = [s['text'] for s in existing_suggestions]
    artist_pipeline = [
        {match_op: {'artist': regex_pattern}},
        {group_op: {'_id': '$artist'}},
        {limit_op: 3}
    ]
    artist_matches = cards_collection.aggregate(artist_pipeline)
    
    suggestions = []
    for doc in artist_matches:
        artist_name = doc['_id']
        if artist_name and artist_name not in existing_texts:
            suggestions.append({
                'text': artist_name,
                'type': 'artist',
                'icon': 'bi-palette',
                'category': 'Artists'
            })
    return suggestions


def _get_set_suggestions(cards_collection, regex_pattern, existing_suggestions, match_op, group_op, limit_op):
    """Get set suggestions."""
    existing_texts = [s['text'] for s in existing_suggestions]
    set_pipeline = [
        {match_op: {
            '$or': [
                {'set_name': regex_pattern},
                {'set': regex_pattern}
            ]
        }},
        {group_op: {'_id': {'set': '$set', 'set_name': '$set_name'}}},
        {limit_op: 3}
    ]
    set_matches = cards_collection.aggregate(set_pipeline)
    
    suggestions = []
    for doc in set_matches:
        set_info = doc['_id']
        set_name = set_info.get('set_name', set_info.get('set', ''))
        if set_name and set_name not in existing_texts:
            suggestions.append({
                'text': set_name,
                'type': 'set',
                'icon': 'bi-collection',
                'category': 'Sets'
            })
    return suggestions
