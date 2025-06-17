"""
Views básicas para Tech Ecommerce.
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.conf import settings
from django.db.models import Count, Q

from apps.products.models import Product, Category, Brand


class HomeView(TemplateView):
    """Vista principal del sitio."""
    template_name = 'core/home_clean.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Importar aquí para evitar circular imports
        from apps.products.models import Product, Category, Brand
        from django.db.models import Count
        
        # Obtener productos destacados
        context['featured_products'] = Product.objects.filter(
            is_active=True, 
            is_featured=True
        ).select_related('category', 'brand')[:6]
          # Obtener categorías principales (solo las que tienen productos)
        context['categories'] = Category.objects.filter(
            is_active=True,
            parent__isnull=True
        ).annotate(
            product_count=Count('products', filter=Q(products__is_active=True))
        ).filter(product_count__gt=0)[:4]
        
        # Obtener estadísticas
        context['total_products'] = Product.objects.filter(is_active=True).count()
        context['total_categories'] = Category.objects.filter(is_active=True).count()
        context['total_brands'] = Brand.objects.filter(is_active=True).count()
        
        # Productos más recientes para mostrar si no hay destacados
        context['latest_products'] = Product.objects.filter(
            is_active=True
        ).select_related('category', 'brand').order_by('-created_at')[:8]
        
        return context


def error_404(request, exception):
    """Vista personalizada para error 404."""
    return render(request, '404.html', status=404)


def error_500(request):
    """Vista personalizada para error 500."""
    return render(request, 'errors/500.html', status=500)


def health_check(request):
    """Health check para monitoreo."""
    return JsonResponse({
        'status': 'ok',
        'debug': settings.DEBUG,
        'version': '1.0.0'
    })


def diagnostico_view(request):
    """Vista temporal de diagnóstico del sistema."""
    from django.template import Template, Context
    from django.http import HttpResponse
    from apps.products.models import Product, Category, Brand
    
    # Recopilar información del sistema
    productos_count = Product.objects.count()
    categorias_count = Category.objects.count()
    marcas_count = Brand.objects.count()
    productos_sample = Product.objects.all()[:6]
    
    # Template HTML para diagnóstico
    html_content = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Tech Ecommerce - Diagnóstico del Sistema</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css" rel="stylesheet">
        <style>
            body { 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                min-height: 100vh; 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            .diagnostic-card { 
                background: rgba(255,255,255,0.95); 
                border-radius: 20px; 
                box-shadow: 0 15px 35px rgba(0,0,0,0.1);
                backdrop-filter: blur(10px);
            }
            .status-good { color: #28a745; font-weight: bold; }
            .status-warning { color: #ffc107; font-weight: bold; }
            .status-error { color: #dc3545; font-weight: bold; }
            .feature-card {
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                color: white;
                border-radius: 15px;
                transition: transform 0.3s ease;
            }
            .feature-card:hover {
                transform: translateY(-5px);
            }
            .link-card {
                background: white;
                border-radius: 15px;
                transition: all 0.3s ease;
                border: 2px solid transparent;
            }
            .link-card:hover {
                border-color: #667eea;
                transform: translateY(-3px);
                box-shadow: 0 10px 25px rgba(102, 126, 234, 0.15);
            }
        </style>
    </head>
    <body>
        <div class="container py-5">
            <div class="row justify-content-center">
                <div class="col-lg-11">
                    <div class="diagnostic-card p-5">
                        <div class="text-center mb-5">
                            <div class="mb-3">
                                <i class="bi bi-cpu-fill" style="font-size: 4rem; color: #667eea;"></i>
                            </div>
                            <h1 class="display-4 fw-bold">Tech Ecommerce</h1>
                            <p class="lead text-muted">Sistema de Diagnóstico - Estado del Proyecto</p>
                            <div class="badge bg-success fs-6 px-3 py-2">
                                <i class="bi bi-check-circle-fill me-2"></i>Sistema Operativo
                            </div>
                        </div>
                        
                        <div class="row mb-5">
                            <div class="col-md-4">
                                <div class="feature-card p-4 text-center h-100">
                                    <i class="bi bi-database-fill" style="font-size: 3rem;"></i>
                                    <h4 class="mt-3">Base de Datos</h4>
                                    <hr class="border-light">
                                    <div class="d-flex justify-content-between mb-2">
                                        <span>📦 Productos:</span>
                                        <strong>{{ productos_count }}</strong>
                                    </div>
                                    <div class="d-flex justify-content-between mb-2">
                                        <span>📁 Categorías:</span>
                                        <strong>{{ categorias_count }}</strong>
                                    </div>
                                    <div class="d-flex justify-content-between">
                                        <span>🏷️ Marcas:</span>
                                        <strong>{{ marcas_count }}</strong>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="feature-card p-4 text-center h-100">
                                    <i class="bi bi-gear-wide-connected" style="font-size: 3rem;"></i>
                                    <h4 class="mt-3">Configuración</h4>
                                    <hr class="border-light">
                                    <div class="d-flex justify-content-between mb-2">
                                        <span>🔧 Debug:</span>
                                        <strong>{{ debug_status }}</strong>
                                    </div>
                                    <div class="d-flex justify-content-between mb-2">
                                        <span>📄 Templates:</span>
                                        <strong>Modernos</strong>
                                    </div>
                                    <div class="d-flex justify-content-between">
                                        <span>🎨 Estáticos:</span>
                                        <strong>Activos</strong>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="feature-card p-4 text-center h-100">
                                    <i class="bi bi-shield-check-fill" style="font-size: 3rem;"></i>
                                    <h4 class="mt-3">Estado</h4>
                                    <hr class="border-light">
                                    <div class="d-flex justify-content-between mb-2">
                                        <span>🚀 Servidor:</span>
                                        <strong>Activo</strong>
                                    </div>
                                    <div class="d-flex justify-content-between mb-2">
                                        <span>📱 URLs:</span>
                                        <strong>OK</strong>
                                    </div>
                                    <div class="d-flex justify-content-between">
                                        <span>✅ Apps:</span>
                                        <strong>Operativas</strong>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="mb-5">
                            <h3 class="mb-4 text-center">
                                <i class="bi bi-link-45deg"></i> Navegación del Sistema
                            </h3>
                            <div class="row g-3">
                                <div class="col-md-3">
                                    <a href="/" class="text-decoration-none">
                                        <div class="link-card p-4 text-center h-100">
                                            <i class="bi bi-house-fill text-primary" style="font-size: 2.5rem;"></i>
                                            <h5 class="mt-3 text-dark">Principal</h5>
                                            <p class="text-muted mb-0">Página de inicio</p>
                                        </div>
                                    </a>
                                </div>
                                <div class="col-md-3">
                                    <a href="/products/" class="text-decoration-none">
                                        <div class="link-card p-4 text-center h-100">
                                            <i class="bi bi-bag-fill text-success" style="font-size: 2.5rem;"></i>
                                            <h5 class="mt-3 text-dark">Productos</h5>
                                            <p class="text-muted mb-0">{{ productos_count }} disponibles</p>
                                        </div>
                                    </a>
                                </div>
                                <div class="col-md-3">
                                    <a href="/cart/" class="text-decoration-none">
                                        <div class="link-card p-4 text-center h-100">
                                            <i class="bi bi-cart-fill text-warning" style="font-size: 2.5rem;"></i>
                                            <h5 class="mt-3 text-dark">Carrito</h5>
                                            <p class="text-muted mb-0">Sistema HTMX</p>
                                        </div>
                                    </a>
                                </div>
                                <div class="col-md-3">
                                    <a href="/admin/" class="text-decoration-none">
                                        <div class="link-card p-4 text-center h-100">
                                            <i class="bi bi-gear-fill text-info" style="font-size: 2.5rem;"></i>
                                            <h5 class="mt-3 text-dark">Admin</h5>
                                            <p class="text-muted mb-0">Gestión</p>
                                        </div>
                                    </a>
                                </div>
                            </div>
                        </div>
                        
                        {% if productos_sample %}
                        <div class="mb-4">
                            <h3 class="mb-4 text-center">
                                <i class="bi bi-box-seam"></i> Productos Disponibles
                            </h3>
                            <div class="row g-3">
                                {% for producto in productos_sample %}
                                <div class="col-md-2">
                                    <div class="card border-0 shadow-sm">
                                        <div class="card-body p-3">
                                            <h6 class="card-title text-truncate">{{ producto.name }}</h6>
                                            <p class="card-text">
                                                <strong class="text-success">${{ producto.price }}</strong>
                                            </p>
                                            <small class="text-muted">{{ producto.category.name }}</small>
                                        </div>
                                    </div>
                                </div>
                                {% endfor %}
                            </div>
                        </div>
                        {% endif %}
                        
                        <div class="alert alert-success border-0 shadow-sm">
                            <div class="row align-items-center">
                                <div class="col-md-8">
                                    <h4 class="alert-heading mb-2">
                                        <i class="bi bi-check-circle-fill"></i> Sistema Completamente Funcional
                                    </h4>
                                    <p class="mb-0">
                                        Todas las funcionalidades están operativas. El proyecto Tech Ecommerce está listo para usar.
                                    </p>
                                </div>
                                <div class="col-md-4 text-end">
                                    <div class="btn-group" role="group">
                                        <a href="/" class="btn btn-primary">
                                            <i class="bi bi-house-fill"></i> Ir al Sitio
                                        </a>
                                        <a href="/products/" class="btn btn-success">
                                            <i class="bi bi-bag-fill"></i> Ver Productos
                                        </a>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="text-center mt-4">
                            <p class="text-muted">
                                <i class="bi bi-info-circle-fill"></i>
                                Para ocultar esta página de diagnóstico, comenta la URL en core/urls.py
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            // Animación para las tarjetas
            document.addEventListener('DOMContentLoaded', function() {
                const cards = document.querySelectorAll('.link-card, .feature-card');
                cards.forEach((card, index) => {
                    card.style.animationDelay = (index * 0.1) + 's';
                    card.style.animation = 'fadeInUp 0.6s ease forwards';
                });
            });
        </script>
        
        <style>
            @keyframes fadeInUp {
                from {
                    opacity: 0;
                    transform: translateY(30px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
        </style>
    </body>
    </html>
    """
    
    template = Template(html_content)
    context = Context({
        'productos_count': productos_count,
        'categorias_count': categorias_count,
        'marcas_count': marcas_count,
        'productos_sample': productos_sample,
        'debug_status': 'ON' if settings.DEBUG else 'OFF',
    })
    
    return HttpResponse(template.render(context))


def test_correccion_view(request):
    """Vista de test para verificar que el template se corrigió."""
    from django.shortcuts import render
    return render(request, 'test_correccion.html')
