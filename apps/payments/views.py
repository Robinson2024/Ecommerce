# filepath: apps/payments/views.py
"""
Views para el manejo de pagos
"""
import json
import logging
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.urls import reverse
from django.conf import settings
from django.views.generic import TemplateView, View
from django.utils.decorators import method_decorator

from apps.orders.models import Order, Payment
from apps.cart.utils import get_cart_data, clear_cart
from .services import StripeService, PayPalService, OrderService, PaymentError

logger = logging.getLogger(__name__)


class PaymentView(TemplateView):
    """Vista temporal básica para pagos"""
    template_name = 'base.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Sistema de Pagos - En Desarrollo'
        return context


class PaymentSelectionView(TemplateView):
    """Vista para selección de método de pago"""
    template_name = 'payments/payment_selection.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener datos del carrito
        cart_data = get_cart_data(self.request)
        if not cart_data.get('items'):
            messages.error(self.request, 'Tu carrito está vacío.')
            return context
        
        # Calcular totales
        subtotal = sum(Decimal(str(item['total_price'])) for item in cart_data['items'])
        shipping_cost = Decimal('15000') if subtotal < Decimal('100000') else Decimal('0')
        tax_amount = subtotal * Decimal('0.19')
        total_amount = subtotal + shipping_cost + tax_amount
        
        context.update({
            'cart_data': cart_data,
            'subtotal': subtotal,
            'shipping_cost': shipping_cost,
            'tax_amount': tax_amount,
            'total_amount': total_amount,
            'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
        })
        
        return context


class PaymentMethodView(TemplateView):
    """Vista para seleccionar método de pago"""
    template_name = 'payments/payment_method_modern.html'


