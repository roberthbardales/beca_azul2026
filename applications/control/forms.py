from django import forms
from django.core.exceptions import ValidationError
from django.db import transaction
from django.forms import formset_factory

from .models import Certificado, Empresa, Incidencia, Trabajador

MAX_PDF_SIZE = 2 * 1024 * 1024
PDF_SIGNATURE = b'%PDF-'
DATE_RANGE_ERROR = 'La fecha no puede ser anterior a la emisión.'
CERTIFICATE_DATE_RANGE_ERROR = 'La fecha de vencimiento no puede ser anterior a la fecha de emisión.'
DNI_ERROR = 'El DNI debe contener exactamente 8 dígitos numéricos.'
DUPLICATE_WORKER_ERROR = 'Ya existe un trabajador con este documento en la empresa seleccionada.'


def add_date_range_error(form, cleaned_data, emission_field, expiration_field, message):
    emission = cleaned_data.get(emission_field)
    expiration = cleaned_data.get(expiration_field)
    if emission and expiration and expiration < emission:
        form.add_error(expiration_field, message)


def validate_pdf(value):
    if not value.name.lower().endswith('.pdf'):
        raise ValidationError('El archivo debe estar en formato PDF.')
    if value.size > MAX_PDF_SIZE:
        raise ValidationError('El archivo PDF no puede superar los 2 MB.')
    position = value.tell()
    try:
        value.seek(0)
        if value.read(len(PDF_SIGNATURE)) != PDF_SIGNATURE:
            raise ValidationError('El archivo no contiene un PDF válido.')
    finally:
        value.seek(position)


class EmpresaForm(forms.ModelForm):
    sctr_archivo = forms.FileField(required=False, validators=[validate_pdf])
    sctr_fecha_emision = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    sctr_fecha_vencimiento = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)

    class Meta:
        model = Empresa
        fields = ('nombre', 'ruc')

    def __init__(self, *args, **kwargs):
        can_edit_sctr = kwargs.pop('can_edit_sctr', False)
        super().__init__(*args, **kwargs)
        if not can_edit_sctr:
            self.fields.pop('sctr_archivo', None)
            self.fields.pop('sctr_fecha_emision', None)
            self.fields.pop('sctr_fecha_vencimiento', None)
        certificado = self.instance.certificados.filter(tipo=Certificado.SCTR).first() if self.instance.pk else None
        if certificado:
            self.initial.update(sctr_archivo=certificado.archivo, sctr_fecha_emision=certificado.fecha_emision.isoformat(), sctr_fecha_vencimiento=certificado.fecha_vencimiento.isoformat())

    def clean(self):
        cleaned = super().clean()
        emision = cleaned.get('sctr_fecha_emision')
        vencimiento = cleaned.get('sctr_fecha_vencimiento')
        if cleaned.get('sctr_archivo') and not emision:
            self.add_error('sctr_fecha_emision', 'La fecha de emisión es obligatoria.')
        if cleaned.get('sctr_archivo') and not vencimiento:
            self.add_error('sctr_fecha_vencimiento', 'La fecha de vencimiento es obligatoria.')
        add_date_range_error(
            self,
            cleaned,
            'sctr_fecha_emision',
            'sctr_fecha_vencimiento',
            DATE_RANGE_ERROR,
        )
        return cleaned

    @transaction.atomic
    def save(self, commit=True):
        empresa = super().save(commit=commit)
        archivo = self.cleaned_data.get('sctr_archivo')
        if commit and archivo:
            certificado, _ = Certificado.objects.get_or_create(empresa=empresa, tipo=Certificado.SCTR)
            certificado.fecha_emision = self.cleaned_data['sctr_fecha_emision']
            certificado.fecha_vencimiento = self.cleaned_data['sctr_fecha_vencimiento']
            certificado.archivo = archivo
            certificado.save()
        return empresa

    def clean_ruc(self):
        ruc = self.cleaned_data.get('ruc')
        if ruc and (not ruc.isdigit() or len(ruc) != 11):
            raise forms.ValidationError('El RUC debe contener exactamente 11 dígitos numéricos.')
        return ruc


