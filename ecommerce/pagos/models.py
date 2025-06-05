from django.db import models
from pedidos.models import Pedido

class Pago(models.Model):
    pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE, related_name='pago')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, choices=[('credit', 'Tarjeta'), ('paypal', 'PayPal')])
    status = models.CharField(max_length=20, choices=[('pending', 'Pendiente'), ('completed', 'Completado')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pago {self.id} - {self.status}"