# filepath: apps/wishlist/urls.py
"""
URLs para la app Wishlist.
"""
from django.urls import path
from . import views

app_name = 'wishlist'

urlpatterns = [
    # Placeholder - se implementarán las URLs reales en la siguiente fase
    path('', views.WishlistView.as_view(), name='detail'),
]
