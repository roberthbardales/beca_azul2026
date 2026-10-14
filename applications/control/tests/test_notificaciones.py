from unittest.mock import patch

from django.test import TestCase, override_settings

from applications.control.models import RegistroNotificacion
from applications.control.services.notificaciones import enviar_notificacion_habilitacion


@override_settings(
    DEFAULT_FROM_EMAIL='CheckID <notificaciones@example.com>',
    NOTIFICACIONES_EMAIL_ADICIONAL='interno@example.com',
)
class RegistroNotificacionTests(TestCase):
    def enviar(self):
        return enviar_notificacion_habilitacion(
            'Trabajador habilitado',
            'El trabajador quedó habilitado.',
            'empresa@example.com',
            (('Empresa', 'Ejemplo'),),
            evento='habilitacion_trabajador',
        )

    @patch('applications.control.services.notificaciones.send_mail', return_value=1)
    def test_registra_envio_exitoso_con_evento_y_destinatarios(self, enviar_correo):
        self.assertEqual(self.enviar(), 1)

        registro = RegistroNotificacion.objects.get()
        self.assertEqual(registro.evento, 'habilitacion_trabajador')
        self.assertEqual(registro.asunto, 'Trabajador habilitado')
        self.assertEqual(
            registro.destinatarios,
            ['empresa@example.com', 'noreply.beca.azul@gmail.com', 'interno@example.com'],
        )
        self.assertEqual(registro.estado, RegistroNotificacion.Estado.ENVIADO)
        self.assertFalse(registro.error)
        enviar_correo.assert_called_once()

    @patch(
        'applications.control.services.notificaciones.send_mail',
        side_effect=OSError('Proveedor no disponible'),
    )
    def test_registra_error_y_propaga_excepcion_del_proveedor(self, enviar_correo):
        with self.assertRaisesMessage(OSError, 'Proveedor no disponible'):
            self.enviar()

        registro = RegistroNotificacion.objects.get()
        self.assertEqual(registro.estado, RegistroNotificacion.Estado.FALLIDO)
        self.assertIn('OSError: Proveedor no disponible', registro.error)
        enviar_correo.assert_called_once()

    @patch('applications.control.services.notificaciones.send_mail', return_value=0)
    def test_registra_fallo_si_el_backend_no_acepta_destinatarios(self, enviar_correo):
        self.assertEqual(self.enviar(), 0)

        registro = RegistroNotificacion.objects.get()
        self.assertEqual(registro.estado, RegistroNotificacion.Estado.FALLIDO)
        self.assertIn('no aceptó ningún destinatario', registro.error)
        enviar_correo.assert_called_once()
