from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import Certificado


@receiver(post_delete, sender=Certificado)
def eliminar_archivo_certificado(sender, instance, **kwargs):
    if instance.archivo.name:
        instance._eliminar_archivo(instance.archivo.name)
