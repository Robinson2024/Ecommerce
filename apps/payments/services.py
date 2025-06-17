# filepath: apps/payments/services.py
"""
Servicios para manejo de pagos con Stripe y PayPal
"""
import stripe
import paypalrestsdk
from decimal import Decimal
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from typing import Dict, Optional, Any

from apps.orders.models import Order, Payment, OrderItem


class PaymentError(Exception):
    """Excepción personalizada para errores de pago"""
    pass


class StripeService:
    """Servicio para manejar pagos con Stripe"""
    
    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        self.publishable_key = settings.STRIPE_PUBLISHABLE_KEY
    
    def create_payment_intent(self, order: Order) -> Dict[str, Any]:
        """
        Crear un Payment Intent en Stripe
        """
        try:
            # Convertir a centavos para Stripe
            amount_cents = int(order.total_amount * 100)
            
            intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=order.currency.lower(),
                metadata={
                    'order_id': str(order.id),
                    'order_number': order.order_number,
                    'customer_email': order.email,
                },
                automatic_payment_methods={
                    'enabled': True,
                },
            )
            
            # Actualizar orden con payment_intent_id
            order.payment_intent_id = intent.id
            order.save()
            
            return {
                'client_secret': intent.client_secret,
                'payment_intent_id': intent.id,
                'publishable_key': self.publishable_key,
                'amount': order.total_amount,
                'currency': order.currency,
            }
            
        except stripe.error.StripeError as e:
            raise PaymentError(f"Error creating Stripe payment intent: {str(e)}")
    
    def confirm_payment(self, payment_intent_id: str) -> Dict[str, Any]:
        """
        Confirmar el estado de un pago en Stripe
        """
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            return {
                'status': intent.status,
                'amount_received': intent.amount_received / 100,  # Convertir de centavos
                'payment_method': intent.payment_method,
                'charges': intent.charges.data if intent.charges else [],
            }
            
        except stripe.error.StripeError as e:
            raise PaymentError(f"Error confirming Stripe payment: {str(e)}")
    
    def process_webhook(self, payload: str, signature: str) -> Dict[str, Any]:
        """
        Procesar webhook de Stripe
        """
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, settings.STRIPE_WEBHOOK_SECRET
            )
            
            if event['type'] == 'payment_intent.succeeded':
                payment_intent = event['data']['object']
                return self._handle_payment_success(payment_intent)
            
            elif event['type'] == 'payment_intent.payment_failed':
                payment_intent = event['data']['object']
                return self._handle_payment_failure(payment_intent)
            
            return {'status': 'ignored', 'event_type': event['type']}
            
        except ValueError as e:
            raise PaymentError(f"Invalid webhook payload: {str(e)}")
        except stripe.error.SignatureVerificationError as e:
            raise PaymentError(f"Invalid webhook signature: {str(e)}")
    
    def _handle_payment_success(self, payment_intent: Dict) -> Dict[str, Any]:
        """Manejar pago exitoso"""
        try:
            order = Order.objects.get(payment_intent_id=payment_intent['id'])
            
            # Crear o actualizar registro de pago
            payment, created = Payment.objects.get_or_create(
                order=order,
                defaults={
                    'payment_method': 'stripe',
                    'payment_intent_id': payment_intent['id'],
                    'amount': Decimal(str(payment_intent['amount_received'] / 100)),
                    'currency': payment_intent['currency'].upper(),
                    'status': 'completed',
                    'gateway_response': payment_intent,
                    'processed_at': timezone.now(),
                }
            )
            
            if not created:
                payment.status = 'completed'
                payment.gateway_response = payment_intent
                payment.processed_at = timezone.now()
                payment.save()
            
            # Actualizar orden
            order.payment_status = 'completed'
            order.status = 'paid'
            order.save()
            
            return {
                'status': 'success',
                'order_id': order.id,
                'payment_id': payment.id,
            }
            
        except Order.DoesNotExist:
            raise PaymentError(f"Order not found for payment intent: {payment_intent['id']}")
    
    def _handle_payment_failure(self, payment_intent: Dict) -> Dict[str, Any]:
        """Manejar pago fallido"""
        try:
            order = Order.objects.get(payment_intent_id=payment_intent['id'])
            
            # Crear o actualizar registro de pago
            payment, created = Payment.objects.get_or_create(
                order=order,
                defaults={
                    'payment_method': 'stripe',
                    'payment_intent_id': payment_intent['id'],
                    'amount': Decimal(str(payment_intent['amount'] / 100)),
                    'currency': payment_intent['currency'].upper(),
                    'status': 'failed',
                    'gateway_response': payment_intent,
                    'failure_reason': payment_intent.get('last_payment_error', {}).get('message', 'Unknown error'),
                }
            )
            
            if not created:
                payment.status = 'failed'
                payment.gateway_response = payment_intent
                payment.failure_reason = payment_intent.get('last_payment_error', {}).get('message', 'Unknown error')
                payment.save()
            
            # Actualizar orden
            order.payment_status = 'failed'
            order.save()
            
            return {
                'status': 'failed',
                'order_id': order.id,
                'payment_id': payment.id,
            }
            
        except Order.DoesNotExist:
            raise PaymentError(f"Order not found for payment intent: {payment_intent['id']}")


