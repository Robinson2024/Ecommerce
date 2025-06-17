# filepath: apps/wishlist/views.py
"""
Views para la app Wishlist.
"""
from django.views.generic import View
from django.http import HttpResponse


class WishlistView(View):
    """View placeholder para wishlist."""
    
    def get(self, request, *args, **kwargs):
        return HttpResponse("Wishlist - Placeholder View")
