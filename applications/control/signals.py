from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from .models import Certificado, Empresa, Trabajador


@receiver(post_delete, sender=Trabajador)
def actualizar_homologado_empresa(sender, instance, **kwargs):
    if instance.empresa_id:
        instance.empresa.actualizar_homologado()


@receiver(pre_save, sender=Trabajador)
def guardar_estado_trabajador(sender, instance, **kwargs):
    if instance.pk:
        instance._estado_anterior = sender.objects.filter(pk=instance.pk).values_list(
            'empresa_id', 'habilitado', 'activo'
        ).first()


@receiver(post_save, sender=Trabajador)
def actualizar_homologado_al_guardar(sender, instance, created, update_fields=None, **kwargs):
    campos_relevantes = update_fields is None or {
        'empresa_id', 'habilitado', 'activo'
    }.intersection(update_fields)
    estado_anterior = getattr(instance, '_estado_anterior', None)
    estado_actual = (instance.empresa_id, instance.habilitado, instance.activo)
    if not campos_relevantes or (not created and estado_anterior == estado_actual):
        return

    empresas_ids = {instance.empresa_id}
    if estado_anterior:
        empresas_ids.add(estado_anterior[0])
    for empresa_id in empresas_ids - {None}:
        Empresa.objects.get(pk=empresa_id).actualizar_homologado()


@receiver(post_delete, sender=Certificado)
def eliminar_archivo_certificado(sender, instance, **kwargs):
    if instance.archivo.name:
        instance._eliminar_archivo(instance.archivo.name)
