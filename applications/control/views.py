from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView, View

from applications.users.mixins import (
    AdministrarEmpresasMixin,
    AdministrarTrabajadoresMixin,
    TrabajadorEmpresaPermisoMixin,
    VerEmpresasMixin,
    VerTrabajadoresMixin,
)
from applications.users.models import User

from .forms import CertificadoForm, EmpresaForm, TrabajadorEmpresaForm, TrabajadorForm
from .models import Certificado, Empresa, Trabajador

MAX_CERTIFICADOS = 4


class DashboardView(LoginRequiredMixin, View):
    template_name = 'users/dashboard.html'

    def get(self, request):
        if request.user.role == '3':
            return redirect('app_control:trabajador_empresa_lista')
        hoy = date.today()
        limite_30 = hoy + timedelta(days=30)
        limite_60 = hoy + timedelta(days=60)

        total_empresas = Empresa.objects.count()
        empresas_activas = Empresa.objects.filter(activo=True).count()

        total_trabajadores = Trabajador.objects.count()
        trabajadores_habilitados = Trabajador.objects.filter(estado=Trabajador.HABILITADO).count()
        trabajadores_pendientes = Trabajador.objects.filter(estado=Trabajador.PENDIENTE).count()
        trabajadores_rechazados = Trabajador.objects.filter(estado=Trabajador.RECHAZADO).count()

        total_certificados = Certificado.objects.count()
        certificados_vencidos = Certificado.objects.filter(fecha_vencimiento__lt=hoy).count()
        certificados_proximos_30 = Certificado.objects.filter(
            fecha_vencimiento__gte=hoy, fecha_vencimiento__lte=limite_30
        ).count()
        certificados_proximos_60 = Certificado.objects.filter(
            fecha_vencimiento__gte=hoy, fecha_vencimiento__lte=limite_60
        ).count()

        context = {
            'total_empresas': total_empresas,
            'empresas_activas': empresas_activas,
            'empresas_inactivas': total_empresas - empresas_activas,
            'total_trabajadores': total_trabajadores,
            'trabajadores_habilitados': trabajadores_habilitados,
            'trabajadores_pendientes': trabajadores_pendientes,
            'trabajadores_rechazados': trabajadores_rechazados,
            'total_certificados': total_certificados,
            'certificados_vencidos': certificados_vencidos,
            'certificados_proximos_30': certificados_proximos_30,
            'certificados_proximos_60': certificados_proximos_60,
            'trabajadores_por_empresa': (
                Empresa.objects.annotate(total=Count('trabajadores', distinct=True)).order_by('nombre')
            ),
        }
        return render(request, self.template_name, context)


class EmpresaListView(VerEmpresasMixin, ListView):
    model = Empresa
    template_name = 'control/empresas/lista.html'
    context_object_name = 'empresas'
    paginate_by = 20

    def get_queryset(self):
        queryset = Empresa.objects.annotate(
            total_trabajadores=Count('trabajadores', distinct=True),
            total_usuarios=Count('usuarios', distinct=True),
        ).order_by('nombre')
        q = self.request.GET.get('q', '').strip()
        if q:
            queryset = queryset.filter(
                Q(nombre__icontains=q)
                | Q(ruc__icontains=q)
                | Q(email__icontains=q)
                | Q(direccion__icontains=q)
            )
        estado = self.request.GET.get('estado', '').strip()
        if estado in ('0', '1'):
            queryset = queryset.filter(activo=(estado == '1'))
        return queryset

    def get_context_data(self, **kwargs):
        kwargs.setdefault('q', self.request.GET.get('q', ''))
        kwargs.setdefault('estado', self.request.GET.get('estado', ''))
        return super().get_context_data(**kwargs)


class EmpresaCreateView(AdministrarEmpresasMixin, CreateView):
    model = Empresa
    form_class = EmpresaForm
    template_name = 'control/empresas/form.html'
    success_url = reverse_lazy('app_control:empresa_lista')

    def form_valid(self, form):
        form.instance.activo = True
        messages.success(self.request, 'Empresa creada correctamente.')
        return super().form_valid(form)


