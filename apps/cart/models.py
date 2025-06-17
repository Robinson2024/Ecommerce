from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal

from apps.core.models import BaseModel, TimeStampedModel
from apps.products.models import Product, ProductVariant


class Cart(TimeStampedModel):
    """
    Modelo para representar un carrito de compras.
    Puede estar asociado a un usuario autenticado o a una sesión anónima.
    """
    session_key = models.CharField(
        max_length=40, 
        null=True, 
        blank=True,
        help_text="Clave de sesión para carritos anónimos"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='carts',
        help_text="Usuario propietario del carrito"
    )
    
    class Meta:
        db_table = 'cart_cart'
        verbose_name = 'Carrito'
        verbose_name_plural = 'Carritos'
        indexes = [
            models.Index(fields=['session_key']),
            models.Index(fields=['user']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        if self.user:
            return f"Carrito de {self.user.get_full_name()}"
        return f"Carrito anónimo ({self.session_key})"
    
    def get_total_price(self):
        """Calcula el precio total del carrito"""
        return sum(item.get_total_price() for item in self.items.all())
    
    def get_total_items(self):
        """Calcula el número total de items en el carrito"""
        return sum(item.quantity for item in self.items.all())
    
    def get_items_count(self):
        """Calcula el número de tipos de productos únicos"""
        return self.items.count()
    
    def clear(self):
        """Vacía todo el carrito"""
        self.items.all().delete()
    
    def add_product(self, product, quantity=1, variant=None, update_quantity=False):
        """
        Agrega un producto al carrito o actualiza la cantidad si ya existe
        
        Args:
            product: Instancia del producto
            quantity: Cantidad a agregar (default: 1)
            variant: Variante del producto (opcional)
            update_quantity: Si True, reemplaza la cantidad; si False, suma
        
        Returns:
            CartItem instance
        """
        # Determinar el precio basado en la variante o producto
        if variant:
            price = variant.price
        else:
            price = product.price
        
        # Buscar si ya existe el item en el carrito
        cart_item, created = self.items.get_or_create(
            product=product,
            variant=variant,
            defaults={
                'quantity': quantity,
                'price': price
            }
        )
        
        if not created:
            if update_quantity:
                cart_item.quantity = quantity
            else:
                cart_item.quantity += quantity
            cart_item.save()
        
        return cart_item
    
    def remove_product(self, product, variant=None):
        """Elimina un producto del carrito"""
        try:
            item = self.items.get(product=product, variant=variant)
            item.delete()
            return True
        except CartItem.DoesNotExist:
            return False
    
    def update_quantity(self, product, quantity, variant=None):
        """Actualiza la cantidad de un producto en el carrito"""
        try:
            item = self.items.get(product=product, variant=variant)
            if quantity <= 0:
                item.delete()
                return None
            else:
                item.quantity = quantity
                item.save()
                return item
        except CartItem.DoesNotExist:
            return None


class CartItem(models.Model):
    """
    Modelo para representar un item individual en el carrito
    """
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Carrito'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='Producto'
    )
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Variante del producto'
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name='Cantidad'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Precio unitario'
    )
    added_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Agregado el'
    )
    
    class Meta:
        db_table = 'cart_item'
        verbose_name = 'Item del carrito'
        verbose_name_plural = 'Items del carrito'
        unique_together = ['cart', 'product', 'variant']
        indexes = [
            models.Index(fields=['cart', 'product']),
            models.Index(fields=['added_at']),
        ]
    
    def __str__(self):
        variant_str = f" ({self.variant})" if self.variant else ""
        return f"{self.quantity}x {self.product.name}{variant_str}"
    
    def get_total_price(self):
        """Calcula el precio total de este item (quantity * price)"""
        return self.quantity * self.price
    
    def get_display_price(self):
        """Precio formateado para mostrar"""
        return f"${self.price:,.2f}"
    
    def get_display_total(self):
        """Total formateado para mostrar"""
        return f"${self.get_total_price():,.2f}"
    
    def clean(self):
        """Validaciones personalizadas"""
        super().clean()
        
        # Validar que el precio coincida con el producto/variante
        if self.variant:
            expected_price = self.variant.price
        else:
            expected_price = self.product.price
        
        if self.price != expected_price:
            self.price = expected_price
    
    def save(self, *args, **kwargs):
        """Override save para ejecutar validaciones"""
        self.clean()
        super().save(*args, **kwargs)


class CartItemHistory(TimeStampedModel):
    """
    Modelo para mantener historial de items agregados/removidos del carrito
    Útil para analytics y recomendaciones
    """
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='history'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    action = models.CharField(
        max_length=20,
        choices=[
            ('added', 'Agregado'),
            ('updated', 'Actualizado'),
            ('removed', 'Removido'),
        ]
    )
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        db_table = 'cart_item_history'
        verbose_name = 'Historial de carrito'
        verbose_name_plural = 'Historiales de carrito'
        indexes = [
            models.Index(fields=['cart', 'action']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.action}: {self.product.name} ({self.quantity})"
