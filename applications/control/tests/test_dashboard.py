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

    def test_dashboard_cuenta_empresas_homologadas_y_no_homologadas(self):
        Empresa.objects.create(
            nombre='Empresa desactivada',
            ruc='20987654320',
            correo='desactivada@example.com',
            activo=False,
            homologacion=True,
        )
        Empresa.objects.create(
            nombre='Empresa homologada',
            ruc='20987654321',
            correo='homologada@example.com',
            homologacion=True,
        )
        empresa_homologada = Empresa.objects.get(ruc='20987654321')
        empresa_homologada.sctr_pension_aprobado = True
        empresa_homologada.sctr_salud_aprobado = True
        empresa_homologada.save(update_fields=('sctr_pension_aprobado', 'sctr_salud_aprobado'))
        for tipo in (
            Certificado.SCTR_PENSION,
            Certificado.SCTR_SALUD,
            Certificado.HOMOLOGACION,
        ):
            Certificado.objects.create(
                empresa=empresa_homologada,
                tipo=tipo,
                fecha_emision=date.today() - timedelta(days=30),
                fecha_vencimiento=date.today() + timedelta(days=30),
                archivo=SimpleUploadedFile(f'{tipo.lower()}.pdf', b'%PDF-1.4 test'),
            )

        response = self.client.get(reverse('app_control:dashboard'))

        self.assertEqual(response.context['total_empresas'], 3)
        self.assertEqual(response.context['empresas_habilitadas'], 1)
        self.assertEqual(response.context['empresas_no_homologadas'], 1)
        self.assertEqual(response.context['empresas_desactivadas'], 1)
        self.assertContains(response, '1 homologadas')
        self.assertContains(response, '1 no homologadas')
        self.assertContains(response, '1 desactivadas')

    def test_dashboard_cuenta_inducciones_vigentes_y_vencidas(self):
        hoy = date.today()
        Certificado.objects.create(
            trabajador=self.trabajador,
            tipo=Certificado.INDUCCION,
            fecha_emision=hoy - timedelta(days=10),
            fecha_vencimiento=hoy + timedelta(days=30),
            archivo=SimpleUploadedFile('induccion_vigente.pdf', b'%PDF-1.4 test'),
            validado=True,
        )
        trabajador_vencido = Trabajador.objects.create(
            empresa=self.empresa,
            dni='87654321',
            nombres='Luis',
            apellidos='Prueba',
        )
        Certificado.objects.create(
            trabajador=trabajador_vencido,
            tipo=Certificado.INDUCCION,
            fecha_emision=hoy - timedelta(days=30),
            fecha_vencimiento=hoy - timedelta(days=1),
            archivo=SimpleUploadedFile('induccion_vencida.pdf', b'%PDF-1.4 test'),
        )

        response = self.client.get(reverse('app_control:dashboard'))

        self.assertEqual(response.context['inducciones_vigentes'], 1)
        self.assertEqual(response.context['inducciones_vencidas'], 1)
        self.assertContains(response, '1 vigentes')
        self.assertContains(response, '1 vencidas')

    def test_dashboard_cuenta_trabajadores_con_sctr_efectivo(self):
        hoy = date.today()
        empresa_sctr = Empresa.objects.create(
            nombre='Empresa con SCTR',
            ruc='20987654322',
            correo='sctr@example.com',
            sctr_salud_aprobado=True,
            sctr_pension_aprobado=True,
        )
        trabajador_sctr = Trabajador.objects.create(
            empresa=empresa_sctr,
            dni='87654321',
            nombres='Luis',
            apellidos='SCTR',
        )
        for tipo in (Certificado.SCTR_SALUD, Certificado.SCTR_PENSION):
            Certificado.objects.create(
                empresa=empresa_sctr,
                tipo=tipo,
                fecha_emision=hoy - timedelta(days=10),
                fecha_vencimiento=hoy + timedelta(days=30),
                archivo=SimpleUploadedFile(f'{tipo.lower()}_vigente.pdf', b'%PDF-1.4 test'),
            )

        response = self.client.get(reverse('app_control:dashboard'))

        self.assertEqual(response.context['trabajadores_sctr_salud'], 1)
        self.assertEqual(response.context['trabajadores_sctr_pension'], 1)
        self.assertEqual(response.context['trabajadores_sin_sctr_salud'], 1)
        self.assertEqual(response.context['trabajadores_sin_sctr_pension'], 1)
        self.assertEqual(response.context['sctr_salud_proximos_vencer'], 1)
        self.assertEqual(response.context['sctr_pension_proximos_vencer'], 1)
        self.assertContains(response, 'SCTR Salud')
        self.assertContains(response, 'SCTR Pensión')

    def test_dashboard_cuenta_trabajadores_con_cursos_vigentes_por_tipo(self):
        hoy = date.today()
        for curso in (CursoTipo.CALIENTE, CursoTipo.ALTURA):
            Certificado.objects.create(
                trabajador=self.trabajador,
                tipo=Certificado.CURSOS,
                curso=curso,
                fecha_emision=hoy - timedelta(days=10),
                fecha_vencimiento=hoy + timedelta(days=30),
                archivo=SimpleUploadedFile(f'{curso.lower()}.pdf', b'%PDF-1.4 test'),
                validado=True,
            )
        Certificado.objects.create(
            trabajador=self.trabajador,
            tipo=Certificado.CURSOS,
            curso=CursoTipo.ELECTRICO,
            fecha_emision=hoy - timedelta(days=30),
            fecha_vencimiento=hoy - timedelta(days=1),
            archivo=SimpleUploadedFile('electrico_vencido.pdf', b'%PDF-1.4 test'),
            validado=True,
        )

        response = self.client.get(reverse('app_control:dashboard'))
        cursos = {curso['codigo']: curso['total'] for curso in response.context['cursos_vigentes']}

        self.assertEqual(cursos[CursoTipo.CALIENTE], 1)
        self.assertEqual(cursos[CursoTipo.ALTURA], 1)
        self.assertEqual(cursos[CursoTipo.ELECTRICO], 0)
        self.assertContains(response, 'Cursos vigentes por tipo')

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

    def test_usuario_garita_puede_ver_trabajadores_desde_la_empresa(self):
        self.user.role = User.GARITA
        self.user.save(update_fields=['role'])

        empresas_response = self.client.get(reverse('app_control:empresa_lista'))
        self.assertContains(
            empresas_response,
            reverse('app_control:empresa_trabajadores_garita', args=[self.empresa.pk]),
        )

        response = self.client.get(
            reverse('app_control:empresa_trabajadores_garita', args=[self.empresa.pk]),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ana')
        self.assertContains(response, 'Prueba')

    def test_usuario_garita_sigue_sin_poder_abrir_lista_general_de_trabajadores(self):
        self.user.role = User.GARITA
        self.user.save(update_fields=['role'])

        response = self.client.get(reverse('app_control:trabajador_lista'))

        self.assertEqual(response.status_code, 403)

    def test_usuario_no_garita_no_puede_abrir_lista_especial_de_empresa(self):
        response = self.client.get(
            reverse('app_control:empresa_trabajadores_garita', args=[self.empresa.pk]),
        )

        self.assertEqual(response.status_code, 403)

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

    def test_lista_y_detalle_muestran_habilitacion_efectiva(self):
        self.assertTrue(self.trabajador.habilitado)
        self.assertFalse(self.trabajador.habilitado_efectivo)

        self.user.role = User.BECA_AZUL
        self.user.save(update_fields=['role'])

        response = self.client.get(
            reverse('app_control:trabajador_lista'),
            {'q': self.trabajador.nombres},
        )

        self.assertContains(response, 'No habilitado')

        response = self.client.get(
            reverse('app_control:trabajador_detalle', args=[self.trabajador.pk]),
        )

        self.assertContains(response, 'No habilitado')
        self.assertContains(response, 'Deshabilitar')

    def test_validacion_individual_sctr_es_requisito_y_solo_beca_azul_puede_cambiarla(self):
        hoy = date.today()
        self.empresa.sctr_pension_aprobado = True
        self.empresa.sctr_salud_aprobado = True
        self.empresa.homologacion = True
        self.empresa.save(update_fields=['sctr_pension_aprobado', 'sctr_salud_aprobado', 'homologacion'])
        for tipo in (Certificado.SCTR_PENSION, Certificado.SCTR_SALUD, Certificado.HOMOLOGACION):
            Certificado.objects.create(
                empresa=self.empresa,
                tipo=tipo,
                fecha_emision=hoy - timedelta(days=1),
                fecha_vencimiento=hoy + timedelta(days=30),
                archivo=SimpleUploadedFile(f'{tipo.lower()}.pdf', b'%PDF-1.4 test'),
            )
        for tipo in (Certificado.INDUCCION, Certificado.APTITUD_MEDICA):
            Certificado.objects.create(
                trabajador=self.trabajador,
                tipo=tipo,
                fecha_emision=hoy - timedelta(days=1),
                fecha_vencimiento=hoy + timedelta(days=30),
                archivo=SimpleUploadedFile(f'{tipo.lower()}.pdf', b'%PDF-1.4 test'),
                validado=True,
            )
        self.assertFalse(self.trabajador.habilitado_efectivo)

        self.user.role = User.USUARIO_EMPRESA
        self.user.empresa = self.empresa
        self.user.save(update_fields=['role', 'empresa'])
        response = self.client.get(reverse('app_control:trabajador_detalle', args=[self.trabajador.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'trabajador_sctr_validar')
        self.assertNotContains(response, 'Gestionado por Beca Azul')
        forbidden = self.client.post(reverse('app_control:trabajador_sctr_validar', args=[self.trabajador.pk, 'pension']))
        self.assertEqual(forbidden.status_code, 403)

        self.user.role = User.BECA_AZUL
        self.user.save(update_fields=['role'])
        pension_url = reverse('app_control:trabajador_sctr_validar', args=[self.trabajador.pk, 'pension'])
        salud_url = reverse('app_control:trabajador_sctr_validar', args=[self.trabajador.pk, 'salud'])
        self.assertRedirects(self.client.post(pension_url, {'validado': '1'}), reverse('app_control:trabajador_detalle', args=[self.trabajador.pk]))
        self.assertTrue(Trabajador.objects.get(pk=self.trabajador.pk).sctr_pension_validado)
        self.assertFalse(Trabajador.objects.get(pk=self.trabajador.pk).habilitado_efectivo)
        self.client.post(salud_url, {'validado': '1'})
        self.assertTrue(Trabajador.objects.get(pk=self.trabajador.pk).habilitado_efectivo)

        Certificado.objects.filter(empresa=self.empresa, tipo=Certificado.SCTR_PENSION).update(fecha_vencimiento=hoy - timedelta(days=1))
        self.client.post(pension_url, {'validado': '0'})
        trabajador = Trabajador.objects.get(pk=self.trabajador.pk)
        self.assertFalse(trabajador.sctr_pension_validado)
        self.assertFalse(trabajador.habilitado_efectivo)

    def test_sctr_individual_pendiente_si_empresa_no_esta_aprobada(self):
        hoy = date.today()
        Certificado.objects.create(
            empresa=self.empresa,
            tipo=Certificado.SCTR_PENSION,
            fecha_emision=hoy - timedelta(days=1),
            fecha_vencimiento=hoy + timedelta(days=30),
            archivo=SimpleUploadedFile('sctr_pension.pdf', b'%PDF-1.4 test'),
        )
        Certificado.objects.create(
            empresa=self.empresa,
            tipo=Certificado.SCTR_SALUD,
            fecha_emision=hoy - timedelta(days=1),
            fecha_vencimiento=hoy + timedelta(days=30),
            archivo=SimpleUploadedFile('sctr_salud.pdf', b'%PDF-1.4 test'),
        )
        self.trabajador.sctr_pension_validado = True
        self.trabajador.sctr_salud_validado = True
        self.trabajador.save(update_fields=['sctr_pension_validado', 'sctr_salud_validado'])
        self.user.role = User.BECA_AZUL
        self.user.save(update_fields=['role'])

        response = self.client.get(reverse('app_control:trabajador_detalle', args=[self.trabajador.pk]))

        self.assertEqual(response.status_code, 200)
        filas_sctr = response.context['certificados_requeridos'][:2]
        self.assertEqual([fila['validado'] for fila in filas_sctr], [False, False])
        self.assertEqual([fila['puede_validarse'] for fila in filas_sctr], [True, True])
        self.assertContains(response, 'Pendiente')
        trabajador = Trabajador.objects.get(pk=self.trabajador.pk)
        self.assertFalse(trabajador.sctr_pension_validado)
        self.assertFalse(trabajador.sctr_salud_validado)

        url = reverse('app_control:trabajador_sctr_validar', args=[self.trabajador.pk, 'pension'])
        response = self.client.post(url, {'validado': '1'}, follow=True)
        self.assertContains(
            response,
            'Primero se requiere que el SCTR pensión en el panel de la empresa esté aprobado.',
        )
        self.assertFalse(Trabajador.objects.get(pk=self.trabajador.pk).sctr_pension_validado)

    def test_no_se_puede_habilitar_sin_las_dos_validaciones_individuales_sctr(self):
        hoy = date.today()
        self.empresa.sctr_pension_aprobado = True
        self.empresa.sctr_salud_aprobado = True
        self.empresa.homologacion = True
        self.empresa.save(update_fields=['sctr_pension_aprobado', 'sctr_salud_aprobado', 'homologacion'])
        for tipo in (Certificado.SCTR_PENSION, Certificado.SCTR_SALUD, Certificado.HOMOLOGACION):
            Certificado.objects.create(
                empresa=self.empresa,
                tipo=tipo,
                fecha_emision=hoy - timedelta(days=1),
                fecha_vencimiento=hoy + timedelta(days=30),
                archivo=SimpleUploadedFile(f'{tipo.lower()}_habilitacion.pdf', b'%PDF-1.4 test'),
            )
        for tipo in (Certificado.INDUCCION, Certificado.APTITUD_MEDICA):
            Certificado.objects.create(
                trabajador=self.trabajador,
                tipo=tipo,
                fecha_emision=hoy - timedelta(days=1),
                fecha_vencimiento=hoy + timedelta(days=30),
                archivo=SimpleUploadedFile(f'{tipo.lower()}_habilitacion.pdf', b'%PDF-1.4 test'),
                validado=True,
            )
        self.trabajador.habilitado = False
        self.trabajador.save(update_fields=['habilitado'])
        self.user.role = User.BECA_AZUL
        self.user.save(update_fields=['role'])

        response = self.client.post(
            reverse('app_control:trabajador_habilitado_toggle', args=[self.trabajador.pk]),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'validación individual del SCTR pensión')
        self.assertContains(response, 'validación individual del SCTR salud')
        trabajador = Trabajador.objects.get(pk=self.trabajador.pk)
        self.assertFalse(trabajador.habilitado)
        self.assertFalse(trabajador.sctr_pension_validado)
        self.assertFalse(trabajador.sctr_salud_validado)

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
        Trabajador.objects.create(
            empresa=self.empresa,
            dni='98765432',
            nombres='Trabajador',
            apellidos='Desactivado',
            activo=False,
        )

        response = self.client.get(reverse('app_control:dashboard'))

        self.assertEqual(response.context['total_trabajadores'], 2)
        self.assertEqual(response.context['trabajadores_habilitados'], 0)
        self.assertEqual(response.context['trabajadores_no_habilitados'], 1)
        self.assertEqual(response.context['trabajadores_desactivados'], 1)

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
    def test_usuario_empresa_no_puede_editar_trabajador_desactivado(self):
        empresa = Empresa.objects.create(nombre='Empresa edición', ruc='20987654321', correo='edicion@example.com')
        user = User.objects.create_user(
            email='edicion@example.com',
            password='test-password',
            first_name='Usuario',
            last_name='Empresa',
            role=User.USUARIO_EMPRESA,
            empresa=empresa,
        )
        trabajador = Trabajador.objects.create(
            empresa=empresa,
            dni='12345678',
            nombres='Ana',
            apellidos='Prueba',
            activo=False,
        )
        self.client.force_login(user)

        response = self.client.get(reverse('app_control:trabajador_empresa_editar', args=[trabajador.pk]))

        self.assertEqual(response.status_code, 403)

    def test_usuario_empresa_puede_editar_su_trabajador_activo(self):
        empresa = Empresa.objects.create(nombre='Empresa edición activa', ruc='20876543210', correo='edicion-activa@example.com')
        user = User.objects.create_user(
            email='edicion-activa@example.com',
            password='test-password',
            first_name='Usuario',
            last_name='Empresa',
            role=User.USUARIO_EMPRESA,
            empresa=empresa,
        )
        trabajador = Trabajador.objects.create(
            empresa=empresa,
            dni='12345678',
            nombres='Ana',
            apellidos='Prueba',
        )
        self.client.force_login(user)

        response = self.client.get(reverse('app_control:trabajador_empresa_editar', args=[trabajador.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Aptitud médica')
        self.assertNotContains(response, 'induccion_archivo')

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