class PayPalService:
    """Servicio para manejar pagos con PayPal"""
    
    def __init__(self):
        paypalrestsdk.configure({
            'mode': settings.PAYPAL_MODE,
            'client_id': settings.PAYPAL_CLIENT_ID,
            'client_secret': settings.PAYPAL_CLIENT_SECRET,
        })
    
    def create_payment(self, order: Order, return_url: str, cancel_url: str) -> Dict[str, Any]:
        """
        Crear un pago en PayPal
        """
        try:
            payment = paypalrestsdk.Payment({
                'intent': 'sale',
                'payer': {
                    'payment_method': 'paypal'
                },
                'redirect_urls': {
                    'return_url': return_url,
                    'cancel_url': cancel_url
                },
                'transactions': [{
                    'item_list': {
                        'items': self._get_order_items(order)
                    },
                    'amount': {
                        'total': str(order.total_amount),
                        'currency': order.currency,
                        'details': {
                            'subtotal': str(order.subtotal),
                            'shipping': str(order.shipping_cost),
                            'tax': str(order.tax_amount),
                        }
                    },
                    'description': f'Orden #{order.order_number} - Tech Ecommerce',
                    'custom': str(order.id),  # Para identificar la orden
                }]
            })
            
            if payment.create():
                # Guardar payment_id en la orden
                order.payment_intent_id = payment.id
                order.save()
                
                # Obtener URL de aprobación
                approval_url = None
                for link in payment.links:
                    if link.rel == 'approval_url':
                        approval_url = link.href
                        break
                
                return {
                    'payment_id': payment.id,
                    'approval_url': approval_url,
                    'status': 'created',
                }
            else:
                raise PaymentError(f"PayPal payment creation failed: {payment.error}")
                
        except Exception as e:
            raise PaymentError(f"Error creating PayPal payment: {str(e)}")
    
    def execute_payment(self, payment_id: str, payer_id: str) -> Dict[str, Any]:
        """
        Ejecutar pago de PayPal después de la aprobación
        """
        try:
            payment = paypalrestsdk.Payment.find(payment_id)
            
            if payment.execute({'payer_id': payer_id}):
                # Obtener orden
                order_id = payment.transactions[0].custom
                order = Order.objects.get(id=order_id)
                
                # Crear registro de pago
                payment_record = Payment.objects.create(
                    order=order,
                    payment_method='paypal',
                    payment_intent_id=payment_id,
                    amount=Decimal(payment.transactions[0].amount.total),
                    currency=payment.transactions[0].amount.currency,
                    status='completed',
                    gateway_response=payment.to_dict(),
                    processed_at=timezone.now(),
                )
                
                # Actualizar orden
                order.payment_status = 'completed'
                order.status = 'paid'
                order.save()
                
                return {
                    'status': 'success',
                    'order_id': order.id,
                    'payment_id': payment_record.id,
                    'transaction_id': payment.transactions[0].related_resources[0].sale.id,
                }
            else:
                raise PaymentError(f"PayPal payment execution failed: {payment.error}")
                
        except Order.DoesNotExist:
            raise PaymentError(f"Order not found for PayPal payment: {payment_id}")
        except Exception as e:
            raise PaymentError(f"Error executing PayPal payment: {str(e)}")
    
    def _get_order_items(self, order: Order) -> list:
        """Convertir items de orden a formato PayPal"""
        items = []
        for item in order.items.all():
            items.append({
                'name': item.product_name[:127],  # PayPal limit
                'sku': item.product_sku,
                'price': str(item.unit_price),
                'currency': order.currency,
                'quantity': item.quantity,
            })
        return items


