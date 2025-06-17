"""
URLs para la app core.
"""

from django.urls import path
from django.views.generic import TemplateView
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('health/', views.health_check, name='health_check'),
    path('diagnostico/', views.diagnostico_view, name='diagnostico'),  # Vista temporal de diagnóstico
    path('test-correccion/', views.test_correccion_view, name='test_correccion'),  # Test de corrección
    path('test-styles/', TemplateView.as_view(template_name='test_styles.html'), name='test_styles'),  # Test de estilos
]
