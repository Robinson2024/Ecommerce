"""
Base models y mixins para Tech Ecommerce.
"""

from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
import uuid


class TimeStampedModel(models.Model):
    """
    Modelo abstracto que proporciona campos de timestamp.
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de actualización')
    
    class Meta:
        abstract = True


class UUIDModel(models.Model):
    """
    Modelo abstracto que proporciona ID único UUID.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    """
    Modelo abstracto para soft delete.
    """
    is_deleted = models.BooleanField(default=False, verbose_name='Eliminado')
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de eliminación')
    
    def delete(self, using=None, keep_parents=False):
        """Override delete para soft delete."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(using=using)
    
    def hard_delete(self):
        """Eliminación real del objeto."""
        super().delete()
    
    def restore(self):
        """Restaurar objeto eliminado."""
        self.is_deleted = False
        self.deleted_at = None
        self.save()
    
    class Meta:
        abstract = True


class BaseModel(TimeStampedModel, SoftDeleteModel):
    """
    Modelo base que combina timestamp y soft delete.
    """
    class Meta:
        abstract = True


class SEOModel(models.Model):
    """
    Modelo abstracto para campos SEO.
    """
    meta_title = models.CharField(
        max_length=60, 
        blank=True, 
        verbose_name='Título SEO',
        help_text='Título para SEO (máx. 60 caracteres)'
    )
    meta_description = models.TextField(
        max_length=160, 
        blank=True, 
        verbose_name='Descripción SEO',
        help_text='Descripción para SEO (máx. 160 caracteres)'
    )
    meta_keywords = models.CharField(
        max_length=255, 
        blank=True, 
        verbose_name='Palabras clave SEO',
        help_text='Palabras clave separadas por comas'
    )
    
    class Meta:
        abstract = True


class PublishableModel(models.Model):
    """
    Modelo abstracto para contenido publicable.
    """
    is_published = models.BooleanField(default=True, verbose_name='Publicado')
    publish_date = models.DateTimeField(
        default=timezone.now, 
        verbose_name='Fecha de publicación'
    )
    
    def is_published_now(self):
        """Verifica si el objeto está publicado actualmente."""
        return self.is_published and self.publish_date <= timezone.now()
    
    class Meta:
        abstract = True


class SortableModel(models.Model):
    """
    Modelo abstracto para ordenamiento.
    """
    sort_order = models.PositiveIntegerField(
        default=0, 
        verbose_name='Orden',
        help_text='Orden de aparición (menor número = primero)'
    )
    
    class Meta:
        abstract = True
        ordering = ['sort_order']


class ActivatableModel(models.Model):
    """
    Modelo abstracto para activación/desactivación.
    """
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    
    class Meta:
        abstract = True


# Custom QuerySets
class ActiveQuerySet(models.QuerySet):
    """QuerySet para objetos activos."""
    
    def active(self):
        return self.filter(is_active=True)
    
    def inactive(self):
        return self.filter(is_active=False)


class PublishedQuerySet(models.QuerySet):
    """QuerySet para objetos publicados."""
    
    def published(self):
        return self.filter(
            is_published=True,
            publish_date__lte=timezone.now()
        )
    
    def unpublished(self):
        return self.filter(
            models.Q(is_published=False) |
            models.Q(publish_date__gt=timezone.now())
        )


class NotDeletedQuerySet(models.QuerySet):
    """QuerySet para objetos no eliminados."""
    
    def not_deleted(self):
        return self.filter(is_deleted=False)
    
    def deleted(self):
        return self.filter(is_deleted=True)


# Custom Managers
class BaseManager(models.Manager):
    """Manager base con funcionalidades comunes."""
    
    def get_queryset(self):
        return NotDeletedQuerySet(self.model, using=self._db).not_deleted()


class ActiveManager(models.Manager):
    """Manager para objetos activos."""
    
    def get_queryset(self):
        return ActiveQuerySet(self.model, using=self._db).active()


class PublishedManager(models.Manager):
    """Manager para objetos publicados."""
    
    def get_queryset(self):
        return PublishedQuerySet(self.model, using=self._db).published()
