# filepath: apps/core/email_service.py
"""
Servicio de emails para notificaciones del ecommerce.
"""
import logging
from typing import Dict, List, Optional, TYPE_CHECKING
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.auth import get_user_model

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser

User = get_user_model()
logger = logging.getLogger(__name__)


class EmailService:
    """Servicio centralizado para el envío de emails"""
    
    DEFAULT_FROM_EMAIL = settings.DEFAULT_FROM_EMAIL
    
    @classmethod
    def send_order_confirmation(cls, order) -> bool:
        """
        Enviar email de confirmación de orden.
        
        Args:
            order: Instancia del modelo Order
            
        Returns:
            bool: True si el email se envió correctamente
        """
        try:
            context = {
                'order': order,
                'site_name': 'Tech Ecommerce',
                'support_email': settings.DEFAULT_FROM_EMAIL,
                'company_name': 'Tech Ecommerce',
                'logo_url': f"{settings.SITE_URL}/static/images/logo.png",
            }
            
            # Renderizar templates
            html_content = render_to_string('emails/order_confirmation.html', context)
            text_content = render_to_string('emails/order_confirmation.txt', context)
            
            subject = f'Confirmación de Pedido #{order.order_number} - Tech Ecommerce'
            
            # Crear email
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=cls.DEFAULT_FROM_EMAIL,
                to=[order.email],
                bcc=[settings.DEFAULT_FROM_EMAIL] if settings.DEBUG else []
            )
            email.attach_alternative(html_content, "text/html")
            
            # Enviar
            result = email.send()
            
            if result:
                logger.info(f"Order confirmation email sent to {order.email} for order {order.order_number}")
                return True
            else:
                logger.error(f"Failed to send order confirmation email to {order.email}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending order confirmation email: {str(e)}")
            return False
    
    @classmethod
    def send_payment_confirmation(cls, order, payment) -> bool:
        """
        Enviar email de confirmación de pago.
        
        Args:
            order: Instancia del modelo Order
            payment: Instancia del modelo Payment
            
        Returns:
            bool: True si el email se envió correctamente
        """
        try:
            context = {
                'order': order,
                'payment': payment,
                'site_name': 'Tech Ecommerce',
                'support_email': settings.DEFAULT_FROM_EMAIL,
                'company_name': 'Tech Ecommerce',
            }
            
            html_content = render_to_string('emails/payment_confirmation.html', context)
            text_content = render_to_string('emails/payment_confirmation.txt', context)
            
            subject = f'Pago Confirmado - Pedido #{order.order_number}'
            
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=cls.DEFAULT_FROM_EMAIL,
                to=[order.email]
            )
            email.attach_alternative(html_content, "text/html")
            
            result = email.send()
            
            if result:
                logger.info(f"Payment confirmation email sent to {order.email}")
                return True
            else:
                logger.error(f"Failed to send payment confirmation email to {order.email}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending payment confirmation email: {str(e)}")
            return False
    
    @classmethod
    def send_shipping_notification(cls, order) -> bool:
        """
        Enviar notificación de envío.
        
        Args:
            order: Instancia del modelo Order
            
        Returns:
            bool: True si el email se envió correctamente
        """
        try:
            context = {
                'order': order,
                'site_name': 'Tech Ecommerce',
                'support_email': settings.DEFAULT_FROM_EMAIL,
                'tracking_url': f"{settings.SITE_URL}/orders/{order.order_number}/track/",
            }
            
            html_content = render_to_string('emails/shipping_notification.html', context)
            text_content = render_to_string('emails/shipping_notification.txt', context)
            
            subject = f'Tu pedido #{order.order_number} ha sido enviado'
            
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=cls.DEFAULT_FROM_EMAIL,
                to=[order.email]
            )
            email.attach_alternative(html_content, "text/html")
            
            result = email.send()
            
            if result:
                logger.info(f"Shipping notification sent to {order.email}")
                return True
            else:
                logger.error(f"Failed to send shipping notification to {order.email}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending shipping notification: {str(e)}")
            return False
    
    @classmethod
    def send_delivery_confirmation(cls, order) -> bool:
        """
        Enviar confirmación de entrega.
        
        Args:
            order: Instancia del modelo Order
            
        Returns:
            bool: True si el email se envió correctamente
        """
        try:
            context = {
                'order': order,
                'site_name': 'Tech Ecommerce',
                'support_email': settings.DEFAULT_FROM_EMAIL,
                'review_url': f"{settings.SITE_URL}/orders/{order.order_number}/review/",
            }
            
            html_content = render_to_string('emails/delivery_confirmation.html', context)
            text_content = render_to_string('emails/delivery_confirmation.txt', context)
            
            subject = f'Tu pedido #{order.order_number} ha sido entregado'
            
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=cls.DEFAULT_FROM_EMAIL,
                to=[order.email]
            )
            email.attach_alternative(html_content, "text/html")
            
            result = email.send()
            
            if result:
                logger.info(f"Delivery confirmation sent to {order.email}")
                return True
            else:
                logger.error(f"Failed to send delivery confirmation to {order.email}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending delivery confirmation: {str(e)}")
            return False
    
    @classmethod
    def send_order_cancelled(cls, order, reason: str = "") -> bool:
        """
        Enviar notificación de orden cancelada.
        
        Args:
            order: Instancia del modelo Order
            reason: Razón de la cancelación
            
        Returns:
            bool: True si el email se envió correctamente
        """
        try:
            context = {
                'order': order,
                'reason': reason,
                'site_name': 'Tech Ecommerce',
                'support_email': settings.DEFAULT_FROM_EMAIL,
                'refund_info': "El reembolso será procesado en 3-5 días hábiles" if order.payment_status == 'completed' else None,
            }
            
            html_content = render_to_string('emails/order_cancelled.html', context)
            text_content = render_to_string('emails/order_cancelled.txt', context)
            
            subject = f'Pedido #{order.order_number} cancelado'
            
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=cls.DEFAULT_FROM_EMAIL,
                to=[order.email]
            )
            email.attach_alternative(html_content, "text/html")            
            result = email.send()
            
            if result:
                logger.info(f"Order cancellation email sent to {order.email}")
                return True
            else:
                logger.error(f"Failed to send order cancellation email to {order.email}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending order cancellation email: {str(e)}")
            return False
    
    @classmethod
    def send_bulk_notification(cls, user_list: List, subject: str, 
                              template_name: str, context: Dict) -> Dict[str, int]:
        """
        Enviar notificación masiva a una lista de usuarios.
        
        Args:
            user_list: Lista de usuarios
            subject: Asunto del email
            template_name: Nombre del template (sin extensión)
            context: Contexto para el template
            
        Returns:
            Dict con contadores de éxito y fallo
        """
        results = {'success': 0, 'failed': 0}
        
        for user in user_list:
            try:
                user_context = {**context, 'user': user}
                
                html_content = render_to_string(f'emails/{template_name}.html', user_context)
                text_content = render_to_string(f'emails/{template_name}.txt', user_context)
                
                email = EmailMultiAlternatives(
                    subject=subject,
                    body=text_content,
                    from_email=cls.DEFAULT_FROM_EMAIL,
                    to=[user.email]
                )
                email.attach_alternative(html_content, "text/html")
                
                if email.send():
                    results['success'] += 1
                else:
                    results['failed'] += 1
                    
            except Exception as e:
                logger.error(f"Error sending bulk email to {user.email}: {str(e)}")
                results['failed'] += 1
        
        logger.info(f"Bulk email sent: {results['success']} success, {results['failed']} failed")
        return results
