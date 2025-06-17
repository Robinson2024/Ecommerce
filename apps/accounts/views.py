"""
Views para la app accounts.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.contrib.auth import logout
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from .models import User, UserProfile, Address, WishlistItem
from .forms import UserProfileForm, AddressForm


class ProfileView(LoginRequiredMixin, TemplateView):
    """Vista del perfil del usuario."""
    template_name = 'accounts/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        context.update({
            'user': user,
            'profile': getattr(user, 'profile', None),
            'addresses': user.addresses.all()[:3],  # Últimas 3 direcciones
            'recent_orders': user.orders.all()[:5],  # Últimos 5 pedidos
            'wishlist_count': user.wishlist_items.count(),
        })
        
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """Vista para editar el perfil del usuario."""
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('accounts:profile')
    
    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile
    
    def form_valid(self, form):
        messages.success(self.request, '¡Perfil actualizado exitosamente!')
        return super().form_valid(form)


class AddressListView(LoginRequiredMixin, ListView):
    """Vista para listar las direcciones del usuario."""
    model = Address
    template_name = 'accounts/address_list.html'
    context_object_name = 'addresses'
    
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user, is_deleted=False)


class AddressCreateView(LoginRequiredMixin, CreateView):
    """Vista para crear una nueva dirección."""
    model = Address
    form_class = AddressForm
    template_name = 'accounts/address_form.html'
    success_url = reverse_lazy('accounts:address_list')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, '¡Dirección agregada exitosamente!')
        return super().form_valid(form)


class AddressUpdateView(LoginRequiredMixin, UpdateView):
    """Vista para actualizar una dirección."""
    model = Address
    form_class = AddressForm
    template_name = 'accounts/address_form.html'
    success_url = reverse_lazy('accounts:address_list')
    
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user, is_deleted=False)
    
    def form_valid(self, form):
        messages.success(self.request, '¡Dirección actualizada exitosamente!')
        return super().form_valid(form)


class AddressDeleteView(LoginRequiredMixin, DeleteView):
    """Vista para eliminar una dirección."""
    model = Address
    template_name = 'accounts/address_confirm_delete.html'
    success_url = reverse_lazy('accounts:address_list')
    
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user, is_deleted=False)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, '¡Dirección eliminada exitosamente!')
        return super().delete(request, *args, **kwargs)


class WishlistView(LoginRequiredMixin, ListView):
    """Vista para la lista de deseos."""
    model = WishlistItem
    template_name = 'accounts/wishlist.html'
    context_object_name = 'wishlist_items'
    paginate_by = 12
    
    def get_queryset(self):
        return WishlistItem.objects.filter(
            user=self.request.user, 
            is_deleted=False
        ).select_related('product')


@login_required
def add_to_wishlist(request):
    """Agregar producto a la wishlist via AJAX."""
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        
        if not product_id:
            return JsonResponse({'success': False, 'message': 'ID de producto requerido'})
        
        try:
            from apps.products.models import Product
            product = Product.objects.get(id=product_id, is_active=True)
            
            wishlist_item, created = WishlistItem.objects.get_or_create(
                user=request.user,
                product=product,
                defaults={'priority': 1}
            )
            
            if created:
                return JsonResponse({
                    'success': True, 
                    'message': 'Producto agregado a tu lista de deseos',
                    'in_wishlist': True
                })
            else:
                return JsonResponse({
                    'success': False, 
                    'message': 'El producto ya está en tu lista de deseos',
                    'in_wishlist': True
                })
                
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Producto no encontrado'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': 'Error interno del servidor'})
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})


@login_required
def remove_from_wishlist(request):
    """Remover producto de la wishlist via AJAX."""
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        
        if not product_id:
            return JsonResponse({'success': False, 'message': 'ID de producto requerido'})
        
        try:
            wishlist_item = WishlistItem.objects.get(
                user=request.user,
                product_id=product_id
            )
            wishlist_item.delete()
            
            return JsonResponse({
                'success': True, 
                'message': 'Producto removido de tu lista de deseos',
                'in_wishlist': False
            })
            
        except WishlistItem.DoesNotExist:
            return JsonResponse({
                'success': False, 
                'message': 'El producto no está en tu lista de deseos',
                'in_wishlist': False
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': 'Error interno del servidor'})
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})


class OrderHistoryView(LoginRequiredMixin, ListView):
    """Vista para el historial de pedidos."""
    template_name = 'accounts/order_history.html'
    context_object_name = 'orders'
    paginate_by = 10
    
    def get_queryset(self):
        return self.request.user.orders.all().order_by('-created_at')


class OrderDetailView(LoginRequiredMixin, TemplateView):
    """Vista para el detalle de un pedido."""
    template_name = 'accounts/order_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_number = kwargs.get('order_number')
        
        try:
            from apps.orders.models import Order
            order = Order.objects.get(
                user=self.request.user, 
                order_number=order_number
            )
            context['order'] = order
        except Order.DoesNotExist:
            context['order'] = None
        
        return context


class LogoutSuccessView(TemplateView):
    """Vista personalizada para mostrar interfaz profesional después del logout."""
    template_name = 'account/logout_success.html'
    
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'logout_success': True,
            'redirect_url': '/',
            'site_name': 'Tech Ecommerce',
        })
        return context
