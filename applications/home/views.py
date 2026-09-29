from django.shortcuts import redirect, render
from django.views.generic import TemplateView

from applications.users.models import User


class IndexView(TemplateView):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_superuser or request.user.role in (
                User.ADMINISTRADOR,
                User.BECA_AZUL,
                User.PLANTA,
            ):
                return redirect('app_users:dashboard')
            if request.user.role == User.USUARIO_EMPRESA:
                return redirect('app_control:trabajador_lista')
            if request.user.role == User.GARITA:
                return redirect('app_control:trabajador_buscar')
        return redirect('app_users:login')


def permission_denied(request, exception=None):
    return render(request, '403.html', status=403)
