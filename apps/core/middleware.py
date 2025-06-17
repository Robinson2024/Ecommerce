"""
Middleware personalizado para logging detallado de requests y responses.
"""
import logging
import time
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

class DetailedLoggingMiddleware(MiddlewareMixin):
    """Middleware que registra información detallada de cada request."""
    
    def process_request(self, request):
        """Log de información de entrada de cada request."""
        request._start_time = time.time()
        
        # Información básica del request
        logger.info(f"🌐 NUEVA REQUEST: {request.method} {request.get_full_path()}")
        logger.info(f"📍 IP: {self.get_client_ip(request)}")
        logger.info(f"🔧 User-Agent: {request.META.get('HTTP_USER_AGENT', 'N/A')}")
        
        # Usuario autenticado
        if hasattr(request, 'user') and request.user.is_authenticated:
            logger.info(f"👤 Usuario: {request.user.username} (ID: {request.user.id})")
        else:
            logger.info("👤 Usuario: Anónimo")
        
        # Headers importantes
        referer = request.META.get('HTTP_REFERER', 'N/A')
        if referer != 'N/A':
            logger.info(f"🔗 Referer: {referer}")
        
        # Query parameters
        if request.GET:
            logger.info(f"❓ Query params: {dict(request.GET)}")
        
        # POST data (sin datos sensibles)
        if request.method == 'POST' and request.POST:
            safe_post_data = {}
            for key, value in request.POST.items():
                if key.lower() in ['password', 'csrfmiddlewaretoken']:
                    safe_post_data[key] = '[HIDDEN]'
                else:
                    safe_post_data[key] = value
            logger.info(f"📝 POST data: {safe_post_data}")
        
        return None
    
    def process_response(self, request, response):
        """Log de información de salida de cada response."""
        if hasattr(request, '_start_time'):
            duration = time.time() - request._start_time
            duration_ms = round(duration * 1000, 2)
            
            # Status code con emoji
            status_emoji = self.get_status_emoji(response.status_code)
            
            logger.info(f"✅ RESPONSE: {status_emoji} {response.status_code} - {duration_ms}ms")
            
            # Log de respuestas lentas
            if duration_ms > 1000:
                logger.warning(f"⚠️ RESPUESTA LENTA: {request.method} {request.get_full_path()} - {duration_ms}ms")
            
            # Log de errores
            if response.status_code >= 400:
                logger.error(f"❌ ERROR RESPONSE: {response.status_code} para {request.get_full_path()}")
        
        return response
    
    def process_exception(self, request, exception):
        """Log de excepciones no manejadas."""
        logger.error(f"💥 EXCEPCIÓN: {type(exception).__name__}: {str(exception)}")
        logger.error(f"🎯 URL: {request.get_full_path()}")
        logger.error(f"🔧 Método: {request.method}")
        
        if hasattr(request, 'user') and request.user.is_authenticated:
            logger.error(f"👤 Usuario afectado: {request.user.username}")
        
        return None
    
    def get_client_ip(self, request):
        """Obtiene la IP real del cliente."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def get_status_emoji(self, status_code):
        """Retorna emoji según el status code."""
        if status_code < 300:
            return "🟢"
        elif status_code < 400:
            return "🟡"
        elif status_code < 500:
            return "🟠"
        else:
            return "🔴"
