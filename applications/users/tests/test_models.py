from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from applications.control.models import Empresa
from applications.users.models import User


class UserModelTests(TestCase):
    def test_usuario_empresa_requiere_empresa(self):
        usuario = User(
            email='usuario@example.com',
            first_name='Usuario',
            last_name='Empresa',
            role=User.USUARIO_EMPRESA,
        )

        with self.assertRaises(ValidationError):
            usuario.full_clean()

    def test_usuario_empresa_con_empresa_es_valido(self):
        empresa = Empresa.objects.create(
            nombre='Empresa',
            ruc='20123456789',
            correo='empresa@example.com',
        )
        usuario = User(
            email='usuario@example.com',
            first_name='Usuario',
            last_name='Empresa',
            role=User.USUARIO_EMPRESA,
            empresa=empresa,
        )
        usuario.set_password('password-segura')

        usuario.full_clean()

    def test_base_de_datos_rechaza_usuario_empresa_sin_empresa(self):
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                'usuario@example.com',
                password='password-segura',
                first_name='Usuario',
                last_name='Empresa',
                role=User.USUARIO_EMPRESA,
            )
