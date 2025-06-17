"""
Middleware simple para testing.
"""
from django.utils.deprecation import MiddlewareMixin


class DetailedLoggingMiddleware(MiddlewareMixin):
    """Middleware simple de prueba."""
    
    def process_request(self, request):
        print(f"Request: {request.method} {request.path}")
        return None
