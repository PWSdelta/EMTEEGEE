"""
Simple Swarm API URLs - INSTANT work assignment
"""

from django.urls import path
from . import simple_swarm_api

urlpatterns = [
    path('register', simple_swarm_api.register_worker_simple, name='simple_swarm_register'),
    path('get_work', simple_swarm_api.get_work_simple, name='simple_swarm_get_work'),
    path('submit_results', simple_swarm_api.submit_results_simple, name='simple_swarm_submit_results'),
    path('status', simple_swarm_api.status_simple, name='simple_swarm_status'),
]
