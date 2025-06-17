# filepath: apps/coupons/apps.py
"""
Configuración de la app Coupons.
"""
from django.apps import AppConfig


class CouponsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.coupons'
    verbose_name = 'Coupons'
