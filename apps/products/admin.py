# filepath: apps/products/admin.py
"""
Configuración del admin para la app Products.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import (
    Category, Brand, Product, ProductImage, 
    ProductAttribute, ProductAttributeValue, ProductVariant
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin para categorías."""
    
    list_display = ['name', 'parent', 'is_active', 'created_at']
    list_filter = ['is_active', 'parent', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active']
    ordering = ['name']


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    """Admin para marcas."""
    
    list_display = ['name', 'website', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active']
    ordering = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin para productos."""
    
    list_display = [
        'name', 'category', 'brand', 'sku', 'price', 
        'stock_quantity', 'is_active', 'is_featured', 'created_at'
    ]
    list_filter = [
        'is_active', 'is_featured', 'category', 'brand', 
        'track_inventory', 'allow_backorder', 'created_at'
    ]
    search_fields = ['name', 'sku', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active', 'is_featured', 'price']
    ordering = ['-created_at']
    
    fieldsets = (
        (_('Información básica'), {
            'fields': ('name', 'slug', 'sku', 'category', 'brand')
        }),
        (_('Descripción'), {
            'fields': ('short_description', 'description')
        }),
        (_('Precios'), {
            'fields': ('price', 'compare_price', 'cost_price'),
            'classes': ('collapse',)
        }),
        (_('Inventario'), {
            'fields': (
                'stock_quantity', 'min_stock_level', 
                'track_inventory', 'allow_backorder'
            ),
            'classes': ('collapse',)
        }),
        (_('Atributos físicos'), {
            'fields': ('weight', 'dimensions'),
            'classes': ('collapse',)
        }),
        (_('Imagen'), {
            'fields': ('featured_image',)
        }),
        (_('Estado'), {
            'fields': ('is_active', 'is_featured')
        }),
        (_('SEO'), {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category', 'brand')
