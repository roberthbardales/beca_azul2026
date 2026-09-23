from datetime import datetime, timedelta

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone
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

    habilitado = models.BooleanField(default=True, db_index=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ('nombre',)
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'

    def __str__(self):
        return self.nombre

    def actualizar_habilitado(self):
        tiene_deshabilitado = self.trabajadores.filter(habilitado=False).exists()
        nuevo_valor = not tiene_deshabilitado
        if self.habilitado != nuevo_valor:
            self.habilitado = nuevo_valor
            self.save(update_fields=['habilitado'])


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


class CategoriaCurso(TimeStampedModel):
    nombre = models.CharField(max_length=150, unique=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ('nombre',)
        verbose_name = 'Categoría de curso'
        verbose_name_plural = 'Categorías de cursos'

    def __str__(self):
        return self.nombre


class Certificado(TimeStampedModel):

    SCTR = 'SCTR'
    INDUCCION = 'INDUCCION'
    CURSOS = 'CURSOS'
    APTITUD_MEDICA = 'APTITUD_MEDICA'
    TIPO_CHOICES = (
        (SCTR, 'SCTR'),
        (INDUCCION, 'Inducción'),
        (CURSOS, 'Cursos'),
        (APTITUD_MEDICA, 'Aptitud médica'),
    )

    trabajador = models.ForeignKey(Trabajador, on_delete=models.CASCADE, related_name='certificados')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    categoria = models.ForeignKey(
        CategoriaCurso, on_delete=models.PROTECT, null=True, blank=True, related_name='certificados'
    )
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
                condition=Q(categoria__isnull=True),
                name='certificado_unico_tipo_trabajador',
            ),
            models.UniqueConstraint(
                fields=('trabajador', 'categoria'),
                condition=Q(tipo='CURSOS'),
                name='certificado_unico_categoria_curso_trabajador',
            ),
            models.CheckConstraint(
                check=Q(fecha_vencimiento__gte=models.F('fecha_emision')),
                name='certificado_fecha_vencimiento_no_antes_de_emision',
            ),
        ]

    def __str__(self):
        categoria = f' - {self.categoria}' if self.categoria else ''
        return f'{self.get_tipo_display()}{categoria} - {self.trabajador}'

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
