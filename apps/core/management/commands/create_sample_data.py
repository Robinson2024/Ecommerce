# filepath: apps/core/management/commands/create_sample_data.py
"""
Comando de Django para crear datos de ejemplo.
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.products.models import Product
from apps.accounts.models import User


class Command(BaseCommand):
    help = 'Crea datos de ejemplo para el ecommerce'

    def handle(self, *args, **options):
        self.stdout.write('Creando productos de ejemplo...')
        
        # Crear productos
        productos = [
            {
                'name': 'iPhone 15 Pro Max 256GB',
                'description': 'El iPhone más avanzado con titanio, cámara de 48MP y chip A17 Pro.',
                'price': 5499000.00
            },
            {
                'name': 'MacBook Pro M3 14" 512GB',
                'description': 'La laptop profesional más potente con el nuevo chip M3.',
                'price': 8999000.00
            },
            {
                'name': 'AirPods Pro 3ra Generación',
                'description': 'Audífonos inalámbricos con cancelación de ruido adaptativa.',
                'price': 899000.00
            },
            {
                'name': 'iPad Air M2 11" 256GB',
                'description': 'El iPad más versátil con el potente chip M2.',
                'price': 3299000.00
            },
            {
                'name': 'Samsung Galaxy S24 Ultra 512GB',
                'description': 'El smartphone Android más avanzado con S Pen integrado.',
                'price': 5199000.00
            },
            {
                'name': 'Nintendo Switch OLED',
                'description': 'La consola híbrida de Nintendo con pantalla OLED.',
                'price': 1599000.00
            },
            {
                'name': 'Sony WH-1000XM5',
                'description': 'Auriculares inalámbricos con la mejor cancelación de ruido.',
                'price': 1299000.00
            },
            {
                'name': 'Tesla Cybertruck Model',
                'description': 'Modelo a escala del revolucionario Cybertruck de Tesla.',
                'price': 299000.00
            }
        ]
        
        created_count = 0
        for producto_data in productos:
            # Verificar si ya existe
            if not Product.objects.filter(name=producto_data['name']).exists():
                producto = Product.objects.create(
                    name=producto_data['name'],
                    slug=slugify(producto_data['name']),
                    description=producto_data['description'],
                    price=producto_data['price'],
                    is_active=True
                )
                created_count += 1
                self.stdout.write(f'✓ Creado: {producto.name}')
            else:
                self.stdout.write(f'- Ya existe: {producto_data["name"]}')
        
        self.stdout.write(
            self.style.SUCCESS(f'¡Proceso completado! Se crearon {created_count} productos.')
        )
