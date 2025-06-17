from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.accounts'
    verbose_name = 'Cuentas de Usuario'
    
    def ready(self):
        """Importar signals cuando la app esté lista."""
        try:
            import apps.accounts.signals  # noqa
        except ImportError:
            pass