class SCTRForm(forms.ModelForm):
    archivo = forms.FileField(required=False, validators=[validate_pdf])
    fecha_emision = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    fecha_vencimiento = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Certificado
        fields = ('archivo', 'fecha_emision', 'fecha_vencimiento')

    def __init__(self, *args, empresa=None, **kwargs):
        self.empresa = empresa
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.initial.update(
                fecha_emision=self.instance.fecha_emision,
                fecha_vencimiento=self.instance.fecha_vencimiento,
            )

    def clean(self):
        cleaned = super().clean()
        if not self.instance.pk and not cleaned.get('archivo'):
            self.add_error('archivo', 'El archivo SCTR es obligatorio.')
        add_date_range_error(
            self,
            cleaned,
            'fecha_emision',
            'fecha_vencimiento',
            DATE_RANGE_ERROR,
        )
        return cleaned

    def save(self, commit=True):
        certificado = super().save(commit=False)
        certificado.empresa = self.empresa
        certificado.trabajador = None
        certificado.tipo = Certificado.SCTR
        if not self.cleaned_data.get('archivo') and certificado.pk:
            certificado.archivo = Certificado.objects.get(pk=certificado.pk).archivo
        if commit:
            certificado.save()
        return certificado


class TrabajadorForm(forms.ModelForm):
    empresa = forms.ModelChoiceField(
        label='Empresa',
        queryset=Empresa.objects.filter(activo=True),
        empty_label='--- Seleccione empresa ---',
    )

    class Meta:
        model = Trabajador
        fields = (
            'empresa', 'tipo_documento', 'dni', 'nombres', 'apellidos',
            'cargo',
        )

    def clean_dni(self):
        dni = self.cleaned_data.get('dni', '').strip()
        empresa = self.cleaned_data.get('empresa')
        tipo_documento = self.cleaned_data.get('tipo_documento')
        if tipo_documento == Trabajador.DNI and not (dni.isdigit() and len(dni) == 8):
            raise forms.ValidationError(DNI_ERROR)
        if dni and empresa:
            qs = Trabajador.objects.filter(empresa=empresa, dni__iexact=dni, activo=True)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError(DUPLICATE_WORKER_ERROR)
        return dni

