from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Perfil


@receiver(post_save, sender=User)
def crear_perfil(sender, instance, created, **kwargs):
    """Crea un Perfil automáticamente cada vez que se crea un User."""
    if created:
        Perfil.objects.create(usuario=instance)


@receiver(post_save, sender=User)
def guardar_perfil(sender, instance, **kwargs):
    """Guarda el Perfil cuando se guarda el User."""
    if hasattr(instance, 'perfil'):
        instance.perfil.save()
