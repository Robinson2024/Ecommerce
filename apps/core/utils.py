"""
Utilidades y helpers para Tech Ecommerce.
"""

import re
import hashlib
from decimal import Decimal
from django.utils.text import slugify
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def generate_unique_slug(model_class, title, slug_field='slug'):
    """
    Genera un slug único para un modelo.
    """
    base_slug = slugify(title)
    slug = base_slug
    counter = 1
    
    while model_class.objects.filter(**{slug_field: slug}).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
    
    return slug


def format_currency(amount):
    """
    Formatea un valor como moneda colombiana.
    """
    if not amount:
        return "$0"
    
    # Convertir a Decimal si no lo es
    if not isinstance(amount, Decimal):
        amount = Decimal(str(amount))
    
    # Formatear con separadores de miles
    formatted = f"{amount:,.0f}"
    return f"${formatted}"


def calculate_tax(amount, tax_rate=None):
    """
    Calcula el impuesto para un monto dado.
    """
    if tax_rate is None:
        tax_rate = Decimal(str(settings.ECOMMERCE_SETTINGS['TAX_RATE']))
    
    if not isinstance(amount, Decimal):
        amount = Decimal(str(amount))
    
    return amount * tax_rate


def calculate_discount(price, discount_percent):
    """
    Calcula el descuento sobre un precio.
    """
    if not isinstance(price, Decimal):
        price = Decimal(str(price))
    
    if not isinstance(discount_percent, Decimal):
        discount_percent = Decimal(str(discount_percent))
    
    discount_amount = price * (discount_percent / 100)
    return price - discount_amount


def generate_order_number():
    """
    Genera un número de orden único.
    """
    import time
    import random
    
    timestamp = str(int(time.time()))
    random_num = str(random.randint(1000, 9999))
    return f"TE{timestamp[-6:]}{random_num}"


def validate_phone_number(phone):
    """
    Valida un número de teléfono colombiano.
    """
    # Remover espacios y caracteres especiales
    clean_phone = re.sub(r'[^\d+]', '', phone)
    
    # Patrones válidos para Colombia
    patterns = [
        r'^\+57[39]\d{9}$',  # +57 + celular (9 o 3 + 9 dígitos)
        r'^[39]\d{9}$',      # celular sin código país
        r'^\+57[1-8]\d{7}$', # +57 + fijo (1-8 + 7 dígitos)
        r'^[1-8]\d{7}$',     # fijo sin código país
    ]
    
    return any(re.match(pattern, clean_phone) for pattern in patterns)


def send_template_email(subject, template_name, context, recipient_list, from_email=None):
    """
    Envía un email usando un template.
    """
    if from_email is None:
        from_email = settings.DEFAULT_FROM_EMAIL
    
    # Renderizar template HTML
    html_message = render_to_string(template_name, context)
    
    # Crear versión de texto plano
    plain_message = strip_tags(html_message)
    
    return send_mail(
        subject=subject,
        message=plain_message,
        from_email=from_email,
        recipient_list=recipient_list,
        html_message=html_message,
        fail_silently=False,
    )


def generate_cache_key(*args):
    """
    Genera una clave de cache única basada en los argumentos.
    """
    key_parts = [str(arg) for arg in args]
    key_string = ':'.join(key_parts)
    
    # Usar hash MD5 para claves muy largas
    if len(key_string) > 200:
        key_string = hashlib.md5(key_string.encode()).hexdigest()
    
    return f"tech_ecommerce:{key_string}"


def paginate_queryset(queryset, page, per_page=20):
    """
    Pagina un queryset de forma eficiente.
    """
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    
    paginator = Paginator(queryset, per_page)
    
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    return page_obj


def clean_html(html_content):
    """
    Limpia contenido HTML de tags peligrosos.
    """
    import bleach
    
    allowed_tags = [
        'p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li',
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote'
    ]
    
    allowed_attributes = {
        '*': ['class'],
    }
    
    return bleach.clean(
        html_content,
        tags=allowed_tags,
        attributes=allowed_attributes,
        strip=True
    )


class ImageProcessor:
    """
    Clase para procesamiento de imágenes.
    """
    
    @staticmethod
    def resize_image(image, max_width=800, max_height=600, quality=85):
        """
        Redimensiona una imagen manteniendo la proporción.
        """
        from PIL import Image
        import io
        
        # Abrir imagen
        img = Image.open(image)
        
        # Convertir a RGB si es necesario
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        
        # Calcular nuevo tamaño manteniendo proporción
        img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        
        # Guardar en memoria
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=quality, optimize=True)
        output.seek(0)
        
        return output
    
    @staticmethod
    def create_thumbnail(image, size=(300, 300)):
        """
        Crea una miniatura cuadrada de una imagen.
        """
        from PIL import Image
        import io
        
        img = Image.open(image)
        
        # Convertir a RGB si es necesario
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        
        # Crear thumbnail cuadrado
        img.thumbnail(size, Image.Resampling.LANCZOS)
        
        # Crear imagen cuadrada con fondo blanco
        square_img = Image.new('RGB', size, (255, 255, 255))
        
        # Centrar la imagen
        x = (size[0] - img.width) // 2
        y = (size[1] - img.height) // 2
        square_img.paste(img, (x, y))
        
        # Guardar en memoria
        output = io.BytesIO()
        square_img.save(output, format='JPEG', quality=85, optimize=True)
        output.seek(0)
        
        return output


def get_client_ip(request):
    """
    Obtiene la IP real del cliente.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def is_ajax(request):
    """
    Verifica si la request es AJAX (compatible con HTMX).
    """
    return (
        request.headers.get('X-Requested-With') == 'XMLHttpRequest' or
        request.headers.get('HX-Request') == 'true'
    )
