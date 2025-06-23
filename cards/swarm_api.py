"""
Django REST API endpoints for AI Analysis Swarm System
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import sys
import os
from bson import ObjectId
from datetime import datetime

# Custom JSON encoder to handle MongoDB ObjectId and datetime objects
class MongoJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

# Add the parent directory to the path to import swarm_manager
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from swarm_manager_simple import SwarmManager
    # Initialize swarm manager
    swarm = SwarmManager()
except ImportError as e:
    print(f"Warning: SwarmManager not available: {e}")
    swarm = None

@csrf_exempt
@require_http_methods(["POST"])
def register_worker(request):
    """Register a new worker node"""
    try:
        data = json.loads(request.body)
        worker_id = data.get('worker_id')
        capabilities = data.get('capabilities', {})
        
        if not worker_id:
            return JsonResponse({'error': 'worker_id required'}, status=400)
        
        result = swarm.register_worker(worker_id, capabilities)
        return JsonResponse(result)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def get_work(request):
    """Get work assignments for a worker"""
    try:
        data = json.loads(request.body)
        worker_id = data.get('worker_id')
        max_tasks = data.get('max_tasks', 1)
        
        if not worker_id:
            return JsonResponse({'error': 'worker_id required'}, status=400)
        
        tasks = swarm.get_work(worker_id, max_tasks)
        
        # Use custom encoder to handle ObjectId
        json_tasks = json.loads(json.dumps(tasks, cls=MongoJSONEncoder))
        return JsonResponse({'tasks': json_tasks})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def submit_results(request):
    """Accept completed work from a worker - simplified approach"""
    try:
        data = json.loads(request.body)
        worker_id = data.get('worker_id')
        card_id = data.get('card_id')
        results = data.get('results', {})
        
        if not all([worker_id, card_id, results]):
            return JsonResponse({'error': 'worker_id, card_id, and results required'}, status=400)
          # Update card directly
        for component_type, component_data in results.items():
            update_data = {
                f'analysis.components.{component_type}': {
                    'content': component_data,
                    'generated_at': datetime.now().isoformat(),
                    'worker_id': worker_id
                }
            }
            
            swarm.cards.update_one(
                {'_id': ObjectId(card_id)},
                {'$set': update_data}
            )
        
        # Update worker stats
        swarm.workers.update_one(
            {'worker_id': worker_id},
            {
                '$inc': {'tasks_completed': 1},
                '$set': {'last_heartbeat': datetime.now().isoformat()}
            }
        )
        
        return JsonResponse({'status': 'success', 'message': 'Results submitted'})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def swarm_status(request):
    """Get overall swarm system status"""
    try:
        status = swarm.get_swarm_status()
        # Use custom encoder for any ObjectId or datetime objects
        json_status = json.loads(json.dumps(status, cls=MongoJSONEncoder))
        return JsonResponse(json_status)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def worker_health(request):
    """Get health status of all workers"""
    try:
        # This would be implemented to show worker health
        return JsonResponse({'status': 'not_implemented'})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def heartbeat(request):
    """Worker heartbeat endpoint"""
    try:
        data = json.loads(request.body)
        worker_id = data.get('worker_id')
        
        if not worker_id:
            return JsonResponse({'error': 'worker_id required'}, status=400)
        
        if swarm is None:
            return JsonResponse({'error': 'SwarmManager not available'}, status=500)
        
        # Update worker heartbeat
        result = swarm.workers.update_one(
            {'worker_id': worker_id},
            {
                '$set': {
                    'last_heartbeat': datetime.now(),
                    'status': data.get('status', 'active'),
                    'active_tasks': data.get('active_tasks', 0),
                    'completed_tasks': data.get('completed_tasks', 0)
                }
            }
        )
        
        if result.matched_count > 0:
            return JsonResponse({'status': 'success', 'message': 'Heartbeat received'})
        else:
            return JsonResponse({'error': 'Worker not found'}, status=404)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
