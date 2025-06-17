"""
Middleware de prueba simple para diagnóstico.
"""
from django.utils.deprecation import MiddlewareMixin


class SimpleLoggingMiddleware(MiddlewareMixin):
    """Middleware de prueba simple."""
    
    def process_request(self, request):
        print(f"Simple middleware: {request.method} {request.path}")
        return None
