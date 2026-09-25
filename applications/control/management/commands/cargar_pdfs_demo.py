from datetime import date, timedelta
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.core.files.storage import default_storage

from applications.control.models import Certificado, Empresa, Trabajador


class Command(BaseCommand):
    help = 'Carga los PDF de la carpeta pdf/ en los primeros datos demo.'

    def handle(self, *args, **options):
        origen = Path(settings.BASE_DIR) / 'pdf'
        archivos = {
            'induccion': origen / 'induccion_01.pdf',
            'aptitud': origen / 'aptitud_01.pdf',
            'altura': origen / 'curso_altura_01.pdf',
            'seguridad': origen / 'curso_seguridad_01.pdf',
            'sctr': origen / 'sctr_01.pdf',
        }
        faltantes = [str(path.name) for path in archivos.values() if not path.is_file()]
        if faltantes:
            raise CommandError(f'No se encontraron los archivos: {", ".join(faltantes)}')
        no_pdf = [str(path.name) for path in archivos.values() if path.suffix.lower() != '.pdf']
        if no_pdf:
            raise CommandError(f'Estos archivos no tienen extensión PDF: {", ".join(no_pdf)}')
        if any(path.stat().st_size > 2 * 1024 * 1024 for path in archivos.values()):
            raise CommandError('Todos los PDF deben pesar como máximo 2 MB.')

        empresa = Empresa.objects.order_by('pk').first()
        trabajador = Trabajador.objects.filter(empresa=empresa).order_by('pk').first() if empresa else None
        if not empresa or not trabajador:
            raise CommandError('Primero carga empresas y trabajadores demo.')

        hoy = date.today()
        with transaction.atomic():
            self._guardar_certificado(
                trabajador=trabajador,
                tipo=Certificado.INDUCCION,
                archivo=archivos['induccion'],
                fecha_emision=hoy - timedelta(days=30),
                fecha_vencimiento=hoy + timedelta(days=180),
            )
            self._materializar_rutas_del_fixture(origen)
            self._guardar_certificado(
                trabajador=trabajador,
                tipo=Certificado.APTITUD_MEDICA,
                archivo=archivos['aptitud'],
                fecha_emision=hoy - timedelta(days=30),
                fecha_vencimiento=hoy + timedelta(days=180),
            )
            self._guardar_certificado(
                trabajador=trabajador,
                tipo=Certificado.CURSOS,
                curso='ALTURA',
                archivo=archivos['altura'],
                fecha_emision=hoy - timedelta(days=30),
                fecha_vencimiento=hoy + timedelta(days=180),
            )
            self._guardar_certificado(
                trabajador=trabajador,
                tipo=Certificado.CURSOS,
                curso='CALIENTE',
                archivo=archivos['seguridad'],
                fecha_emision=hoy - timedelta(days=30),
                fecha_vencimiento=hoy + timedelta(days=180),
            )
            self._guardar_certificado(
                empresa=empresa,
                tipo=Certificado.SCTR,
                archivo=archivos['sctr'],
                fecha_emision=hoy - timedelta(days=30),
                fecha_vencimiento=hoy + timedelta(days=180),
            )

        self.stdout.write(self.style.SUCCESS(
            f'PDF demo cargados para {trabajador} y {empresa}. '
            'curso_seguridad_01.pdf se asignó al curso Caliente.'
        ))

    def _materializar_rutas_del_fixture(self, origen):
        fuentes = {
            'induccion': origen / 'induccion_01.pdf',
            'aptitud': origen / 'aptitud_01.pdf',
            'sctr': origen / 'sctr_01.pdf',
            'altura': origen / 'curso_altura_01.pdf',
            'curso': origen / 'curso_seguridad_01.pdf',
        }
        for certificado in Certificado.objects.filter(archivo__startswith='certificados/demo/'):
            nombre = certificado.archivo.name.rsplit('/', 1)[-1].lower()
            if nombre.startswith('induccion_'):
                fuente = fuentes['induccion']
            elif nombre.startswith('aptitud_'):
                fuente = fuentes['aptitud']
            elif nombre.startswith('sctr_'):
                fuente = fuentes['sctr']
            elif '_altura' in nombre:
                fuente = fuentes['altura']
            else:
                fuente = fuentes['curso']
            default_storage.delete(certificado.archivo.name)
            with fuente.open('rb') as contenido:
                default_storage.save(certificado.archivo.name, File(contenido))

    def _guardar_certificado(self, *, archivo, fecha_emision, fecha_vencimiento, tipo, trabajador=None, empresa=None, curso=None):
        filtros = {'tipo': tipo, 'trabajador': trabajador, 'empresa': empresa}
        if tipo == Certificado.CURSOS:
            filtros['curso'] = curso
        certificado = Certificado.objects.filter(**filtros).first() or Certificado(**filtros)
        certificado.fecha_emision = fecha_emision
        certificado.fecha_vencimiento = fecha_vencimiento
        with archivo.open('rb') as contenido:
            certificado.archivo.save(archivo.name, File(contenido), save=False)
        certificado.save()
