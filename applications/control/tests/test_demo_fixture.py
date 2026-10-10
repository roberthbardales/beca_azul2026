from io import StringIO
from tempfile import TemporaryDirectory

from django.core.files.storage import default_storage
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.utils import timezone

from ..models import Certificado, Empresa, Trabajador


class DemoFixturePreparationTests(TestCase):
    fixtures = ['seed.json']

    def test_fixture_includes_varied_worker_sctr_checks_without_numeric_name_suffixes(self):
        expected = {
            53: (True, True),
            54: (True, False),
            55: (False, True),
            56: (False, False),
            63: (False, True),
        }
        for pk, estados in expected.items():
            trabajador = Trabajador.objects.get(pk=pk)
            self.assertEqual(
                (trabajador.sctr_pension_validado, trabajador.sctr_salud_validado),
                estados,
            )

        self.assertFalse(any(
            trabajador.apellidos.rsplit(' ', 1)[-1].isdigit()
            for trabajador in Trabajador.objects.all()
        ))

    def test_command_prepares_files_and_varied_current_states_repeatably(self):
        with TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                call_command('preparar_demo_certificados', stdout=StringIO())

                certificado = Certificado.objects.get(pk=234)
                self.assertTrue(default_storage.exists(certificado.archivo.name))
                self.assertFalse(certificado.validado)
                self.assertGreaterEqual(certificado.fecha_vencimiento, certificado.fecha_emision)

                expirado = Certificado.objects.get(pk=235)
                self.assertLess(expirado.fecha_vencimiento, timezone.localdate())

                empresa = Empresa.objects.get(pk=21)
                self.assertTrue(empresa.sctr_pension_aprobado)
                self.assertTrue(empresa.sctr_salud_aprobado)
                self.assertTrue(empresa.homologacion)

                call_command('preparar_demo_certificados', stdout=StringIO())
                self.assertTrue(default_storage.exists(certificado.archivo.name))