class StripePaymentView(View):
    """Vista para procesar pagos con Stripe"""
    
    def post(self, request):
        try:
            # Obtener datos del formulario
            customer_data = {
                'email': request.POST.get('email'),
                'phone': request.POST.get('phone'),
                'shipping_address': {
                    'first_name': request.POST.get('first_name'),
                    'last_name': request.POST.get('last_name'),
                    'address_line1': request.POST.get('address_line1'),
                    'address_line2': request.POST.get('address_line2', ''),
                    'city': request.POST.get('city'),
                    'state': request.POST.get('state'),
                    'postal_code': request.POST.get('postal_code'),
                    'country': request.POST.get('country', 'CO'),
                }
            }
            
            # Crear orden desde el carrito
            cart_data = get_cart_data(request)
            if not cart_data.get('items'):
                return JsonResponse({'error': 'Carrito vacío'}, status=400)
            
            order = OrderService.create_order_from_cart(
                cart_data,
                user=request.user if request.user.is_authenticated else None,
                payment_method='stripe',
                **customer_data
            )
            
            # Crear Payment Intent con Stripe
            stripe_service = StripeService()
            payment_data = stripe_service.create_payment_intent(order)
            
            return JsonResponse({
                'success': True,
                'order_id': order.id,
                'client_secret': payment_data['client_secret'],
                'publishable_key': payment_data['publishable_key'],
            })
            
        except Exception as e:
            logger.error(f"Error in Stripe payment: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)


class StripeCreateIntentView(View):
    """Vista para crear payment intent de Stripe"""
    
    def post(self, request):
        # Implementación temporal
        return JsonResponse({'error': 'En desarrollo'})


class StripeConfirmView(View):
    """Vista para confirmar pago de Stripe"""
    
    def post(self, request):
        # Implementación temporal
        return JsonResponse({'error': 'En desarrollo'})


class PayPalPaymentView(View):
    """Vista para procesar pagos con PayPal"""
    
    def post(self, request):
        try:
            # Obtener datos del formulario
            customer_data = {
                'email': request.POST.get('email'),
                'phone': request.POST.get('phone'),
                'shipping_address': {
                    'first_name': request.POST.get('first_name'),
                    'last_name': request.POST.get('last_name'),
                    'address_line1': request.POST.get('address_line1'),
                    'address_line2': request.POST.get('address_line2', ''),
                    'city': request.POST.get('city'),
                    'state': request.POST.get('state'),
                    'postal_code': request.POST.get('postal_code'),
                    'country': request.POST.get('country', 'CO'),
                }
            }
            
            # Crear orden desde el carrito
            cart_data = get_cart_data(request)
            if not cart_data.get('items'):
                return JsonResponse({'error': 'Carrito vacío'}, status=400)
            
            order = OrderService.create_order_from_cart(
                cart_data,
                user=request.user if request.user.is_authenticated else None,
                payment_method='paypal',
                **customer_data
            )
            
            # Crear pago con PayPal
            paypal_service = PayPalService()
            return_url = request.build_absolute_uri(reverse('payments:paypal_success'))
            cancel_url = request.build_absolute_uri(reverse('payments:paypal_cancel'))
            
            payment_data = paypal_service.create_payment(order, return_url, cancel_url)
            
            return JsonResponse({
                'success': True,
                'order_id': order.id,
                'approval_url': payment_data['approval_url'],
            })
            
        except Exception as e:
            logger.error(f"Error in PayPal payment: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)


class PayPalCreateView(View):
    """Vista para crear orden de PayPal"""
    
    def post(self, request):
        # Implementación temporal
        return JsonResponse({'error': 'En desarrollo'})


class PayPalExecuteView(View):
    """Vista para ejecutar pago de PayPal"""
    
    def post(self, request):
        # Implementación temporal
        return JsonResponse({'error': 'En desarrollo'})


class PayPalSuccessView(View):
    """Vista para manejar éxito de PayPal"""
    
    def get(self, request):
        payment_id = request.GET.get('paymentId')
        payer_id = request.GET.get('PayerID')
        
        if not payment_id or not payer_id:
            messages.error(request, 'Datos de pago incompletos.')
            return redirect('cart:detail')
        
        try:
            paypal_service = PayPalService()
            result = paypal_service.execute_payment(payment_id, payer_id)
            
            # Limpiar carrito
            clear_cart(request)
            
            messages.success(request, 'Pago procesado exitosamente.')
            return redirect('payments:success', order_id=result['order_id'])
            
        except PaymentError as e:
            logger.error(f"PayPal payment execution error: {str(e)}")
            messages.error(request, f'Error procesando pago: {str(e)}')
            return redirect('cart:detail')


class PayPalCancelView(TemplateView):
    """Vista para cancelación de PayPal"""
    template_name = 'payments/payment_cancelled.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        messages.warning(self.request, 'Pago cancelado.')
        return context


class PaymentSuccessView(TemplateView):
    """Vista de éxito de pago"""
    template_name = 'payments/payment_success_modern.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_id = kwargs.get('order_id')
        
        try:
            order = get_object_or_404(Order, id=order_id)
            
            # Verificar que el pago esté completado
            if order.payment_status != 'completed':
                messages.warning(self.request, 'El pago aún está siendo procesado.')
            
            # Actualizar inventario
            OrderService.update_inventory(order, 'decrease')
            
            # Enviar email de confirmación
            OrderService.send_order_confirmation(order)
            
            context['order'] = order
            
        except Order.DoesNotExist:
            messages.error(self.request, 'Orden no encontrada.')
            
        return context


class PaymentErrorView(TemplateView):
    """Vista de error de pago"""
    template_name = 'payments/payment_error_modern.html'


class PaymentCancelledView(TemplateView):
    """Vista de pago cancelado"""
    template_name = 'payments/payment_cancelled.html'


class StripeWebhookView(View):
    """Vista para webhooks de Stripe"""
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
        # Implementación temporal
        return HttpResponse(status=200)


class PayPalWebhookView(View):
    """Vista para webhooks de PayPal"""
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
        # Implementación temporal
        return HttpResponse(status=200)


@login_required
def order_detail_view(request, order_number):
    """Vista para ver detalles de una orden"""
    order = get_object_or_404(
        Order,
        order_number=order_number,
        user=request.user if request.user.is_authenticated else None
    )
    
    return render(request, 'orders/order_detail.html', {
        'order': order,
    })


def payment_status_check(request):
    """AJAX endpoint para verificar estado de pago"""
    payment_intent_id = request.GET.get('payment_intent_id')
    
    if not payment_intent_id:
        return JsonResponse({'error': 'Payment intent ID required'}, status=400)
    
    try:
        # Buscar orden por payment_intent_id
        order = Order.objects.get(payment_intent_id=payment_intent_id)
        
        return JsonResponse({
            'status': order.payment_status,
            'order_status': order.status,
            'order_id': order.id,
            'order_number': order.order_number,
        })
        
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
