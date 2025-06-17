"""
Context processors para Tech Ecommerce.
"""

from django.conf import settings
# from apps.cart.models import Cart  # TODO: Implementar en Fase 2


def site_context(request):
    """
    Context processor que añade información global del sitio.
    """
    context = {
        'SITE_NAME': 'Tech Ecommerce',
        'SITE_URL': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
        'CURRENCY': settings.ECOMMERCE_SETTINGS.get('CURRENCY', 'COP'),
        'CURRENCY_SYMBOL': settings.ECOMMERCE_SETTINGS.get('CURRENCY_SYMBOL', '$'),
        'FREE_SHIPPING_THRESHOLD': settings.ECOMMERCE_SETTINGS.get('FREE_SHIPPING_THRESHOLD', 100000),
    }
    
    # TODO: Implementar carrito en Fase 2
    context['cart_items_count'] = 0
    context['cart_total'] = 0
    
    return context
