"""
Middleware personalizado para logging detallado de requests y responses.
"""
import logging
import time
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class DetailedLoggingMiddleware(MiddlewareMixin):
    """Middleware que registra informacion detallada de cada request."""
    
    def process_request(self, request):
        """Log de informacion de entrada de cada request."""
        request._start_time = time.time()
        
        # Informacion basica del request
        logger.info(f"NEW REQUEST: {request.method} {request.get_full_path()}")
        
        # IP del cliente
        client_ip = self.get_client_ip(request)
        logger.info(f"Client IP: {client_ip}")
        
        # Usuario autenticado
        if hasattr(request, 'user') and request.user.is_authenticated:
            logger.info(f"User: {request.user.username} (ID: {request.user.id})")
        else:
            logger.info("User: Anonymous")
        
        # Headers importantes
        user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
        if len(user_agent) > 50:
            user_agent = user_agent[:50] + "..."
        logger.info(f"Browser: {user_agent}")
        
        # Referer si existe
        referer = request.META.get('HTTP_REFERER')
        if referer:
            logger.info(f"From: {referer}")
        
        # Query parameters
        if request.GET:
            logger.info(f"Params: {dict(request.GET)}")
        
        # POST data (sin datos sensibles)
        if request.method == 'POST' and request.POST:
            safe_post_data = {}
            for key, value in request.POST.items():
                if key.lower() in ['password', 'csrfmiddlewaretoken']:
                    safe_post_data[key] = '[HIDDEN]'
                else:
                    safe_post_data[key] = value
            logger.info(f"POST Data: {safe_post_data}")
        
        return None
    def process_response(self, request, response):
        """Log de informacion de salida de cada response."""
        if hasattr(request, '_start_time'):
            duration = time.time() - request._start_time
            duration_ms = round(duration * 1000, 2)
            
            logger.info(f"RESPONSE: {response.status_code} - {duration_ms}ms")
            
            # Log de respuestas lentas
            if duration_ms > 1000:
                logger.warning(f"SLOW RESPONSE: {request.method} {request.get_full_path()} - {duration_ms}ms")
            
            # Log de errores
            if response.status_code >= 400:
                logger.error(f"ERROR RESPONSE: {response.status_code} for {request.get_full_path()}")
        
        return response
    
    def process_exception(self, request, exception):
        """Log de excepciones no manejadas."""
        logger.error(f"EXCEPTION: {type(exception).__name__}: {str(exception)}")
        logger.error(f"URL: {request.get_full_path()}")
        logger.error(f"Method: {request.method}")
        
        if hasattr(request, 'user') and request.user.is_authenticated:
            logger.error(f"Affected User: {request.user.username}")
        
        return None
    
    def get_client_ip(self, request):
        """Obtiene la IP real del cliente."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
