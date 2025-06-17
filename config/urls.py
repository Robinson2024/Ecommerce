"""
URL configuration para Tech Ecommerce.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.views.generic import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Favicon
    path('favicon.ico', RedirectView.as_view(url='/static/favicon.svg', permanent=True)),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
      # Authentication
    path('accounts/', include('allauth.urls')),
    path('accounts/', include('apps.accounts.urls')),  # URLs personalizadas bajo accounts/# Apps URLs
    path('', include('apps.core.urls')),
    path('products/', include('apps.products.urls')),
    path('cart/', include('apps.cart.urls')),
    path('orders/', include('apps.orders.urls')),
    path('payments/', include('apps.payments.urls')),
    path('reviews/', include('apps.reviews.urls')),
    path('wishlist/', include('apps.wishlist.urls')),
    
    # API URLs
    path('api/v1/', include('apps.api.urls')),
]

# Media files en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Debug toolbar
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns

# Custom error handlers
handler404 = 'apps.core.views.error_404'
handler500 = 'apps.core.views.error_500'

# Admin customization
admin.site.site_header = 'Tech Ecommerce Admin'
admin.site.site_title = 'Tech Ecommerce'
admin.site.index_title = 'Panel de Administración'
