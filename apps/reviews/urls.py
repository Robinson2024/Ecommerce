# filepath: apps/reviews/urls.py
"""
URLs para la app Reviews.
"""
from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    # Placeholder - se implementarán las URLs reales en la siguiente fase
    path('', views.ReviewListView.as_view(), name='list'),
]
