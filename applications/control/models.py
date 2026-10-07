from datetime import timedelta
from uuid import uuid4

from django.conf import settings
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.db import models
from django.db.models import Prefetch, Q
from django.utils import timezone
from django.utils.functional import cached_property
from model_utils.models import TimeStampedModel


class CursoTipo(models.TextChoices):
    CALIENTE = 'CALIENTE', 'T. Caliente.'
    ALTURA = 'ALTURA', 'T. Altura.'
    ESPACIO_CONFINADO = 'ESPACIO_CONFINADO', 'T. Esp. Confinado.'
    ELECTRICO = 'ELECTRICO', 'T. Eléctricos.'
    EXCAVACION = 'EXCAVACION', 'T. Exca./ Perf'
    IZAJE = 'IZAJE', 'T. de izaje.'


class CertificadoTipo(models.TextChoices):
    SCTR_PENSION = 'SCTR_PENSION', 'SCTR pensión'
    SCTR_SALUD = 'SCTR_SALUD', 'SCTR salud'
    HOMOLOGACION = 'HOMOLOGACION', 'Homologación'
    INDUCCION = 'INDUCCION', 'Inducción'
    CURSOS = 'CURSOS', 'Cursos'
    APTITUD_MEDICA = 'APTITUD_MEDICA', 'Aptitud médica'


