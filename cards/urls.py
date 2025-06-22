"""
URL configuration for Cards app including Swarm API
"""

from django.urls import path
from . import views, swarm_api

app_name = 'cards'

urlpatterns = [
    # Standard card views (to be implemented)
    path('', views.index, name='index'),
    
    # Swarm API endpoints
    path('api/swarm/register', swarm_api.register_worker, name='swarm_register'),
    path('api/swarm/get_work', swarm_api.get_work, name='swarm_get_work'),
    path('api/swarm/submit_results', swarm_api.submit_results, name='swarm_submit_results'),
    path('api/swarm/status', swarm_api.swarm_status, name='swarm_status'),
    path('api/swarm/workers', swarm_api.worker_health, name='swarm_workers'),
]
