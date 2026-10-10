from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import date, timedelta

from django.test import SimpleTestCase, TestCase

from ..forms import (
    CertificadoForm,
    EmpresaForm,
    IncidenciaForm,
    SCTRForm,
    TrabajadorEmpresaForm,
    TrabajadorForm,
    validate_pdf,
)
from ..models import Certificado, Empresa, Trabajador


class PdfValidationTests(SimpleTestCase):
    def test_accepts_pdf_with_valid_signature(self):
        archivo = SimpleUploadedFile('documento.pdf', b'%PDF-1.4 contenido')

        validate_pdf(archivo)

    def test_rejects_file_with_pdf_extension_but_invalid_content(self):
        archivo = SimpleUploadedFile('documento.pdf', b'no es un pdf')

        with self.assertRaisesMessage(ValidationError, 'El archivo no contiene un PDF válido.'):
            validate_pdf(archivo)

    def test_rejects_pdf_over_one_mb(self):
        archivo = SimpleUploadedFile('documento.pdf', b'%PDF-' + b'x' * (1024 * 1024))

        with self.assertRaisesMessage(ValidationError, 'El archivo PDF no puede superar 1 MB.'):
            validate_pdf(archivo)


class FormValidationTests(TestCase):
    def setUp(self):
        self.empresa = Empresa.objects.create(nombre='Empresa', ruc='20123456789', correo='empresa@example.com')
        self.trabajador = Trabajador.objects.create(
            empresa=self.empresa,
            dni='12345678',
            nombres='Ana',
            apellidos='Prueba',
        )
        self.fechas = {
            'fecha_emision': date.today(),
            'fecha_vencimiento': date.today() + timedelta(days=1),
        }

    def test_crear_trabajador_empresa_exige_induccion_y_aptitud_medica(self):
        form = TrabajadorEmpresaForm(
            data={
                'tipo_documento': Trabajador.DNI,
                'dni': '87654321',
                'nombres': 'Nuevo',
                'apellidos': 'Trabajador',
                'induccion_fecha_emision': date.today().isoformat(),
                'induccion_fecha_vencimiento': (date.today() + timedelta(days=1)).isoformat(),
                'aptitud_medica_fecha_emision': date.today().isoformat(),
                'aptitud_medica_fecha_vencimiento': (date.today() + timedelta(days=1)).isoformat(),
            },
            files={
                'induccion_archivo': SimpleUploadedFile('induccion.pdf', b'%PDF-1.4 induccion'),
            },
            empresa=self.empresa,
        )

        self.assertFalse(form.is_valid())
        self.assertIn('aptitud_medica_archivo', form.errors)

    def test_crear_trabajador_empresa_exige_fechas_de_ambos_certificados(self):
        form = TrabajadorEmpresaForm(
            data={
                'tipo_documento': Trabajador.DNI,
                'dni': '87654321',
                'nombres': 'Nuevo',
                'apellidos': 'Trabajador',
            },
            files={
                'induccion_archivo': SimpleUploadedFile('induccion.pdf', b'%PDF-1.4 induccion'),
                'aptitud_medica_archivo': SimpleUploadedFile('aptitud.pdf', b'%PDF-1.4 aptitud'),
            },
            empresa=self.empresa,
        )

        self.assertFalse(form.is_valid())
        self.assertIn('induccion_fecha_emision', form.errors)
        self.assertIn('aptitud_medica_fecha_vencimiento', form.errors)

    def test_trabajador_form_rechaza_dni_invalido(self):
        form = TrabajadorForm(data={
            'empresa': self.empresa.pk,
            'tipo_documento': Trabajador.DNI,
            'dni': '123',
            'nombres': 'Nuevo',
            'apellidos': 'Trabajador',
        })

        self.assertFalse(form.is_valid())
        self.assertIn('dni', form.errors)

    def test_trabajador_form_no_incluye_sctr(self):
        form = TrabajadorForm(data={
            'empresa': self.empresa.pk,
            'tipo_documento': Trabajador.DNI,
            'dni': '87654321',
            'nombres': 'Nuevo',
            'apellidos': 'Trabajador',
        })

        self.assertTrue(form.is_valid(), form.errors)
        trabajador = form.save()
        self.assertFalse(trabajador.sctr_pension_efectivo)
        self.assertFalse(trabajador.sctr_salud_efectivo)

    def test_certificado_form_exige_curso(self):
        form = CertificadoForm(
            data={
                'tipo': Certificado.CURSOS,
                **self.fechas,
            },
            instance=Certificado(trabajador=self.trabajador),
        )

        self.assertFalse(form.is_valid())
        self.assertIn('curso', form.errors)

    def test_certificado_form_exige_pdf_antes_de_aceptar_fechas(self):
        form = CertificadoForm(
            data={
                'tipo': Certificado.INDUCCION,
                **self.fechas,
            },
            instance=Certificado(trabajador=self.trabajador),
        )

        self.assertFalse(form.is_valid())
        self.assertIn('archivo', form.errors)
        self.assertIn('Primero debe subir un archivo PDF', form.errors['archivo'][0])

    def test_certificado_form_rechaza_requisito_duplicado_al_crear(self):
        Certificado.objects.create(
            trabajador=self.trabajador,
            tipo=Certificado.INDUCCION,
            fecha_emision=date.today(),
            fecha_vencimiento=date.today() + timedelta(days=1),
            archivo=SimpleUploadedFile('induccion.pdf', b'%PDF-1.4 existente'),
        )
        form = CertificadoForm(
            data={
                'tipo': Certificado.INDUCCION,
                **self.fechas,
            },
            files={'archivo': SimpleUploadedFile('nuevo.pdf', b'%PDF-1.4 nuevo')},
            trabajador=self.trabajador,
        )

        self.assertFalse(form.is_valid())
        self.assertIn('tipo', form.errors)

    def test_sctr_form_exige_archivo_al_crear(self):
        form = SCTRForm(data=self.fechas, empresa=self.empresa)

        self.assertFalse(form.is_valid())
        self.assertIn('archivo', form.errors)

    def test_sctr_form_conserva_archivo_al_actualizar_fechas(self):
        certificado = Certificado.objects.create(
            empresa=self.empresa,
            tipo=Certificado.SCTR,
            fecha_emision=date.today() - timedelta(days=10),
            fecha_vencimiento=date.today() + timedelta(days=10),
            archivo=SimpleUploadedFile('sctr.pdf', b'%PDF-1.4 existente'),
        )
        archivo_original = certificado.archivo.name
        fechas_actualizadas = {
            'fecha_emision': date.today().isoformat(),
            'fecha_vencimiento': (date.today() + timedelta(days=30)).isoformat(),
        }

        form = SCTRForm(
            data=fechas_actualizadas,
            instance=certificado,
            empresa=self.empresa,
        )

        self.assertTrue(form.is_valid(), form.errors)
        actualizado = form.save()
        self.assertEqual(actualizado.archivo.name, archivo_original)
        self.assertEqual(actualizado.fecha_vencimiento, date.today() + timedelta(days=30))

    def test_empresa_form_actualiza_fechas_sctr_sin_nuevo_archivo(self):
        certificado = Certificado.objects.create(
            empresa=self.empresa,
            tipo=Certificado.SCTR,
            fecha_emision=date.today() - timedelta(days=10),
            fecha_vencimiento=date.today() + timedelta(days=10),
            archivo=SimpleUploadedFile('sctr.pdf', b'%PDF-1.4 existente'),
        )
        archivo_original = certificado.archivo.name
        form = EmpresaForm(
            data={
                'nombre': self.empresa.nombre,
                'ruc': self.empresa.ruc,
                'correo': self.empresa.correo,
                'sctr_fecha_emision': date.today().isoformat(),
                'sctr_fecha_vencimiento': (date.today() + timedelta(days=30)).isoformat(),
            },
            instance=self.empresa,
            can_edit_sctr=True,
        )

        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        certificado.refresh_from_db()
        self.assertEqual(certificado.archivo.name, archivo_original)
        self.assertEqual(certificado.fecha_vencimiento, date.today() + timedelta(days=30))

    def test_editar_trabajador_no_edita_certificados_ni_exige_los_que_faltan(self):
        certificado = Certificado.objects.create(
            trabajador=self.trabajador,
            tipo=Certificado.INDUCCION,
            fecha_emision=date.today() - timedelta(days=10),
            fecha_vencimiento=date.today() + timedelta(days=10),
            archivo=SimpleUploadedFile('induccion.pdf', b'%PDF-1.4 existente'),
        )
        archivo_original = certificado.archivo.name
        datos = {
            'tipo_documento': Trabajador.DNI,
            'dni': self.trabajador.dni,
            'nombres': 'Ana Actualizada',
            'apellidos': self.trabajador.apellidos,
            'cargo': '',
        }
        form = TrabajadorEmpresaForm(
            data={
                **datos,
                'induccion_fecha_emision': date.today().isoformat(),
                'induccion_fecha_vencimiento': (date.today() + timedelta(days=20)).isoformat(),
                'aptitud_medica_fecha_emision': date.today().isoformat(),
                'aptitud_medica_fecha_vencimiento': (date.today() + timedelta(days=20)).isoformat(),
            },
            instance=self.trabajador,
            empresa=self.empresa,
        )

        self.assertTrue(form.is_valid(), form.errors)
        self.assertNotIn('induccion_archivo', form.fields)
        self.assertNotIn('aptitud_medica_archivo', form.fields)
        form.save()
        certificado.refresh_from_db()
        self.assertEqual(certificado.archivo.name, archivo_original)
        self.assertEqual(certificado.fecha_emision, date.today() - timedelta(days=10))
        self.assertEqual(certificado.fecha_vencimiento, date.today() + timedelta(days=10))
        self.assertFalse(Certificado.objects.filter(trabajador=self.trabajador, tipo=Certificado.APTITUD_MEDICA).exists())
        self.assertEqual(self.trabajador.__class__.objects.get(pk=self.trabajador.pk).nombres, 'Ana Actualizada')

    def test_editar_trabajador_ignora_campos_de_certificado_enviados(self):
        certificado = Certificado.objects.create(
            trabajador=self.trabajador,
            tipo=Certificado.INDUCCION,
            fecha_emision=date.today() - timedelta(days=10),
            fecha_vencimiento=date.today() + timedelta(days=10),
            archivo=SimpleUploadedFile('induccion.pdf', b'%PDF-1.4 existente'),
        )
        form = TrabajadorEmpresaForm(
            data={
                'tipo_documento': Trabajador.DNI,
                'dni': self.trabajador.dni,
                'nombres': self.trabajador.nombres,
                'apellidos': self.trabajador.apellidos,
                'induccion_fecha_emision': date.today().isoformat(),
            },
            instance=self.trabajador,
            empresa=self.empresa,
        )

        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        certificado.refresh_from_db()
        self.assertEqual(certificado.fecha_emision, date.today() - timedelta(days=10))
        self.assertEqual(certificado.fecha_vencimiento, date.today() + timedelta(days=10))

    def test_incidencia_form_rechaza_descripcion_vacia(self):
        form = IncidenciaForm(data={'descripcion': '   '})

        self.assertFalse(form.is_valid())
        self.assertIn('descripcion', form.errors)
