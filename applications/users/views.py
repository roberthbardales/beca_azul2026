from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView, View
from django.views.generic.edit import FormView

from .forms import (
    LoginForm,
    PerfilForm,
    ResetPasswordForm,
    UpdatePasswordForm,
    UserRegisterForm,
    UsuarioGestionForm,
)
from .mixins import CrearUsuariosPermisoMixin, ConsultaUsuariosPermisoMixin, GestionUsuariosPermisoMixin
from .models import User
from . import services


class UserRegisterView(FormView):
    template_name = 'users/register.html'
    form_class = UserRegisterForm
    success_url = reverse_lazy('app_users:login')

    def form_valid(self, form):
        services.create_user(form.cleaned_data)
        messages.success(self.request, 'Cuenta creada correctamente. Inicia sesión.')
        return super().form_valid(form)


class LoginUser(FormView):
    template_name = 'users/login.html'
    form_class = LoginForm
    success_url = reverse_lazy('app_users:dashboard')

    def form_invalid(self, form):
        if not form.non_field_errors():
            form.add_error(None, 'Email o contraseña incorrectos.')
        return super().form_invalid(form)

    def form_valid(self, form):
        user = services.authenticate_user(
            self.request,
            form.cleaned_data['email'],
            form.cleaned_data['password'],
        )
        if user is None:
            form.add_error(None, 'Email o contraseña incorrectos.')
            return self.form_invalid(form)
        if user.role == User.GARITA:
            return redirect('app_control:empresa_buscar')
        return super().form_valid(form)


class LogoutView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        services.logout_user(request)
        return HttpResponseRedirect(reverse('app_users:login'))


class UpdatePasswordView(LoginRequiredMixin, FormView):
    template_name = 'users/cambiar_password.html'
    form_class = UpdatePasswordForm
    success_url = reverse_lazy('app_users:login')
    login_url = reverse_lazy('app_users:login')

    def form_valid(self, form):
        usuario = self.request.user
        user = services.authenticate_user(
            self.request,
            usuario.email,
            form.cleaned_data['password1'],
        )
        if user is None:
            form.add_error(None, 'La contraseña actual es incorrecta.')
            return self.form_invalid(form)

        services.change_password(usuario, form.cleaned_data['password2'])
        services.logout_user(self.request)
        messages.success(self.request, 'Contraseña actualizada correctamente. Vuelve a iniciar sesión.')
        return super().form_valid(form)


class DashboardView(LoginRequiredMixin, View):
    def get(self, request):
        return HttpResponseRedirect(reverse('app_control:dashboard'))


class MiPerfilView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = PerfilForm
    template_name = 'users/perfil.html'
    success_url = reverse_lazy('app_users:mi_perfil')
    login_url = reverse_lazy('app_users:login')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Perfil actualizado correctamente.')
        return super().form_valid(form)


class UsuarioListView(ConsultaUsuariosPermisoMixin, ListView):
    model = User
    template_name = 'users/usuarios/lista.html'
    context_object_name = 'usuarios'
    paginate_by = 20

    def get_queryset(self):
        user = self.request.user
        if user.role == User.BECA_AZUL:
            queryset = User.objects.filter(role=User.USUARIO_EMPRESA).order_by('first_name', 'last_name')
        else:
            queryset = User.objects.filter(
                role__in=[User.BECA_AZUL, User.PLANTA, User.GARITA]
            ).order_by('role', 'first_name', 'last_name')
        q = self.request.GET.get('q', '').strip()
        if q:
            queryset = queryset.filter(
                Q(first_name__icontains=q)
                | Q(last_name__icontains=q)
                | Q(email__icontains=q)
            )
        rol = self.request.GET.get('rol', '').strip()
        if rol:
            queryset = queryset.filter(role=rol)
        estado = self.request.GET.get('estado', '').strip()
        if estado in ('0', '1'):
            queryset = queryset.filter(is_active=estado == '1')
        return queryset

    def get_context_data(self, **kwargs):
        user = self.request.user
        kwargs.setdefault('q', self.request.GET.get('q', ''))
        kwargs.setdefault('rol', self.request.GET.get('rol', ''))
        kwargs.setdefault('estado', self.request.GET.get('estado', ''))
        if user.role == User.BECA_AZUL:
            kwargs.setdefault('roles', [(User.USUARIO_EMPRESA, 'Usuario Empresa')])
        elif user.is_superuser or user.role == User.ADMINISTRADOR:
            kwargs.setdefault(
                'roles',
                [(v, l) for v, l in User.ROLE_CHOICES if v != User.ADMINISTRADOR],
            )
        else:
            kwargs.setdefault(
                'roles',
                [(v, l) for v, l in User.ROLE_CHOICES if v in (User.BECA_AZUL, User.PLANTA, User.GARITA)],
            )
        return super().get_context_data(**kwargs)


