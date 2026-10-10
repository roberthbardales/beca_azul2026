from datetime import date, timedelta
from tempfile import TemporaryDirectory

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from applications.users.models import User

from ..models import Certificado, CursoObligatorio, CursoTipo, Empresa, Trabajador


class CertificadoEmpresaUpdateValidationTests(TestCase):
    def setUp(self):
        self.media_root = TemporaryDirectory()
        self.addCleanup(self.media_root.cleanup)
        self.settings(MEDIA_ROOT=self.media_root.name)
        self.empresa = Empresa.objects.create(
            nombre='Empresa', ruc='20123456789', correo='empresa@example.com'
        )
        self.trabajador = Trabajador.objects.create(
            empresa=self.empresa,
            dni='12345678',
            nombres='Ana',
            apellidos='Prueba',
        )
        self.usuario = User.objects.create_user(
            email='empresa@example.com',
            password='test-password',
            role=User.USUARIO_EMPRESA,
            empresa=self.empresa,
        )
        self.certificado = Certificado.objects.create(
            trabajador=self.trabajador,
            tipo=Certificado.INDUCCION,
            fecha_emision=date.today() - timedelta(days=10),
            fecha_vencimiento=date.today() + timedelta(days=20),
            archivo=SimpleUploadedFile('induccion_original.pdf', b'%PDF-1.4 original'),
            validado=True,
        )
        self.url = reverse('app_control:certificado_empresa_editar', args=[self.certificado.pk])
        self.client.force_login(self.usuario)

    def datos(self, fecha_emision=None, fecha_vencimiento=None):
        return {
            'tipo': Certificado.INDUCCION,
            'curso': '',
            'fecha_emision': (fecha_emision or self.certificado.fecha_emision).isoformat(),
            'fecha_vencimiento': (fecha_vencimiento or self.certificado.fecha_vencimiento).isoformat(),
        }

    def test_reemplazar_pdf_reinicia_validacion(self):
        archivo_original = self.certificado.archivo.name
        response = self.client.post(
            self.url,
            {
                **self.datos(),
                'archivo': SimpleUploadedFile('induccion_nuevo.pdf', b'%PDF-1.4 nuevo'),
            },
        )

        self.assertRedirects(response, reverse('app_control:trabajador_detalle', args=[self.trabajador.pk]))
        self.certificado.refresh_from_db()
        self.assertFalse(self.certificado.validado)
        self.assertNotEqual(self.certificado.archivo.name, archivo_original)
        with self.certificado.archivo.open('rb') as archivo:
            self.assertEqual(archivo.read(), b'%PDF-1.4 nuevo')

    def test_cambiar_fechas_sin_reemplazar_pdf_reinicia_validacion(self):
        response = self.client.post(
            self.url,
            self.datos(
                fecha_emision=date.today() - timedelta(days=5),
                fecha_vencimiento=date.today() + timedelta(days=40),
            ),
        )

        self.assertRedirects(response, reverse('app_control:trabajador_detalle', args=[self.trabajador.pk]))
        self.certificado.refresh_from_db()
        self.assertFalse(self.certificado.validado)
        self.assertEqual(self.certificado.fecha_vencimiento, date.today() + timedelta(days=40))

    def test_guardar_sin_cambios_conserva_validacion(self):
        response = self.client.post(self.url, self.datos())

        self.assertRedirects(response, reverse('app_control:trabajador_detalle', args=[self.trabajador.pk]))
        self.certificado.refresh_from_db()
        self.assertTrue(self.certificado.validado)

    def test_reemplazar_pdf_de_curso_reinicia_validacion(self):
        CursoObligatorio.objects.create(trabajador=self.trabajador, curso=CursoTipo.ALTURA)
        certificado_curso = Certificado.objects.create(
            trabajador=self.trabajador,
            tipo=Certificado.CURSOS,
            curso=CursoTipo.ALTURA,
            fecha_emision=date.today() - timedelta(days=10),
            fecha_vencimiento=date.today() + timedelta(days=20),
            archivo=SimpleUploadedFile('altura_original.pdf', b'%PDF-1.4 original'),
            validado=True,
        )
        url = reverse('app_control:certificado_empresa_editar', args=[certificado_curso.pk])

        response = self.client.post(
            url,
            {
                'tipo': Certificado.CURSOS,
                'curso': CursoTipo.ALTURA,
                'fecha_emision': certificado_curso.fecha_emision.isoformat(),
                'fecha_vencimiento': certificado_curso.fecha_vencimiento.isoformat(),
                'archivo': SimpleUploadedFile('altura_nuevo.pdf', b'%PDF-1.4 nuevo'),
            },
        )

        self.assertRedirects(response, reverse('app_control:trabajador_detalle', args=[self.trabajador.pk]))
        certificado_curso.refresh_from_db()
        self.assertFalse(certificado_curso.validado)
