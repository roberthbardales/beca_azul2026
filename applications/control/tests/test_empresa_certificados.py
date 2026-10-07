from datetime import date, timedelta
from tempfile import TemporaryDirectory

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.test import override_settings
from django.urls import reverse

from applications.users.models import User

from ..models import Certificado, Empresa, Trabajador


@override_settings(MEDIA_ROOT='/tmp/private-media-test')
class EmpresaCertificadoViewTests(TestCase):
    def setUp(self):
        self.media_root = TemporaryDirectory()
        self.addCleanup(self.media_root.cleanup)
        self.settings(MEDIA_ROOT=self.media_root.name)
        self.empresa = Empresa.objects.create(nombre='Empresa', ruc='20123456789', correo='empresa@example.com')
        self.certificado = Certificado.objects.create(
            empresa=self.empresa, tipo=Certificado.SCTR, fecha_emision=date.today(),
            fecha_vencimiento=date.today() + timedelta(days=30),
            archivo=SimpleUploadedFile('sctr.pdf', b'%PDF-1.4 test'),
        )
        self.url = reverse('app_control:empresa_certificado_ver', args=[self.certificado.pk])

    def crear_usuario(self, role, email):
        return User.objects.create_user(
            email=email, password='test-password', role=role,
            first_name='Usuario', last_name='Prueba',
            empresa=self.empresa if role == User.USUARIO_EMPRESA else None,
        )

    def test_beca_azul_puede_ver_pdf_de_empresa(self):
        self.client.force_login(self.crear_usuario(User.BECA_AZUL, 'beca@example.com'))
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertEqual(b''.join(response.streaming_content), b'%PDF-1.4 test')

    def test_url_fisica_tambien_exige_beca_azul(self):
        url = self.certificado.archivo.url
        self.client.force_login(self.crear_usuario(User.PLANTA, 'planta@example.com'))
        self.assertEqual(self.client.get(url).status_code, 403)

        self.client.force_login(self.crear_usuario(User.BECA_AZUL, 'beca-fisica@example.com'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(b''.join(response.streaming_content), b'%PDF-1.4 test')

    def test_otros_roles_no_pueden_ver_pdf_de_empresa(self):
        for role in (User.ADMINISTRADOR, User.PLANTA):
            with self.subTest(role=role):
                self.client.force_login(self.crear_usuario(role, f'{role}@example.com'))
                self.assertEqual(self.client.get(self.url).status_code, 403)

    def test_beca_azul_no_puede_ver_certificado_de_trabajador_en_esta_ruta(self):
        trabajador = Trabajador.objects.create(empresa=self.empresa, dni='12345678', nombres='Ana', apellidos='Prueba')
        certificado = Certificado.objects.create(
            trabajador=trabajador, tipo=Certificado.INDUCCION, fecha_emision=date.today(),
            fecha_vencimiento=date.today() + timedelta(days=30),
            archivo=SimpleUploadedFile('induccion.pdf', b'%PDF-1.4 test'),
        )
        self.client.force_login(self.crear_usuario(User.BECA_AZUL, 'beca2@example.com'))
        response = self.client.get(reverse('app_control:empresa_certificado_ver', args=[certificado.pk]))
        self.assertEqual(response.status_code, 404)

    def test_url_fisica_permite_ver_certificado_de_trabajador_de_la_empresa(self):
        trabajador = Trabajador.objects.create(empresa=self.empresa, dni='87654321', nombres='Luis', apellidos='Prueba')
        certificado = Certificado.objects.create(
            trabajador=trabajador, tipo=Certificado.CURSOS, curso='CALIENTE',
            fecha_emision=date.today(), fecha_vencimiento=date.today() + timedelta(days=30),
            archivo=SimpleUploadedFile('curso.pdf', b'%PDF-1.4 test'),
        )
        self.client.force_login(self.crear_usuario(User.BECA_AZUL, 'beca-worker@example.com'))

        response = self.client.get(certificado.archivo.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(b''.join(response.streaming_content), b'%PDF-1.4 test')

    def test_certificado_sin_archivo_fisico_devuelve_404(self):
        self.certificado.archivo.storage.delete(self.certificado.archivo.name)
        self.client.force_login(self.crear_usuario(User.BECA_AZUL, 'beca-missing@example.com'))

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 404)
