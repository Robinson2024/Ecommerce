# filepath: apps/orders/views.py
"""
Views para la app Orders.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse, HttpResponseRedirect
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
import json
import logging

from apps.cart.models import Cart
from apps.cart.utils import CartManager
from apps.core.email_service import EmailService
from .models import Order, OrderItem, ShippingRate
from apps.products.models import Product, ProductVariant


logger = logging.getLogger(__name__)


class CheckoutView(TemplateView):
    """Vista principal de checkout"""
    template_name = 'orders/checkout_modern.html'
    
    def dispatch(self, request, *args, **kwargs):
        """Verificar que hay items en el carrito"""
        cart_manager = CartManager(request)
        cart = cart_manager.get_cart(create=False)
        if not cart or cart.items.count() == 0:
            messages.warning(request, 'Tu carrito está vacío.')
            return redirect('cart:detail')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        """Agregar datos del carrito y métodos de envío"""
        context = super().get_context_data(**kwargs)
          # Obtener carrito
        cart_manager = CartManager(self.request)
        cart = cart_manager.get_cart(create=False)
        context['cart'] = cart
        
        # Calcular totales
        items_data = []
        subtotal = Decimal('0.00')
        
        for item in cart.items.select_related('product', 'variant'):
            item_total = item.quantity * item.product.price
            items_data.append({
                'product': item.product,
                'variant': item.variant,
                'quantity': item.quantity,
                'unit_price': item.product.price,
                'total_price': item_total
            })
            subtotal += item_total
        
        context['items_data'] = items_data
        context['subtotal'] = subtotal
        
        # Calcular envío (gratis si subtotal >= $100,000)
        shipping_cost = Decimal('0.00') if subtotal >= Decimal('100000') else Decimal('15000')
        context['shipping_cost'] = shipping_cost
        
        # Calcular impuestos (19% IVA)
        tax_amount = subtotal * Decimal('0.19')
        context['tax_amount'] = tax_amount
        
        # Total final
        total_amount = subtotal + shipping_cost + tax_amount
        context['total_amount'] = total_amount
        
        # Métodos de envío disponibles
        context['shipping_methods'] = ShippingRate.objects.filter(is_active=True)
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Procesar el checkout y crear orden"""
        try:
            with transaction.atomic():                # Obtener carrito
                cart_manager = CartManager(request)
                cart = cart_manager.get_cart(create=False)
                if not cart or cart.items.count() == 0:
                    messages.error(request, 'Tu carrito está vacío.')
                    return redirect('cart:detail')
                
                # Crear orden
                order = Order.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    email=request.POST.get('email'),
                    phone=request.POST.get('phone'),
                    shipping_address={
                        'first_name': request.POST.get('first_name'),
                        'last_name': request.POST.get('last_name'),
                        'address_line1': request.POST.get('address_line1'),
                        'address_line2': request.POST.get('address_line2', ''),
                        'city': request.POST.get('city'),
                        'state': request.POST.get('state'),
                        'postal_code': request.POST.get('postal_code'),
                        'country': request.POST.get('country', 'Colombia'),
                    },
                    billing_address={
                        'first_name': request.POST.get('first_name'),
                        'last_name': request.POST.get('last_name'),
                        'address_line1': request.POST.get('address_line1'),
                        'address_line2': request.POST.get('address_line2', ''),
                        'city': request.POST.get('city'),
                        'state': request.POST.get('state'),
                        'postal_code': request.POST.get('postal_code'),
                        'country': request.POST.get('country', 'Colombia'),
                    },
                    notes=request.POST.get('notes', ''),
                    status='pending',
                    payment_status='pending'
                )
                
                # Crear items de la orden
                for cart_item in cart.items.select_related('product', 'variant'):
                    OrderItem.objects.create(
                        order=order,
                        product=cart_item.product,
                        variant=cart_item.variant,
                        product_name=cart_item.product.name,
                        product_sku=cart_item.product.sku,
                        variant_info=str(cart_item.variant) if cart_item.variant else '',
                        quantity=cart_item.quantity,
                        unit_price=cart_item.product.price,
                        total_price=cart_item.quantity * cart_item.product.price
                    )
                
                # Calcular totales
                order.calculate_totals()
                order.save()
                
                # Guardar orden en sesión
                request.session['pending_order_id'] = order.id
                
                # Redirigir a selección de método de pago
                return redirect('payments:method')
                
        except Exception as e:
            logger.error(f"Error creating order: {str(e)}")
            messages.error(request, 'Error al procesar la orden. Por favor intenta nuevamente.')
            return self.get(request, *args, **kwargs)


