# filepath: apps/payments/admin.py
"""
Admin interface para la app Payments.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from apps.orders.models import Order, OrderItem, Payment, ShippingRate


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin para órdenes"""
    list_display = [
        'order_number', 'user', 'status', 'payment_status', 
        'total_amount', 'created_at', 'payment_link'
    ]
    list_filter = [
        'status', 'payment_status', 'payment_method', 
        'created_at', 'updated_at'
    ]
    search_fields = [
        'order_number', 'user__email', 'user__first_name', 
        'user__last_name', 'email'
    ]
    readonly_fields = [
        'order_number', 'created_at', 'updated_at', 
        'subtotal', 'total_amount'
    ]
    fieldsets = (
        ('Información General', {
            'fields': ('order_number', 'user', 'email', 'phone')
        }),
        ('Estado', {
            'fields': ('status', 'payment_status', 'payment_method')
        }),
        ('Montos', {
            'fields': ('subtotal', 'shipping_cost', 'tax_amount', 'total_amount', 'currency')
        }),
        ('Direcciones', {
            'fields': ('shipping_address', 'billing_address'),
            'classes': ('collapse',)
        }),
        ('Envío', {
            'fields': ('tracking_number', 'shipped_at', 'delivered_at'),
            'classes': ('collapse',)
        }),
        ('Notas', {
            'fields': ('notes', 'admin_notes'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    inlines = []
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    def payment_link(self, obj):
        """Link al payment relacionado"""
        try:
            payment = obj.payment
            url = reverse('admin:orders_payment_change', args=[payment.id])
            return format_html('<a href="{}">Ver Pago</a>', url)
        except Payment.DoesNotExist:
            return format_html('<span style="color: red;">Sin Pago</span>')
    payment_link.short_description = 'Pago'
    
    def save_model(self, request, obj, form, change):
        """Guardar modelo con cálculo de totales"""
        if change:
            obj.calculate_totals()
        super().save_model(request, obj, form, change)


class OrderItemInline(admin.TabularInline):
    """Inline para items de orden"""
    model = OrderItem
    extra = 0
    readonly_fields = ['total_price']
    fields = [
        'product', 'variant', 'quantity', 'unit_price', 'total_price'
    ]


# Re-register Order with inlines
admin.site.unregister(Order)
@admin.register(Order)
class OrderWithItemsAdmin(OrderAdmin):
    """Order admin con items incluidos"""
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Admin para items de orden"""
    list_display = [
        'order', 'product_name', 'quantity', 'unit_price', 'total_price'
    ]
    list_filter = ['order__status', 'order__created_at']
    search_fields = [
        'order__order_number', 'product_name', 'product_sku'
    ]
    readonly_fields = ['total_price']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin para pagos"""
    list_display = [
        'order', 'payment_method', 'amount', 'status', 
        'created_at', 'processed_at'
    ]
    list_filter = [
        'payment_method', 'status', 'currency', 
        'created_at', 'processed_at'
    ]
    search_fields = [
        'order__order_number', 'payment_intent_id'
    ]
    readonly_fields = [
        'created_at', 'updated_at', 'processed_at', 'gateway_response'
    ]
    fieldsets = (
        ('Información General', {
            'fields': ('order', 'payment_method', 'payment_intent_id')
        }),
        ('Montos', {
            'fields': ('amount', 'currency')
        }),
        ('Estado', {
            'fields': ('status', 'processed_at', 'failure_reason')
        }),
        ('Gateway Response', {
            'fields': ('gateway_response',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    date_hierarchy = 'created_at'
    ordering = ['-created_at']


@admin.register(ShippingRate)
class ShippingRateAdmin(admin.ModelAdmin):
    """Admin para tarifas de envío"""
    list_display = [
        'name', 'base_cost', 'cost_per_kg', 'free_shipping_threshold',
        'estimated_delivery_display', 'is_active'
    ]
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    fieldsets = (
        ('Información General', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Costos', {
            'fields': ('base_cost', 'cost_per_kg', 'free_shipping_threshold')
        }),
        ('Tiempos de Entrega', {
            'fields': ('estimated_days_min', 'estimated_days_max')
        }),
    )
    
    def estimated_delivery_display(self, obj):
        """Display del tiempo de entrega"""
        return obj.get_estimated_delivery()
    estimated_delivery_display.short_description = 'Tiempo Entrega'


# Customizar admin site
admin.site.site_header = 'Tech Ecommerce Admin'
admin.site.site_title = 'Tech Ecommerce'
admin.site.index_title = 'Panel de Administración'
