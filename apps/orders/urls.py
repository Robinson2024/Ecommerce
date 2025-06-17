# filepath: apps/orders/urls.py
"""
URLs para la app Orders.
"""
from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Order management
    path('', views.OrderListView.as_view(), name='list'),
    path('create/', views.OrderCreateView.as_view(), name='create'),
    path('<str:order_number>/', views.OrderDetailView.as_view(), name='detail'),
    path('<str:order_number>/cancel/', views.OrderCancelView.as_view(), name='cancel'),
    path('<str:order_number>/track/', views.OrderTrackingView.as_view(), name='track'),
    
    # Checkout process
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('checkout/shipping/', views.ShippingMethodView.as_view(), name='shipping_method'),
    path('confirmation/', views.OrderConfirmationView.as_view(), name='confirmation'),
    
    # HTMX endpoints
    path('htmx/calculate-shipping/', views.CalculateShippingView.as_view(), name='calculate_shipping'),
    path('htmx/update-address/', views.UpdateAddressView.as_view(), name='update_address'),
]
