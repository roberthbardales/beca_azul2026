from datetime import date, timedelta
from tempfile import TemporaryDirectory

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from ..models import Certificado, CursoTipo, Empresa, Trabajador, certificado_upload_path


class CertificadoModelTests(TestCase):
    def setUp(self):
        self.empresa = Empresa.objects.create(nombre='Empresa', ruc='20123456789')
        self.trabajador = Trabajador.objects.create(
            empresa=self.empresa,
            dni='12345678',
            nombres='Ana',
            apellidos='Prueba',
        )

    def test_clean_rechaza_certificado_de_cursos_sin_curso(self):
        certificado = Certificado(
            trabajador=self.trabajador,
            tipo=Certificado.CURSOS,
            fecha_emision=date.today(),
            fecha_vencimiento=date.today() + timedelta(days=1),
        )

        with self.assertRaises(ValidationError):
            certificado.full_clean()

    def test_eliminar_trabajador_elimina_archivo_de_certificado(self):
        with TemporaryDirectory() as media_root, self.settings(MEDIA_ROOT=media_root):
            certificado = Certificado.objects.create(
                trabajador=self.trabajador,
                tipo=Certificado.CURSOS,
                curso=CursoTipo.ALTURA,
                fecha_emision=date.today(),
                fecha_vencimiento=date.today() + timedelta(days=1),
                archivo=SimpleUploadedFile('certificado.pdf', b'contenido'),
            )
            nombre = certificado.archivo.name

            self.assertTrue(certificado.archivo.storage.exists(nombre))
            self.trabajador.delete()
            self.assertFalse(certificado.archivo.storage.exists(nombre))

    def test_upload_path_rechaza_certificado_sin_propietario(self):
        certificado = Certificado(
            tipo=Certificado.SCTR,
            fecha_emision=date.today(),
            fecha_vencimiento=date.today() + timedelta(days=1),
        )

        with self.assertRaises(ValueError):
            certificado_upload_path(certificado, 'certificado.pdf')


class TrabajadorSignalTests(TestCase):
    def test_cambiar_empresa_actualiza_la_homologacion_de_ambas(self):
        empresa_anterior = Empresa.objects.create(nombre='Anterior', ruc='20123456789')
        empresa_nueva = Empresa.objects.create(nombre='Nueva', ruc='20987654321')
        trabajador = Trabajador.objects.create(
            empresa=empresa_anterior,
            dni='12345678',
            nombres='Ana',
            apellidos='Prueba',
            habilitado=True,
        )
        empresa_anterior.refresh_from_db()
        self.assertTrue(empresa_anterior.homologado)

        trabajador.empresa = empresa_nueva
        trabajador.save()

        empresa_anterior.refresh_from_db()
        empresa_nueva.refresh_from_db()
        self.assertFalse(empresa_anterior.homologado)
        self.assertTrue(empresa_nueva.homologado)
