# filepath: apps/products/apps.py
"""
Configuración de la app Products.
"""
from django.apps import AppConfig


class ProductsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.products'
    verbose_name = 'Products'
