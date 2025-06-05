from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('products/', include('products.urls')),
    path('pagos/', include('pagos.urls')),
    path('pedidos/', include('pedidos.urls')),
    path('usuarios/', include('usuarios.urls')),
    path('accounts/', include('allauth.urls')),
]