class OrderListView(LoginRequiredMixin, ListView):
    """Vista para listar órdenes del usuario"""
    model = Order
    template_name = 'orders/list.html'
    context_object_name = 'orders'
    paginate_by = 10
    
    def get_queryset(self):
        """Filtrar órdenes del usuario actual"""
        return Order.objects.filter(
            user=self.request.user
        ).prefetch_related('items__product').order_by('-created_at')


class OrderDetailView(DetailView):
    """Vista para detalles de una orden"""
    model = Order
    template_name = 'orders/detail.html'
    context_object_name = 'order'
    slug_field = 'order_number'
    slug_url_kwarg = 'order_number'
    
    def get_queryset(self):
        """Filtrar por usuario si está autenticado"""
        queryset = Order.objects.prefetch_related(
            'items__product', 'items__variant'
        )
        
        if self.request.user.is_authenticated:
            # Usuarios autenticados solo ven sus órdenes
            queryset = queryset.filter(user=self.request.user)
        else:
            # Usuarios anónimos pueden ver órdenes con email de sesión
            session_email = self.request.session.get('guest_email')
            if session_email:
                queryset = queryset.filter(email=session_email, user__isnull=True)
            else:
                queryset = queryset.none()
        
        return queryset


class OrderCreateView(CreateView):
    """Vista para crear una nueva orden"""
    model = Order
    fields = ['email', 'phone', 'notes']
    template_name = 'orders/create.html'
    
    def form_valid(self, form):
        """Procesar creación de orden"""
        # Asociar con usuario si está autenticado
        if self.request.user.is_authenticated:
            form.instance.user = self.request.user
        
        return super().form_valid(form)
    
    def get_success_url(self):
        """Redirigir a detalle de orden"""
        return reverse('orders:detail', kwargs={'order_number': self.object.order_number})


class OrderTrackingView(DetailView):
    """Vista para tracking de órdenes"""
    model = Order
    template_name = 'orders/tracking.html'
    context_object_name = 'order'
    slug_field = 'order_number'
    slug_url_kwarg = 'order_number'
    
    def get_queryset(self):
        """Permitir tracking público con número de orden"""
        return Order.objects.prefetch_related('items__product')


class OrderCancelView(LoginRequiredMixin, DetailView):
    """Vista para cancelar una orden"""
    model = Order
    slug_field = 'order_number'
    slug_url_kwarg = 'order_number'
    
    def get_queryset(self):
        """Solo órdenes del usuario actual"""
        return Order.objects.filter(user=self.request.user)
    
    def post(self, request, *args, **kwargs):
        """Procesar cancelación de orden"""
        order = self.get_object()
        
        if order.can_cancel():
            order.status = 'cancelled'
            order.save()
            
            # Enviar email de cancelación
            try:
                EmailService.send_order_cancelled(order, "Cancelado por el cliente")
            except Exception as e:
                logger.error(f"Error sending cancellation email: {str(e)}")
            
            messages.success(request, f'Orden #{order.order_number} cancelada exitosamente.')
        else:
            messages.error(request, 'Esta orden no puede ser cancelada.')
        
        return redirect('orders:detail', order_number=order.order_number)


class ShippingMethodView(TemplateView):
    """Vista para seleccionar método de envío"""
    template_name = 'orders/shipping_method.html'
    
    def get_context_data(self, **kwargs):
        """Agregar métodos de envío disponibles"""
        context = super().get_context_data(**kwargs)
        
        # Obtener orden pendiente
        order_id = self.request.session.get('pending_order_id')
        if order_id:
            try:
                order = Order.objects.get(id=order_id)
                context['order'] = order
                context['shipping_methods'] = ShippingRate.objects.filter(is_active=True)
            except Order.DoesNotExist:
                messages.error(self.request, 'Orden no encontrada.')
                return redirect('cart:detail')
        else:
            messages.warning(self.request, 'No hay orden pendiente.')
            return redirect('cart:detail')
        
        return context


