from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from .models import Certificado, Trabajador


@receiver(post_delete, sender=Trabajador)
def actualizar_homologado_empresa(sender, instance, **kwargs):
    if instance.empresa_id:
        instance.empresa.actualizar_homologado()


@receiver(pre_save, sender=Trabajador)
def guardar_estado_trabajador(sender, instance, **kwargs):
    if instance.pk:
        instance._estado_anterior = sender.objects.filter(pk=instance.pk).values_list(
            'habilitado', 'activo'
        ).first()


@receiver(post_save, sender=Trabajador)
def actualizar_homologado_al_guardar(sender, instance, created, update_fields=None, **kwargs):
    campos_relevantes = update_fields is None or {'habilitado', 'activo'}.intersection(update_fields)
    cambio_estado = created or getattr(instance, '_estado_anterior', None) != (
        instance.habilitado,
        instance.activo,
    )
    if instance.empresa_id and campos_relevantes and cambio_estado:
        instance.empresa.actualizar_homologado()


@receiver(post_delete, sender=Certificado)
def eliminar_archivo_certificado(sender, instance, **kwargs):
    if instance.archivo.name:
        instance._eliminar_archivo(instance.archivo.name)
