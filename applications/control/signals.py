from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Trabajador


@receiver([post_save, post_delete], sender=Trabajador)
def actualizar_habilitado_empresa(sender, instance, **kwargs):
    if instance.empresa_id:
        instance.empresa.actualizar_habilitado()