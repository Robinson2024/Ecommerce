# filepath: apps/cart/views.py
"""
Views para la app Cart con funcionalidad HTMX.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.generic import View, TemplateView
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.template.loader import render_to_string

from .utils import get_cart_manager
from .models import Cart, CartItem
from apps.products.models import Product, ProductVariant


class CartDetailView(TemplateView):
    """Vista para mostrar el detalle completo del carrito"""
    template_name = 'cart/cart_detail_modern.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_manager = get_cart_manager(self.request)
        cart_data = cart_manager.get_cart_data()
        
        context.update(cart_data)
        return context


class AddToCartView(View):
    """Vista para agregar productos al carrito usando HTMX"""
    
    def post(self, request, *args, **kwargs):
        try:
            product_id = request.POST.get('product_id')
            quantity = int(request.POST.get('quantity', 1))
            variant_id = request.POST.get('variant_id')
            update_quantity = request.POST.get('update_quantity') == 'true'
            
            if not product_id:
                return JsonResponse({
                    'success': False,
                    'message': 'ID del producto requerido.'
                }, status=400)
            
            cart_manager = get_cart_manager(request)
            result = cart_manager.add_product(
                product_id=product_id,
                quantity=quantity,
                variant_id=variant_id,
                update_quantity=update_quantity
            )
            
            if result['success']:
                # Para requests HTMX, devolver HTML actualizado
                if request.headers.get('HX-Request'):
                    # Renderizar mini-cart actualizado
                    cart_data = cart_manager.get_cart_data()
                    mini_cart_html = render_to_string(
                        'cart/partials/mini_cart_content.html',
                        cart_data,
                        request=request
                    )
                    
                    # Renderizar contador del carrito
                    cart_count_html = render_to_string(
                        'cart/partials/cart_count.html',
                        {'cart_count': result['cart_count']},
                        request=request
                    )
                    
                    return HttpResponse(
                        f"""
                        <div hx-swap-oob="innerHTML:#mini-cart-content">{mini_cart_html}</div>
                        <div hx-swap-oob="innerHTML:#cart-count">{cart_count_html}</div>
                        <div class="alert alert-success alert-dismissible fade show" role="alert">
                            <i class="bi bi-check-circle"></i> {result['message']}
                            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                        </div>
                        """
                    )
                else:
                    messages.success(request, result['message'])
                    return redirect('cart:detail')
            else:
                if request.headers.get('HX-Request'):
                    return HttpResponse(
                        f"""
                        <div class="alert alert-danger alert-dismissible fade show" role="alert">
                            <i class="bi bi-exclamation-triangle"></i> {result['message']}
                            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                        </div>
                        """
                    )
                else:
                    messages.error(request, result['message'])
                    return redirect('products:detail', slug=kwargs.get('slug', ''))
                    
        except ValueError:
            error_msg = 'Cantidad inválida.'
            if request.headers.get('HX-Request'):
                return HttpResponse(
                    f"""
                    <div class="alert alert-danger alert-dismissible fade show" role="alert">
                        <i class="bi bi-exclamation-triangle"></i> {error_msg}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                    """
                )
            else:
                messages.error(request, error_msg)
                return redirect('cart:detail')
        
        except Exception as e:
            error_msg = f'Error inesperado: {str(e)}'
            if request.headers.get('HX-Request'):
                return HttpResponse(
                    f"""
                    <div class="alert alert-danger alert-dismissible fade show" role="alert">
                        <i class="bi bi-exclamation-triangle"></i> {error_msg}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                    """
                )
            else:
                messages.error(request, error_msg)
                return redirect('cart:detail')


class UpdateCartItemView(View):
    """Vista para actualizar cantidad de items del carrito"""
    
    def post(self, request, *args, **kwargs):
        try:
            product_id = request.POST.get('product_id')
            quantity = int(request.POST.get('quantity', 1))
            variant_id = request.POST.get('variant_id')
            
            if not product_id:
                return JsonResponse({
                    'success': False,
                    'message': 'ID del producto requerido.'
                }, status=400)
            
            cart_manager = get_cart_manager(request)
            result = cart_manager.update_quantity(
                product_id=product_id,
                quantity=quantity,
                variant_id=variant_id
            )
            
            if request.headers.get('HX-Request'):
                if result['success']:
                    cart_data = cart_manager.get_cart_data()
                    
                    if result['action'] == 'removed':
                        # Item fue eliminado, actualizar toda la página del carrito
                        cart_content_html = render_to_string(
                            'cart/partials/cart_items.html',
                            cart_data,
                            request=request
                        )
                        cart_summary_html = render_to_string(
                            'cart/partials/cart_summary.html',
                            cart_data,
                            request=request
                        )
                        
                        return HttpResponse(
                            f"""
                            <div hx-swap-oob="innerHTML:#cart-items">{cart_content_html}</div>
                            <div hx-swap-oob="innerHTML:#cart-summary">{cart_summary_html}</div>
                            <div hx-swap-oob="innerHTML:#cart-count">{result['cart_count']}</div>
                            """
                        )
                    else:
                        # Item actualizado, solo actualizar el item específico
                        item_html = render_to_string(
                            'cart/partials/cart_item.html',
                            {
                                'item': result['cart_item'],
                                'cart_total': result['cart_total']
                            },
                            request=request
                        )
                        
                        return HttpResponse(
                            f"""
                            <div hx-swap-oob="outerHTML:#cart-item-{product_id}">{item_html}</div>
                            <div hx-swap-oob="innerHTML:#cart-count">{result['cart_count']}</div>
                            <div hx-swap-oob="innerHTML:#cart-total">${result['cart_total']:,.2f}</div>
                            """
                        )
                else:
                    return HttpResponse(
                        f"""
                        <div class="alert alert-danger alert-dismissible fade show" role="alert">
                            <i class="bi bi-exclamation-triangle"></i> {result['message']}
                            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                        </div>
                        """
                    )
            else:
                if result['success']:
                    messages.success(request, result['message'])
                else:
                    messages.error(request, result['message'])
                return redirect('cart:detail')
                
        except ValueError:
            error_msg = 'Cantidad inválida.'
            if request.headers.get('HX-Request'):
                return HttpResponse(
                    f"""
                    <div class="alert alert-danger" role="alert">
                        <i class="bi bi-exclamation-triangle"></i> {error_msg}
                    </div>
                    """
                )
            else:
                messages.error(request, error_msg)
                return redirect('cart:detail')
        
        except Exception as e:
            error_msg = f'Error al actualizar: {str(e)}'
            if request.headers.get('HX-Request'):
                return HttpResponse(f'<div class="alert alert-danger">{error_msg}</div>')
            else:
                messages.error(request, error_msg)
                return redirect('cart:detail')


class RemoveFromCartView(View):
    """Vista para eliminar productos del carrito"""
    
    def post(self, request, *args, **kwargs):
        try:
            product_id = request.POST.get('product_id')
            variant_id = request.POST.get('variant_id')
            
            if not product_id:
                return JsonResponse({
                    'success': False,
                    'message': 'ID del producto requerido.'
                }, status=400)
            
            cart_manager = get_cart_manager(request)
            result = cart_manager.remove_product(
                product_id=product_id,
                variant_id=variant_id
            )
            
            if request.headers.get('HX-Request'):
                if result['success']:
                    cart_data = cart_manager.get_cart_data()
                    
                    # Renderizar carrito completo actualizado
                    cart_content_html = render_to_string(
                        'cart/partials/cart_items.html',
                        cart_data,
                        request=request
                    )
                    cart_summary_html = render_to_string(
                        'cart/partials/cart_summary.html',
                        cart_data,
                        request=request
                    )
                    
                    return HttpResponse(
                        f"""
                        <div hx-swap-oob="innerHTML:#cart-items">{cart_content_html}</div>
                        <div hx-swap-oob="innerHTML:#cart-summary">{cart_summary_html}</div>
                        <div hx-swap-oob="innerHTML:#cart-count">{result['cart_count']}</div>
                        <div class="alert alert-success alert-dismissible fade show" role="alert">
                            <i class="bi bi-check-circle"></i> {result['message']}
                            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                        </div>
                        """
                    )
                else:
                    return HttpResponse(
                        f"""
                        <div class="alert alert-danger alert-dismissible fade show" role="alert">
                            <i class="bi bi-exclamation-triangle"></i> {result['message']}
                            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                        </div>
                        """
                    )
            else:
                if result['success']:
                    messages.success(request, result['message'])
                else:
                    messages.error(request, result['message'])
                return redirect('cart:detail')
                
        except Exception as e:
            error_msg = f'Error al eliminar: {str(e)}'
            if request.headers.get('HX-Request'):
                return HttpResponse(f'<div class="alert alert-danger">{error_msg}</div>')
            else:
                messages.error(request, error_msg)
                return redirect('cart:detail')


class ClearCartView(View):
    """Vista para vaciar completamente el carrito"""
    
    def post(self, request, *args, **kwargs):
        try:
            cart_manager = get_cart_manager(request)
            result = cart_manager.clear_cart()
            
            if request.headers.get('HX-Request'):
                if result['success']:
                    # Carrito vacío
                    empty_cart_html = render_to_string(
                        'cart/partials/empty_cart.html',
                        {},
                        request=request
                    )
                    
                    return HttpResponse(
                        f"""
                        <div hx-swap-oob="innerHTML:#cart-content">{empty_cart_html}</div>
                        <div hx-swap-oob="innerHTML:#cart-count">0</div>
                        <div class="alert alert-success alert-dismissible fade show" role="alert">
                            <i class="bi bi-check-circle"></i> {result['message']}
                            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                        </div>
                        """
                    )
                else:
                    return HttpResponse(
                        f"""
                        <div class="alert alert-danger alert-dismissible fade show" role="alert">
                            <i class="bi bi-exclamation-triangle"></i> {result['message']}
                            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                        </div>
                        """
                    )
            else:
                if result['success']:
                    messages.success(request, result['message'])
                else:
                    messages.error(request, result['message'])
                return redirect('cart:detail')
                
        except Exception as e:
            error_msg = f'Error al vaciar carrito: {str(e)}'
            if request.headers.get('HX-Request'):
                return HttpResponse(f'<div class="alert alert-danger">{error_msg}</div>')
            else:
                messages.error(request, error_msg)
                return redirect('cart:detail')


class CartSummaryView(View):
    """Vista para obtener resumen del carrito (para mini-cart)"""
    
    def get(self, request, *args, **kwargs):
        cart_manager = get_cart_manager(request)
        cart_data = cart_manager.get_cart_data()
        
        if request.headers.get('HX-Request'):
            mini_cart_html = render_to_string(
                'cart/partials/mini_cart_content.html',
                cart_data,
                request=request
            )
            return HttpResponse(mini_cart_html)
        else:
            return JsonResponse(cart_data)


class CartCountView(View):
    """Vista para obtener solo el contador del carrito"""
    
    def get(self, request, *args, **kwargs):
        cart_manager = get_cart_manager(request)
        cart_data = cart_manager.get_cart_data()
        
        if request.headers.get('HX-Request'):
            count_html = render_to_string(
                'cart/partials/cart_count.html',
                {'cart_count': cart_data['total_items']},
                request=request
            )
            return HttpResponse(count_html)
        else:
            return JsonResponse({'cart_count': cart_data['total_items']})


# Context processor para hacer el carrito disponible en todos los templates
def cart_context(request):
    """Context processor para agregar datos del carrito a todos los templates"""
    if hasattr(request, 'cart_data'):
        return request.cart_data
    
    cart_manager = get_cart_manager(request)
    cart_data = cart_manager.get_cart_data()
    
    # Cache para esta request
    request.cart_data = cart_data
    
    return {
        'cart_total_items': cart_data['total_items'],
        'cart_total_price': cart_data['total_price'],
        'cart_items_count': cart_data['items_count']
    }
