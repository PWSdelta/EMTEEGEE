"""
Direct API URLs for swarm workers (without cards/ prefix)
"""

from django.urls import path
from . import swarm_api

urlpatterns = [
    # Swarm API endpoints - direct access for workers
    path('register', swarm_api.register_worker, name='api_swarm_register'),
    path('get_work', swarm_api.get_work, name='api_swarm_get_work'),
    path('submit_results', swarm_api.submit_results, name='api_swarm_submit_results'),
    path('status', swarm_api.swarm_status, name='api_swarm_status'),
    path('workers', swarm_api.worker_health, name='api_swarm_workers'),
]
