from datetime import datetime, timedelta

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone
from model_utils.models import TimeStampedModel


class CursoTipo(models.TextChoices):
    CALIENTE = 'CALIENTE', 'Caliente'
    ALTURA = 'ALTURA', 'Altura'
    ESPACIO_CONFINADO = 'ESPACIO_CONFINADO', 'Espacio confinado'
    ELECTRICO = 'ELECTRICO', 'Eléctrico'
    EXCAVACION = 'EXCAVACION', 'Excavación'
    IZAJE = 'IZAJE', 'Izaje'


class CertificadoTipo(models.TextChoices):
    SCTR = 'SCTR', 'SCTR'
    INDUCCION = 'INDUCCION', 'Inducción'
    CURSOS = 'CURSOS', 'Cursos'
    APTITUD_MEDICA = 'APTITUD_MEDICA', 'Aptitud médica'


def certificado_upload_path(instance, filename):
    extension = filename.rsplit('.', 1)[-1] if '.' in filename else ''
    base = instance.trabajador.dni if instance.trabajador_id else instance.empresa.ruc
    fecha = instance.fecha_emision
    nombre = datetime.now().strftime('%d%m%Y%H%M%S')
    nombre_archivo = f'{base}_{nombre}.{extension}' if extension else f'{base}_{nombre}'
    empresa_id = instance.trabajador.empresa_id if instance.trabajador_id else instance.empresa_id
    return f'certificados/empresa_{empresa_id}/{fecha:%Y}/{fecha:%m}/{nombre_archivo}'


class Empresa(TimeStampedModel):

    nombre = models.CharField(max_length=150)
    ruc = models.CharField(max_length=11, unique=True)

    homologado = models.BooleanField(default=False, db_index=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ('nombre',)
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'

    def __str__(self):
        return self.nombre

    def actualizar_homologado(self):
        trabajadores = self.trabajadores.all()
        nuevo_valor = trabajadores.exists() and not trabajadores.filter(habilitado=False).exists()
        if self.homologado != nuevo_valor:
            self.homologado = nuevo_valor
            self.save(update_fields=['homologado'])


class Trabajador(TimeStampedModel):
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
    cargo = models.CharField(max_length=150, blank=True)

    habilitado = models.BooleanField(default=True, db_index=True)
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


class Incidencia(TimeStampedModel):

    trabajador = models.ForeignKey(Trabajador, on_delete=models.CASCADE, related_name='incidencias')
    descripcion = models.TextField()
    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Incidencia'
        verbose_name_plural = 'Incidencias'

    def __str__(self):
        return f'Incidencia - {self.trabajador}'


class Certificado(TimeStampedModel):

    SCTR = CertificadoTipo.SCTR
    INDUCCION = CertificadoTipo.INDUCCION
    CURSOS = CertificadoTipo.CURSOS
    APTITUD_MEDICA = CertificadoTipo.APTITUD_MEDICA
    CURSO_CHOICES = CursoTipo.choices
    TIPO_CHOICES = CertificadoTipo.choices

    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, null=True, blank=True, related_name='certificados')
    trabajador = models.ForeignKey(Trabajador, on_delete=models.CASCADE, null=True, blank=True, related_name='certificados')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    curso = models.CharField(max_length=30, choices=CURSO_CHOICES, null=True, blank=True)
    fecha_emision = models.DateField()
    fecha_vencimiento = models.DateField()
    archivo = models.FileField(upload_to=certificado_upload_path)

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Certificado'
        verbose_name_plural = 'Certificados'
        constraints = [
            models.UniqueConstraint(
                fields=('trabajador', 'tipo'),
                condition=Q(trabajador__isnull=False, curso__isnull=True),
                name='certificado_unico_tipo_trabajador',
            ),
            models.UniqueConstraint(
                fields=('trabajador', 'curso'),
                condition=Q(trabajador__isnull=False, tipo='CURSOS', curso__isnull=False),
                name='certificado_unico_curso_trabajador',
            ),
            models.UniqueConstraint(fields=('empresa', 'tipo'), condition=Q(empresa__isnull=False, tipo='SCTR'), name='certificado_unico_sctr_empresa'),
            models.CheckConstraint(
                check=(Q(tipo='SCTR', empresa__isnull=False, trabajador__isnull=True, curso__isnull=True) | Q(tipo__in=('INDUCCION', 'APTITUD_MEDICA'), trabajador__isnull=False, empresa__isnull=True, curso__isnull=True) | Q(tipo='CURSOS', trabajador__isnull=False, empresa__isnull=True, curso__isnull=False)),
                name='certificado_propietario_segun_tipo',
            ),
            models.CheckConstraint(
                check=Q(fecha_vencimiento__gte=models.F('fecha_emision')),
                name='certificado_fecha_vencimiento_no_antes_de_emision',
            ),
        ]

    def __str__(self):
        curso = f' - {self.get_curso_display()}' if self.curso else ''
        return f'{self.get_tipo_display()}{curso} - {self.trabajador or self.empresa}'

    def save(self, *args, **kwargs):
        archivo_anterior = None
        if self.pk:
            archivo_anterior = Certificado.objects.filter(pk=self.pk).values_list('archivo', flat=True).first()
        super().save(*args, **kwargs)
        if archivo_anterior and archivo_anterior != self.archivo.name:
            self._eliminar_archivo(archivo_anterior)

    def delete(self, *args, **kwargs):
        archivo = self.archivo.name
        result = super().delete(*args, **kwargs)
        if archivo:
            self._eliminar_archivo(archivo)
        return result

    @staticmethod
    def _eliminar_archivo(nombre):
        from django.core.files.storage import default_storage
        if default_storage.exists(nombre):
            default_storage.delete(nombre)

    @property
    def estado(self):
        hoy = timezone.localdate()
        if self.fecha_vencimiento < hoy:
            return 'Vencido'
        if self.fecha_vencimiento <= hoy + timedelta(days=30):
            return 'Próximo a vencer'
        return 'Vigente'
