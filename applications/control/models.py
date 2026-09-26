from datetime import timedelta
from uuid import uuid4

from django.conf import settings
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.db import models
from django.db.models import Case, CharField, Q, Value, When
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


class TipoDocumento(models.TextChoices):
    DNI = 'DNI', 'DNI'
    CE = 'CE', 'Carné de extranjería'
    PASAPORTE = 'PASAPORTE', 'Pasaporte'


class CertificadoQuerySet(models.QuerySet):
    def with_estado(self):
        hoy = timezone.localdate()
        return self.annotate(
            estado_queryset=Case(
                When(fecha_vencimiento__lt=hoy, then=Value('Vencido')),
                When(fecha_vencimiento__lte=hoy + timedelta(days=30), then=Value('Próximo a vencer')),
                default=Value('Vigente'),
                output_field=CharField(),
            )
        )

    def filter_estado(self, estado):
        return self.with_estado().filter(estado_queryset=estado)


def certificado_upload_path(instance, filename):
    extension = filename.rsplit('.', 1)[-1] if '.' in filename else ''
    if instance.trabajador_id:
        base = instance.trabajador.dni
        empresa_id = instance.trabajador.empresa_id
    elif instance.empresa_id:
        base = instance.empresa.ruc
        empresa_id = instance.empresa_id
    else:
        raise ValueError('El certificado debe pertenecer a una empresa o trabajador.')

    fecha = instance.fecha_emision
    nombre = uuid4().hex
    nombre_archivo = f'{base}_{nombre}.{extension}' if extension else f'{base}_{nombre}'
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
        trabajadores = self.trabajadores.filter(activo=True)
        nuevo_valor = trabajadores.exists() and not trabajadores.filter(habilitado=False).exists()
        if self.homologado != nuevo_valor:
            self.homologado = nuevo_valor
            self.save(update_fields=['homologado'])


class Trabajador(TimeStampedModel):
    DNI = TipoDocumento.DNI
    CE = TipoDocumento.CE
    PASAPORTE = TipoDocumento.PASAPORTE
    TIPO_DOCUMENTO_CHOICES = TipoDocumento.choices

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
    fecha_vencimiento = models.DateField(db_index=True)
    archivo = models.FileField(upload_to=certificado_upload_path)
    objects = CertificadoQuerySet.as_manager()

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
                condition=Q(
                    trabajador__isnull=False,
                    tipo=CertificadoTipo.CURSOS,
                    curso__isnull=False,
                ),
                name='certificado_unico_curso_trabajador',
            ),
            models.UniqueConstraint(
                fields=('empresa', 'tipo'),
                condition=Q(empresa__isnull=False, tipo=CertificadoTipo.SCTR),
                name='certificado_unico_sctr_empresa',
            ),
            models.CheckConstraint(
                check=(
                    Q(
                        tipo=CertificadoTipo.SCTR,
                        empresa__isnull=False,
                        trabajador__isnull=True,
                        curso__isnull=True,
                    )
                    | Q(
                        tipo__in=(CertificadoTipo.INDUCCION, CertificadoTipo.APTITUD_MEDICA),
                        trabajador__isnull=False,
                        empresa__isnull=True,
                        curso__isnull=True,
                    )
                    | Q(
                        tipo=CertificadoTipo.CURSOS,
                        trabajador__isnull=False,
                        empresa__isnull=True,
                        curso__isnull=False,
                    )
                ),
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

    def clean(self):
        super().clean()
        errores = {}

        if self.tipo == self.SCTR:
            if not self.empresa_id or self.trabajador_id or self.curso:
                errores[NON_FIELD_ERRORS] = (
                    'Un certificado SCTR debe pertenecer a una empresa y no tener trabajador ni curso.',
                )
        elif self.tipo:
            if not self.trabajador_id or self.empresa_id:
                errores[NON_FIELD_ERRORS] = (
                    'Este tipo de certificado debe pertenecer a un trabajador y no a una empresa.',
                )
            elif self.tipo == self.CURSOS and not self.curso:
                errores['curso'] = ('Un certificado de cursos debe especificar un curso.',)
            elif self.tipo != self.CURSOS and self.curso:
                errores['curso'] = ('Este tipo de certificado no puede tener un curso.',)

        if self.fecha_emision and self.fecha_vencimiento and self.fecha_vencimiento < self.fecha_emision:
            errores['fecha_vencimiento'] = (
                'La fecha de vencimiento no puede ser anterior a la fecha de emisión.',
            )

        if errores:
            raise ValidationError(errores)

    def save(self, *args, **kwargs):
        self.full_clean()
        archivo_anterior = None
        if self.pk:
            archivo_anterior = Certificado.objects.filter(pk=self.pk).values_list('archivo', flat=True).first()
        super().save(*args, **kwargs)
        if archivo_anterior and archivo_anterior != self.archivo.name:
            self._eliminar_archivo(archivo_anterior)

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
