"""
URL configuration for the cards app.
"""

from django.urls import path
from . import views
from . import views

app_name = 'cards'

urlpatterns = [
    # Public views
    path('', views.home, name='home'),
    path('card/<str:card_uuid>/', views.card_detail, name='card_detail'),
    path('browse/', views.browse_cards, name='browse'),
    path('abyss/', views.the_abyss, name='the_abyss'),
    
    # Analysis features
    path('analysis/dashboard/', views.analysis_dashboard, name='analysis_dashboard'),
    path('api/analyze/<str:card_uuid>/', views.start_analysis, name='start_analysis'),
    
    # Job Queue Management    path('queue/control/', views.worker_control_panel, name='worker_control_panel'),
    path('api/queue/status/', views.job_queue_status, name='job_queue_status'),
    path('api/queue/bulk-queue/', views.bulk_queue_cards, name='bulk_queue_cards'),
    path('api/queue/retry/<str:job_id>/', views.retry_failed_job, name='retry_failed_job'),
    path('api/queue/cleanup/', views.cleanup_old_jobs, name='cleanup_old_jobs'),
    path('api/queue/reset-stuck/', views.reset_stuck_jobs, name='reset_stuck_jobs'),
    
    # Admin views (legacy, keeping for compatibility)
    path('admin-cards/', views.admin_card_list, name='admin_card_list'),
    path('admin-cards/<str:card_uuid>/', views.admin_card_detail, name='admin_card_detail'),
]
