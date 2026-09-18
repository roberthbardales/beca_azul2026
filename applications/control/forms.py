from datetime import date

from django import forms

from .models import Certificado, Empresa, Trabajador


class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = ('nombre', 'ruc', 'direccion', 'telefono', 'email', 'activo')

    def clean_ruc(self):
        ruc = self.cleaned_data.get('ruc')
        if ruc and (not ruc.isdigit() or len(ruc) != 11):
            raise forms.ValidationError('El RUC debe contener exactamente 11 dígitos numéricos.')
        return ruc


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
            'fecha_nacimiento', 'telefono', 'cargo', 'area',
        )
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_dni(self):
        dni = self.cleaned_data.get('dni', '').strip()
        empresa = self.cleaned_data.get('empresa')
        tipo_documento = self.cleaned_data.get('tipo_documento')
        if tipo_documento == Trabajador.DNI and not (dni.isdigit() and len(dni) == 8):
            raise forms.ValidationError('El DNI debe contener exactamente 8 dígitos numéricos.')
        if dni and empresa:
            qs = Trabajador.objects.filter(empresa=empresa, dni__iexact=dni, activo=True)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError('Ya existe un trabajador con este documento en la empresa seleccionada.')
        return dni

    def clean_fecha_nacimiento(self):
        fecha = self.cleaned_data.get('fecha_nacimiento')
        if fecha and fecha > date.today():
            raise forms.ValidationError('La fecha de nacimiento no puede estar en el futuro.')
        return fecha


class TrabajadorEmpresaForm(forms.ModelForm):
    class Meta:
        model = Trabajador
        fields = (
            'tipo_documento', 'dni', 'nombres', 'apellidos',
            'fecha_nacimiento', 'telefono', 'cargo', 'area',
        )
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        self.empresa = kwargs.pop('empresa', None)
        super().__init__(*args, **kwargs)

    def clean_dni(self):
        dni = self.cleaned_data.get('dni', '').strip()
        tipo_documento = self.cleaned_data.get('tipo_documento')
        if tipo_documento == Trabajador.DNI and not (dni.isdigit() and len(dni) == 8):
            raise forms.ValidationError('El DNI debe contener exactamente 8 dígitos numéricos.')
        empresa = self.empresa or getattr(self.instance, 'empresa', None)
        if dni and empresa:
            qs = Trabajador.objects.filter(empresa=empresa, dni__iexact=dni, activo=True)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError('Ya existe un trabajador con este documento en la empresa seleccionada.')
        return dni

    def clean_fecha_nacimiento(self):
        fecha = self.cleaned_data.get('fecha_nacimiento')
        if fecha and fecha > date.today():
            raise forms.ValidationError('La fecha de nacimiento no puede estar en el futuro.')
        return fecha

    def save(self, commit=True):
        trabajador = super().save(commit=False)
        if self.empresa:
            trabajador.empresa = self.empresa
        if commit:
            trabajador.save()
        return trabajador


class CertificadoForm(forms.ModelForm):
    class Meta:
        model = Certificado
        fields = ('nombre', 'descripcion', 'fecha_emision', 'fecha_vencimiento', 'archivo')
        widgets = {
            'fecha_emision': forms.DateInput(attrs={'type': 'date'}),
            'fecha_vencimiento': forms.DateInput(attrs={'type': 'date'}),
            'descripcion': forms.Textarea(attrs={'rows': 2}),
        }

    def clean(self):
        cleaned = super().clean()
        emision = cleaned.get('fecha_emision')
        vencimiento = cleaned.get('fecha_vencimiento')
        if emision and vencimiento and vencimiento < emision:
            self.add_error('fecha_vencimiento', 'La fecha de vencimiento no puede ser anterior a la fecha de emisión.')
        return cleaned