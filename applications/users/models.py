from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import UserManager
from model_utils.models import TimeStampedModel


class User(AbstractBaseUser, PermissionsMixin,TimeStampedModel):

    ADMINISTRADOR = '0'
    BECA_AZUL = '1'
    PLANTA = '2'
    USUARIO_EMPRESA = '3'
    GARITA = '4'

    VARON = 'M'
    MUJER = 'F'
    OTROS = 'O'

    ROLE_CHOICES = (
        (ADMINISTRADOR, 'Administrador'),
        (BECA_AZUL, 'Beca Azul'),
        (PLANTA, 'Usuario Planta'),
        (USUARIO_EMPRESA, 'Usuario Empresa'),
        (GARITA, 'Usuario Garita'),
    )

    GENDER_CHOICES = (
        (VARON, 'Masculino'),
        (MUJER, 'Femenino'),
        (OTROS, 'Otro'),
    )

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    role = models.CharField(max_length=2, choices=ROLE_CHOICES)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    date_birth = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    empresa = models.ForeignKey(
        'control.Empresa',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='usuarios',
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return f'{self.get_full_name()} ({self.email})'

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()

    def get_short_name(self):
        return self.first_name
