"""
Enhanced Django REST API endpoints for AI Analysis Swarm System v2.0
Integrates with enhanced_swarm_manager.py for production-ready distributed AI analysis
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import sys
import os
from bson import ObjectId
from datetime import datetime, timezone

# Custom JSON encoder to handle MongoDB ObjectId and datetime objects
class MongoJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

try:
    from .enhanced_swarm_manager import enhanced_swarm
    from .swarm_logging import get_swarm_logger
    logger = get_swarm_logger('ENHANCED_API')
except ImportError as e:
    print(f"Warning: Enhanced SwarmManager not available: {e}")
    enhanced_swarm = None
    logger = None

@csrf_exempt
@require_http_methods(["POST"])
def register_worker(request):
    """Register a new worker node with enhanced capabilities"""
    try:
        data = json.loads(request.body)
        worker_id = data.get('worker_id')
        capabilities = data.get('capabilities', {})
        
        if not worker_id:
            return JsonResponse({'error': 'worker_id required'}, status=400)
        
        if enhanced_swarm is None:
            return JsonResponse({'error': 'Enhanced SwarmManager not available'}, status=500)
        
        result = enhanced_swarm.register_worker(worker_id, capabilities)
        
        if logger:
            logger.info(f"🔌 Worker registered: {worker_id} with capabilities: {capabilities}")
        
        return JsonResponse(result)
        
    except Exception as e:
        if logger:
            logger.error(f"❌ Worker registration failed: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def get_work(request):
    """Get work assignments for a worker - SIMPLIFIED VERSION"""
    try:
        data = json.loads(request.body)
        worker_id = data.get('worker_id')
        
        if not worker_id:
            return JsonResponse({'error': 'worker_id required'}, status=400)
        
        if enhanced_swarm is None:
            return JsonResponse({'error': 'Enhanced SwarmManager not available'}, status=500)
        
        if logger:
            logger.info(f"🔍 Work request from {worker_id}")
        
        # Use the simplified get_work method
        tasks = enhanced_swarm.get_work(worker_id)
        
        # Convert ObjectId fields to strings for JSON serialization
        json_tasks = json.loads(json.dumps(tasks, cls=MongoJSONEncoder))
        
        if logger:
            logger.info(f"✅ API returning {len(json_tasks)} task(s) to {worker_id}")
        
        return JsonResponse({'tasks': json_tasks})
        
    except Exception as e:
        if logger:
            logger.error(f"❌ Get work failed for {worker_id}: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def submit_results(request):
    """Accept completed work from a worker with enhanced validation"""
    try:
        data = json.loads(request.body)
        worker_id = data.get('worker_id')
        task_id = data.get('task_id')
        card_id = data.get('card_id')
        results = data.get('results', {})
        
        if not all([worker_id, card_id, results]):
            return JsonResponse({'error': 'worker_id, card_id, and results required'}, status=400)
        
        if enhanced_swarm is None:
            return JsonResponse({'error': 'Enhanced SwarmManager not available'}, status=500)
        
        # Enhanced submit with coherence validation
        success = enhanced_swarm.submit_task_result(
            task_id=task_id,
            worker_id=worker_id,
            card_id=card_id,
            results=results
        )
        
        if success:
            if logger:
                logger.info(f"✅ Results submitted by {worker_id} for card {card_id}")
            return JsonResponse({'status': 'success', 'message': 'Results submitted and validated'})
        else:
            return JsonResponse({'error': 'Failed to submit results'}, status=500)
        
    except Exception as e:
        if logger:
            logger.error(f"❌ Submit results failed for {worker_id}: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def enhanced_swarm_status(request):
    """Get comprehensive enhanced swarm system status"""
    try:
        if enhanced_swarm is None:
            return JsonResponse({'error': 'Enhanced SwarmManager not available'}, status=500)
        
        status = enhanced_swarm.get_enhanced_swarm_status()
        
        # Use custom encoder for any ObjectId or datetime objects
        json_status = json.loads(json.dumps(status, cls=MongoJSONEncoder))
        
        return JsonResponse(json_status)
        
    except Exception as e:
        if logger:
            logger.error(f"❌ Status request failed: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def worker_health(request):
    """Get detailed health status of all enhanced workers"""
    try:
        if enhanced_swarm is None:
            return JsonResponse({'error': 'Enhanced SwarmManager not available'}, status=500)
        
        # Get all workers with their recent activity
        workers = list(enhanced_swarm.workers.find({}))
        
        # Enrich with recent task data
        for worker in workers:
            recent_tasks = enhanced_swarm.tasks.count_documents({
                'worker_id': worker['worker_id'],
                'status': 'completed',
                'completed_at': {'$gte': datetime.now(timezone.utc).replace(hour=0, minute=0, second=0)}
            })
            worker['tasks_today'] = recent_tasks
        
        json_workers = json.loads(json.dumps(workers, cls=MongoJSONEncoder))
        
        return JsonResponse({
            'workers': json_workers,
            'total_workers': len(workers),
            'active_workers': len([w for w in workers if w.get('status') == 'active'])
        })
        
    except Exception as e:
        if logger:
            logger.error(f"❌ Worker health check failed: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def heartbeat(request):
    """Enhanced worker heartbeat endpoint with detailed status tracking"""
    try:
        data = json.loads(request.body)
        worker_id = data.get('worker_id')
        
        if not worker_id:
            return JsonResponse({'error': 'worker_id required'}, status=400)
        
        if enhanced_swarm is None:
            return JsonResponse({'error': 'Enhanced SwarmManager not available'}, status=500)
        
        # Enhanced heartbeat with comprehensive status update
        current_time = datetime.now(timezone.utc)
        
        update_data = {
            'last_heartbeat': current_time,
            'status': data.get('status', 'active'),
            'active_tasks': data.get('active_tasks', 0),
            'system_info': data.get('system_info', {}),
            'performance_metrics': data.get('performance_metrics', {})
        }
        
        result = enhanced_swarm.workers.update_one(
            {'worker_id': worker_id},
            {'$set': update_data}
        )
        
        if result.matched_count > 0:
            # Check for any priority work available
            available_work = enhanced_swarm.priority_cache.count_documents({
                'status': 'pending'
            })
            
            response_data = {
                'status': 'success', 
                'message': 'Heartbeat received',
                'available_work': available_work,
                'server_time': current_time.isoformat()
            }
            
            return JsonResponse(response_data)
        else:
            return JsonResponse({'error': 'Worker not found - please register first'}, status=404)
        
    except Exception as e:
        if logger:
            logger.error(f"❌ Heartbeat failed for {worker_id}: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def system_metrics(request):
    """Get detailed system performance metrics"""
    try:
        if enhanced_swarm is None:
            return JsonResponse({'error': 'Enhanced SwarmManager not available'}, status=500)
        
        # Get comprehensive metrics
        total_cards = enhanced_swarm.cards.count_documents({})
        analyzed_cards = enhanced_swarm.cards.count_documents({
            'analysis.status.fully_analyzed': True
        })
        
        active_workers = enhanced_swarm.workers.count_documents({
            'status': 'active',
            'last_heartbeat': {
                '$gte': datetime.now(timezone.utc).replace(
                    hour=datetime.now(timezone.utc).hour - 1
                )
            }
        })
        
        pending_tasks = enhanced_swarm.tasks.count_documents({'status': 'pending'})
        completed_today = enhanced_swarm.tasks.count_documents({
            'status': 'completed',
            'completed_at': {
                '$gte': datetime.now(timezone.utc).replace(hour=0, minute=0, second=0)
            }
        })
        
        priority_pending = enhanced_swarm.priority_cache.count_documents({
            'status': 'pending'
        })
        
        metrics = {
            'database': {
                'total_cards': total_cards,
                'analyzed_cards': analyzed_cards,
                'analysis_percentage': round((analyzed_cards / total_cards * 100), 2) if total_cards > 0 else 0
            },
            'workers': {
                'total_registered': enhanced_swarm.workers.count_documents({}),
                'currently_active': active_workers
            },
            'tasks': {
                'pending': pending_tasks,
                'completed_today': completed_today,
                'high_priority_pending': priority_pending
            },
            'system': {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'version': '2.0-enhanced'
            }
        }
        
        return JsonResponse(metrics)
        
    except Exception as e:
        if logger:
            logger.error(f"❌ System metrics failed: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

# Alias for backward compatibility with universal worker
status = enhanced_swarm_status