class OrderService:
    """Servicio para gestión de órdenes"""
    
    @staticmethod
    def create_order_from_cart(cart_data: Dict, user=None, **kwargs) -> Order:
        """
        Crear una orden desde los datos del carrito
        """
        try:
            # Crear orden
            order = Order.objects.create(
                user=user,
                email=kwargs.get('email', user.email if user else ''),
                phone=kwargs.get('phone', ''),
                shipping_address=kwargs.get('shipping_address', {}),
                billing_address=kwargs.get('billing_address', {}),
                payment_method=kwargs.get('payment_method', 'stripe'),
                currency=kwargs.get('currency', 'COP'),
            )
            
            # Crear items de la orden
            for item in cart_data.get('items', []):
                OrderItem.objects.create(
                    order=order,
                    product_id=item['product_id'],
                    variant_id=item.get('variant_id'),
                    product_name=item['product_name'],
                    product_sku=item.get('product_sku', ''),
                    quantity=item['quantity'],
                    unit_price=Decimal(str(item['unit_price'])),
                    total_price=Decimal(str(item['total_price'])),
                )
            
            # Calcular totales
            order.calculate_totals()
            order.save()
            
            return order
            
        except Exception as e:
            raise ValidationError(f"Error creating order: {str(e)}")
    
    @staticmethod
    def update_inventory(order: Order, operation: str = 'decrease'):
        """
        Actualizar inventario basado en la orden
        """
        from apps.products.models import Product, ProductVariant
        
        try:
            for item in order.items.all():
                if item.variant:
                    # Actualizar variant
                    variant = item.variant
                    if operation == 'decrease':
                        variant.stock -= item.quantity
                    else:  # increase
                        variant.stock += item.quantity
                    variant.save()
                else:
                    # Actualizar producto
                    product = item.product
                    if operation == 'decrease':
                        product.stock -= item.quantity
                    else:  # increase
                        product.stock += item.quantity
                    product.save()
                    
        except Exception as e:
            raise ValidationError(f"Error updating inventory: {str(e)}")
    
    @staticmethod
    def send_order_confirmation(order: Order):
        """
        Enviar email de confirmación de orden
        """
        from django.core.mail import send_mail
        from django.template.loader import render_to_string
        from django.utils.html import strip_tags
        
        try:
            subject = f'Confirmación de Orden #{order.order_number} - Tech Ecommerce'
            
            html_message = render_to_string('emails/order_confirmation.html', {
                'order': order,
                'site_name': 'Tech Ecommerce',
            })
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[order.email],
                html_message=html_message,
                fail_silently=False,
            )
            
        except Exception as e:
            # Log error but don't fail the order
            print(f"Error sending order confirmation email: {str(e)}")


class ShippingService:
    """Servicio para cálculo de envíos"""
    
    @staticmethod
    def calculate_shipping_cost(subtotal: Decimal, weight: Optional[Decimal] = None, 
                              shipping_method: str = 'standard') -> Decimal:
        """
        Calcular costo de envío
        """
        from apps.orders.models import ShippingRate
        
        try:
            # Obtener tarifa de envío
            if shipping_method:
                rate = ShippingRate.objects.filter(
                    name__icontains=shipping_method,
                    is_active=True
                ).first()
            else:
                rate = ShippingRate.objects.filter(is_active=True).first()
            
            if not rate:
                # Costo por defecto si no hay tarifas configuradas
                return Decimal('15000') if subtotal < Decimal('100000') else Decimal('0')
            
            return rate.calculate_cost(subtotal, weight)
            
        except Exception as e:
            print(f"Error calculating shipping cost: {str(e)}")
            return Decimal('15000')  # Fallback
    
    @staticmethod
    def get_available_shipping_methods():
        """
        Obtener métodos de envío disponibles
        """
        from apps.orders.models import ShippingRate
        
        return ShippingRate.objects.filter(is_active=True).order_by('base_cost')
