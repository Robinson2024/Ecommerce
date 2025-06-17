from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import Cart, CartItem, CartItemHistory


class CartItemInline(admin.TabularInline):
    """Inline para mostrar items del carrito"""
    model = CartItem
    extra = 0
    readonly_fields = ['get_total_price', 'added_at']
    fields = ['product', 'variant', 'quantity', 'price', 'get_total_price', 'added_at']
    
    def get_total_price(self, obj):
        if obj.pk:
            return f"${obj.get_total_price():,.2f}"
        return "-"
    get_total_price.short_description = "Total"


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Admin para el modelo Cart"""
    list_display = [
        'id', 
        'get_owner', 
        'get_items_count', 
        'get_total_items', 
        'get_total_price_display',
        'created_at',
        'updated_at'
    ]
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'session_key']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [CartItemInline]
    date_hierarchy = 'created_at'
    
    def get_owner(self, obj):
        """Muestra el propietario del carrito"""
        if obj.user:
            url = reverse('admin:accounts_customuser_change', args=[obj.user.pk])
            return format_html('<a href="{}">{}</a>', url, obj.user.get_full_name())
        return f"Anónimo ({obj.session_key})"
    get_owner.short_description = "Propietario"
    get_owner.admin_order_field = 'user'
    
    def get_items_count(self, obj):
        """Número de tipos de productos únicos"""
        return obj.get_items_count()
    get_items_count.short_description = "Tipos de productos"
    
    def get_total_items(self, obj):
        """Número total de items"""
        count = obj.get_total_items()
        if count > 10:
            return format_html('<span style="color: orange;">{}</span>', count)
        return count
    get_total_items.short_description = "Total items"
    
    def get_total_price_display(self, obj):
        """Precio total formateado"""
        total = obj.get_total_price()
        if total > 1000:
            return format_html('<strong style="color: green;">${:,.2f}</strong>', total)
        return f"${total:,.2f}"
    get_total_price_display.short_description = "Total"
    
    def get_queryset(self, request):
        """Optimizar queryset con select_related"""
        return super().get_queryset(request).select_related('user').prefetch_related('items__product')


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """Admin para el modelo CartItem"""
    list_display = [
        'id',
        'get_cart_owner',
        'product',
        'variant',
        'quantity',
        'get_price_display',
        'get_total_display',
        'added_at'
    ]
    list_filter = ['added_at', 'product__category', 'product__brand']
    search_fields = [
        'product__name',
        'cart__user__email',
        'cart__user__first_name',
        'cart__user__last_name'
    ]
    readonly_fields = ['added_at', 'get_total_price']
    date_hierarchy = 'added_at'
    
    def get_cart_owner(self, obj):
        """Muestra el propietario del carrito"""
        if obj.cart.user:
            return obj.cart.user.get_full_name()
        return f"Anónimo ({obj.cart.session_key})"
    get_cart_owner.short_description = "Propietario"
    get_cart_owner.admin_order_field = 'cart__user'
    
    def get_price_display(self, obj):
        """Precio unitario formateado"""
        return f"${obj.price:,.2f}"
    get_price_display.short_description = "Precio unitario"
    
    def get_total_display(self, obj):
        """Total formateado"""
        return f"${obj.get_total_price():,.2f}"
    get_total_display.short_description = "Total"
    
    def get_queryset(self, request):
        """Optimizar queryset"""
        return super().get_queryset(request).select_related(
            'cart__user', 'product', 'variant'
        )


@admin.register(CartItemHistory)
class CartItemHistoryAdmin(admin.ModelAdmin):
    """Admin para el historial de items del carrito"""
    list_display = [
        'id',
        'get_cart_owner',
        'product',
        'action',
        'quantity',
        'get_price_display',
        'created_at'
    ]
    list_filter = ['action', 'created_at', 'product__category']
    search_fields = [
        'product__name',
        'cart__user__email',
        'cart__user__first_name',
        'cart__user__last_name'
    ]
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    def get_cart_owner(self, obj):
        """Muestra el propietario del carrito"""
        if obj.cart.user:
            return obj.cart.user.get_full_name()
        return f"Anónimo ({obj.cart.session_key})"
    get_cart_owner.short_description = "Propietario"
    
    def get_price_display(self, obj):
        """Precio formateado"""
        return f"${obj.price:,.2f}"
    get_price_display.short_description = "Precio"
    
    def get_queryset(self, request):
        """Optimizar queryset"""
        return super().get_queryset(request).select_related(
            'cart__user', 'product', 'variant'
        )
    
    def has_add_permission(self, request):
        """No permitir agregar manualmente historial"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Solo lectura para el historial"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """No permitir eliminar historial"""
        return False


# Personalización del admin
admin.site.site_header = "Tech Ecommerce - Administración"
admin.site.site_title = "Tech Ecommerce Admin"
admin.site.index_title = "Panel de Control"