class EmpresaUpdateView(AdministrarEmpresasMixin, UpdateView):
    model = Empresa
    form_class = EmpresaForm
    template_name = 'control/empresas/form.html'
    success_url = reverse_lazy('app_control:empresa_lista')

    def form_valid(self, form):
        messages.success(self.request, 'Empresa actualizada correctamente.')
        return super().form_valid(form)


class EmpresaToggleView(AdministrarEmpresasMixin, View):
    def post(self, request, pk):
        empresa = get_object_or_404(Empresa, pk=pk)
        empresa.activo = not empresa.activo
        empresa.save(update_fields=['activo'])
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'activo': empresa.activo, 'nombre': empresa.nombre})
        estado = 'activada' if empresa.activo else 'desactivada'
        messages.success(self.request, f'La empresa "{empresa.nombre}" fue {estado}.')
        return redirect('app_control:empresa_detalle', pk=empresa.pk)


class EmpresaDetailView(VerEmpresasMixin, DetailView):
    model = Empresa
    template_name = 'control/empresas/detalle.html'
    context_object_name = 'empresa'

    def get_context_data(self, **kwargs):
        trabajadores = self.object.trabajadores.order_by('apellidos', 'nombres')
        kwargs.setdefault('total_trabajadores', trabajadores.count())
        kwargs.setdefault('total_usuarios', self.object.usuarios.count())
        kwargs.setdefault('trabajadores', trabajadores)
        kwargs.setdefault(
            'trabajadores_por_estado',
            [
                {
                    'estado': grupo['estado'],
                    'total': grupo['total'],
                    'label': dict(Trabajador.ESTADO_CHOICES).get(grupo['estado'], grupo['estado']),
                }
                for grupo in trabajadores.values('estado').annotate(total=Count('estado')).order_by('estado')
            ],
        )
        kwargs.setdefault('estado_choices', dict(Trabajador.ESTADO_CHOICES))
        return super().get_context_data(**kwargs)


class EmpresaDeleteView(AdministrarEmpresasMixin, DeleteView):
    model = Empresa
    template_name = 'control/empresas/confirm_delete.html'
    context_object_name = 'empresa'
    success_url = reverse_lazy('app_control:empresa_lista')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.trabajadores.exists() or self.object.usuarios.exists():
            messages.error(
                self.request,
                f'No se puede eliminar la empresa "{self.object.nombre}", tiene trabajadores o usuarios asociados.',
            )
            return redirect('app_control:empresa_detalle', pk=self.object.pk)
        nombre = self.object.nombre
        self.object.delete()
        messages.success(self.request, f'La empresa "{nombre}" fue eliminada.')
        return HttpResponseRedirect(self.get_success_url())


