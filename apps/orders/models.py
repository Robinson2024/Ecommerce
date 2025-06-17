# filepath: apps/orders/models.py
"""
Modelos para la gestión de órdenes y pagos.
"""
import uuid
from decimal import Decimal

from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.db.models import JSONField

from apps.products.models import Product, ProductVariant

User = get_user_model()


class OrderQuerySet(models.QuerySet):
    """QuerySet personalizado para Order"""
    
    def pending(self):
        return self.filter(status='pending')
    
    def paid(self):
        return self.filter(status='paid')
    
    def processing(self):
        return self.filter(status='processing')
    
    def shipped(self):
        return self.filter(status='shipped')
    
    def delivered(self):
        return self.filter(status='delivered')
    
    def cancelled(self):
        return self.filter(status='cancelled')
    
    def by_user(self, user):
        return self.filter(user=user)


class OrderManager(models.Manager):
    """Manager personalizado para Order"""
    
    def get_queryset(self):
        return OrderQuerySet(self.model, using=self._db)
    
    def pending(self):
        return self.get_queryset().pending()
    
    def paid(self):
        return self.get_queryset().paid()
    
    def create_from_cart(self, cart, customer_data, shipping_data):
        """Crear una orden desde un carrito"""
        order = self.create(
            user=cart.user if cart.user else None,
            email=customer_data['email'],
            phone=customer_data.get('phone', ''),
            shipping_address=shipping_data,
            billing_address=shipping_data,  # Por ahora usar la misma dirección
        )
        
        # Crear items de la orden
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                variant=cart_item.variant,
                product_name=cart_item.product.name,
                product_sku=cart_item.product.sku or '',
                quantity=cart_item.quantity,
                unit_price=cart_item.price,
                total_price=cart_item.get_total_price(),
            )
        
        # Calcular totales
        order.calculate_totals()
        order.save()
        
        return order


class Order(models.Model):
    """Modelo para las órdenes de compra"""
    
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending Payment'),
        ('paid', 'Payment Confirmed'),
        ('processing', 'Order Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('stripe', 'Stripe (Credit Card)'),
        ('paypal', 'PayPal'),
        ('cash', 'Cash on Delivery'),
        ('bank_transfer', 'Bank Transfer'),
    ]
    
    # Identificación
    order_number = models.CharField(max_length=50, unique=True, db_index=True)
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='orders'
    )
    
    # Información de contacto
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    
    # Direcciones (almacenadas como JSON)
    shipping_address = JSONField(default=dict)
    billing_address = JSONField(default=dict)
    
    # Estados
    status = models.CharField(
        max_length=20, 
        choices=ORDER_STATUS_CHOICES, 
        default='pending',
        db_index=True
    )
    payment_status = models.CharField(
        max_length=20, 
        choices=PAYMENT_STATUS_CHOICES, 
        default='pending',
        db_index=True
    )
    
    # Información de pago
    payment_method = models.CharField(
        max_length=20, 
        choices=PAYMENT_METHOD_CHOICES, 
        default='stripe'
    )
    payment_intent_id = models.CharField(max_length=200, blank=True)
    
    # Totales
    subtotal = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    shipping_cost = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    tax_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    total_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    currency = models.CharField(max_length=3, default='COP')
    
    # Información de envío
    tracking_number = models.CharField(max_length=100, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    # Notas
    notes = models.TextField(blank=True)
    admin_notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = OrderManager()
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['payment_status', '-created_at']),
        ]
    
    def __str__(self):
        return f"Order #{self.order_number}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)
    
    def generate_order_number(self):
        """Generar número de orden único"""
        timestamp = timezone.now().strftime('%Y%m%d')
        uuid_short = str(uuid.uuid4())[:8].upper()
        return f"TE{timestamp}{uuid_short}"
    
    def get_absolute_url(self):
        return reverse('orders:detail', kwargs={'order_number': self.order_number})
    
    def calculate_totals(self):
        """Calcular totales de la orden"""
        self.subtotal = sum(item.total_price for item in self.items.all())
        
        # Calcular envío (gratis si subtotal >= 100,000)
        if self.subtotal >= Decimal('100000'):
            self.shipping_cost = Decimal('0.00')
        else:
            self.shipping_cost = Decimal('15000')  # $15,000 COP por defecto
        
        # Calcular impuestos (19% IVA en Colombia)
        self.tax_amount = self.subtotal * Decimal('0.19')
        
        # Total final
        self.total_amount = self.subtotal + self.shipping_cost + self.tax_amount
    
    def can_cancel(self):
        """Verificar si la orden puede ser cancelada"""
        return self.status in ['pending', 'paid']
    
    def can_refund(self):
        """Verificar si la orden puede ser reembolsada"""
        return self.status in ['paid', 'processing'] and self.payment_status == 'completed'
    
    def get_full_name(self):
        """Obtener nombre completo del cliente"""
        if self.user:
            return self.user.get_full_name()
        return f"{self.shipping_address.get('first_name', '')} {self.shipping_address.get('last_name', '')}"
    
    def get_shipping_address_display(self):
        """Formatear dirección de envío para display"""
        addr = self.shipping_address
        lines = []
        
        if addr.get('address_line1'):
            lines.append(addr['address_line1'])
        if addr.get('address_line2'):
            lines.append(addr['address_line2'])
        if addr.get('city') and addr.get('state'):
            lines.append(f"{addr['city']}, {addr['state']} {addr.get('postal_code', '')}")
        if addr.get('country'):
            lines.append(addr['country'])
        
        return '\n'.join(lines)


