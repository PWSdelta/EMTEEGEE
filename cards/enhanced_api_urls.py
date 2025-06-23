"""
Enhanced API URLs for swarm workers v2.0
Routes for the enhanced distributed AI analysis system
"""

from django.urls import path
from . import enhanced_swarm_api

urlpatterns = [
    # Enhanced Swarm API endpoints - v2.0 with smart prioritization
    path('register', enhanced_swarm_api.register_worker, name='enhanced_swarm_register'),
    path('get_work', enhanced_swarm_api.get_work, name='enhanced_swarm_get_work'),
    path('submit_results', enhanced_swarm_api.submit_results, name='enhanced_swarm_submit_results'),
    path('heartbeat', enhanced_swarm_api.heartbeat, name='enhanced_swarm_heartbeat'),
    path('status', enhanced_swarm_api.enhanced_swarm_status, name='enhanced_swarm_status'),
    path('workers', enhanced_swarm_api.worker_health, name='enhanced_swarm_workers'),
    path('metrics', enhanced_swarm_api.system_metrics, name='enhanced_swarm_metrics'),
]
