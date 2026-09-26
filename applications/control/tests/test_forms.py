from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import date, timedelta

from django.test import SimpleTestCase, TestCase

from ..forms import (
    CertificadoForm,
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


class FormValidationTests(TestCase):
    def setUp(self):
        self.empresa = Empresa.objects.create(nombre='Empresa', ruc='20123456789')
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

    def test_editar_trabajador_sin_cambios_de_certificados_los_conserva(self):
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
        fecha_emision_actualizada = date.today() - timedelta(days=5)
        fecha_vencimiento_actualizada = date.today() + timedelta(days=20)
        fechas_certificado = {
            'induccion_fecha_emision': fecha_emision_actualizada.isoformat(),
            'induccion_fecha_vencimiento': fecha_vencimiento_actualizada.isoformat(),
        }

        form = TrabajadorEmpresaForm(
            data={**datos, **fechas_certificado},
            instance=self.trabajador,
            empresa=self.empresa,
        )

        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        certificado.refresh_from_db()
        self.assertEqual(certificado.archivo.name, archivo_original)
        self.assertEqual(certificado.fecha_emision, fecha_emision_actualizada)
        self.assertEqual(certificado.fecha_vencimiento, fecha_vencimiento_actualizada)
        self.assertEqual(self.trabajador.__class__.objects.get(pk=self.trabajador.pk).nombres, 'Ana Actualizada')

    def test_editar_trabajador_rechaza_fechas_parciales_de_certificado(self):
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

        self.assertFalse(form.is_valid())
        self.assertIn('induccion_fecha_vencimiento', form.errors)

    def test_incidencia_form_rechaza_descripcion_vacia(self):
        form = IncidenciaForm(data={'descripcion': '   '})

        self.assertFalse(form.is_valid())
        self.assertIn('descripcion', form.errors)
