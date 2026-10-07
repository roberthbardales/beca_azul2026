from datetime import date, timedelta

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from applications.users.models import User

from ..models import Certificado, CursoTipo, Empresa, Trabajador


class DashboardViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='admin@example.com',
            password='test-password',
            first_name='Admin',
            last_name='Test',
            role=User.ADMINISTRADOR,
        )
        self.client.force_login(self.user)
        self.empresa = Empresa.objects.create(nombre='Empresa principal', ruc='20123456789', correo='principal@example.com')
        self.trabajador = Trabajador.objects.create(
            empresa=self.empresa,
            dni='12345678',
            nombres='Ana',
            apellidos='Prueba',
        )

    def crear_certificado(self, tipo, vencimiento):
        return Certificado.objects.create(
            empresa=self.empresa if tipo == Certificado.SCTR else None,
            trabajador=None if tipo == Certificado.SCTR else self.trabajador,
            tipo=tipo,
            curso=CursoTipo.ALTURA if tipo == Certificado.CURSOS else None,
            fecha_emision=date.today() - timedelta(days=30),
            fecha_vencimiento=vencimiento,
            archivo=SimpleUploadedFile('certificado.pdf', b'%PDF-1.4 test'),
        )

    def test_clasifica_todos_los_estados_de_certificados(self):
        hoy = date.today()
        self.crear_certificado(Certificado.SCTR, hoy + timedelta(days=31))
        self.crear_certificado(Certificado.INDUCCION, hoy + timedelta(days=10))
        self.crear_certificado(Certificado.APTITUD_MEDICA, hoy - timedelta(days=1))
        self.crear_certificado(Certificado.CURSOS, hoy + timedelta(days=20))

        response = self.client.get(reverse('app_control:dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['dashboard_charts']['cumplimiento'], [1, 2, 1])
        self.assertEqual(response.context['certificados_sin_vencimiento'], 0)

    def test_usuario_garita_no_puede_ver_reportes(self):
        self.user.role = User.GARITA
        self.user.save(update_fields=['role'])

        response = self.client.get(reverse('app_control:reportes'))

        self.assertEqual(response.status_code, 403)

    def test_usuario_garita_no_ve_reportes_en_el_sidebar(self):
        self.user.role = User.GARITA
        self.user.save(update_fields=['role'])

        response = self.client.get(reverse('app_control:trabajador_buscar'))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Reportes')

    def test_superusuario_puede_ver_detalle_desde_el_buscador(self):
        self.user.is_superuser = True
        self.user.save(update_fields=['is_superuser'])

        response = self.client.get(
            reverse('app_control:trabajador_buscar'),
            {'q': self.trabajador.dni},
        )

        self.assertContains(response, 'Ver detalle completo')
        self.assertContains(
            response,
            reverse('app_control:trabajador_detalle', args=[self.trabajador.pk]),
        )

    def test_buscador_muestra_todas_las_coincidencias(self):
        segundo = Trabajador.objects.create(
            empresa=self.empresa,
            dni='87654321',
            nombres='Ana María',
            apellidos='Prueba',
        )

        response = self.client.get(
            reverse('app_control:trabajador_buscar'),
            {'q': 'Prueba'},
        )

        self.assertEqual(response.context['resultados'], 2)
        self.assertContains(response, self.trabajador.dni)
        self.assertContains(response, segundo.dni)

    def test_buscador_ignora_tildes_y_acepta_nombre_completo(self):
        self.trabajador.nombres = 'Rosa María'
        self.trabajador.apellidos = 'Torres Cárdenas'
        self.trabajador.save(update_fields=['nombres', 'apellidos'])

        for termino in ('cardenas', 'rosa maria', 'Rosa María Torres Cárdenas'):
            response = self.client.get(
                reverse('app_control:trabajador_buscar'),
                {'q': termino},
            )
            self.assertEqual(response.context['resultados'], 1, termino)
            self.assertEqual(response.context['trabajador'], self.trabajador)

    def test_lista_busca_nombre_completo_por_palabras_y_dni_exacto(self):
        self.trabajador.nombres = 'Peter'
        self.trabajador.apellidos = 'Parker'
        self.trabajador.save(update_fields=['nombres', 'apellidos'])

        response = self.client.get(
            reverse('app_control:trabajador_lista'),
            {'q': 'parker peter'},
        )
        self.assertContains(response, self.trabajador.dni)

        response = self.client.get(
            reverse('app_control:trabajador_lista'),
            {'q': self.trabajador.dni[:-1]},
        )
        self.assertNotContains(response, self.trabajador.dni)

    def test_grafica_agrupa_trabajadores_por_estado_e_incluye_inactivos(self):
        self.trabajador.activo = False
        self.trabajador.habilitado = False
        self.trabajador.save(update_fields=['activo', 'habilitado'])

        response = self.client.get(reverse('app_control:dashboard'))
        estados = response.context['dashboard_charts']['trabajadores_empresa']

        self.assertEqual(estados['labels'], ['Empresa principal'])
        self.assertEqual(estados['habilitados'], [0])
        self.assertEqual(estados['inhabilitados'], [1])

    def test_grafica_agrupa_trabajadores_activos_por_empresa_y_estado(self):
        otra_empresa = Empresa.objects.create(nombre='Empresa secundaria', ruc='20987654321', correo='secundaria@example.com')
        Trabajador.objects.create(
            empresa=self.empresa, dni='22345678', nombres='Luis', apellidos='Prueba', habilitado=False,
        )
        Trabajador.objects.create(
            empresa=otra_empresa, dni='32345678', nombres='Marta', apellidos='Prueba', habilitado=False,
        )
        Trabajador.objects.create(
            empresa=otra_empresa, dni='42345678', nombres='Rosa', apellidos='Prueba', activo=False,
        )

        response = self.client.get(reverse('app_control:dashboard'))
        estados = response.context['dashboard_charts']['trabajadores_empresa']

        self.assertEqual(estados['labels'], ['Empresa principal', 'Empresa secundaria'])
        self.assertEqual(estados['habilitados'], [0, 0])
        self.assertEqual(estados['inhabilitados'], [2, 2])

    def test_dashboard_cuenta_trabajadores_no_habilitados(self):
        self.trabajador.habilitado = False
        self.trabajador.save(update_fields=['habilitado'])

        response = self.client.get(reverse('app_control:dashboard'))

        self.assertEqual(response.context['trabajadores_deshabilitados'], 1)

    def test_beca_azul_puede_alternar_estado_habilitado(self):
        user = User.objects.create_user(
            email='beca@example.com',
            password='test-password',
            first_name='Beca',
            last_name='Azul',
            role=User.BECA_AZUL,
        )
        self.client.force_login(user)

        response = self.client.post(
            reverse('app_control:trabajador_habilitado_toggle', args=[self.trabajador.pk]),
            {},
        )

        self.assertRedirects(response, reverse('app_control:trabajador_detalle', args=[self.trabajador.pk]))
        self.trabajador.refresh_from_db()
        self.assertFalse(self.trabajador.habilitado)

    def test_usuario_no_beca_azul_no_puede_alternar_estado_habilitado(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('app_control:trabajador_habilitado_toggle', args=[self.trabajador.pk]),
        )

        self.assertEqual(response.status_code, 403)
        self.trabajador.refresh_from_db()
        self.assertTrue(self.trabajador.habilitado)


class TrabajadorEmpresaCreateViewTests(TestCase):
    def test_usuario_empresa_puede_crear_trabajador(self):
        empresa = Empresa.objects.create(nombre='Empresa', ruc='20123456789', correo='empresa@example.com')
        user = User.objects.create_user(
            email='empresa@example.com',
            password='test-password',
            first_name='Usuario',
            last_name='Empresa',
            role=User.USUARIO_EMPRESA,
            empresa=empresa,
        )
        self.client.force_login(user)
        data = {
            'tipo_documento': Trabajador.DNI,
            'dni': '12345678',
            'nombres': 'Ana',
            'apellidos': 'Prueba',
            'cargo': 'Operadora',
            'induccion_fecha_emision': date.today().isoformat(),
            'induccion_fecha_vencimiento': (date.today() + timedelta(days=30)).isoformat(),
            'aptitud_medica_fecha_emision': date.today().isoformat(),
            'aptitud_medica_fecha_vencimiento': (date.today() + timedelta(days=30)).isoformat(),
            'certificados-TOTAL_FORMS': '6',
            'certificados-INITIAL_FORMS': '0',
            'certificados-MIN_NUM_FORMS': '0',
            'certificados-MAX_NUM_FORMS': '1000',
        }
        for index, curso in enumerate((
            CursoTipo.CALIENTE,
            CursoTipo.ALTURA,
            CursoTipo.ESPACIO_CONFINADO,
            CursoTipo.ELECTRICO,
            CursoTipo.EXCAVACION,
            CursoTipo.IZAJE,
        )):
            data[f'certificados-{index}-tipo'] = Certificado.CURSOS
            data[f'certificados-{index}-curso'] = curso
        files = {
            'induccion_archivo': SimpleUploadedFile('induccion.pdf', b'%PDF-1.4 test'),
            'aptitud_medica_archivo': SimpleUploadedFile('aptitud.pdf', b'%PDF-1.4 test'),
        }

        response = self.client.post(
            reverse('app_control:trabajador_empresa_crear'),
            {**data, **files},
        )

        if response.status_code == 200:
            self.fail(
                f'Formulario inválido: {response.context["form"].errors}; '
                f'formset: {response.context["certificado_formset"].errors}'
            )
        self.assertRedirects(response, reverse('app_control:trabajador_lista'))
        trabajador = Trabajador.objects.get(dni='12345678')
        self.assertEqual(trabajador.empresa, empresa)
        self.assertEqual(trabajador.certificados.count(), 2)
