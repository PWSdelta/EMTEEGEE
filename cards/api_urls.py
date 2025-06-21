from django.urls import path
from . import api_views

app_name = 'cards_api'

urlpatterns = [
    # Analysis request endpoints
    path('request-analysis/', api_views.RequestAnalysisView.as_view(), name='request_analysis'),
    path('queue-status/', api_views.analysis_queue_status, name='queue_status'),
    path('card-status/<str:card_uuid>/', api_views.card_analysis_status, name='card_status'),
]
