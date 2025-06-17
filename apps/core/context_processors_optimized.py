"""
Context processor optimizado para evitar consultas innecesarias en login.
"""
from django.core.cache import cache
from django.conf import settings

def optimized_cart_context(request):
    """Context processor optimizado para el carrito."""
    # Solo procesar carrito si el usuario está autenticado y no está en páginas de auth
    if (request.user.is_authenticated and 
        not request.path.startswith('/accounts/') and
        not request.path.startswith('/auth/')):
        
        # Usar cache para evitar consultas repetidas
        cache_key = f"cart_count_{request.user.id}"
        cart_count = cache.get(cache_key)
        
        if cart_count is None:
            try:
                from apps.cart.models import Cart
                cart = Cart.objects.filter(user=request.user).first()
                cart_count = cart.items.count() if cart else 0
                cache.set(cache_key, cart_count, 300)  # Cache por 5 minutos
            except:
                cart_count = 0
        
        return {'cart_count': cart_count}
    
    return {'cart_count': 0}

def optimized_site_context(request):
    """Context processor optimizado para información del sitio."""
    # Usar cache para información estática del sitio
    cache_key = 'site_context_data'
    site_data = cache.get(cache_key)
    
    if site_data is None:
        site_data = {
            'site_name': 'Tech Ecommerce',
            'site_description': 'Tecnología de Vanguardia',
            'support_email': 'soporte@techecommerce.com',
            'current_year': 2025,
        }
        cache.set(cache_key, site_data, 3600)  # Cache por 1 hora
    
    return site_data