class TrabajadorListView(VerTrabajadoresMixin, ListView):
    model = Trabajador
    template_name = 'control/trabajadores/lista.html'
    context_object_name = 'trabajadores'
    paginate_by = 20
    sortable_columns = {
        'dni': ('dni',),
        'nombre': ('apellidos', 'nombres'),
        'empresa': ('empresa__nombre', 'apellidos', 'nombres'),
        'cargo': ('cargo', 'apellidos', 'nombres'),
        'area': ('area', 'apellidos', 'nombres'),
        'certificados': ('certificados_count', 'apellidos', 'nombres'),
        'estado': ('estado', 'apellidos', 'nombres'),
    }

    def get_queryset(self):
        queryset = Trabajador.objects.select_related('empresa').prefetch_related('certificados').annotate(
            certificados_count=Count('certificados', distinct=True)
        ).order_by('estado', 'apellidos', 'nombres')
        q = self.request.GET.get('q', '').strip()
        if q:
            queryset = queryset.filter(
                Q(dni__icontains=q)
                | Q(nombres__icontains=q)
                | Q(apellidos__icontains=q)
                | Q(cargo__icontains=q)
                | Q(area__icontains=q)
                | Q(empresa__nombre__icontains=q)
            )
        estado = self.request.GET.get('estado', '').strip()
        if estado in dict(Trabajador.ESTADO_CHOICES):
            queryset = queryset.filter(estado=estado)
        empresa_id = self.request.GET.get('empresa', '').strip()
        if empresa_id.isdigit():
            queryset = queryset.filter(empresa_id=empresa_id)
        sort = self.request.GET.get('sort', '').strip()
        direction = self.request.GET.get('dir', 'asc').strip().lower()
        if direction not in ('asc', 'desc'):
            direction = 'asc'
        order_fields = self.sortable_columns.get(sort)
        if order_fields:
            if direction == 'desc':
                order_fields = tuple(f'-{field}' for field in order_fields)
            queryset = queryset.order_by(*order_fields)
        return queryset

    def get_context_data(self, **kwargs):
        query_params = self.request.GET.copy()
        query_params.pop('page', None)
        query_params.pop('sort', None)
        query_params.pop('dir', None)
        kwargs.setdefault('q', self.request.GET.get('q', ''))
        kwargs.setdefault('estado', self.request.GET.get('estado', ''))
        kwargs.setdefault('empresa_id', self.request.GET.get('empresa', ''))
        kwargs.setdefault('sort', self.request.GET.get('sort', ''))
        kwargs.setdefault('dir', self.request.GET.get('dir', 'asc'))
        kwargs.setdefault('query_string', query_params.urlencode())
        kwargs.setdefault('empresas', Empresa.objects.order_by('nombre'))
        kwargs.setdefault('estado_choices', Trabajador.ESTADO_CHOICES)
        kwargs.setdefault('sortable_columns', {
            'dni': 'DNI',
            'nombre': 'Nombre completo',
            'empresa': 'Empresa',
            'cargo': 'Cargo',
            'area': 'Area',
            'certificados': 'Certificados',
            'estado': 'Estado',
        })
        return super().get_context_data(**kwargs)


class TrabajadorBuscarView(LoginRequiredMixin, View):
    template_name = 'control/trabajadores/buscar.html'

    def get(self, request):
        q = request.GET.get('q', '').strip()
        trabajador = None
        resultados = 0
        if q:
            queryset = Trabajador.objects.select_related('empresa')
            if request.user.role == User.USUARIO_EMPRESA:
                queryset = queryset.filter(empresa=request.user.empresa)
            queryset = queryset.filter(dni=q)
            resultados = queryset.count()
            if resultados == 1:
                trabajador = queryset.first()
        context = {
            'q': q,
            'trabajador': trabajador,
            'resultados': resultados,
            'es_empresa': request.user.role == User.USUARIO_EMPRESA,
            'puede_ver_detalle': request.user.role in (User.ADMINISTRADOR, User.BECA_AZUL, User.USUARIO_EMPRESA),
        }
        return render(request, self.template_name, context)


class TrabajadorCreateView(AdministrarTrabajadoresMixin, CreateView):
    model = Trabajador
    form_class = TrabajadorForm
    template_name = 'control/trabajadores/form.html'
    success_url = reverse_lazy('app_control:trabajador_lista')

    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, 'Trabajador registrado correctamente.')
        return HttpResponseRedirect(self.get_success_url())


class TrabajadorUpdateView(AdministrarTrabajadoresMixin, UpdateView):
    model = Trabajador
    form_class = TrabajadorForm
    template_name = 'control/trabajadores/form.html'
    success_url = reverse_lazy('app_control:trabajador_lista')

    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, 'Trabajador actualizado correctamente.')
        return HttpResponseRedirect(self.get_success_url())


class TrabajadorDetailView(VerTrabajadoresMixin, DetailView):
    model = Trabajador
    template_name = 'control/trabajadores/detalle.html'
    context_object_name = 'trabajador'

    def get_context_data(self, **kwargs):
        kwargs.setdefault('certificados', self.object.certificados.all().order_by('-fecha_emision'))
        return super().get_context_data(**kwargs)


