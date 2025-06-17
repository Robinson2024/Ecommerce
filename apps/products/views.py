# filepath: apps/products/views.py
"""
Views para la app Products.
"""
from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import Product, Category, Brand


class ProductListView(ListView):
    """Vista para lista de productos."""
    model = Product
    template_name = 'products/search_modern.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).select_related('category', 'brand')
        
        # Filtro por categoría
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Filtro por marca
        brand_slug = self.request.GET.get('brand')
        if brand_slug:
            queryset = queryset.filter(brand__slug=brand_slug)
        
        # Filtro por productos destacados
        featured = self.request.GET.get('featured')
        if featured:
            queryset = queryset.filter(is_featured=True)
        
        # Búsqueda
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search) |
                Q(short_description__icontains=search) |
                Q(sku__icontains=search)
            )
        
        # Filtro por rango de precios
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Ordenamiento
        sort = self.request.GET.get('sort', '-created_at')
        if sort:
            queryset = queryset.order_by(sort)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True).order_by('name')
        context['brands'] = Brand.objects.filter(is_active=True).order_by('name')
        context['current_category'] = self.request.GET.get('category')
        context['current_brand'] = self.request.GET.get('brand')
        context['current_search'] = self.request.GET.get('search', '')
        context['current_sort'] = self.request.GET.get('sort', '-created_at')
        return context


class ProductDetailView(DetailView):
    """Vista para detalle de producto."""
    model = Product
    template_name = 'products/detail_new.html'
    context_object_name = 'product'
    
    def get_queryset(self):
        return Product.objects.filter(is_active=True).select_related('category', 'brand').prefetch_related('images', 'variants')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Productos relacionados de la misma categoría
        if self.object.category:
            context['related_products'] = Product.objects.filter(
                category=self.object.category,
                is_active=True
            ).exclude(id=self.object.id).select_related('category', 'brand')[:4]
        return context
