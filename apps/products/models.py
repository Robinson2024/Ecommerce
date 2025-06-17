# filepath: apps/products/models.py
"""
Modelos para la app Products.
"""
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from apps.core.models import TimeStampedModel, UUIDModel


class Category(TimeStampedModel, UUIDModel):
    """Modelo para categorías de productos."""
    
    name = models.CharField(
        _('Nombre'),
        max_length=100,
        help_text=_('Nombre de la categoría')
    )
    
    slug = models.SlugField(
        _('Slug'),
        max_length=100,
        unique=True,
        help_text=_('URL amigable de la categoría')
    )
    
    description = models.TextField(
        _('Descripción'),
        blank=True,
        help_text=_('Descripción de la categoría')
    )
    
    parent = models.ForeignKey(
        'self',
        verbose_name=_('Categoría padre'),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        help_text=_('Categoría padre para crear jerarquías')
    )
    
    is_active = models.BooleanField(
        _('Activa'),
        default=True,
        help_text=_('¿Está activa la categoría?')
    )
    
    class Meta:
        verbose_name = _('Categoría')
        verbose_name_plural = _('Categorías')
        ordering = ['name']
        unique_together = ['slug', 'parent']
    
    def __str__(self):
        return self.name


class Brand(TimeStampedModel, UUIDModel):
    """Modelo para marcas de productos."""
    
    name = models.CharField(
        _('Nombre'),
        max_length=100,
        unique=True,
        help_text=_('Nombre de la marca')
    )
    
    slug = models.SlugField(
        _('Slug'),
        max_length=100,
        unique=True,
        help_text=_('URL amigable de la marca')
    )
    
    description = models.TextField(
        _('Descripción'),
        blank=True,
        help_text=_('Descripción de la marca')
    )
    
    logo = models.ImageField(
        _('Logo'),
        upload_to='brands/',
        blank=True,
        null=True,
        help_text=_('Logo de la marca')
    )
    
    website = models.URLField(
        _('Sitio web'),
        blank=True,
        help_text=_('Sitio web oficial de la marca')
    )
    
    is_active = models.BooleanField(
        _('Activa'),
        default=True,
        help_text=_('¿Está activa la marca?')
    )
    
    class Meta:
        verbose_name = _('Marca')
        verbose_name_plural = _('Marcas')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Product(TimeStampedModel, UUIDModel):
    """Modelo para productos."""
    
    name = models.CharField(
        _('Nombre'),
        max_length=200,
        help_text=_('Nombre del producto')
    )
    
    slug = models.SlugField(
        _('Slug'),
        max_length=200,
        unique=True,
        help_text=_('URL amigable del producto')
    )
    
    description = models.TextField(
        _('Descripción'),
        blank=True,
        help_text=_('Descripción detallada del producto')
    )
    
    short_description = models.CharField(
        _('Descripción corta'),
        max_length=500,
        blank=True,
        help_text=_('Descripción breve del producto')
    )
    
    category = models.ForeignKey(
        Category,
        verbose_name=_('Categoría'),
        on_delete=models.PROTECT,
        related_name='products',
        null=True,
        blank=True,
        help_text=_('Categoría del producto')
    )
    
    brand = models.ForeignKey(
        Brand,
        verbose_name=_('Marca'),
        on_delete=models.PROTECT,
        related_name='products',
        null=True,
        blank=True,
        help_text=_('Marca del producto')
    )
    
    sku = models.CharField(
        _('SKU'),
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        help_text=_('Código único del producto')
    )
    
    price = models.DecimalField(
        _('Precio'),
        max_digits=10,
        decimal_places=2,
        help_text=_('Precio del producto')
    )
    
    compare_price = models.DecimalField(
        _('Precio de comparación'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_('Precio original para mostrar descuento')
    )
    
    cost_price = models.DecimalField(
        _('Precio de costo'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_('Precio de costo del producto')
    )
    
    stock_quantity = models.PositiveIntegerField(
        _('Cantidad en stock'),
        default=0,
        help_text=_('Cantidad disponible en inventario')
    )
    
    min_stock_level = models.PositiveIntegerField(
        _('Nivel mínimo de stock'),
        default=5,
        help_text=_('Cantidad mínima antes de avisar stock bajo')
    )
    
    weight = models.DecimalField(
        _('Peso (kg)'),
        max_digits=8,
        decimal_places=3,
        null=True,
        blank=True,
        help_text=_('Peso del producto en kilogramos')
    )
    
    dimensions = models.CharField(
        _('Dimensiones (L x W x H cm)'),
        max_length=100,
        blank=True,
        help_text=_('Dimensiones del producto en centímetros')
    )
    
    featured_image = models.ImageField(
        _('Imagen principal'),
        upload_to='products/',
        null=True,
        blank=True,
        help_text=_('Imagen principal del producto')
    )
    
    is_active = models.BooleanField(
        _('Activo'),
        default=True,
        help_text=_('¿Está disponible para la venta?')
    )
    
    is_featured = models.BooleanField(
        _('Destacado'),
        default=False,
        help_text=_('¿Es un producto destacado?')
    )
    
    track_inventory = models.BooleanField(
        _('Rastrear inventario'),
        default=True,
        help_text=_('¿Se debe rastrear el inventario de este producto?')
    )
    
    allow_backorder = models.BooleanField(
        _('Permitir pedidos pendientes'),
        default=False,
        help_text=_('¿Permitir venta cuando no hay stock?')
    )
    
    meta_title = models.CharField(
        _('Meta título'),
        max_length=60,
        blank=True,
        help_text=_('Título para SEO')
    )
    
    meta_description = models.CharField(
        _('Meta descripción'),
        max_length=160,
        blank=True,
        help_text=_('Descripción para SEO')
    )
    
    class Meta:
        verbose_name = _('Producto')
        verbose_name_plural = _('Productos')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['sku']),
            models.Index(fields=['is_active']),
            models.Index(fields=['is_featured']),
            models.Index(fields=['category']),
            models.Index(fields=['brand']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('products:detail', kwargs={'slug': self.slug})
    
    @property
    def is_on_sale(self):
        """Verifica si el producto está en oferta."""
        return self.compare_price and self.compare_price > self.price
    
    @property
    def discount_percentage(self):
        """Calcula el porcentaje de descuento."""
        if self.is_on_sale:
            return round(((self.compare_price - self.price) / self.compare_price) * 100)
        return 0
    
    @property
    def is_in_stock(self):
        """Verifica si hay stock disponible."""
        if not self.track_inventory:
            return True
        return self.stock_quantity > 0 or self.allow_backorder
    
    @property
    def is_low_stock(self):
        """Verifica si el stock está bajo."""
        if not self.track_inventory:
            return False
        return self.stock_quantity <= self.min_stock_level


class ProductImage(TimeStampedModel, UUIDModel):
    """Modelo para imágenes adicionales de productos."""
    
    product = models.ForeignKey(
        Product,
        verbose_name=_('Producto'),
        on_delete=models.CASCADE,
        related_name='images',
        help_text=_('Producto al que pertenece la imagen')
    )
    
    image = models.ImageField(
        _('Imagen'),
        upload_to='products/gallery/',
        help_text=_('Imagen del producto')
    )
    
    alt_text = models.CharField(
        _('Texto alternativo'),
        max_length=255,
        blank=True,
        help_text=_('Texto alternativo para accesibilidad')
    )
    
    position = models.PositiveIntegerField(
        _('Posición'),
        default=0,
        help_text=_('Orden de visualización')
    )
    
    class Meta:
        verbose_name = _('Imagen de producto')
        verbose_name_plural = _('Imágenes de productos')
        ordering = ['position', 'created_at']
        unique_together = ['product', 'position']
    
    def __str__(self):
        return f'{self.product.name} - Imagen {self.position}'


class ProductAttribute(TimeStampedModel, UUIDModel):
    """Modelo para atributos de productos (color, talla, etc.)."""
    
    name = models.CharField(
        _('Nombre'),
        max_length=100,
        help_text=_('Nombre del atributo (ej: Color, Talla)')
    )
    
    slug = models.SlugField(
        _('Slug'),
        max_length=100,
        unique=True,
        help_text=_('URL amigable del atributo')
    )
    
    class Meta:
        verbose_name = _('Atributo de producto')
        verbose_name_plural = _('Atributos de productos')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class ProductAttributeValue(TimeStampedModel, UUIDModel):
    """Modelo para valores de atributos de productos."""
    
    attribute = models.ForeignKey(
        ProductAttribute,
        verbose_name=_('Atributo'),
        on_delete=models.CASCADE,
        related_name='values',
        help_text=_('Atributo al que pertenece este valor')
    )
    
    value = models.CharField(
        _('Valor'),
        max_length=100,
        help_text=_('Valor del atributo (ej: Rojo, XL)')
    )
    
    slug = models.SlugField(
        _('Slug'),
        max_length=100,
        help_text=_('URL amigable del valor')
    )
    
    color_code = models.CharField(
        _('Código de color'),
        max_length=7,
        blank=True,
        help_text=_('Código hexadecimal del color (ej: #FF0000)')
    )
    
    class Meta:
        verbose_name = _('Valor de atributo')
        verbose_name_plural = _('Valores de atributos')
        ordering = ['attribute', 'value']
        unique_together = ['attribute', 'slug']
    
    def __str__(self):
        return f'{self.attribute.name}: {self.value}'


class ProductVariant(TimeStampedModel, UUIDModel):
    """Modelo para variantes de productos."""
    
    product = models.ForeignKey(
        Product,
        verbose_name=_('Producto'),
        on_delete=models.CASCADE,
        related_name='variants',
        help_text=_('Producto principal')
    )
    
    sku = models.CharField(
        _('SKU'),
        max_length=50,
        unique=True,
        help_text=_('Código único de la variante')
    )
    
    price = models.DecimalField(
        _('Precio'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_('Precio específico de la variante (opcional)')
    )
    
    stock_quantity = models.PositiveIntegerField(
        _('Cantidad en stock'),
        default=0,
        help_text=_('Cantidad disponible de esta variante')
    )
    
    weight = models.DecimalField(
        _('Peso (kg)'),
        max_digits=8,
        decimal_places=3,
        null=True,
        blank=True,
        help_text=_('Peso específico de la variante')
    )
    
    is_active = models.BooleanField(
        _('Activa'),
        default=True,
        help_text=_('¿Está disponible para la venta?')
    )
    
    attribute_values = models.ManyToManyField(
        ProductAttributeValue,
        verbose_name=_('Valores de atributos'),
        help_text=_('Valores de atributos que definen esta variante')
    )
    
    class Meta:
        verbose_name = _('Variante de producto')
        verbose_name_plural = _('Variantes de productos')
        ordering = ['product', 'sku']
    
    def __str__(self):
        attrs = ', '.join([str(av) for av in self.attribute_values.all()])
        return f'{self.product.name} - {attrs}'
    
    @property
    def display_price(self):
        """Retorna el precio de la variante o del producto principal."""
        return self.price or self.product.price