class TrabajadorEstadoView(AdministrarTrabajadoresMixin, View):
    def post(self, request, pk):
        trabajador = get_object_or_404(Trabajador, pk=pk)
        estado = request.POST.get('estado')
        if estado not in dict(Trabajador.ESTADO_CHOICES):
            messages.error(self.request, 'Estado no válido.')
            return redirect('app_control:trabajador_detalle', pk=trabajador.pk)
        trabajador.estado = estado
        trabajador.save(update_fields=['estado'])
        messages.success(self.request, f'El estado del trabajador "{trabajador}" fue actualizado.')
        return redirect('app_control:trabajador_detalle', pk=trabajador.pk)


class TrabajadorToggleView(AdministrarTrabajadoresMixin, View):
    def post(self, request, pk):
        trabajador = get_object_or_404(Trabajador, pk=pk)
        trabajador.activo = not trabajador.activo
        trabajador.save(update_fields=['activo'])
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'activo': trabajador.activo, 'nombre': str(trabajador)})
        estado = 'activado' if trabajador.activo else 'desactivado'
        messages.success(request, f'El trabajador "{trabajador}" fue {estado}.')
        return redirect('app_control:trabajador_detalle', pk=trabajador.pk)


class TrabajadorDeleteView(AdministrarTrabajadoresMixin, DeleteView):
    model = Trabajador
    template_name = 'control/trabajadores/confirm_delete.html'
    context_object_name = 'trabajador'
    success_url = reverse_lazy('app_control:trabajador_lista')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        nombre = str(self.object)
        self.object.delete()
        messages.success(self.request, f'El trabajador "{nombre}" fue eliminado.')
        return HttpResponseRedirect(self.get_success_url())


class CertificadoCreateView(AdministrarTrabajadoresMixin, CreateView):
    model = Certificado
    form_class = CertificadoForm
    template_name = 'control/certificados/form.html'

    def get_trabajador(self):
        return get_object_or_404(Trabajador, pk=self.kwargs['trabajador_pk'])

    def get_context_data(self, **kwargs):
        kwargs.setdefault('trabajador', self.get_trabajador())
        kwargs.setdefault('certificados_count', self.get_trabajador().certificados.count())
        kwargs.setdefault('max_certificados', MAX_CERTIFICADOS)
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        self.trabajador = self.get_trabajador()
        if self.trabajador.certificados.count() >= MAX_CERTIFICADOS:
            messages.error(
                self.request,
                f'El trabajador ya tiene el máximo de {MAX_CERTIFICADOS} certificados.',
            )
            return redirect('app_control:trabajador_detalle', pk=self.trabajador.pk)
        form.instance.trabajador = self.trabajador
        messages.success(self.request, 'Certificado registrado correctamente.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('app_control:trabajador_detalle', args=[self.trabajador.pk])


class CertificadoUpdateView(AdministrarTrabajadoresMixin, UpdateView):
    model = Certificado
    form_class = CertificadoForm
    template_name = 'control/certificados/form.html'

    def get_context_data(self, **kwargs):
        kwargs.setdefault('trabajador', self.object.trabajador)
        kwargs.setdefault('max_certificados', MAX_CERTIFICADOS)
        kwargs.setdefault('certificados_count', self.object.trabajador.certificados.count())
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, 'Certificado actualizado correctamente.')
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('app_control:trabajador_detalle', args=[self.object.trabajador.pk])


class CertificadoDeleteView(AdministrarTrabajadoresMixin, DeleteView):
    model = Certificado
    template_name = 'control/certificados/confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        trabajador_pk = self.object.trabajador.pk
        self.object.delete()
        messages.success(self.request, 'Certificado eliminado correctamente.')
        return HttpResponseRedirect(reverse('app_control:trabajador_detalle', args=[trabajador_pk]))


