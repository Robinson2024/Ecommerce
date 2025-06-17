from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiplica dos números"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter 
def sub(value, arg):
    """Resta dos números"""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def add_class(field, css_class):
    """Agrega clases CSS a un campo de formulario"""
    try:
        # Para campos de Django forms
        if hasattr(field, 'as_widget'):
            return field.as_widget(attrs={'class': css_class})
        # Para widgets directos
        elif hasattr(field, 'field') and hasattr(field.field, 'widget'):
            field.field.widget.attrs.update({'class': css_class})
            return field
        else:
            return field
    except:
        return field