class TipoDocumento(models.TextChoices):
    DNI = 'DNI', 'DNI'
    CE = 'CE', 'Carné de extranjería'
    PASAPORTE = 'PASAPORTE', 'Pasaporte'


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
    correo = models.EmailField(unique=True)
    representante_legal = models.CharField(max_length=150, blank=True)

    homologacion = models.BooleanField(default=False, db_index=True)
    sctr_pension_aprobado = models.BooleanField(default=False)
    sctr_salud_aprobado = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ('nombre',)
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'

    def __str__(self):
        return self.nombre

    def _certificado_vigente(self, tipo, attr_name):
        certificado = self._certificado(tipo, attr_name)
        return bool(certificado and certificado.esta_vigente)

    def _certificado(self, tipo, attr_name):
        certificados = getattr(self, attr_name, None)
        if certificados is None:
            certificados = getattr(self, 'certificados_habilitacion', None)
        if certificados is None:
            certificados = getattr(self, 'sctr_certificados_heredados', None)
        if certificados is None:
            return self.certificados.filter(tipo=tipo).first()
        else:
            return next((item for item in certificados if item.tipo == tipo), None)

    def _certificado_estado(self, tipo, attr_name, aprobado=True):
        certificado = self._certificado(tipo, attr_name)
        if not certificado or not certificado.archivo or not certificado.archivo.storage.exists(certificado.archivo.name):
            return 'Pendiente'
        if not certificado.esta_vigente:
            return 'Vencido'
        if not aprobado:
            return 'Desaprobado'
        return 'Vigente'

    @cached_property
    def sctr_pension_vigente(self):
        return self._certificado_vigente(CertificadoTipo.SCTR_PENSION, 'sctr_pension_certificados')

    @cached_property
    def sctr_salud_vigente(self):
        return self._certificado_vigente(CertificadoTipo.SCTR_SALUD, 'sctr_salud_certificados')

    @property
    def sctr_pension_estado(self):
        return self._certificado_estado(CertificadoTipo.SCTR_PENSION, 'sctr_pension_certificados', self.sctr_pension_aprobado)

    @property
    def sctr_salud_estado(self):
        return self._certificado_estado(CertificadoTipo.SCTR_SALUD, 'sctr_salud_certificados', self.sctr_salud_aprobado)

    @cached_property
    def homologacion_vigente(self):
        return self._certificado_vigente(CertificadoTipo.HOMOLOGACION, 'homologacion_certificados')

    @property
    def homologacion_estado(self):
        return self._certificado_estado(CertificadoTipo.HOMOLOGACION, 'homologacion_certificados', self.homologacion)

    def invalidar_homologacion_si_corresponde(self):
        homologacion_valida = (
            self.homologacion_vigente
            and self.sctr_pension_aprobado
            and self.sctr_salud_aprobado
            and self.sctr_empresa_vigente(CertificadoTipo.SCTR_PENSION)
            and self.sctr_empresa_vigente(CertificadoTipo.SCTR_SALUD)
        )
        if self.homologacion and not homologacion_valida:
            type(self).objects.filter(pk=self.pk, homologacion=True).update(homologacion=False)
            self.homologacion = False
            return True
        return False

    def sctr_empresa_vigente(self, tipo):
        attr_name = {
            CertificadoTipo.SCTR_PENSION: 'sctr_pension_certificados',
            CertificadoTipo.SCTR_SALUD: 'sctr_salud_certificados',
        }[tipo]
        return self._certificado_vigente(tipo, attr_name)

    @classmethod
    def sincronizar_homologaciones(cls):
        empresas = cls.objects.filter(homologacion=True).prefetch_related(
            Prefetch(
                'certificados',
                queryset=Certificado.objects.filter(tipo=CertificadoTipo.HOMOLOGACION),
                to_attr='homologacion_certificados',
            )
        )
        for empresa in empresas:
            empresa.invalidar_homologacion_si_corresponde()

    def clean(self):
        super().clean()

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

    sctr_pension = models.BooleanField(default=False)
    sctr_salud = models.BooleanField(default=False)
    habilitado = models.BooleanField(default=True, db_index=True)
    activo = models.BooleanField(default=True)

    @cached_property
    def habilitado_efectivo(self):
        empresa = self.empresa
        certificados = {
            certificado.tipo: certificado
            for certificado in self.certificados.all()
            if certificado.tipo in (CertificadoTipo.INDUCCION, CertificadoTipo.APTITUD_MEDICA)
        }
        requisitos_trabajador = (
            certificados.get(CertificadoTipo.INDUCCION),
            certificados.get(CertificadoTipo.APTITUD_MEDICA),
        )
        cursos_obligatorios = self.cursos_obligatorios.values_list('curso', flat=True)
        cursos = {
            certificado.curso: certificado
            for certificado in self.certificados.all()
            if certificado.tipo == CertificadoTipo.CURSOS
        }
        return bool(
            self.habilitado
            and self.activo
            and empresa.activo
            and empresa.sctr_pension_aprobado
            and empresa.sctr_salud_aprobado
            and empresa.homologacion
            and empresa.sctr_pension_vigente
            and empresa.sctr_salud_vigente
            and empresa.homologacion_vigente
            and all(certificado and certificado.validacion_vigente for certificado in requisitos_trabajador)
            and all(cursos.get(curso) and cursos[curso].validacion_vigente for curso in cursos_obligatorios)
        )

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

    @property
    def sctr(self):
        """Compatibility alias for code that still reads the old field."""
        return self.sctr_pension

    def _sctr_empresa_vigente(self, tipo):
        certificados = getattr(self.empresa, 'sctr_certificados_heredados', None)
        if certificados is None:
            certificado = self.empresa.certificados.filter(tipo=tipo).first()
        else:
            certificado = next((item for item in certificados if item.tipo == tipo), None)
        return bool(certificado and certificado.esta_vigente)

    @property
    def sctr_pension_efectivo(self):
        return self.empresa.sctr_pension_aprobado and self._sctr_empresa_vigente(CertificadoTipo.SCTR_PENSION)

    @property
    def sctr_salud_efectivo(self):
        return self.empresa.sctr_salud_aprobado and self._sctr_empresa_vigente(CertificadoTipo.SCTR_SALUD)

    @property
    def sctr_pension_estado(self):
        return self.empresa.sctr_pension_estado

    @property
    def sctr_salud_estado(self):
        return self.empresa.sctr_salud_estado

    @property
    def sctr_pension_estado_detalle(self):
        if self.empresa.sctr_pension_aprobado and self.sctr_pension_efectivo:
            return 'Aprobado y vigente'
        if self.empresa.sctr_pension_aprobado:
            return 'Aprobado, vencido'
        return 'Desaprobado'

    @property
    def sctr_salud_estado_detalle(self):
        if self.empresa.sctr_salud_aprobado and self.sctr_salud_efectivo:
            return 'Aprobado y vigente'
        if self.empresa.sctr_salud_aprobado:
            return 'Aprobado, vencido'
        return 'Desaprobado'

    def _estado_certificado_trabajador(self, tipo, curso=None):
        certificados = getattr(self, 'certificados_lista', None)
        if certificados is None:
            certificados = self.certificados.all()
        certificado = next(
            (
                item for item in certificados
                if item.tipo == tipo and (curso is None or item.curso == curso)
            ),
            None,
        )
        return certificado.estado if certificado else 'Pendiente'

    def _estado_validacion_certificado(self, tipo):
        certificados = getattr(self, 'certificados_lista', None)
        if certificados is None:
            certificados = self.certificados.all()
        certificado = next((item for item in certificados if item.tipo == tipo), None)
        if not certificado:
            return 'Pendiente'
        if certificado.fecha_vencimiento < timezone.localdate():
            return 'Vencido'
        return 'Vigente' if certificado.validacion_vigente else 'Pendiente'

    @property
    def estado_induccion(self):
        return self._estado_validacion_certificado(CertificadoTipo.INDUCCION)

    @property
    def estado_aptitud_medica(self):
        return self._estado_validacion_certificado(CertificadoTipo.APTITUD_MEDICA)

    def estado_curso(self, curso):
        cursos_obligatorios = getattr(self, 'cursos_obligatorios_lista', None)
        if cursos_obligatorios is None:
            cursos_obligatorios = self.cursos_obligatorios.values_list('curso', flat=True)
        else:
            cursos_obligatorios = [requisito.curso for requisito in cursos_obligatorios]
        if curso not in cursos_obligatorios:
            return '-'

        certificados = getattr(self, 'certificados_lista', None)
        if certificados is None:
            certificados = self.certificados.all()
        certificado = next(
            (item for item in certificados if item.tipo == CertificadoTipo.CURSOS and item.curso == curso),
            None,
        )
        if not certificado:
            return 'Pendiente'
        if certificado.fecha_vencimiento < timezone.localdate():
            return 'Vencido'
        return 'Vigente' if certificado.validacion_vigente else 'Pendiente'

    @property
    def estado_curso_caliente(self):
        return self.estado_curso('CALIENTE')

    @property
    def estado_curso_altura(self):
        return self.estado_curso('ALTURA')

    @property
    def estado_curso_espacio_confinado(self):
        return self.estado_curso('ESPACIO_CONFINADO')

    @property
    def estado_curso_electrico(self):
        return self.estado_curso('ELECTRICO')

    @property
    def estado_curso_excavacion(self):
        return self.estado_curso('EXCAVACION')

    @property
    def estado_curso_izaje(self):
        return self.estado_curso('IZAJE')