class TrabajadorEmpresaListView(TrabajadorEmpresaPermisoMixin, ListView):
    model = Trabajador
    template_name = 'control/trabajadores/lista_empresa.html'
    context_object_name = 'trabajadores'
    paginate_by = 20

    def get_queryset(self):
        queryset = Trabajador.objects.filter(empresa=self.request.user.empresa).select_related(
            'empresa'
        ).prefetch_related('certificados').annotate(
            certificados_count=Count('certificados', distinct=True)
        ).order_by('estado', 'apellidos', 'nombres')
        q = self.request.GET.get('q', '').strip()
        if q:
            queryset = queryset.filter(
                Q(dni__icontains=q)
                | Q(nombres__icontains=q)
                | Q(apellidos__icontains=q)
                | Q(cargo__icontains=q)
                | Q(area__icontains=q)
            )
        estado = self.request.GET.get('estado', '').strip()
        if estado in dict(Trabajador.ESTADO_CHOICES):
            queryset = queryset.filter(estado=estado)
        sort = self.request.GET.get('sort', '').strip()
        direction = self.request.GET.get('dir', 'asc').strip().lower()
        if direction not in ('asc', 'desc'):
            direction = 'asc'
        sortable_columns = {
            'dni': ('dni',),
            'nombre': ('apellidos', 'nombres'),
            'cargo': ('cargo', 'apellidos', 'nombres'),
            'area': ('area', 'apellidos', 'nombres'),
            'certificados': ('certificados_count', 'apellidos', 'nombres'),
            'estado': ('estado', 'apellidos', 'nombres'),
        }
        order_fields = sortable_columns.get(sort)
        if order_fields:
            if direction == 'desc':
                order_fields = tuple(f'-{field}' for field in order_fields)
            queryset = queryset.order_by(*order_fields)
        return queryset

    def get_context_data(self, **kwargs):
        query_params = self.request.GET.copy()
        query_params.pop('page', None)
        query_params.pop('sort', None)
        query_params.pop('dir', None)
        kwargs.setdefault('q', self.request.GET.get('q', ''))
        kwargs.setdefault('estado', self.request.GET.get('estado', ''))
        kwargs.setdefault('sort', self.request.GET.get('sort', ''))
        kwargs.setdefault('dir', self.request.GET.get('dir', 'asc'))
        kwargs.setdefault('query_string', query_params.urlencode())
        kwargs.setdefault('estado_choices', Trabajador.ESTADO_CHOICES)
        kwargs.setdefault('sortable_columns', {
            'dni': 'DNI',
            'nombre': 'Nombre completo',
            'cargo': 'Cargo',
            'area': 'Area',
            'certificados': 'Certificados',
            'estado': 'Estado',
        })
        kwargs.setdefault('empresa', self.request.user.empresa)
        return super().get_context_data(**kwargs)


class TrabajadorEmpresaBaseMixin(TrabajadorEmpresaPermisoMixin):
    def get_queryset(self):
        return Trabajador.objects.filter(empresa=self.request.user.empresa)


class TrabajadorEmpresaDetailView(TrabajadorEmpresaBaseMixin, DetailView):
    model = Trabajador
    template_name = 'control/trabajadores/detalle.html'
    context_object_name = 'trabajador'

    def get_context_data(self, **kwargs):
        kwargs.setdefault('certificados', self.object.certificados.all().order_by('-fecha_emision'))
        kwargs.setdefault('es_empresa', True)
        return super().get_context_data(**kwargs)


class TrabajadorEmpresaCreateView(TrabajadorEmpresaBaseMixin, CreateView):
    model = Trabajador
    form_class = TrabajadorEmpresaForm
    template_name = 'control/trabajadores/form.html'
    success_url = reverse_lazy('app_control:trabajador_empresa_lista')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['empresa'] = self.request.user.empresa
        return kwargs

    def form_valid(self, form):
        form.instance.empresa = self.request.user.empresa
        self.object = form.save()
        messages.success(self.request, 'Trabajador registrado correctamente.')
        return HttpResponseRedirect(self.get_success_url())


class TrabajadorEmpresaUpdateView(TrabajadorEmpresaBaseMixin, UpdateView):
    model = Trabajador
    form_class = TrabajadorEmpresaForm
    template_name = 'control/trabajadores/form.html'
    success_url = reverse_lazy('app_control:trabajador_empresa_lista')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['empresa'] = self.request.user.empresa
        return kwargs

    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, 'Trabajador actualizado correctamente.')
        return HttpResponseRedirect(self.get_success_url())


