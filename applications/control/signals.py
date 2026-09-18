from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Certificado


@receiver(post_save, sender=Certificado)
def actualizar_estado_trabajador(sender, instance, **kwargs):
    if instance.trabajador_id:
        instance.trabajador.actualizar_estado()