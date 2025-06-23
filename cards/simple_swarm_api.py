"""
SUPER SIMPLE Swarm API - Instant Work Assignment
================================================

Just 3 endpoints:
1. register - Register worker
2. get_work - Get work INSTANTLY (pop from queue)
3. submit_results - Submit completed work

No complex logic, no batching, no fancy algorithms.
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

try:
    from .simple_swarm_manager import simple_swarm
    print("✅ Simple swarm manager imported successfully")
except ImportError as e:
    print(f"❌ Simple swarm manager import failed: {e}")
    simple_swarm = None

@csrf_exempt
@require_http_methods(["POST"])
def register_worker_simple(request):
    """Register a worker - SIMPLE"""
    try:
        data = json.loads(request.body)
        worker_id = data.get('worker_id')
        capabilities = data.get('capabilities', {})
        
        if not worker_id:
            return JsonResponse({'error': 'worker_id required'}, status=400)
        
        if simple_swarm is None:
            return JsonResponse({'error': 'Simple swarm not available'}, status=500)
        
        result = simple_swarm.register_worker(worker_id, capabilities)
        return JsonResponse(result)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def get_work_simple(request):
    """Get work INSTANTLY - just pop from queue"""
    try:
        data = json.loads(request.body)
        worker_id = data.get('worker_id')
        
        if not worker_id:
            return JsonResponse({'error': 'worker_id required'}, status=400)
        
        if simple_swarm is None:
            return JsonResponse({'error': 'Simple swarm not available'}, status=500)
        
        # Get work instantly
        task = simple_swarm.get_work_instant(worker_id)
        
        if task:
            return JsonResponse({'tasks': [task]})
        else:
            return JsonResponse({'tasks': []})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def submit_results_simple(request):
    """Submit completed work - SIMPLE"""
    try:
        data = json.loads(request.body)
        worker_id = data.get('worker_id')
        card_id = data.get('card_id')
        results = data.get('results', {})
        
        if not all([worker_id, card_id, results]):
            return JsonResponse({'error': 'worker_id, card_id, and results required'}, status=400)
        
        if simple_swarm is None:
            return JsonResponse({'error': 'Simple swarm not available'}, status=500)
        
        success = simple_swarm.submit_results(worker_id, card_id, results)
        
        if success:
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'error': 'Failed to submit results'}, status=500)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def status_simple(request):
    """Get simple status"""
    try:
        if simple_swarm is None:
            return JsonResponse({'error': 'Simple swarm not available'}, status=500)
        
        status = simple_swarm.get_status()
        return JsonResponse(status)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
