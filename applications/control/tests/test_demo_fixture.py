from io import StringIO
from tempfile import TemporaryDirectory

from django.core.files.storage import default_storage
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.utils import timezone

from ..models import Certificado, Empresa, Trabajador


class DemoFixturePreparationTests(TestCase):
    fixtures = ['seed.json']

    def test_fixture_has_five_companies_with_five_workers_each(self):
        self.assertEqual(Empresa.objects.count(), 5)
        self.assertEqual(Trabajador.objects.count(), 25)
        self.assertTrue(all(empresa.trabajadores.count() == 5 for empresa in Empresa.objects.all()))

    def test_command_prepares_files_and_varied_current_states_repeatably(self):
        with TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                call_command('preparar_demo_certificados', stdout=StringIO())

                certificado = Certificado.objects.get(pk=252)
                self.assertTrue(default_storage.exists(certificado.archivo.name))
                self.assertFalse(certificado.validado)
                self.assertGreaterEqual(certificado.fecha_vencimiento, certificado.fecha_emision)

                expirado = Certificado.objects.get(pk=255)
                self.assertLess(expirado.fecha_vencimiento, timezone.localdate())

                empresas_homologadas = Empresa.objects.filter(homologacion=True)
                self.assertEqual(set(empresas_homologadas.values_list('pk', flat=True)), {21, 22, 23})
                self.assertEqual(
                    sum(trabajador.habilitado_efectivo for trabajador in Trabajador.objects.all()),
                    10,
                )

                call_command('preparar_demo_certificados', stdout=StringIO())
                self.assertTrue(default_storage.exists(certificado.archivo.name))
