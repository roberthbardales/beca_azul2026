from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.core.files.storage import default_storage
from django.db import transaction
from django.utils import timezone

from applications.control.models import Certificado, CertificadoTipo, Empresa


class Command(BaseCommand):
    help = 'Instala los PDFs demo y prepara estados variados sin borrar empresas ni trabajadores.'

    def handle(self, *args, **options):
        origen = Path(settings.BASE_DIR) / 'pdf'
        fuentes = {
            'sctr': origen / 'sctr_01.pdf',
            'induccion': origen / 'induccion_01.pdf',
            'aptitud': origen / 'aptitud_01.pdf',
            'curso_caliente': origen / 'curso_seguridad_01.pdf',
            'curso_altura': origen / 'curso_altura_01.pdf',
        }
        faltantes = [path.name for path in fuentes.values() if not path.is_file()]
        if faltantes:
            raise CommandError(f'Faltan archivos fuente en pdf/: {", ".join(faltantes)}')

        certificados = list(
            Certificado.objects.filter(archivo__startswith='certificados/demo/')
            .select_related('empresa', 'trabajador')
            .order_by('pk')
        )
        if not certificados:
            raise CommandError(
                'No se encontraron certificados demo. Carga fixtures/seed.json antes de ejecutar este comando.'
            )

        hoy = timezone.localdate()
        for certificado in certificados:
            self._preparar(certificado, fuentes, hoy)

        empresas = {
            certificado.empresa_id: certificado.empresa
            for certificado in certificados
            if certificado.empresa_id
        }
        with transaction.atomic():
            for empresa in empresas.values():
                self._preparar_empresa(empresa)

        self.stdout.write(self.style.SUCCESS(
            f'{len(certificados)} certificados demo preparados en {len(empresas)} empresas.'
        ))

    def _preparar(self, certificado, fuentes, hoy):
        fuente = self._fuente(certificado, fuentes)
        nombre = certificado.archivo.name
        if not nombre:
            raise CommandError(f'El certificado demo {certificado.pk} no tiene una ruta de archivo.')

        # Las rutas demo son propiedad de este comando; reemplazarlas es seguro y repetible.
        if default_storage.exists(nombre):
            default_storage.delete(nombre)
        with fuente.open('rb') as contenido:
            nombre_guardado = default_storage.save(nombre, File(contenido))
        if nombre_guardado != nombre:
            default_storage.delete(nombre_guardado)
            raise CommandError(f'No se pudo escribir el PDF demo en la ruta esperada: {nombre}')

        if certificado.empresa_id:
            fecha_emision = hoy - timedelta(days=30)
            fecha_vencimiento = hoy + timedelta(days=180)
            validado = True
        else:
            variacion = certificado.pk % 5
            if variacion == 0:
                fecha_emision = hoy - timedelta(days=395)
                fecha_vencimiento = hoy - timedelta(days=30)
            else:
                fecha_emision = hoy - timedelta(days=30)
                fecha_vencimiento = hoy + timedelta(days=30 + variacion * 60)
            validado = certificado.pk % 3 != 0

        Certificado.objects.filter(pk=certificado.pk).update(
            fecha_emision=fecha_emision,
            fecha_vencimiento=fecha_vencimiento,
            validado=validado,
        )

    @staticmethod
    def _fuente(certificado, fuentes):
        if certificado.empresa_id:
            return fuentes['sctr']
        if certificado.tipo == CertificadoTipo.INDUCCION:
            return fuentes['induccion']
        if certificado.tipo == CertificadoTipo.APTITUD_MEDICA:
            return fuentes['aptitud']
        if certificado.tipo == CertificadoTipo.CURSOS and certificado.curso == 'ALTURA':
            return fuentes['curso_altura']
        return fuentes['curso_caliente']

    @staticmethod
    def _preparar_empresa(empresa):
        grupo = (empresa.pk - 21) % 4
        empresa.sctr_pension_aprobado = grupo in (0, 1)
        empresa.sctr_salud_aprobado = grupo in (0, 1, 2)
        empresa.homologacion = grupo == 0
        empresa.save(update_fields=(
            'sctr_pension_aprobado',
            'sctr_salud_aprobado',
            'homologacion',
        ))