class CursoObligatorio(TimeStampedModel):
    trabajador = models.ForeignKey(Trabajador, on_delete=models.CASCADE, related_name='cursos_obligatorios')
    curso = models.CharField(max_length=30, choices=CursoTipo.choices)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=('trabajador', 'curso'), name='curso_obligatorio_unico_trabajador'),
        ]


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

    SCTR_PENSION = CertificadoTipo.SCTR_PENSION
    SCTR_SALUD = CertificadoTipo.SCTR_SALUD
    SCTR = SCTR_PENSION
    HOMOLOGACION = CertificadoTipo.HOMOLOGACION
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
    validado = models.BooleanField(default=False)
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
                condition=Q(empresa__isnull=False, tipo__in=(CertificadoTipo.SCTR_PENSION, CertificadoTipo.SCTR_SALUD, CertificadoTipo.HOMOLOGACION)),
                name='certificado_unico_empresa_tipo',
            ),
            models.CheckConstraint(
                check=(
                    Q(
                        tipo__in=(CertificadoTipo.SCTR_PENSION, CertificadoTipo.SCTR_SALUD, CertificadoTipo.HOMOLOGACION),
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

    @property
    def esta_vigente(self):
        return bool(
            self.archivo
            and self.archivo.storage.exists(self.archivo.name)
            and self.fecha_vencimiento >= timezone.localdate()
        )

    def clean(self):
        super().clean()
        errores = {}

        if self.tipo in (self.SCTR_PENSION, self.SCTR_SALUD, self.HOMOLOGACION):
            if not self.empresa_id or self.trabajador_id or self.curso:
                errores[NON_FIELD_ERRORS] = (
                    'Este certificado debe pertenecer a una empresa y no tener trabajador ni curso.',
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
            anterior = Certificado.objects.get(pk=self.pk)
            archivo_anterior = anterior.archivo.name
            if (
                self.trabajador_id
                and self.tipo in (self.INDUCCION, self.APTITUD_MEDICA, self.CURSOS)
                and not (set(kwargs.get('update_fields', ())) <= {'validado'})
                and (
                    self.fecha_emision != anterior.fecha_emision
                    or self.fecha_vencimiento != anterior.fecha_vencimiento
                    or self.archivo.name != anterior.archivo.name
                )
            ):
                self.validado = False
                if kwargs.get('update_fields') is not None:
                    kwargs['update_fields'] = set(kwargs['update_fields']) | {'validado'}
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

    @property
    def validacion_vigente(self):
        archivo_requerido = self.tipo != self.INDUCCION
        archivo_disponible = bool(
            self.archivo and self.archivo.storage.exists(self.archivo.name)
        )
        return bool(
            self.validado
            and self.fecha_vencimiento >= timezone.localdate()
            and (not archivo_requerido or archivo_disponible)
        )

    @property
    def validacion_estado(self):
        if self.fecha_vencimiento < timezone.localdate():
            return 'Desaprobado'
        if self.tipo != self.INDUCCION and not (
            self.archivo and self.archivo.storage.exists(self.archivo.name)
        ):
            return 'Pendiente'
        if self.validacion_vigente:
            return 'Vigente'
        return 'Pendiente'
