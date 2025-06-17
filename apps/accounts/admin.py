"""
Admin configuration para la app accounts.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, UserProfile, Address, WishlistItem, RecentlyViewedProduct


class AddressInline(admin.TabularInline):
    """Inline para direcciones del usuario."""
    model = Address
    extra = 0
    fields = ['title', 'city', 'state', 'is_default_billing', 'is_default_shipping']
    readonly_fields = ['created_at']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin para el modelo User personalizado."""
    
    list_display = [
        'email', 'get_full_name', 'username', 'phone', 
        'orders_count', 'total_spent', 'get_loyalty_tier',
        'is_active', 'date_joined'
    ]
    list_filter = [
        'is_active', 'is_staff', 'is_superuser', 'gender',
        'newsletter_subscription', 'notifications_enabled', 'date_joined'
    ]
    search_fields = ['email', 'username', 'first_name', 'last_name', 'phone']
    ordering = ['-date_joined']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Información Personal Adicional', {
            'fields': ('phone', 'birth_date', 'gender', 'avatar')
        }),
        ('Configuraciones', {
            'fields': ('newsletter_subscription', 'notifications_enabled')
        }),
        ('Estadísticas de Compras', {
            'fields': ('total_spent', 'orders_count')
        }),
        ('Metadata', {
            'fields': ('last_activity',),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Información Personal', {
            'fields': ('email', 'first_name', 'last_name', 'phone')
        }),
    )
    
    readonly_fields = ['total_spent', 'orders_count', 'last_activity']
    inlines = [AddressInline]
    
    def get_loyalty_tier(self, obj):
        """Mostrar nivel de lealtad con colores."""
        tier = obj.get_loyalty_tier()
        colors = {
            'Platinum': '#E5E4E2',
            'Gold': '#FFD700',
            'Silver': '#C0C0C0',
            'Bronze': '#CD7F32',
            'Standard': '#808080'
        }
        return format_html(            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(tier, '#000000'),
            tier
        )
    get_loyalty_tier.short_description = 'Nivel de Lealtad'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin para UserProfile."""
    
    list_display = [
        'user', 'document_type', 'document_number', 
        'occupation', 'company', 'preferred_language'
    ]
    list_filter = ['document_type', 'preferred_language', 'timezone']
    search_fields = [
        'user__email', 'user__first_name', 'user__last_name',
        'document_number', 'occupation', 'company'
    ]
    
    fieldsets = [
        ('Usuario', {
            'fields': ('user',)
        }),
        ('Información Personal', {
            'fields': ('document_type', 'document_number', 'occupation', 'company')
        }),
        ('Preferencias', {
            'fields': ('preferred_language', 'timezone')
        }),        ('Redes Sociales', {
            'fields': ('bio', 'website', 'instagram', 'twitter'),
            'classes': ('collapse',)
        }),
    ]


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    """Admin para Address."""
    
    list_display = [
        'user', 'title', 'city', 'state', 'country',
        'is_default_billing', 'is_default_shipping', 'created_at'
    ]
    list_filter = [
        'is_default_billing', 'is_default_shipping', 
        'country', 'state', 'created_at'
    ]
    search_fields = [
        'user__email', 'user__first_name', 'user__last_name',
        'title', 'first_name', 'last_name', 'city', 'state'
    ]
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = [
        ('Usuario', {
            'fields': ('user',)
        }),
        ('Identificación', {
            'fields': ('title',)
        }),
        ('Contacto', {
            'fields': ('first_name', 'last_name', 'phone')
        }),
        ('Dirección', {
            'fields': (
                'address_line_1', 'address_line_2', 
                'city', 'state', 'postal_code', 'country'
            )
        }),
        ('Configuraciones', {
            'fields': ('is_default_billing', 'is_default_shipping')
        }),
        ('Instrucciones', {
            'fields': ('delivery_instructions',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    ]


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    """Admin para WishlistItem."""
    
    list_display = ['user', 'product', 'priority', 'created_at']
    list_filter = ['priority', 'created_at']
    search_fields = [
        'user__email', 'user__first_name', 'user__last_name',
        'product__name'
    ]
    ordering = ['-created_at']


@admin.register(RecentlyViewedProduct)
class RecentlyViewedProductAdmin(admin.ModelAdmin):
    """Admin para RecentlyViewedProduct."""
    
    list_display = ['user', 'product', 'viewed_at']
    list_filter = ['viewed_at']
    search_fields = [
        'user__email', 'user__first_name', 'user__last_name',
        'product__name'
    ]
    ordering = ['-viewed_at']
    
    # Limitar la lista a los últimos 1000 registros para performance
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs[:1000]
