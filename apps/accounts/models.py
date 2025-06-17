"""
Custom User Model y modelos relacionados para Tech Ecommerce.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from apps.core.models import BaseModel, UUIDModel
from apps.core.utils import generate_unique_slug


class User(AbstractUser):
    """
    Custom User Model extendido.
    """
    # Campos básicos (heredados de AbstractUser: username, email, first_name, last_name, etc.)
    
    # Información personal adicional
    phone = models.CharField(
        max_length=20, 
        blank=True, 
        verbose_name='Teléfono',
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Formato: '+999999999'. Hasta 15 dígitos."
            )
        ]
    )
    
    birth_date = models.DateField(
        null=True, 
        blank=True, 
        verbose_name='Fecha de nacimiento'
    )
    
    gender_choices = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
        ('N', 'Prefiero no decir'),
    ]
    gender = models.CharField(
        max_length=1, 
        choices=gender_choices, 
        blank=True, 
        null=True,
        verbose_name='Género'
    )
    
    # Configuraciones del usuario
    newsletter_subscription = models.BooleanField(
        default=True, 
        verbose_name='Suscripción al newsletter'
    )
    
    notifications_enabled = models.BooleanField(
        default=True, 
        verbose_name='Notificaciones habilitadas'
    )
    
    # Información de compras
    total_spent = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0, 
        verbose_name='Total gastado'
    )
    
    orders_count = models.PositiveIntegerField(
        default=0, 
        verbose_name='Número de pedidos'
    )
    
    # Avatar
    avatar = models.ImageField(
        upload_to='avatars/', 
        blank=True, 
        null=True, 
        verbose_name='Avatar'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de registro')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última actualización')
    last_activity = models.DateTimeField(null=True, blank=True, verbose_name='Última actividad')
    
    # Campo para hacer email único y requerido
    email = models.EmailField(_('email address'), unique=True)
    
    # Usar email como username
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    def get_full_name(self):
        """Devuelve el nombre completo del usuario."""
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else self.username
    
    def get_display_name(self):
        """Devuelve el nombre para mostrar."""
        return self.get_full_name() or self.username
    
    def get_initials(self):
        """Devuelve las iniciales del usuario."""
        if self.first_name and self.last_name:
            return f"{self.first_name[0]}{self.last_name[0]}".upper()
        return self.username[:2].upper()
    
    def is_premium_customer(self):
        """Verifica si es un cliente premium (más de $500,000 en compras)."""
        return self.total_spent >= 500000
    
    def get_loyalty_tier(self):
        """Devuelve el nivel de lealtad del cliente."""
        if self.total_spent >= 1000000:
            return 'Platinum'
        elif self.total_spent >= 500000:
            return 'Gold'
        elif self.total_spent >= 200000:
            return 'Silver'
        elif self.total_spent >= 50000:
            return 'Bronze'
        return 'Standard'


class UserProfile(BaseModel):
    """
    Perfil extendido del usuario con información adicional.
    """
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='profile',
        verbose_name='Usuario'
    )
    
    # Información personal extendida
    document_type_choices = [
        ('CC', 'Cédula de Ciudadanía'),
        ('CE', 'Cédula de Extranjería'),
        ('PA', 'Pasaporte'),
        ('NIT', 'NIT'),
    ]
    document_type = models.CharField(
        max_length=3, 
        choices=document_type_choices, 
        blank=True,
        verbose_name='Tipo de documento'
    )
    document_number = models.CharField(
        max_length=20, 
        blank=True, 
        verbose_name='Número de documento'
    )
    
    # Información profesional
    occupation = models.CharField(
        max_length=100, 
        blank=True, 
        verbose_name='Ocupación'
    )
    company = models.CharField(
        max_length=100, 
        blank=True, 
        verbose_name='Empresa'
    )
    
    # Preferencias
    preferred_language = models.CharField(
        max_length=10, 
        default='es', 
        verbose_name='Idioma preferido'
    )
    timezone = models.CharField(
        max_length=50, 
        default='America/Bogota', 
        verbose_name='Zona horaria'
    )
    
    # Bio y redes sociales
    bio = models.TextField(
        max_length=500, 
        blank=True, 
        verbose_name='Biografía'
    )
    website = models.URLField(blank=True, verbose_name='Sitio web')
    instagram = models.CharField(max_length=50, blank=True, verbose_name='Instagram')
    twitter = models.CharField(max_length=50, blank=True, verbose_name='Twitter')
    
    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'
    
    def __str__(self):
        return f"Perfil de {self.user.get_display_name()}"


class Address(BaseModel, UUIDModel):
    """
    Modelo para direcciones de usuarios.
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='addresses',
        verbose_name='Usuario'
    )
    
    # Identificación de la dirección
    title = models.CharField(
        max_length=50, 
        verbose_name='Título',
        help_text='Ej: Casa, Oficina, etc.'
    )
    
    # Información de contacto
    first_name = models.CharField(max_length=50, verbose_name='Nombre')
    last_name = models.CharField(max_length=50, verbose_name='Apellido')
    phone = models.CharField(
        max_length=20, 
        verbose_name='Teléfono',
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Formato: '+999999999'. Hasta 15 dígitos."
            )
        ]
    )
    
    # Dirección
    address_line_1 = models.CharField(
        max_length=255, 
        verbose_name='Dirección línea 1'
    )
    address_line_2 = models.CharField(
        max_length=255, 
        blank=True, 
        verbose_name='Dirección línea 2'
    )
    city = models.CharField(max_length=100, verbose_name='Ciudad')
    state = models.CharField(max_length=100, verbose_name='Departamento/Estado')
    postal_code = models.CharField(max_length=20, verbose_name='Código postal')
    country = models.CharField(max_length=50, default='Colombia', verbose_name='País')
    
    # Configuraciones
    is_default_billing = models.BooleanField(
        default=False, 
        verbose_name='Dirección de facturación por defecto'
    )
    is_default_shipping = models.BooleanField(
        default=False, 
        verbose_name='Dirección de envío por defecto'
    )
    
    # Instrucciones especiales
    delivery_instructions = models.TextField(
        max_length=500, 
        blank=True, 
        verbose_name='Instrucciones de entrega'
    )
    
    class Meta:
        verbose_name = 'Dirección'
        verbose_name_plural = 'Direcciones'
        ordering = ['-is_default_shipping', '-is_default_billing', '-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.get_display_name()}"
    
    def get_full_address(self):
        """Devuelve la dirección completa formateada."""
        parts = [
            self.address_line_1,
            self.address_line_2,
            f"{self.city}, {self.state}",
            f"{self.postal_code}, {self.country}"
        ]
        return ', '.join(filter(None, parts))
    
    def get_recipient_name(self):
        """Devuelve el nombre completo del destinatario."""
        return f"{self.first_name} {self.last_name}"


class WishlistItem(BaseModel):
    """
    Items en la wishlist del usuario.
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='wishlist_items',
        verbose_name='Usuario'
    )
    product = models.ForeignKey(
        'products.Product', 
        on_delete=models.CASCADE,
        verbose_name='Producto'
    )
    
    # Metadatos
    notes = models.TextField(
        max_length=255, 
        blank=True, 
        verbose_name='Notas'
    )
    priority = models.IntegerField(
        default=1, 
        choices=[(i, i) for i in range(1, 6)],
        verbose_name='Prioridad'
    )
    
    class Meta:
        verbose_name = 'Item de Lista de Deseos'
        verbose_name_plural = 'Items de Lista de Deseos'
        unique_together = ['user', 'product']
        ordering = ['-priority', '-created_at']
    
    def __str__(self):
        return f"{self.user.get_display_name()} - {self.product.name}"


class RecentlyViewedProduct(models.Model):
    """
    Productos vistos recientemente por el usuario.
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='recently_viewed',
        verbose_name='Usuario'
    )
    product = models.ForeignKey(
        'products.Product', 
        on_delete=models.CASCADE,
        verbose_name='Producto'
    )
    viewed_at = models.DateTimeField(auto_now=True, verbose_name='Visto en')
    
    class Meta:
        verbose_name = 'Producto Visto Recientemente'
        verbose_name_plural = 'Productos Vistos Recientemente'
        unique_together = ['user', 'product']
        ordering = ['-viewed_at']
    
    def __str__(self):
        return f"{self.user.get_display_name()} vio {self.product.name}"