class TrabajadorEmpresaForm(forms.ModelForm):
    induccion_archivo = forms.FileField(required=False, validators=[validate_pdf])
    induccion_fecha_emision = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    induccion_fecha_vencimiento = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    aptitud_medica_archivo = forms.FileField(required=False, validators=[validate_pdf])
    aptitud_medica_fecha_emision = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    aptitud_medica_fecha_vencimiento = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)

    class Meta:
        model = Trabajador
        fields = (
            'tipo_documento', 'dni', 'nombres', 'apellidos',
            'cargo',
        )

    def __init__(self, *args, **kwargs):
        self.empresa = kwargs.pop('empresa', None)
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            for prefix in ('induccion', 'aptitud_medica'):
                for suffix in ('archivo', 'fecha_emision', 'fecha_vencimiento'):
                    self.fields[f'{prefix}_{suffix}'].required = True
        else:
            for certificado in self.instance.certificados.all():
                if certificado.tipo in (Certificado.INDUCCION, Certificado.APTITUD_MEDICA):
                    prefix = certificado.tipo.lower()
                    self.initial[f'{prefix}_archivo'] = certificado.archivo
                    self.initial[f'{prefix}_fecha_emision'] = certificado.fecha_emision.isoformat()
                    self.initial[f'{prefix}_fecha_vencimiento'] = certificado.fecha_vencimiento.isoformat()

    def clean_dni(self):
        dni = self.cleaned_data.get('dni', '').strip()
        tipo_documento = self.cleaned_data.get('tipo_documento')
        if tipo_documento == Trabajador.DNI and not (dni.isdigit() and len(dni) == 8):
            raise forms.ValidationError(DNI_ERROR)
        empresa = self.empresa or getattr(self.instance, 'empresa', None)
        if dni and empresa:
            qs = Trabajador.objects.filter(empresa=empresa, dni__iexact=dni, activo=True)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError(DUPLICATE_WORKER_ERROR)
        return dni

    def clean(self):
        cleaned = super().clean()
        for prefix in ('induccion', 'aptitud_medica'):
            archivo = cleaned.get(f'{prefix}_archivo')
            fecha_emision = cleaned.get(f'{prefix}_fecha_emision')
            fecha_vencimiento = cleaned.get(f'{prefix}_fecha_vencimiento')
            certificado_existente = (
                self.instance.certificados.filter(tipo=prefix.upper()).first()
                if self.instance.pk
                else None
            )
            if not certificado_existente and any((archivo, fecha_emision, fecha_vencimiento)):
                for field_name, value in (
                    (f'{prefix}_archivo', archivo),
                    (f'{prefix}_fecha_emision', fecha_emision),
                    (f'{prefix}_fecha_vencimiento', fecha_vencimiento),
                ):
                    if not value:
                        self.add_error(field_name, 'Complete archivo y fechas para registrar el certificado.')
            elif certificado_existente and (fecha_emision or fecha_vencimiento):
                if not fecha_emision:
                    self.add_error(f'{prefix}_fecha_emision', 'La fecha de emisión es obligatoria.')
                if not fecha_vencimiento:
                    self.add_error(f'{prefix}_fecha_vencimiento', 'La fecha de vencimiento es obligatoria.')
            add_date_range_error(
                self,
                cleaned,
                f'{prefix}_fecha_emision',
                f'{prefix}_fecha_vencimiento',
                DATE_RANGE_ERROR,
            )
        return cleaned

    @transaction.atomic
    def save(self, commit=True):
        trabajador = super().save(commit=False)
        if self.empresa:
            trabajador.empresa = self.empresa
        if commit:
            trabajador.save()
            for tipo, prefix in (
                (Certificado.INDUCCION, 'induccion'),
                (Certificado.APTITUD_MEDICA, 'aptitud_medica'),
            ):
                archivo = self.cleaned_data.get(f'{prefix}_archivo')
                fecha_emision = self.cleaned_data.get(f'{prefix}_fecha_emision')
                fecha_vencimiento = self.cleaned_data.get(f'{prefix}_fecha_vencimiento')
                certificado = Certificado.objects.filter(trabajador=trabajador, tipo=tipo).first()
                if certificado and not any((archivo, fecha_emision, fecha_vencimiento)):
                    continue
                if not certificado and not all((archivo, fecha_emision, fecha_vencimiento)):
                    continue
                certificado = certificado or Certificado(trabajador=trabajador, tipo=tipo)
                certificado.fecha_emision = fecha_emision
                certificado.fecha_vencimiento = fecha_vencimiento
                if archivo:
                    certificado.archivo = archivo
                certificado.save()
        return trabajador


class IncidenciaForm(forms.ModelForm):
    class Meta:
        model = Incidencia
        fields = ('descripcion',)
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4}),
        }

    def clean_descripcion(self):
        descripcion = self.cleaned_data.get('descripcion', '').strip()
        if not descripcion:
            raise forms.ValidationError('La descripción es obligatoria.')
        return descripcion


