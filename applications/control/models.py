from datetime import datetime

from django.conf import settings
from django.db import models
from django.db.models import Q
from model_utils.models import TimeStampedModel


def certificado_upload_path(instance, filename):
    extension = filename.rsplit('.', 1)[-1] if '.' in filename else ''
    base = instance.trabajador.dni
    fecha = instance.fecha_emision
    nombre = datetime.now().strftime('%d%m%Y%H%M%S')
    nombre_archivo = f'{base}_{nombre}.{extension}' if extension else f'{base}_{nombre}'
    return f'certificados/empresa_{instance.trabajador.empresa_id}/{fecha:%Y}/{fecha:%m}/{nombre_archivo}'


class Empresa(TimeStampedModel):

    nombre = models.CharField(max_length=150)
    ruc = models.CharField(max_length=11, unique=True)
    direccion = models.CharField(max_length=255, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ('nombre',)
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'

    def __str__(self):
        return self.nombre


class Trabajador(TimeStampedModel):
    PENDIENTE = 'PENDIENTE'
    HABILITADO = 'HABILITADO'
    RECHAZADO = 'RECHAZADO'

    ESTADO_CHOICES = (
        (PENDIENTE, 'Pendiente'),
        (HABILITADO, 'Habilitado'),
        (RECHAZADO, 'Rechazado'),
    )

    DNI = 'DNI'
    CE = 'CE'
    PASAPORTE = 'PASAPORTE'
    TIPO_DOCUMENTO_CHOICES = (
        (DNI, 'DNI'),
        (CE, 'Carné de extranjería'),
        (PASAPORTE, 'Pasaporte'),
    )

    empresa = models.ForeignKey(Empresa, on_delete=models.PROTECT, related_name='trabajadores')
    tipo_documento = models.CharField(max_length=10, choices=TIPO_DOCUMENTO_CHOICES, default=DNI)
    dni = models.CharField(max_length=20, db_index=True)
    nombres = models.CharField(max_length=150)
    apellidos = models.CharField(max_length=150)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    cargo = models.CharField(max_length=150, blank=True)
    area = models.CharField(max_length=150, blank=True)

    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default=PENDIENTE, db_index=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ('empresa__nombre', 'apellidos', 'nombres')
        verbose_name = 'Trabajador'
        verbose_name_plural = 'Trabajadores'
        constraints = [
            models.UniqueConstraint(
                fields=('empresa', 'dni'),
                condition=Q(activo=True),
                name='unique_trabajador_activo_empresa_dni',
            ),
        ]

    def __str__(self):
        return f'{self.nombres} {self.apellidos}'

    def actualizar_estado(self):
        certificados = self.certificados.all()
        if certificados.count() >= 2 and all(c.aprobado for c in certificados):
            self.estado = self.HABILITADO
        else:
            self.estado = self.PENDIENTE
        self.save(update_fields=['estado'])


class Certificado(TimeStampedModel):

    trabajador = models.ForeignKey(Trabajador, on_delete=models.CASCADE, related_name='certificados')
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    fecha_emision = models.DateField()
    fecha_vencimiento = models.DateField(null=True, blank=True)
    archivo = models.FileField(upload_to=certificado_upload_path, blank=True, null=True)

    aprobado = models.BooleanField(default=False)
    aprobado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    fecha_aprobacion = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Certificado'
        verbose_name_plural = 'Certificados'
        constraints = [
            models.CheckConstraint(
                check=Q(fecha_vencimiento__isnull=True) | Q(fecha_vencimiento__gte=models.F('fecha_emision')),
                name='certificado_fecha_vencimiento_no_antes_de_emision',
            ),
        ]

    def __str__(self):
        return f'{self.nombre} - {self.trabajador}'