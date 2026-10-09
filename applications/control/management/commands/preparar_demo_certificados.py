from datetime import date, timedelta
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction
from django.core.files.storage import default_storage

from applications.control.models import Certificado


class Command(BaseCommand):
    help = 'Prepara certificados demo variados sin borrar empresas ni trabajadores.'

    def handle(self, *args, **options):
        origen = Path(settings.BASE_DIR) / 'pdf'
        fuentes = {
            'sctr': origen / 'sctr_01.pdf',
            'induccion': origen / 'induccion_01.pdf',
            'aptitud': origen / 'aptitud_01.pdf',
            'curso': origen / 'curso_seguridad_01.pdf',
        }
        faltantes = [path.name for path in fuentes.values() if not path.is_file()]
        if faltantes:
            self.stderr.write(f'Faltan archivos en pdf/: {", ".join(faltantes)}')
            return

        certificados = list(
            Certificado.objects.filter(archivo__startswith='certificados/demo/')
            .select_related('empresa', 'trabajador')
            .order_by('pk')
        )
        with transaction.atomic():
            for certificado in certificados:
                self._preparar(certificado, fuentes)

        self.stdout.write(self.style.SUCCESS(
            f'{len(certificados)} certificados demo preparados correctamente.'
        ))

    def _preparar(self, certificado, fuentes):
        empresa_id = certificado.empresa_id or certificado.trabajador.empresa_id
        variacion = empresa_id % 4
        fecha_emision = date(2026, 1 + variacion, 5 + variacion * 3)
        vencimientos = (
            date(2026, 3, 15),
            date(2026, 7, 20),
            date(2026, 11, 30),
            date(2027, 2, 10),
        )
        certificado.fecha_emision = fecha_emision
        certificado.fecha_vencimiento = vencimientos[variacion]
        if certificado.trabajador_id:
            certificado.validado = certificado.pk % 3 != 0

        # Deja algunos registros pendientes para probar el flujo sin archivo.
        if certificado.pk % 5 == 0:
            Certificado.objects.filter(pk=certificado.pk).update(
                archivo='',
                fecha_emision=certificado.fecha_emision,
                fecha_vencimiento=certificado.fecha_vencimiento,
                validado=certificado.validado,
            )
            return

        if certificado.empresa_id:
            fuente = fuentes['sctr']
        elif certificado.tipo == Certificado.APTITUD_MEDICA:
            fuente = fuentes['aptitud']
        elif certificado.tipo == Certificado.INDUCCION:
            fuente = fuentes['induccion']
        else:
            fuente = fuentes['curso']

        nombre = certificado.archivo.name
        default_storage.delete(nombre)
        with fuente.open('rb') as contenido:
            default_storage.save(nombre, File(contenido))
        certificado.save(update_fields=['fecha_emision', 'fecha_vencimiento', 'validado'])
