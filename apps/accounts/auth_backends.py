"""
Backend de autenticación optimizado para mejorar rendimiento del login.
"""
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db.models import Q
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class OptimizedAuthBackend(ModelBackend):
    """
    Backend de autenticación optimizado con cache y consultas eficientes.
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Autenticación optimizada con cache de usuarios.
        """
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
        
        if username is None or password is None:
            return None
        
        # Crear clave de cache basada en username/email
        cache_key = f"auth_user_{username}"
        user = cache.get(cache_key)
        
        if user is None:
            try:
                # Consulta optimizada con select_related si es necesario
                user = User.objects.select_related().get(
                    Q(username__iexact=username) | Q(email__iexact=username),
                    is_active=True
                )
                # Cache del usuario por 5 minutos
                cache.set(cache_key, user, 300)
                logger.info(f"Usuario {username} cargado desde DB y cacheado")
            except User.DoesNotExist:
                logger.warning(f"Intento de login fallido para usuario: {username}")
                return None
            except User.MultipleObjectsReturned:
                logger.error(f"Múltiples usuarios encontrados para: {username}")
                return None
        else:
            logger.info(f"Usuario {username} cargado desde cache")
        
        # Verificar contraseña
        if user and user.check_password(password):
            logger.info(f"Login exitoso para usuario: {username}")
            # Actualizar cache con datos frescos después del login exitoso
            cache.set(cache_key, user, 300)
            return user
        
        logger.warning(f"Contraseña incorrecta para usuario: {username}")
        return None
    
    def get_user(self, user_id):
        """
        Obtener usuario por ID con cache.
        """
        cache_key = f"auth_user_id_{user_id}"
        user = cache.get(cache_key)
        
        if user is None:
            try:
                user = User.objects.select_related().get(pk=user_id, is_active=True)
                cache.set(cache_key, user, 600)  # Cache por 10 minutos
            except User.DoesNotExist:
                return None
        
        return user
