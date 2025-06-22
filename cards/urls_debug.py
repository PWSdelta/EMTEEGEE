"""
URL configuration for Cards app - debug version
"""

from django.urls import path

app_name = 'cards'

# Test each import separately
try:
    from . import views
    print("Views import successful")
except Exception as e:
    print(f"Views import failed: {e}")

urlpatterns = []