class CalculateShippingView(TemplateView):
    """Vista HTMX para calcular costos de envío"""
    
    def post(self, request, *args, **kwargs):
        """Calcular costo de envío dinámicamente"""
        try:
            shipping_method_id = request.POST.get('shipping_method')
            
            if not shipping_method_id:
                return JsonResponse({'error': 'Método de envío requerido'}, status=400)
            
            # Obtener método de envío
            try:
                shipping_method = ShippingRate.objects.get(id=shipping_method_id, is_active=True)
            except ShippingRate.DoesNotExist:
                return JsonResponse({'error': 'Método de envío no válido'}, status=400)
            
            # Obtener orden pendiente
            order_id = request.session.get('pending_order_id')
            if not order_id:
                return JsonResponse({'error': 'No hay orden pendiente'}, status=400)
            
            try:
                order = Order.objects.get(id=order_id)
            except Order.DoesNotExist:
                return JsonResponse({'error': 'Orden no encontrada'}, status=400)
            
            # Calcular costo de envío
            shipping_cost = shipping_method.calculate_cost(order.subtotal)
            
            # Actualizar orden
            order.shipping_cost = shipping_cost
            order.calculate_totals()
            order.save()
            
            return JsonResponse({
                'success': True,
                'shipping_cost': float(shipping_cost),
                'total_amount': float(order.total_amount),
                'method_name': shipping_method.name,
                'estimated_delivery': shipping_method.get_estimated_delivery()
            })
            
        except Exception as e:
            logger.error(f"Error calculating shipping: {str(e)}")
            return JsonResponse({'error': 'Error calculando envío'}, status=500)


class UpdateAddressView(TemplateView):
    """Vista HTMX para actualizar dirección"""
    
    def post(self, request, *args, **kwargs):
        """Actualizar dirección de envío"""
        try:
            order_id = request.session.get('pending_order_id')
            if not order_id:
                return JsonResponse({'error': 'No hay orden pendiente'}, status=400)
            
            order = Order.objects.get(id=order_id)
            
            # Actualizar dirección
            address_data = {
                'first_name': request.POST.get('first_name'),
                'last_name': request.POST.get('last_name'),
                'address_line1': request.POST.get('address_line1'),
                'address_line2': request.POST.get('address_line2', ''),
                'city': request.POST.get('city'),
                'state': request.POST.get('state'),
                'postal_code': request.POST.get('postal_code'),
                'country': request.POST.get('country', 'Colombia'),
            }
            
            order.shipping_address = address_data
            order.billing_address = address_data  # Por ahora usar la misma
            order.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Dirección actualizada correctamente'
            })
            
        except Order.DoesNotExist:
            return JsonResponse({'error': 'Orden no encontrada'}, status=400)
        except Exception as e:
            logger.error(f"Error updating address: {str(e)}")
            return JsonResponse({'error': 'Error actualizando dirección'}, status=500)


class OrderConfirmationView(TemplateView):
    """Vista de confirmación de orden"""
    template_name = 'orders/confirmation_modern.html'
    
    def get_context_data(self, **kwargs):
        """Agregar datos de la orden confirmada"""
        context = super().get_context_data(**kwargs)
        
        # Obtener orden de la sesión
        order_id = self.request.session.get('confirmed_order_id')
        if order_id:
            try:
                order = Order.objects.get(id=order_id)
                context['order'] = order
                
                # Limpiar sesión
                if 'confirmed_order_id' in self.request.session:
                    del self.request.session['confirmed_order_id']
                if 'pending_order_id' in self.request.session:
                    del self.request.session['pending_order_id']
                    
            except Order.DoesNotExist:
                messages.error(self.request, 'Orden no encontrada.')
                return redirect('orders:list')
        else:
            messages.warning(self.request, 'No hay orden para confirmar.')
            return redirect('cart:detail')
        
        return context