class TrabajadorEmpresaEstadoView(TrabajadorEmpresaBaseMixin, View):
    def post(self, request, pk):
        trabajador = get_object_or_404(Trabajador, pk=pk, empresa=self.request.user.empresa)
        estado = request.POST.get('estado')
        if estado not in dict(Trabajador.ESTADO_CHOICES):
            messages.error(self.request, 'Estado no válido.')
            return redirect('app_control:trabajador_empresa_detalle', pk=trabajador.pk)
        trabajador.estado = estado
        trabajador.save(update_fields=['estado'])
        messages.success(self.request, f'El estado del trabajador "{trabajador}" fue actualizado.')
        return redirect('app_control:trabajador_empresa_detalle', pk=trabajador.pk)


class TrabajadorEmpresaToggleView(TrabajadorEmpresaBaseMixin, View):
    def post(self, request, pk):
        trabajador = get_object_or_404(Trabajador, pk=pk, empresa=self.request.user.empresa)
        trabajador.activo = not trabajador.activo
        trabajador.save(update_fields=['activo'])
        estado = 'activado' if trabajador.activo else 'desactivado'
        messages.success(request, f'El trabajador "{trabajador}" fue {estado}.')
        return redirect('app_control:trabajador_empresa_detalle', pk=trabajador.pk)


class TrabajadorEmpresaDeleteView(TrabajadorEmpresaBaseMixin, DeleteView):
    model = Trabajador
    template_name = 'control/trabajadores/confirm_delete.html'
    context_object_name = 'trabajador'
    success_url = reverse_lazy('app_control:trabajador_empresa_lista')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        nombre = str(self.object)
        self.object.delete()
        messages.success(self.request, f'El trabajador "{nombre}" fue eliminado.')
        return HttpResponseRedirect(self.get_success_url())


class CertificadoEmpresaCreateView(TrabajadorEmpresaBaseMixin, CreateView):
    model = Certificado
    form_class = CertificadoForm
    template_name = 'control/certificados/form.html'

    def get_trabajador(self):
        return get_object_or_404(Trabajador, pk=self.kwargs['trabajador_pk'], empresa=self.request.user.empresa)

    def get_context_data(self, **kwargs):
        kwargs.setdefault('trabajador', self.get_trabajador())
        kwargs.setdefault('certificados_count', self.get_trabajador().certificados.count())
        kwargs.setdefault('max_certificados', MAX_CERTIFICADOS)
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        self.trabajador = self.get_trabajador()
        if self.trabajador.certificados.count() >= MAX_CERTIFICADOS:
            messages.error(
                self.request,
                f'El trabajador ya tiene el máximo de {MAX_CERTIFICADOS} certificados.',
            )
            return redirect('app_control:trabajador_empresa_detalle', pk=self.trabajador.pk)
        form.instance.trabajador = self.trabajador
        messages.success(self.request, 'Certificado registrado correctamente.')
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('app_control:trabajador_empresa_detalle', args=[self.trabajador.pk])


class CertificadoEmpresaUpdateView(TrabajadorEmpresaBaseMixin, UpdateView):
    model = Certificado
    form_class = CertificadoForm
    template_name = 'control/certificados/form.html'

    def get_queryset(self):
        return Certificado.objects.filter(
            trabajador__empresa=self.request.user.empresa
        )

    def get_context_data(self, **kwargs):
        kwargs.setdefault('trabajador', self.object.trabajador)
        kwargs.setdefault('max_certificados', MAX_CERTIFICADOS)
        kwargs.setdefault('certificados_count', self.object.trabajador.certificados.count())
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, 'Certificado actualizado correctamente.')
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('app_control:trabajador_empresa_detalle', args=[self.object.trabajador.pk])


class CertificadoEmpresaDeleteView(TrabajadorEmpresaBaseMixin, DeleteView):
    model = Certificado
    template_name = 'control/certificados/confirm_delete.html'

    def get_queryset(self):
        return Certificado.objects.filter(
            trabajador__empresa=self.request.user.empresa
        )

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        trabajador_pk = self.object.trabajador.pk
        self.object.delete()
        messages.success(self.request, 'Certificado eliminado correctamente.')
        return HttpResponseRedirect(reverse('app_control:trabajador_empresa_detalle', args=[trabajador_pk]))