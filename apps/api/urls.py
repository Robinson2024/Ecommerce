# filepath: apps/api/urls.py
"""
URLs para la API REST.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

app_name = 'api'

# Router para ViewSets
router = DefaultRouter()
# Se registrarán los ViewSets en la siguiente fase

urlpatterns = [
    path('', include(router.urls)),
    # Placeholder - se implementarán las URLs de API reales en la siguiente fase
]
