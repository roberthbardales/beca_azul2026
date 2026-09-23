from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse_lazy

from .models import User


class BaseRolePermisoMixin(LoginRequiredMixin):
    login_url = reverse_lazy('app_users:login')
    required_roles = None

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        if request.user.role not in self.required_roles:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class AdministradorPermisoMixin(BaseRolePermisoMixin):
    required_roles = (User.ADMINISTRADOR,)


class GestionUsuariosPermisoMixin(BaseRolePermisoMixin):
    required_roles = (User.ADMINISTRADOR, User.BECA_AZUL)


class CrearUsuariosPermisoMixin(BaseRolePermisoMixin):
    required_roles = (User.BECA_AZUL,)


class ConsultaUsuariosPermisoMixin(BaseRolePermisoMixin):
    required_roles = (User.ADMINISTRADOR, User.BECA_AZUL, User.PLANTA)


class VerEmpresasMixin(BaseRolePermisoMixin):
    required_roles = (User.ADMINISTRADOR, User.BECA_AZUL, User.PLANTA)


class AdministrarEmpresasMixin(BaseRolePermisoMixin):
    required_roles = (User.BECA_AZUL,)


class VerTrabajadoresMixin(BaseRolePermisoMixin):
    required_roles = (User.ADMINISTRADOR, User.BECA_AZUL, User.GARITA)


class VerTrabajadorDetalleMixin(BaseRolePermisoMixin):
    required_roles = (User.ADMINISTRADOR, User.BECA_AZUL, User.PLANTA, User.USUARIO_EMPRESA, User.GARITA)


class AdministrarTrabajadoresMixin(BaseRolePermisoMixin):
    # Worker CRUD is handled through the company-scoped views.
    required_roles = ()


class GestionarIncidenciasMixin(BaseRolePermisoMixin):
    required_roles = (User.BECA_AZUL,)


class TrabajadorEmpresaPermisoMixin(LoginRequiredMixin):
    login_url = reverse_lazy('app_users:login')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.role != User.USUARIO_EMPRESA:
            raise PermissionDenied
        if not request.user.empresa:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class BecaAzulRequiredMixin(BaseRolePermisoMixin):
    required_roles = (User.BECA_AZUL,)


class UsuarioPlantaRequiredMixin(BaseRolePermisoMixin):
    required_roles = (User.PLANTA,)


class UsuarioEmpresaRequiredMixin(BaseRolePermisoMixin):
    required_roles = (User.USUARIO_EMPRESA,)


class UsuarioGaritaRequiredMixin(BaseRolePermisoMixin):
    required_roles = (User.GARITA,)