class UsuarioDetailView(ConsultaUsuariosPermisoMixin, DetailView):
    model = User
    template_name = 'users/usuarios/detalle.html'
    context_object_name = 'usuario'

    def get_queryset(self):
        user = self.request.user
        if user.role == User.BECA_AZUL:
            return User.objects.filter(role=User.USUARIO_EMPRESA)
        if user.is_superuser or user.role == User.ADMINISTRADOR:
            return User.objects.exclude(role=User.ADMINISTRADOR)
        return User.objects.filter(role__in=[User.BECA_AZUL, User.PLANTA, User.GARITA])


class UsuarioCreateView(CrearUsuariosPermisoMixin, CreateView):
    model = User
    form_class = UsuarioGestionForm
    template_name = 'users/usuarios/form.html'
    success_url = reverse_lazy('app_users:usuario_lista')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['current_user'] = self.request.user
        kwargs['allow_all_roles'] = True
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Usuario creado correctamente.')
        return super().form_valid(form)


class UsuarioUpdateView(GestionUsuariosPermisoMixin, UpdateView):
    model = User
    form_class = UsuarioGestionForm
    template_name = 'users/usuarios/form.html'
    success_url = reverse_lazy('app_users:usuario_lista')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['current_user'] = self.request.user
        return kwargs

    def get_queryset(self):
        user = self.request.user
        if user.role == User.BECA_AZUL:
            return User.objects.filter(role=User.USUARIO_EMPRESA)
        if user.is_superuser or user.role == User.ADMINISTRADOR:
            return User.objects.exclude(role=User.ADMINISTRADOR)
        return User.objects.filter(role__in=[User.BECA_AZUL, User.PLANTA, User.GARITA])

    def form_valid(self, form):
        messages.success(self.request, 'Usuario actualizado correctamente.')
        return super().form_valid(form)


class UsuarioToggleView(GestionUsuariosPermisoMixin, View):
    def post(self, request, pk):
        user = request.user
        if user.role == User.BECA_AZUL:
            usuario = get_object_or_404(User, pk=pk, role=User.USUARIO_EMPRESA)
        elif user.is_superuser or user.role == User.ADMINISTRADOR:
            usuario = get_object_or_404(User, pk=pk)
        else:
            usuario = get_object_or_404(User, pk=pk, role__in=[User.BECA_AZUL, User.PLANTA, User.GARITA])
        if usuario.pk == request.user.pk:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'error': 'No puedes desactivar tu propia cuenta.'}, status=400)
            messages.error(request, 'No puedes desactivar tu propia cuenta.')
            return redirect('app_users:usuario_lista')
        usuario.is_active = not usuario.is_active
        usuario.save(update_fields=['is_active'])
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'is_active': usuario.is_active, 'email': usuario.email})
        estado = 'activado' if usuario.is_active else 'desactivado'
        messages.success(request, f'El usuario "{usuario.email}" fue {estado}.')
        return redirect('app_users:usuario_lista')


class UsuarioDeleteView(GestionUsuariosPermisoMixin, DeleteView):
    model = User
    template_name = 'users/usuarios/confirm_delete.html'
    context_object_name = 'usuario'
    success_url = reverse_lazy('app_users:usuario_lista')

    def get_queryset(self):
        user = self.request.user
        if user.role == User.BECA_AZUL:
            return User.objects.filter(role=User.USUARIO_EMPRESA)
        if user.is_superuser or user.role == User.ADMINISTRADOR:
            return User.objects.exclude(role=User.ADMINISTRADOR)
        return User.objects.filter(role__in=[User.BECA_AZUL, User.PLANTA, User.GARITA])

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.pk == self.request.user.pk:
            messages.error(self.request, 'No puedes eliminar tu propia cuenta.')
            return HttpResponseRedirect(self.get_success_url())
        email = self.object.email
        self.object.delete()
        messages.success(self.request, f'El usuario "{email}" fue eliminado.')
        return HttpResponseRedirect(self.get_success_url())


class UsuarioPasswordResetView(GestionUsuariosPermisoMixin, FormView):
    template_name = 'users/usuarios/reset_password.html'
    form_class = ResetPasswordForm
    success_url = reverse_lazy('app_users:usuario_lista')

    def get_object(self):
        user = self.request.user
        if user.role == User.BECA_AZUL:
            return get_object_or_404(User, pk=self.kwargs['pk'], role=User.USUARIO_EMPRESA)
        if user.is_superuser or user.role == User.ADMINISTRADOR:
            return get_object_or_404(User, pk=self.kwargs['pk'])
        return get_object_or_404(
            User,
            pk=self.kwargs['pk'],
            role__in=[User.BECA_AZUL, User.PLANTA, User.GARITA],
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['usuario'] = self.get_object()
        return context

    def form_valid(self, form):
        usuario = self.get_object()
        services.change_password(usuario, form.cleaned_data['password1'])
        messages.success(self.request, f'Contraseña de "{usuario.email}" restablecida correctamente.')
        return super().form_valid(form)