class CertificadoForm(forms.ModelForm):
    class Meta:
        model = Certificado
        fields = ('tipo', 'curso', 'fecha_emision', 'fecha_vencimiento', 'archivo')
        widgets = {
            'fecha_emision': forms.DateInput(attrs={'type': 'date'}),
            'fecha_vencimiento': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tipo'].choices = tuple(choice for choice in self.fields['tipo'].choices if choice[0] != Certificado.SCTR)
        self.fields['curso'].required = False
        self.fields['archivo'].validators.append(validate_pdf)

    def clean(self):
        cleaned = super().clean()
        tipo = cleaned.get('tipo')
        curso = cleaned.get('curso')
        if tipo == Certificado.CURSOS and not curso:
            self.add_error('curso', 'El curso es obligatorio para los certificados de cursos.')
        if tipo != Certificado.CURSOS and curso:
            self.add_error('curso', 'El curso solo aplica a los certificados de cursos.')
        if tipo and self.instance.trabajador_id:
            qs = Certificado.objects.filter(trabajador=self.instance.trabajador, tipo=tipo)
            qs = qs.filter(curso=curso) if tipo == Certificado.CURSOS else qs.filter(curso__isnull=True)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists() and tipo != Certificado.CURSOS:
                self.add_error('tipo', 'Ya existe un certificado para este requisito.')
        add_date_range_error(
            self,
            cleaned,
            'fecha_emision',
            'fecha_vencimiento',
            CERTIFICATE_DATE_RANGE_ERROR,
        )
        return cleaned


class CertificadoCargaForm(forms.ModelForm):
    class Meta:
        model = Certificado
        fields = ('tipo', 'curso', 'fecha_emision', 'fecha_vencimiento', 'archivo')
        widgets = {
            'fecha_emision': forms.DateInput(attrs={'type': 'date'}),
            'fecha_vencimiento': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tipo'].widget = forms.HiddenInput()
        self.fields['tipo'].initial = Certificado.CURSOS
        self.fields['curso'].required = False
        self.fields['curso'].widget = forms.HiddenInput()
        self.fields['fecha_emision'].required = False
        self.fields['fecha_vencimiento'].required = False
        self.fields['archivo'].required = False
        self.fields['archivo'].validators.append(validate_pdf)

    def clean(self):
        cleaned = super().clean()
        if not cleaned:
            return cleaned
        tipo = cleaned.get('tipo')
        curso = cleaned.get('curso')
        if tipo and tipo != Certificado.CURSOS:
            self.add_error('tipo', 'Este formulario solo permite certificados de cursos.')
        if tipo == Certificado.CURSOS and not curso:
            self.add_error('curso', 'El curso es obligatorio para los certificados de cursos.')
        if tipo == Certificado.SCTR and curso:
            self.add_error('curso', 'SCTR no utiliza curso.')
        if tipo == Certificado.CURSOS and curso:
            self.cleaned_data['curso'] = curso
        emision = cleaned.get('fecha_emision')
        vencimiento = cleaned.get('fecha_vencimiento')
        archivo = cleaned.get('archivo')
        archivo_existente = bool(self.initial.get('archivo'))
        if any((archivo, emision, vencimiento)) and not all((archivo or archivo_existente, emision, vencimiento)):
            for field_name in ('archivo', 'fecha_emision', 'fecha_vencimiento'):
                if field_name == 'archivo' and archivo_existente:
                    continue
                if not cleaned.get(field_name):
                    self.add_error(field_name, 'Complete este campo para registrar el certificado.')
        add_date_range_error(
            self,
            cleaned,
            'fecha_emision',
            'fecha_vencimiento',
            DATE_RANGE_ERROR,
        )
        return cleaned


class CertificadoCargaFormSetBase(forms.BaseFormSet):
    def clean(self):
        super().clean()
        vistos = set()
        for form in self.forms:
            if not getattr(form, 'cleaned_data', None):
                continue
            tipo = form.cleaned_data.get('tipo')
            curso = form.cleaned_data.get('curso')
            if not tipo:
                continue
            clave = (tipo, curso if curso else None)
            if clave in vistos:
                raise forms.ValidationError('No se puede repetir el mismo tipo o categoría de certificado.')
            vistos.add(clave)


CertificadoCargaFormSet = formset_factory(CertificadoCargaForm, formset=CertificadoCargaFormSetBase, extra=0)
