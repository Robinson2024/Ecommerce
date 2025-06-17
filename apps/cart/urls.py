# filepath: apps/cart/urls.py
"""
URLs para la app Cart con funcionalidad HTMX.
"""
from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    # Vista principal del carrito
    path('', views.CartDetailView.as_view(), name='detail'),
    
    # HTMX endpoints para operaciones del carrito
    path('add/', views.AddToCartView.as_view(), name='add'),
    path('update/', views.UpdateCartItemView.as_view(), name='update'),
    path('remove/', views.RemoveFromCartView.as_view(), name='remove'),
    path('clear/', views.ClearCartView.as_view(), name='clear'),
    
    # Endpoints para componentes específicos
    path('summary/', views.CartSummaryView.as_view(), name='summary'),
    path('count/', views.CartCountView.as_view(), name='count'),
]
