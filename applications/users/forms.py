from django import forms
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from ..control.models import Empresa
from .models import User


class UserRegisterForm(forms.Form):
    email = forms.EmailField(label='Correo electrónico')
    first_name = forms.CharField(label='Nombres', max_length=50)
    last_name = forms.CharField(label='Apellidos', max_length=50)
    role = forms.ChoiceField(label='Rol', choices=User.ROLE_CHOICES)
    gender = forms.ChoiceField(label='Género', choices=User.GENDER_CHOICES)
    phone = forms.CharField(label='Celular', max_length=15, required=False)
    date_birth = forms.DateField(label='Fecha de nacimiento', required=False)
    empresa = forms.ModelChoiceField(
        label='Empresa',
        queryset=Empresa.objects.all(),
        required=False,
        empty_label='--- Seleccione empresa ---',
    )
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            self.add_error('password2', 'Las contraseñas no coinciden.')
        role = cleaned_data.get('role')
        empresa = cleaned_data.get('empresa')
        if role == User.USUARIO_EMPRESA and not empresa:
            self.add_error('empresa', 'El usuario con rol "Usuario Empresa" requiere una empresa asignada.')
        elif role and role != User.USUARIO_EMPRESA and empresa:
            self.add_error('empresa', 'Solo el rol "Usuario Empresa" puede tener una empresa asignada.')
        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email__iexact=email).exists():
            self.add_error('email', 'Ya existe un usuario con este correo electrónico.')
        return email

    def clean_date_birth(self):
        date_birth = self.cleaned_data.get('date_birth')
        if date_birth and date_birth > timezone.localdate():
            self.add_error('date_birth', 'La fecha de nacimiento no puede ser futura.')
        return date_birth

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if password:
            validate_password(password)
        return password


class UsuarioGestionForm(forms.ModelForm):
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput, required=False)
    role = forms.ChoiceField(label='Tipo de usuario', choices=[])
    empresa = forms.ModelChoiceField(
        label='Empresa',
        queryset=Empresa.objects.filter(activo=True),
        required=False,
        empty_label='--- Seleccione empresa ---',
    )

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'gender', 'phone', 'date_birth')

    def __init__(self, *args, **kwargs):
        self.current_user = kwargs.pop('current_user', None)
        allow_all_roles = kwargs.pop('allow_all_roles', False)
        super().__init__(*args, **kwargs)
        if self.current_user and self.current_user.role == User.BECA_AZUL and allow_all_roles:
            choices = [
                (User.PLANTA, 'Usuario Planta'),
                (User.USUARIO_EMPRESA, 'Usuario Empresa'),
                (User.GARITA, 'Usuario Garita'),
            ]
        elif self.current_user and self.current_user.role == User.BECA_AZUL:
            choices = [
                (User.USUARIO_EMPRESA, 'Usuario Empresa'),
            ]
        elif self.current_user and self.current_user.role == User.ADMINISTRADOR:
            choices = [
                (User.BECA_AZUL, 'Beca Azul'),
                (User.PLANTA, 'Usuario Planta'),
                (User.GARITA, 'Usuario Garita'),
            ]
        else:
            choices = [
                (User.PLANTA, 'Usuario Planta'),
                (User.USUARIO_EMPRESA, 'Usuario Empresa'),
                (User.GARITA, 'Usuario Garita'),
            ]
        self.fields['role'].choices = choices
        if not self.instance.pk:
            self.instance.role = choices[0][0] if choices else User.PLANTA
            self.fields['password1'].required = True
            self.fields['password2'].required = True
        else:
            self.fields.pop('password1')
            self.fields.pop('password2')
        self.fields['role'].initial = self.instance.role

    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = User.objects.filter(email__iexact=email)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Ya existe un usuario con este correo electrónico.')
        return email

    def clean_date_birth(self):
        date_birth = self.cleaned_data.get('date_birth')
        if date_birth and date_birth > timezone.localdate():
            raise forms.ValidationError('La fecha de nacimiento no puede ser futura.')
        return date_birth

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if password:
            validate_password(password)
        return password

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 or password2:
            if password1 != password2:
                self.add_error('password2', 'Las contraseñas no coinciden.')
        role = cleaned_data.get('role')
        empresa = cleaned_data.get('empresa')
        if role == User.USUARIO_EMPRESA and not empresa:
            self.add_error('empresa', 'El usuario con rol "Usuario Empresa" requiere una empresa asignada.')
        elif role and role != User.USUARIO_EMPRESA and empresa:
            self.add_error('empresa', 'Solo el rol "Usuario Empresa" puede tener una empresa asignada.')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        role = self.cleaned_data.get('role')
        if role:
            user.role = role
        user.empresa = self.cleaned_data.get('empresa')
        if user.role != User.USUARIO_EMPRESA:
            user.empresa = None
        password = self.cleaned_data.get('password1')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user


class PerfilForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'gender', 'phone', 'date_birth')

    def clean_date_birth(self):
        date_birth = self.cleaned_data.get('date_birth')
        if date_birth and date_birth > timezone.localdate():
            raise forms.ValidationError('La fecha de nacimiento no puede ser futura.')
        return date_birth


class LoginForm(forms.Form):
    email = forms.EmailField(label='Correo electrónico')
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)


class ResetPasswordForm(forms.Form):
    password1 = forms.CharField(label='Nueva contraseña', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            self.add_error('password2', 'Las contraseñas no coinciden.')
        return cleaned_data

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if password:
            validate_password(password)
        return password


class UpdatePasswordForm(forms.Form):
    password1 = forms.CharField(label='Contraseña actual', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Nueva contraseña', widget=forms.PasswordInput)
    password3 = forms.CharField(label='Confirmar nueva contraseña', widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        password2 = cleaned_data.get('password2')
        password3 = cleaned_data.get('password3')
        password1 = cleaned_data.get('password1')
        if password2 and password3 and password2 != password3:
            self.add_error('password3', 'Las contraseñas no coinciden.')
        if password1 and password2 and password1 == password2:
            self.add_error('password2', 'La nueva contraseña no puede ser igual a la actual.')
        return cleaned_data

    def clean_password2(self):
        password = self.cleaned_data.get('password2')
        if password:
            validate_password(password)
        return password
