# filepath: apps/core/signals.py
"""
Signals para la app core
"""
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(post_save, sender=User)
def user_post_save_handler(sender, instance, created, **kwargs):
    """
    Signal que se ejecuta después de guardar un usuario
    """
    if created:
        # Acciones a realizar cuando se crea un nuevo usuario
        pass


@receiver(pre_delete, sender=User)
def user_pre_delete_handler(sender, instance, **kwargs):
    """
    Signal que se ejecuta antes de eliminar un usuario
    """
    # Acciones a realizar antes de eliminar un usuario
    pass
