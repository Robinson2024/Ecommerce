from django.shortcuts import get_object_or_404
from django.contrib.sessions.models import Session
from django.contrib.auth import get_user_model

from .models import Cart, CartItem
from apps.products.models import Product, ProductVariant

User = get_user_model()


class CartManager:
    """
    Manejador para operaciones del carrito
    Abstrae la lógica de manejo de carritos para usuarios autenticados y anónimos
    """
    
    def __init__(self, request):
        self.request = request
        self.user = request.user if request.user.is_authenticated else None
        self.session_key = request.session.session_key
        self._cart = None
    
    def get_cart(self, create=True):
        """
        Obtiene o crea el carrito para el usuario/sesión actual
        
        Args:
            create: Si True, crea el carrito si no existe
        
        Returns:
            Cart instance o None
        """
        if self._cart is not None:
            return self._cart
        
        if self.user:
            # Usuario autenticado: buscar por usuario
            try:
                self._cart = Cart.objects.get(user=self.user)
            except Cart.DoesNotExist:
                if create:
                    self._cart = Cart.objects.create(user=self.user)
                else:
                    return None
        else:
            # Usuario anónimo: buscar por sesión
            if not self.session_key:
                if create:
                    # Crear sesión si no existe
                    self.request.session.create()
                    self.session_key = self.request.session.session_key
                else:
                    return None
            
            try:
                self._cart = Cart.objects.get(session_key=self.session_key)
            except Cart.DoesNotExist:
                if create:
                    self._cart = Cart.objects.create(session_key=self.session_key)
                else:
                    return None
        
        return self._cart
    
    def add_product(self, product_id, quantity=1, variant_id=None, update_quantity=False):
        """
        Agrega un producto al carrito
        
        Args:
            product_id: ID del producto
            quantity: Cantidad a agregar
            variant_id: ID de la variante (opcional)
            update_quantity: Si True, reemplaza la cantidad; si False, suma
        
        Returns:
            dict con resultado de la operación
        """
        try:
            product = get_object_or_404(Product, id=product_id, is_active=True)
            variant = None
            
            if variant_id:
                variant = get_object_or_404(ProductVariant, id=variant_id, product=product)
                # Verificar stock de la variante
                if variant.stock < quantity:
                    return {
                        'success': False,
                        'message': f'Stock insuficiente. Solo quedan {variant.stock} unidades disponibles.',
                        'stock_available': variant.stock
                    }
            else:
                # Verificar stock del producto principal
                total_stock = sum(v.stock for v in product.variants.all()) if product.variants.exists() else product.stock
                if total_stock < quantity:
                    return {
                        'success': False,
                        'message': f'Stock insuficiente. Solo quedan {total_stock} unidades disponibles.',
                        'stock_available': total_stock
                    }
            
            cart = self.get_cart(create=True)
            cart_item = cart.add_product(
                product=product,
                quantity=quantity,
                variant=variant,
                update_quantity=update_quantity
            )
            
            return {
                'success': True,
                'message': f'{product.name} agregado al carrito exitosamente.',
                'cart_item': cart_item,
                'cart_total': cart.get_total_price(),
                'cart_count': cart.get_total_items()
            }
            
        except Product.DoesNotExist:
            return {
                'success': False,
                'message': 'El producto solicitado no existe o no está disponible.'
            }
        except ProductVariant.DoesNotExist:
            return {
                'success': False,
                'message': 'La variante del producto no existe.'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error al agregar el producto: {str(e)}'
            }
    
    def update_quantity(self, product_id, quantity, variant_id=None):
        """
        Actualiza la cantidad de un producto en el carrito
        
        Args:
            product_id: ID del producto
            quantity: Nueva cantidad
            variant_id: ID de la variante (opcional)
        
        Returns:
            dict con resultado de la operación
        """
        try:
            cart = self.get_cart(create=False)
            if not cart:
                return {
                    'success': False,
                    'message': 'No se encontró el carrito.'
                }
            
            product = get_object_or_404(Product, id=product_id)
            variant = None
            
            if variant_id:
                variant = get_object_or_404(ProductVariant, id=variant_id)
            
            if quantity <= 0:
                # Eliminar item del carrito
                removed = cart.remove_product(product, variant)
                if removed:
                    return {
                        'success': True,
                        'message': f'{product.name} eliminado del carrito.',
                        'cart_total': cart.get_total_price(),
                        'cart_count': cart.get_total_items(),
                        'action': 'removed'
                    }
                else:
                    return {
                        'success': False,
                        'message': 'El producto no estaba en el carrito.'
                    }
            else:
                # Actualizar cantidad
                cart_item = cart.update_quantity(product, quantity, variant)
                if cart_item:
                    return {
                        'success': True,
                        'message': f'Cantidad actualizada para {product.name}.',
                        'cart_item': cart_item,
                        'cart_total': cart.get_total_price(),
                        'cart_count': cart.get_total_items(),
                        'action': 'updated'
                    }
                else:
                    return {
                        'success': False,
                        'message': 'No se pudo actualizar la cantidad.'
                    }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error al actualizar el carrito: {str(e)}'
            }
    
    def remove_product(self, product_id, variant_id=None):
        """
        Elimina un producto del carrito
        
        Args:
            product_id: ID del producto
            variant_id: ID de la variante (opcional)
        
        Returns:
            dict con resultado de la operación
        """
        try:
            cart = self.get_cart(create=False)
            if not cart:
                return {
                    'success': False,
                    'message': 'No se encontró el carrito.'
                }
            
            product = get_object_or_404(Product, id=product_id)
            variant = None
            
            if variant_id:
                variant = get_object_or_404(ProductVariant, id=variant_id)
            
            removed = cart.remove_product(product, variant)
            if removed:
                return {
                    'success': True,
                    'message': f'{product.name} eliminado del carrito exitosamente.',
                    'cart_total': cart.get_total_price(),
                    'cart_count': cart.get_total_items()
                }
            else:
                return {
                    'success': False,
                    'message': 'El producto no estaba en el carrito.'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error al eliminar el producto: {str(e)}'
            }
    
    def clear_cart(self):
        """
        Vacía completamente el carrito
        
        Returns:
            dict con resultado de la operación
        """
        try:
            cart = self.get_cart(create=False)
            if not cart:
                return {
                    'success': False,
                    'message': 'No se encontró el carrito.'
                }
            
            cart.clear()
            return {
                'success': True,
                'message': 'Carrito vaciado exitosamente.',
                'cart_total': 0,
                'cart_count': 0
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error al vaciar el carrito: {str(e)}'
            }
    
    def get_cart_data(self):
        """
        Obtiene datos completos del carrito para templates
        
        Returns:
            dict con datos del carrito
        """
        cart = self.get_cart(create=False)
        if not cart:
            return {
                'cart': None,
                'items': [],
                'total_price': 0,
                'total_items': 0,
                'items_count': 0
            }
        
        return {
            'cart': cart,
            'items': cart.items.select_related('product', 'variant').all(),
            'total_price': cart.get_total_price(),
            'total_items': cart.get_total_items(),
            'items_count': cart.get_items_count()
        }
    
    def merge_carts(self, user):
        """
        Fusiona carrito anónimo con carrito de usuario autenticado
        Se llama después del login
        
        Args:
            user: Usuario recién autenticado
        """
        if not self.session_key:
            return
        
        try:
            # Carrito anónimo (de la sesión)
            anonymous_cart = Cart.objects.get(session_key=self.session_key)
            
            # Carrito del usuario autenticado
            user_cart, created = Cart.objects.get_or_create(user=user)
            
            # Fusionar items del carrito anónimo al carrito del usuario
            for item in anonymous_cart.items.all():
                user_cart.add_product(
                    product=item.product,
                    quantity=item.quantity,
                    variant=item.variant,
                    update_quantity=False  # Sumar cantidades
                )
            
            # Eliminar carrito anónimo
            anonymous_cart.delete()
            
            # Actualizar referencia interna
            self._cart = user_cart
            self.user = user
            
        except Cart.DoesNotExist:
            # No hay carrito anónimo, no hacer nada
            pass
        except Exception as e:
            # Log del error pero no fallar
            print(f"Error fusionando carritos: {e}")


def get_cart_manager(request):
    """
    Factory function para obtener un CartManager
    
    Args:
        request: HttpRequest object
    
    Returns:
        CartManager instance
    """
    return CartManager(request)

# Funciones auxiliares para compatibilidad
def get_cart(request, create=True):
    """
    Función auxiliar para obtener el carrito.
    Mantiene compatibilidad con código existente.
    """
    cart_manager = CartManager(request)
    return cart_manager.get_cart(create=create)


def get_cart_data(request):
    """
    Función auxiliar para obtener datos del carrito.
    """
    cart_manager = CartManager(request)
    return cart_manager.get_cart_data()


def clear_cart(request):
    """
    Función auxiliar para limpiar el carrito.
    """
    cart_manager = CartManager(request)
    return cart_manager.clear_cart()
