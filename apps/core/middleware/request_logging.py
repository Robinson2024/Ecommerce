"""
Middleware de logging para requests y responses.
"""
import logging
import time
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class DetailedLoggingMiddleware(MiddlewareMixin):
    """Middleware para logging detallado."""
    
    def process_request(self, request):
        """Procesa requests entrantes."""
        request._start_time = time.time()
        logger.info(f"REQUEST: {request.method} {request.get_full_path()}")
        
        # IP del cliente
        client_ip = self.get_client_ip(request)
        logger.info(f"Client IP: {client_ip}")
        
        # Usuario
        if hasattr(request, 'user') and request.user.is_authenticated:
            logger.info(f"User: {request.user.username}")
        else:
            logger.info("User: Anonymous")
        
        return None
    
    def process_response(self, request, response):
        """Procesa responses salientes."""
        if hasattr(request, '_start_time'):
            duration = time.time() - request._start_time
            duration_ms = round(duration * 1000, 2)
            logger.info(f"RESPONSE: {response.status_code} - {duration_ms}ms")
            
            if duration_ms > 1000:
                logger.warning(f"SLOW: {request.method} {request.get_full_path()} - {duration_ms}ms")
            
            if response.status_code >= 400:
                logger.error(f"ERROR: {response.status_code} for {request.get_full_path()}")
        
        return response
    
    def process_exception(self, request, exception):
        """Procesa excepciones."""
        logger.error(f"EXCEPTION: {type(exception).__name__}: {str(exception)}")
        logger.error(f"URL: {request.get_full_path()}")
        return None
    
    def get_client_ip(self, request):
        """Obtiene IP del cliente."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
