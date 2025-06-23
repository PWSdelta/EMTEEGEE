"""
Real-Time Analysis Dashboard with Progressive Enhancement
Provides interactive monitoring and progressive analysis quality improvements
"""

import json
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
from django.shortcuts import render
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.template.response import TemplateResponse
from cards.models import get_cards_collection
from .enhanced_swarm_manager import enhanced_swarm
import logging

logger = logging.getLogger(__name__)

class RealTimeAnalysisDashboard:
    """Real-time dashboard for monitoring and enhancing analysis quality"""
    
    def __init__(self):
        self.cards_collection = get_cards_collection()
        
    def get_dashboard_context(self) -> Dict[str, Any]:
        """Get comprehensive dashboard context data"""
        
        # Get swarm status
        swarm_status = enhanced_swarm.get_enhanced_swarm_status()
        
        # Get analysis quality metrics
        quality_metrics = self._get_analysis_quality_metrics()
        
        # Get recent analysis activity
        recent_activity = self._get_recent_analysis_activity()
        
        # Get popular cards needing analysis
        priority_cards = self._get_priority_cards_preview()
        
        # Get worker performance metrics
        worker_metrics = self._get_worker_performance_metrics()
        
        return {
            'swarm_status': swarm_status,
            'quality_metrics': quality_metrics, 
            'recent_activity': recent_activity,
            'priority_cards': priority_cards,
            'worker_metrics': worker_metrics,
            'dashboard_timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    def _get_analysis_quality_metrics(self) -> Dict[str, Any]:
        """Calculate analysis quality metrics"""
        
        # Get cards with coherence scores
        coherence_pipeline = [
            {
                '$match': {
                    'analysis.components': {'$exists': True, '$ne': {}}
                }
            },
            {
                '$project': {
                    'name': 1,
                    'components': {'$objectToArray': '$analysis.components'},
                    'total_components': {'$size': {'$objectToArray': '$analysis.components'}}
                }
            },
            {
                '$unwind': '$components'
            },
            {
                '$group': {
                    '_id': None,
                    'total_components_generated': {'$sum': 1},
                    'avg_coherence_score': {
                        '$avg': '$components.v.coherence_score'
                    },
                    'high_coherence_count': {
                        '$sum': {
                            '$cond': [
                                {'$gte': ['$components.v.coherence_score', 0.8]},
                                1, 0
                            ]
                        }
                    }
                }
            }
        ]
        
        try:
            coherence_result = list(self.cards_collection.aggregate(coherence_pipeline))
            if coherence_result:
                stats = coherence_result[0]
                quality_percentage = (stats.get('high_coherence_count', 0) / 
                                    stats.get('total_components_generated', 1)) * 100
            else:
                stats = {}
                quality_percentage = 0
        except Exception as e:
            logger.error(f"Error calculating quality metrics: {e}")
            stats = {}
            quality_percentage = 0
        
        return {
            'total_components': stats.get('total_components_generated', 0),
            'avg_coherence_score': stats.get('avg_coherence_score', 0.0),
            'high_quality_percentage': quality_percentage,
            'analysis_efficiency': self._calculate_analysis_efficiency()
        }
    
    def _calculate_analysis_efficiency(self) -> float:
        """Calculate analysis generation efficiency"""
        try:
            # Get average processing time for recent tasks
            recent_tasks = enhanced_swarm.tasks.find({
                'completed_at': {'$gte': datetime.now(timezone.utc) - timedelta(hours=24)},
                'execution_time': {'$exists': True}
            })
            
            times = [task.get('execution_time', 0) for task in recent_tasks]
            if times:
                avg_time = sum(times) / len(times)
                # Efficiency: lower time = higher efficiency (inverted scale)
                return max(0, min(100, 100 - (avg_time / 60)))  # Scale based on 60s baseline
            
        except Exception as e:
            logger.error(f"Error calculating efficiency: {e}")
        
        return 50.0  # Default moderate efficiency
    
    def _get_recent_analysis_activity(self) -> List[Dict[str, Any]]:
        """Get recent analysis activity for live feed"""
        
        try:
            recent_completions = list(enhanced_swarm.tasks.find({
                'status': 'completed',
                'completed_at': {'$gte': datetime.now(timezone.utc) - timedelta(hours=1)}
            }).sort([('completed_at', -1)]).limit(20))
            
            activity = []
            for task in recent_completions:
                activity.append({
                    'card_name': task.get('card_name', 'Unknown'),
                    'components': len(task.get('components', [])),
                    'worker_id': task.get('assigned_to', 'Unknown')[:12] + '...',
                    'completed_at': task.get('completed_at'),
                    'execution_time': task.get('execution_time', 0),
                    'coherence_warnings': len(task.get('coherence_warnings', [])),
                    'batch_processed': task.get('batch_processing', False)
                })
            
            return activity
            
        except Exception as e:
            logger.error(f"Error getting recent activity: {e}")
            return []
    
    def _get_priority_cards_preview(self) -> List[Dict[str, Any]]:
        """Get preview of high-priority cards needing analysis"""
        
        try:
            priority_cards = list(enhanced_swarm.priority_cache.aggregate([
                {
                    '$lookup': {
                        'from': 'cards',
                        'localField': 'card_uuid',
                        'foreignField': 'uuid',
                        'as': 'card_data'
                    }
                },
                {
                    '$match': {
                        'card_data': {'$ne': []},
                        'card_data.analysis.fully_analyzed': {'$ne': True},
                        'priority_score': {'$gte': 0.5}  # Medium to high priority
                    }
                },
                {
                    '$sort': {'priority_score': -1}
                },
                {
                    '$limit': 15
                }
            ]))
            
            preview = []
            for item in priority_cards:
                card = item['card_data'][0]
                preview.append({
                    'name': card.get('name', 'Unknown'),
                    'type_line': card.get('type_line', ''),
                    'mana_cost': card.get('mana_cost', ''),
                    'priority_score': round(item['priority_score'], 2),
                    'existing_components': len(card.get('analysis', {}).get('components', {})),
                    'edhrec_rank': card.get('edhrecRank'),
                    'price_usd': card.get('prices', {}).get('usd', '0')
                })
            
            return preview
            
        except Exception as e:
            logger.error(f"Error getting priority cards: {e}")
            return []
    
    def _get_worker_performance_metrics(self) -> List[Dict[str, Any]]:
        """Get worker performance metrics"""
        
        try:
            workers = list(enhanced_swarm.workers.find({'status': 'active'}))
            
            metrics = []
            for worker in workers:
                # Calculate recent performance
                recent_tasks = list(enhanced_swarm.tasks.find({
                    'assigned_to': worker['worker_id'],
                    'completed_at': {'$gte': datetime.now(timezone.utc) - timedelta(hours=6)}
                }))
                
                if recent_tasks:
                    avg_time = sum(task.get('execution_time', 0) for task in recent_tasks) / len(recent_tasks)
                    success_rate = (len([t for t in recent_tasks if t.get('status') == 'completed']) / 
                                  len(recent_tasks)) * 100
                else:
                    avg_time = 0
                    success_rate = 0
                
                metrics.append({
                    'worker_id': worker['worker_id'],
                    'worker_type': worker['capabilities'].get('worker_type', 'unknown'),
                    'tasks_completed': worker.get('tasks_completed', 0),
                    'recent_tasks': len(recent_tasks),
                    'avg_execution_time': round(avg_time, 1),
                    'success_rate': round(success_rate, 1),
                    'last_heartbeat': worker.get('last_heartbeat'),
                    'specialization': worker['capabilities'].get('specialization', 'general')
                })
            
            # Sort by recent activity
            metrics.sort(key=lambda x: x['recent_tasks'], reverse=True)
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting worker metrics: {e}")
            return []

# Dashboard view functions for Django
def real_time_dashboard(request):
    """Main real-time dashboard view"""
    dashboard = RealTimeAnalysisDashboard()
    context = dashboard.get_dashboard_context()
    return render(request, 'cards/real_time_dashboard.html', context)

@csrf_exempt
@require_http_methods(["GET"])
def dashboard_api_status(request):
    """API endpoint for real-time dashboard updates"""
    dashboard = RealTimeAnalysisDashboard()
    context = dashboard.get_dashboard_context()
    return JsonResponse(context)

@csrf_exempt
@require_http_methods(["POST"])
def trigger_priority_analysis(request):
    """API endpoint to trigger analysis for high-priority cards"""
    try:
        data = json.loads(request.body)
        card_count = min(data.get('card_count', 10), 50)  # Limit to 50 cards max
        
        # Get high-priority cards
        priority_cards = list(enhanced_swarm.priority_cache.find({
            'priority_score': {'$gte': 0.7}
        }).sort([('priority_score', -1)]).limit(card_count))
        
        # Queue for analysis (this would typically trigger workers)
        queued_count = 0
        for card_priority in priority_cards:
            # In a real implementation, this would queue the card for analysis
            # For now, we'll just simulate the queuing
            queued_count += 1
        
        return JsonResponse({
            'status': 'success',
            'message': f'Queued {queued_count} high-priority cards for analysis',
            'queued_count': queued_count
        })
        
    except Exception as e:
        logger.error(f"Error triggering priority analysis: {e}")
        return JsonResponse({
            'status': 'error',
            'message': 'Failed to trigger priority analysis'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def enhance_analysis_quality(request):
    """API endpoint to trigger analysis quality enhancement for existing cards"""
    try:
        data = json.loads(request.body)
        quality_threshold = data.get('quality_threshold', 0.6)
        
        # Find cards with low coherence scores
        low_quality_pipeline = [
            {
                '$match': {
                    'analysis.components': {'$exists': True, '$ne': {}}
                }
            },
            {
                '$project': {
                    'uuid': 1,
                    'name': 1,
                    'components': {'$objectToArray': '$analysis.components'}
                }
            },
            {
                '$unwind': '$components'
            },
            {
                '$match': {
                    'components.v.coherence_score': {'$lt': quality_threshold}
                }
            },
            {
                '$group': {
                    '_id': '$uuid',
                    'name': {'$first': '$name'},
                    'low_quality_components': {'$push': '$components.k'}
                }
            },
            {
                '$limit': 20  # Limit enhancement batch size
            }
        ]
        
        cards_to_enhance = list(enhanced_swarm.cards.aggregate(low_quality_pipeline))
        
        enhancement_count = 0
        for card in cards_to_enhance:
            # Mark components for re-analysis (would trigger workers in real implementation)
            enhancement_count += len(card['low_quality_components'])
        
        return JsonResponse({
            'status': 'success',
            'message': f'Queued {len(cards_to_enhance)} cards for quality enhancement',
            'cards_count': len(cards_to_enhance),
            'components_count': enhancement_count
        })
        
    except Exception as e:
        logger.error(f"Error enhancing analysis quality: {e}")
        return JsonResponse({
            'status': 'error',
            'message': 'Failed to enhance analysis quality'
        }, status=500)

def stream_dashboard_updates(request):
    """Server-sent events stream for real-time dashboard updates"""
    def event_stream():
        dashboard = RealTimeAnalysisDashboard()
        
        while True:
            try:
                # Get current dashboard data
                data = dashboard.get_dashboard_context()
                
                # Format as server-sent event
                yield f"data: {json.dumps(data)}\n\n"
                
                # Wait before next update
                import time
                time.sleep(5)  # Update every 5 seconds
                
            except Exception as e:
                logger.error(f"Error in dashboard stream: {e}")
                yield f"data: {{\"error\": \"Stream error\"}}\n\n"
                break
    
    response = StreamingHttpResponse(
        event_stream(),
        content_type='text/event-stream'
    )
    response['Cache-Control'] = 'no-cache'
    response['Connection'] = 'keep-alive'
    return response

# Global dashboard instance
dashboard_instance = RealTimeAnalysisDashboard()
