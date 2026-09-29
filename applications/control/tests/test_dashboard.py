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
        self.empresa = Empresa.objects.create(nombre='Empresa principal', ruc='20123456789')
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

    def test_agrupa_empresas_fuera_del_top_diez(self):
        for index in range(11):
            Empresa.objects.create(nombre=f'Empresa {index:02d}', ruc=f'20{index:09d}')

        response = self.client.get(reverse('app_control:dashboard'))
        empresas = response.context['dashboard_charts']['empresas']

        self.assertEqual(len(empresas['labels']), 10)
        self.assertEqual(empresas['labels'][0], 'Empresa principal')
        self.assertNotIn('Otros', empresas['labels'])

    def test_agrupa_trabajadores_de_empresas_restantes(self):
        for index in range(10):
            empresa = Empresa.objects.create(nombre=f'Empresa {index:02d}', ruc=f'20{index:09d}')
            Trabajador.objects.create(
                empresa=empresa,
                dni=f'{index:08d}',
                nombres='Trabajador',
                apellidos=str(index),
            )
        empresa_extra = Empresa.objects.create(nombre='Empresa extra', ruc='20999999999')
        Trabajador.objects.create(
            empresa=empresa_extra,
            dni='99999999',
            nombres='Trabajador',
            apellidos='Extra',
        )

        response = self.client.get(reverse('app_control:dashboard'))
        empresas = response.context['dashboard_charts']['empresas']

        self.assertEqual(empresas['labels'][-1], 'Otros')
        self.assertEqual(empresas['data'][-1], 2)


class TrabajadorEmpresaCreateViewTests(TestCase):
    def test_usuario_empresa_puede_crear_trabajador(self):
        empresa = Empresa.objects.create(nombre='Empresa', ruc='20123456789')
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