class OrderItem(models.Model):
    """Items individuales de una orden"""
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Información del producto al momento de la compra
    product_name = models.CharField(max_length=255)
    product_sku = models.CharField(max_length=100, blank=True)
    
    # Cantidad y precios
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    total_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    
    class Meta:
        indexes = [
            models.Index(fields=['order', 'product']),
        ]
    
    def __str__(self):
        return f"{self.quantity}x {self.product_name}"
    
    def save(self, *args, **kwargs):
        if not self.total_price:
            self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)
    
    def get_total_price(self):
        """Calcular precio total del item"""
        return self.unit_price * self.quantity


class Payment(models.Model):
    """Información de pagos procesados"""
    
    PAYMENT_METHOD_CHOICES = [
        ('stripe', 'Stripe'),
        ('paypal', 'PayPal'),
        ('cash', 'Cash on Delivery'),
        ('bank_transfer', 'Bank Transfer'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_intent_id = models.CharField(max_length=200, unique=True)
    
    # Montos
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    currency = models.CharField(max_length=3, default='COP')
    
    # Estado
    status = models.CharField(
        max_length=20, 
        choices=PAYMENT_STATUS_CHOICES, 
        default='pending',
        db_index=True
    )
    
    # Información del gateway
    gateway_response = JSONField(default=dict)
    failure_reason = models.TextField(blank=True)
    
    # Timestamps
    processed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['payment_intent_id']),
            models.Index(fields=['status', '-created_at']),
        ]
    
    def __str__(self):
        return f"Payment for {self.order.order_number} - {self.get_status_display()}"
    
    def mark_completed(self):
        """Marcar pago como completado"""
        self.status = 'completed'
        self.processed_at = timezone.now()
        self.save()
        
        # Actualizar estado de la orden
        self.order.payment_status = 'completed'
        self.order.status = 'paid'
        self.order.save()
    
    def mark_failed(self, reason=''):
        """Marcar pago como fallido"""
        self.status = 'failed'
        self.failure_reason = reason
        self.save()
        
        # Actualizar estado de la orden
        self.order.payment_status = 'failed'
        self.order.save()


class ShippingRate(models.Model):
    """Tarifas y métodos de envío"""
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Costos
    base_cost = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    cost_per_kg = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    free_shipping_threshold = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('100000'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    
    # Tiempos de entrega
    estimated_days_min = models.PositiveIntegerField(default=1)
    estimated_days_max = models.PositiveIntegerField(default=5)
    
    # Estado
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['base_cost']
    
    def __str__(self):
        return self.name
    
    def calculate_cost(self, subtotal, weight=None):
        """Calcular costo de envío"""
        if subtotal >= self.free_shipping_threshold:
            return Decimal('0.00')
        
        cost = self.base_cost
        if weight and self.cost_per_kg > 0:
            cost += weight * self.cost_per_kg
        
        return cost
    
    def get_estimated_delivery(self):
        """Obtener tiempo estimado de entrega"""
        if self.estimated_days_min == self.estimated_days_max:
            return f"{self.estimated_days_min} días"
        return f"{self.estimated_days_min}-{self.estimated_days_max} días"
