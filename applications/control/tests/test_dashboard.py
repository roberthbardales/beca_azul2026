from datetime import date, timedelta

from django.test import TestCase
from django.urls import reverse

from applications.users.models import User

from ..models import Certificado, Empresa, Trabajador


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
            trabajador=self.trabajador,
            tipo=tipo,
            fecha_emision=date.today() - timedelta(days=30),
            fecha_vencimiento=vencimiento,
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
