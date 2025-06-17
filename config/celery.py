"""
Configuración de Celery para Tech Ecommerce.
"""

import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

app = Celery('tech_ecommerce')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Configuración de tareas periódicas
app.conf.beat_schedule = {
    'clean-expired-carts': {
        'task': 'apps.cart.tasks.clean_expired_carts',
        'schedule': 3600.0,  # cada hora
    },
    'update-product-rankings': {
        'task': 'apps.products.tasks.update_product_rankings',
        'schedule': 86400.0,  # cada día
    },
    'send-abandoned-cart-emails': {
        'task': 'apps.cart.tasks.send_abandoned_cart_emails',
        'schedule': 7200.0,  # cada 2 horas
    },
    'generate-daily-reports': {
        'task': 'apps.analytics.tasks.generate_daily_reports',
        'schedule': 86400.0,  # cada día a las 2 AM
    },
}

app.conf.timezone = 'America/Bogota'

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
