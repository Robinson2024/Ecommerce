from django.core.management.base import BaseCommand
from django.utils.text import slugify
from decimal import Decimal


class Command(BaseCommand):
    help = 'Pobla la base de datos con datos de ejemplo'

    def handle(self, *args, **options):
        from apps.products.models import Product
        from apps.accounts.models import User
        
        self.stdout.write('🚀 Creando datos de ejemplo...')
        
        # Productos de ejemplo
        products = [
            {'name': 'iPhone 15 Pro Max', 'price': '5499000.00'},
            {'name': 'MacBook Pro M3 14"', 'price': '8999000.00'},
            {'name': 'AirPods Pro 3ra Gen', 'price': '899000.00'},
            {'name': 'iPad Air M2 11"', 'price': '3299000.00'},
            {'name': 'Samsung Galaxy S24 Ultra', 'price': '5199000.00'}
        ]

        for p in products:
            product, created = Product.objects.get_or_create(
                name=p['name'],
                defaults={
                    'slug': slugify(p['name']),
                    'description': f'Descripción de {p["name"]}',
                    'price': Decimal(p['price']),
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'✅ {product.name}')

        # Usuarios de ejemplo
        users = [
            {'email': 'cliente1@test.com', 'username': 'cliente1', 'first_name': 'María'},
            {'email': 'cliente2@test.com', 'username': 'cliente2', 'first_name': 'Carlos'}
        ]

        for u in users:
            user, created = User.objects.get_or_create(
                email=u['email'],
                defaults=u
            )
            if created:
                user.set_password('password123')
                user.save()
                self.stdout.write(f'✅ {user.email}')
        
        self.stdout.write(self.style.SUCCESS('✅ Completado!'))
