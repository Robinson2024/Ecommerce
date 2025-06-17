"""
Middleware personalizado para optimizar rendimiento en páginas de autenticación.
"""
from django.core.cache import cache
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin
import time

class LoginOptimizationMiddleware(MiddlewareMixin):
    """
    Middleware para optimizar el rendimiento de las páginas de autenticación.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.auth_urls = [
            '/accounts/login/',
            '/accounts/signup/',
            '/accounts/logout/',
            '/accounts/logout-success/',
            '/accounts/password/reset/',
        ]
        super().__init__(get_response)
    
    def process_request(self, request):
        """
        Optimizaciones antes de procesar la request.
        """
        # Marcar inicio de tiempo para páginas de auth
        if any(request.path.startswith(url) for url in self.auth_urls):
            request._auth_start_time = time.time()
            
            # Para páginas de login/signup, deshabilitar algunos context processors innecesarios
            if request.path.startswith('/accounts/login/') or request.path.startswith('/accounts/signup/'):
                # Marcar para optimización
                request._optimize_auth = True
        
        return None
    
    def process_response(self, request, response):
        """
        Optimizaciones después de procesar la response.
        """
        # Medir tiempo de procesamiento para páginas de auth
        if hasattr(request, '_auth_start_time'):
            duration = time.time() - request._auth_start_time
            
            # Log si el tiempo es mayor a 1 segundo
            if duration > 1.0:
                import logging
                logger = logging.getLogger('performance')
                logger.warning(f"Página de auth lenta: {request.path} tomó {duration:.2f}s")
        
        # Cache de páginas estáticas de auth por poco tiempo
        if (response.status_code == 200 and 
            request.method == 'GET' and 
            not request.user.is_authenticated and
            request.path in ['/accounts/login/', '/accounts/signup/']):
            
            # Cache solo por 5 minutos para páginas de auth
            response['Cache-Control'] = 'public, max-age=300'
        
        return response
