"""
URLs para la app accounts.
"""

from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Profile URLs
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileEditView.as_view(), name='profile_edit'),
    
    # Authentication URLs
    path('logout-success/', views.LogoutSuccessView.as_view(), name='logout_success'),
    
    # Address URLs
    path('addresses/', views.AddressListView.as_view(), name='address_list'),
    path('addresses/add/', views.AddressCreateView.as_view(), name='address_create'),
    path('addresses/<uuid:pk>/edit/', views.AddressUpdateView.as_view(), name='address_update'),
    path('addresses/<uuid:pk>/delete/', views.AddressDeleteView.as_view(), name='address_delete'),
    
    # Wishlist URLs
    path('wishlist/', views.WishlistView.as_view(), name='wishlist'),
    path('wishlist/add/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/', views.remove_from_wishlist, name='remove_from_wishlist'),
    
    # Order history
    path('orders/', views.OrderHistoryView.as_view(), name='order_history'),
    path('orders/<str:order_number>/', views.OrderDetailView.as_view(), name='order_detail'),
]
