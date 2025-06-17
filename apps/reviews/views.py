# filepath: apps/reviews/views.py
"""
Views para la app Reviews.
"""
from django.views.generic import ListView
from django.http import HttpResponse


class ReviewListView(ListView):
    """View placeholder para lista de reseñas."""
    
    def get(self, request, *args, **kwargs):
        return HttpResponse("Reviews List - Placeholder View")
