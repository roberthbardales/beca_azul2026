from datetime import date, timedelta

from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from applications.users.models import User

from ..models import Certificado, Empresa


class HomologacionToggleViewTests(TestCase):
    def setUp(self):
        self.empresa = Empresa.objects.create(
            nombre='Empresa', ruc='20123456789', correo='empresa@example.com'
        )
        self.url = reverse(
            'app_control:empresa_homologacion_toggle', args=[self.empresa.pk]
        )

    def crear_usuario(self, role):
        return User.objects.create_user(
            email=f'{role}@example.com',
            password='test-password',
            first_name='Usuario',
            last_name='Prueba',
            role=role,
            empresa=self.empresa if role == User.USUARIO_EMPRESA else None,
        )

    def test_beca_azul_aprueba_y_desaprueba_homologacion(self):
        for tipo, nombre in (
            (Certificado.SCTR_PENSION, 'sctr-pension.pdf'),
            (Certificado.SCTR_SALUD, 'sctr-salud.pdf'),
            (Certificado.HOMOLOGACION, 'homologacion.pdf'),
        ):
            Certificado.objects.create(
                empresa=self.empresa,
                tipo=tipo,
                fecha_emision=date.today(),
                fecha_vencimiento=date.today() + timedelta(days=30),
                archivo=SimpleUploadedFile(nombre, b'%PDF-1.4 test'),
            )
        self.client.force_login(self.crear_usuario(User.BECA_AZUL))

        response = self.client.post(self.url)
        self.assertRedirects(response, reverse('app_control:empresa_detalle', args=[self.empresa.pk]))
        self.empresa.refresh_from_db()
        self.assertTrue(self.empresa.homologacion)

        self.client.post(self.url)
        self.empresa.refresh_from_db()
        self.assertFalse(self.empresa.homologacion)

    def test_otros_roles_no_pueden_cambiar_homologacion(self):
        for role in (User.ADMINISTRADOR, User.PLANTA, User.USUARIO_EMPRESA):
            with self.subTest(role=role):
                self.client.force_login(self.crear_usuario(role))
                response = self.client.post(self.url)
                self.assertEqual(response.status_code, 403)
                self.empresa.refresh_from_db()
                self.assertFalse(self.empresa.homologacion)

    def test_no_puede_aprobar_sin_sctr_y_homologacion(self):
        self.client.force_login(self.crear_usuario(User.BECA_AZUL))

        response = self.client.post(self.url)

        self.assertRedirects(response, reverse('app_control:empresa_detalle', args=[self.empresa.pk]))
        self.empresa.refresh_from_db()
        self.assertFalse(self.empresa.homologacion)
        self.assertEqual(len(list(response.wsgi_request._messages)), 3)

    def test_no_puede_aprobar_si_falta_un_certificado(self):
        Certificado.objects.create(
            empresa=self.empresa,
            tipo=Certificado.SCTR,
            fecha_emision=date.today(),
            fecha_vencimiento=date.today() + timedelta(days=30),
            archivo=SimpleUploadedFile('sctr.pdf', b'%PDF-1.4 test'),
        )
        self.client.force_login(self.crear_usuario(User.BECA_AZUL))

        response = self.client.post(self.url)

        self.empresa.refresh_from_db()
        self.assertFalse(self.empresa.homologacion)
        self.assertEqual(len(list(response.wsgi_request._messages)), 2)

    def test_no_puede_aprobar_con_certificados_vencidos(self):
        for tipo, nombre in (
            (Certificado.SCTR_PENSION, 'sctr-pension-vencido.pdf'),
            (Certificado.SCTR_SALUD, 'sctr-salud-vencido.pdf'),
            (Certificado.HOMOLOGACION, 'homologacion-vencida.pdf'),
        ):
            Certificado.objects.create(
                empresa=self.empresa,
                tipo=tipo,
                fecha_emision=date.today() - timedelta(days=60),
                fecha_vencimiento=date.today() - timedelta(days=1),
                archivo=SimpleUploadedFile(nombre, b'%PDF-1.4 test'),
            )
        self.client.force_login(self.crear_usuario(User.BECA_AZUL))

        response = self.client.post(self.url)

        self.empresa.refresh_from_db()
        self.assertFalse(self.empresa.homologacion)
        self.assertEqual(len(list(response.wsgi_request._messages)), 3)

    def test_puede_desaprobar_sin_certificados(self):
        self.empresa.homologacion = True
        self.empresa.save(update_fields=['homologacion'])
        self.client.force_login(self.crear_usuario(User.BECA_AZUL))

        self.client.post(self.url)

        self.empresa.refresh_from_db()
        self.assertFalse(self.empresa.homologacion)

    def test_detalle_muestra_pendiente_y_bloquea_aprobacion_si_falta_archivo(self):
        sctr = Certificado.objects.create(
            empresa=self.empresa,
            tipo=Certificado.SCTR,
            fecha_emision=date.today(),
            fecha_vencimiento=date.today() + timedelta(days=30),
            archivo=SimpleUploadedFile('sctr.pdf', b'%PDF-1.4 test'),
        )
        Certificado.objects.create(
            empresa=self.empresa,
            tipo=Certificado.SCTR_SALUD,
            fecha_emision=date.today(),
            fecha_vencimiento=date.today() + timedelta(days=30),
            archivo=SimpleUploadedFile('sctr-salud.pdf', b'%PDF-1.4 test'),
        )
        homologacion = Certificado.objects.create(
            empresa=self.empresa,
            tipo=Certificado.HOMOLOGACION,
            fecha_emision=date.today(),
            fecha_vencimiento=date.today() + timedelta(days=30),
            archivo=SimpleUploadedFile('homologacion.pdf', b'%PDF-1.4 test'),
        )
        homologacion.archivo.storage.delete(homologacion.archivo.name)
        self.client.force_login(self.crear_usuario(User.BECA_AZUL))

        response = self.client.get(reverse('app_control:empresa_detalle', args=[self.empresa.pk]))

        self.assertTrue(response.context['sctr_pension_valido'])
        self.assertTrue(response.context['sctr_salud_valido'])
        self.assertFalse(response.context['homologacion_valida'])
        self.assertContains(response, 'Pendiente de carga')
        self.assertContains(response, 'disabled')

    def test_detalle_habilita_aprobacion_con_ambos_archivos(self):
        for tipo, nombre in (
            (Certificado.SCTR_PENSION, 'sctr-pension.pdf'),
            (Certificado.SCTR_SALUD, 'sctr-salud.pdf'),
            (Certificado.HOMOLOGACION, 'homologacion.pdf'),
        ):
            Certificado.objects.create(
                empresa=self.empresa,
                tipo=tipo,
                fecha_emision=date.today(),
                fecha_vencimiento=date.today() + timedelta(days=30),
                archivo=SimpleUploadedFile(nombre, b'%PDF-1.4 test'),
            )
        self.client.force_login(self.crear_usuario(User.BECA_AZUL))

        response = self.client.get(reverse('app_control:empresa_detalle', args=[self.empresa.pk]))

        self.assertTrue(response.context['sctr_pension_valido'])
        self.assertTrue(response.context['sctr_salud_valido'])
        self.assertTrue(response.context['homologacion_valida'])
        self.assertNotContains(response, 'Pendiente de carga')

    def test_detalle_invalida_homologacion_aprobada_si_el_certificado_vence(self):
        Certificado.objects.create(
            empresa=self.empresa,
            tipo=Certificado.HOMOLOGACION,
            fecha_emision=date.today() - timedelta(days=60),
            fecha_vencimiento=date.today() - timedelta(days=1),
            archivo=SimpleUploadedFile('homologacion-vencida.pdf', b'%PDF-1.4 test'),
        )
        self.empresa.homologacion = True
        self.empresa.save(update_fields=['homologacion'])
        self.client.force_login(self.crear_usuario(User.BECA_AZUL))

        response = self.client.get(reverse('app_control:empresa_detalle', args=[self.empresa.pk]))

        self.empresa.refresh_from_db()
        self.assertFalse(self.empresa.homologacion)
        self.assertFalse(response.context['empresa'].homologacion)
