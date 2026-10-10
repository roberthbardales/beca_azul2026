from datetime import date, timedelta
from tempfile import TemporaryDirectory

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.db.models import Prefetch
from django.db import IntegrityError, transaction

from ..models import Certificado, CursoObligatorio, CursoTipo, Empresa, Trabajador, certificado_upload_path


class CertificadoModelTests(TestCase):
    def setUp(self):
        self.empresa = Empresa.objects.create(nombre='Empresa', ruc='20123456789', correo='empresa@example.com')
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

    def test_bulk_create_rechaza_certificado_con_propietario_inconsistente(self):
        certificado = Certificado(
            trabajador=self.trabajador,
            tipo=Certificado.SCTR_PENSION,
            fecha_emision=date.today(),
            fecha_vencimiento=date.today() + timedelta(days=1),
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Certificado.objects.bulk_create([certificado])

    def test_estado_curso_usa_cursos_obligatorios_prefijados(self):
        CursoObligatorio.objects.create(trabajador=self.trabajador, curso=CursoTipo.ALTURA)
        Certificado.objects.create(
            trabajador=self.trabajador,
            tipo=Certificado.CURSOS,
            curso=CursoTipo.ALTURA,
            fecha_emision=date.today(),
            fecha_vencimiento=date.today() + timedelta(days=30),
            archivo=SimpleUploadedFile('altura.pdf', b'contenido'),
            validado=True,
        )
        trabajador = Trabajador.objects.prefetch_related(
            Prefetch('cursos_obligatorios', to_attr='cursos_obligatorios_lista'),
        ).get(pk=self.trabajador.pk)

        self.assertEqual(trabajador.estado_curso_altura, 'Vigente')

    def test_certificado_curso_sin_archivo_no_se_considera_validado(self):
        certificado = Certificado.objects.create(
            trabajador=self.trabajador,
            tipo=Certificado.CURSOS,
            curso=CursoTipo.ALTURA,
            fecha_emision=date.today(),
            fecha_vencimiento=date.today() + timedelta(days=30),
            archivo='certificados/no-existe.pdf',
            validado=True,
        )

        self.assertEqual(certificado.estado, 'Pendiente')
        self.assertEqual(certificado.validacion_estado, 'Pendiente')
        self.assertFalse(certificado.validacion_vigente)

    def test_certificado_con_emision_futura_no_se_considera_vigente(self):
        certificado = Certificado.objects.create(
            empresa=self.empresa,
            tipo=Certificado.SCTR_PENSION,
            fecha_emision=date.today() + timedelta(days=1),
            fecha_vencimiento=date.today() + timedelta(days=30),
            archivo=SimpleUploadedFile('sctr_futuro.pdf', b'%PDF-1.4 test'),
            validado=True,
        )

        self.assertFalse(certificado.esta_vigente)
        self.assertEqual(certificado.estado, 'Pendiente')
        self.assertEqual(certificado.validacion_estado, 'Pendiente')
        self.assertFalse(certificado.validacion_vigente)


class HomologacionManualTests(TestCase):
    def test_empresa_rechaza_sctr_aprobado_sin_certificado_vigente(self):
        empresa = Empresa.objects.create(
            nombre='Empresa',
            ruc='20123456789',
            correo='empresa@example.com',
            sctr_pension_aprobado=True,
        )

        with self.assertRaises(ValidationError):
            empresa.full_clean()

    def test_empresa_no_puede_homologarse_sin_ambos_sctr_aprobados(self):
        empresa = Empresa.objects.create(
            nombre='Empresa',
            ruc='20123456789',
            correo='empresa@example.com',
            homologacion=True,
            sctr_pension_aprobado=True,
            sctr_salud_aprobado=False,
        )

        with self.assertRaises(ValidationError):
            empresa.full_clean()

    def test_empresa_rechaza_ruc_invalido(self):
        empresa = Empresa(
            nombre='Empresa',
            ruc='ABC',
            correo='empresa@example.com',
        )

        with self.assertRaises(ValidationError):
            empresa.full_clean()

    def test_cambiar_empresa_no_actualiza_la_homologacion(self):
        empresa_anterior = Empresa.objects.create(nombre='Anterior', ruc='20123456789', correo='anterior@example.com')
        empresa_nueva = Empresa.objects.create(nombre='Nueva', ruc='20987654321', correo='nueva@example.com')
        trabajador = Trabajador.objects.create(
            empresa=empresa_anterior,
            dni='12345678',
            nombres='Ana',
            apellidos='Prueba',
            habilitado=True,
        )
        empresa_anterior.homologacion = True
        empresa_anterior.save(update_fields=['homologacion'])

        trabajador.empresa = empresa_nueva
        trabajador.save()

        empresa_anterior.refresh_from_db()
        empresa_nueva.refresh_from_db()
        self.assertTrue(empresa_anterior.homologacion)
        self.assertFalse(empresa_nueva.homologacion)


class SctrEfectivoTests(TestCase):
    def setUp(self):
        self.empresa = Empresa.objects.create(nombre='Empresa', ruc='20123456789', correo='empresa@example.com')
        self.empresa.sctr_pension_aprobado = True
        self.empresa.sctr_salud_aprobado = True
        self.empresa.save(update_fields=['sctr_pension_aprobado', 'sctr_salud_aprobado'])
        self.trabajador = Trabajador.objects.create(
            empresa=self.empresa,
            dni='12345678',
            nombres='Ana',
            apellidos='Prueba',
        )

    def crear_certificado(self, tipo, vencimiento):
        certificado = Certificado.objects.create(
            empresa=self.empresa,
            tipo=tipo,
            fecha_emision=date.today() - timedelta(days=1),
            fecha_vencimiento=vencimiento,
            archivo=SimpleUploadedFile(f'{tipo.lower()}.pdf', b'%PDF-1.4 test'),
        )
        return certificado

    def test_sctr_efectivo_requiere_aprobacion_y_certificado_vigente(self):
        self.crear_certificado(Certificado.SCTR_PENSION, date.today() + timedelta(days=1))
        self.crear_certificado(Certificado.SCTR_SALUD, date.today() + timedelta(days=1))

        self.assertTrue(self.trabajador.sctr_pension_efectivo)
        self.assertTrue(self.trabajador.sctr_salud_efectivo)

    def test_sctr_efectivo_es_falso_si_falta_el_archivo(self):
        pension = self.crear_certificado(Certificado.SCTR_PENSION, date.today() + timedelta(days=1))
        self.crear_certificado(Certificado.SCTR_SALUD, date.today() + timedelta(days=1))
        pension.archivo.storage.delete(pension.archivo.name)

        self.assertFalse(self.trabajador.sctr_pension_efectivo)
        self.assertTrue(self.trabajador.sctr_salud_efectivo)

    def test_sctr_efectivo_es_falso_si_esta_vencido(self):
        self.crear_certificado(Certificado.SCTR_PENSION, date.today() - timedelta(days=1))
        self.crear_certificado(Certificado.SCTR_SALUD, date.today() + timedelta(days=1))

        self.assertFalse(self.trabajador.sctr_pension_efectivo)
        self.assertTrue(self.trabajador.sctr_salud_efectivo)

    def test_sctr_efectivo_es_falso_antes_de_la_fecha_de_emision(self):
        pension = Certificado.objects.create(
            empresa=self.empresa,
            tipo=Certificado.SCTR_PENSION,
            fecha_emision=date.today() + timedelta(days=1),
            fecha_vencimiento=date.today() + timedelta(days=30),
            archivo=SimpleUploadedFile('pension_futuro.pdf', b'%PDF-1.4 test'),
        )
        self.crear_certificado(Certificado.SCTR_SALUD, date.today() + timedelta(days=30))

        self.assertFalse(pension.esta_vigente)
        self.assertEqual(pension.estado, 'Pendiente')
        self.assertFalse(self.trabajador.sctr_pension_efectivo)
        self.assertTrue(self.trabajador.sctr_salud_efectivo)

    def test_sctr_efectivo_es_falso_si_no_esta_aprobado(self):
        self.crear_certificado(Certificado.SCTR_PENSION, date.today() + timedelta(days=1))
        self.crear_certificado(Certificado.SCTR_SALUD, date.today() + timedelta(days=1))
        self.empresa.sctr_pension_aprobado = False
        self.empresa.save(update_fields=['sctr_pension_aprobado'])

        self.assertFalse(self.trabajador.sctr_pension_efectivo)
        self.assertTrue(self.trabajador.sctr_salud_efectivo)
