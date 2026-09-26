from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Count, Exists, OuterRef, Prefetch, Q
from django.db.models.functions import TruncDate
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView, View

from applications.users.mixins import (
    AdministrarEmpresasMixin,
    AdministrarTrabajadoresMixin,
    BecaAzulRequiredMixin,
    GestionarIncidenciasMixin,
    TrabajadorEmpresaPermisoMixin,
    VerEmpresasMixin,
    VerTrabajadorDetalleMixin,
    VerTrabajadoresMixin,
)
from applications.users.models import User

from .forms import (
    CertificadoCargaFormSet,
    CertificadoForm,
    EmpresaForm,
    IncidenciaForm,
    SCTRForm,
    TrabajadorEmpresaForm,
    TrabajadorForm,
)
from .models import Certificado, Empresa, Incidencia, Trabajador

class DashboardView(LoginRequiredMixin, View):
    template_name = 'users/dashboard.html'

    def get(self, request):
        if request.user.role == User.GARITA:
            raise PermissionDenied
        if request.user.role == User.USUARIO_EMPRESA:
            return redirect('app_control:trabajador_lista')
        hoy = timezone.localdate()
        limite_30 = hoy + timedelta(days=30)
        limite_60 = hoy + timedelta(days=60)

        total_empresas = Empresa.objects.count()
        empresas_activas = Empresa.objects.filter(activo=True).count()
        empresas_habilitadas = Empresa.objects.filter(homologado=True).count()

        total_trabajadores = Trabajador.objects.count()
        trabajadores_habilitados = Trabajador.objects.filter(habilitado=True).count()
        trabajadores_deshabilitados = Trabajador.objects.filter(habilitado=False).count()

        total_certificados = Certificado.objects.count()
        certificados_sin_vencimiento = 0
        certificados_vencidos = Certificado.objects.filter(fecha_vencimiento__lt=hoy).count()
        certificados_proximos_30 = Certificado.objects.filter(
            fecha_vencimiento__gte=hoy, fecha_vencimiento__lte=limite_30
        ).count()
        certificados_proximos_60 = Certificado.objects.filter(
            fecha_vencimiento__gte=hoy, fecha_vencimiento__lte=limite_60
        ).count()

        trabajadores_por_empresa = list(
            Empresa.objects.annotate(total=Count('trabajadores', distinct=True))
            .order_by('-total', 'nombre')
        )
        empresas_grafica = trabajadores_por_empresa[:10]
        otros_trabajadores = sum(empresa.total for empresa in trabajadores_por_empresa[10:])

        inicio_semana = hoy - timedelta(days=6)
        altas_por_dia = {
            item['dia']: item['total']
            for item in (
                Trabajador.objects.filter(created__date__gte=inicio_semana)
                .annotate(dia=TruncDate('created'))
                .values('dia')
                .annotate(total=Count('id'))
                .order_by('dia')
            )
        }
        dias_semana = [inicio_semana + timedelta(days=offset) for offset in range(7)]
        certificados_vigentes = Certificado.objects.filter(
            fecha_vencimiento__gt=limite_30
        ).count()

        empresas_labels = [empresa.nombre for empresa in empresas_grafica]
        empresas_data = [empresa.total for empresa in empresas_grafica]
        if otros_trabajadores:
            empresas_labels.append('Otros')
            empresas_data.append(otros_trabajadores)

        context = {
            'total_empresas': total_empresas,
            'empresas_activas': empresas_activas,
            'empresas_inactivas': total_empresas - empresas_activas,
            'empresas_habilitadas': empresas_habilitadas,
            'empresas_deshabilitadas': total_empresas - empresas_habilitadas,
            'total_trabajadores': total_trabajadores,
            'trabajadores_habilitados': trabajadores_habilitados,
            'trabajadores_deshabilitados': trabajadores_deshabilitados,
            'total_certificados': total_certificados,
            'certificados_vencidos': certificados_vencidos,
            'certificados_sin_vencimiento': certificados_sin_vencimiento,
            'certificados_proximos_30': certificados_proximos_30,
            'certificados_proximos_60': certificados_proximos_60,
            'trabajadores_por_empresa': trabajadores_por_empresa,
            'dashboard_charts': {
                'empresas': {
                    'labels': empresas_labels,
                    'data': empresas_data,
                },
                'cumplimiento': [
                    certificados_vigentes,
                    certificados_proximos_30,
                    certificados_vencidos,
                ],
                'altas': {
                    'labels': [dia.strftime('%d/%m') for dia in dias_semana],
                    'data': [altas_por_dia.get(dia, 0) for dia in dias_semana],
                },
            },
            'trabajadores_recientes': (
                Trabajador.objects.select_related('empresa').order_by('-created')[:5]
            ),
            'certificados_por_vencer': (
                Certificado.objects.select_related('trabajador__empresa').filter(
                    trabajador__isnull=False,
                    fecha_vencimiento__gte=hoy,
                    fecha_vencimiento__lte=limite_30,
                ).order_by('fecha_vencimiento')[:5]
            ),
        }
        return render(request, self.template_name, context)


class EmpresaListView(VerEmpresasMixin, ListView):
    model = Empresa
    template_name = 'control/empresas/lista.html'
    context_object_name = 'empresas'
    paginate_by = 20

    def get_queryset(self):
        if self.request.user.role == User.PLANTA:
            queryset = Trabajador.objects.select_related('empresa').filter(empresa__activo=True).order_by('empresa__nombre', 'apellidos', 'nombres')
            q = self.request.GET.get('q', '').strip()
            if q:
                queryset = queryset.filter(Q(nombres__icontains=q) | Q(apellidos__icontains=q) | Q(dni__icontains=q))
            empresa_id = self.request.GET.get('empresa', '').strip()
            if empresa_id.isdigit():
                queryset = queryset.filter(empresa_id=empresa_id)
            return queryset
        queryset = Empresa.objects.annotate(
            total_trabajadores=Count('trabajadores', distinct=True),
            total_usuarios=Count('usuarios', distinct=True),
        ).prefetch_related(
            Prefetch('certificados', queryset=Certificado.objects.filter(tipo=Certificado.SCTR), to_attr='sctr_certificados')
        ).order_by('-activo', 'nombre')
        q = self.request.GET.get('q', '').strip()
        if q:
            queryset = queryset.filter(
                Q(nombre__icontains=q)
                | Q(ruc__icontains=q)
            )
        estado = self.request.GET.get('estado', '').strip()
        if estado in ('0', '1'):
            queryset = queryset.filter(activo=(estado == '1'))
        return queryset

    def get_context_data(self, **kwargs):
        if self.request.user.role == User.PLANTA:
            kwargs['trabajadores'] = self.object_list
            kwargs['empresas_filtro'] = Empresa.objects.filter(activo=True, trabajadores__isnull=False).distinct().order_by('nombre')
            kwargs['empresa_seleccionada'] = self.request.GET.get('empresa', '')
            kwargs['q'] = self.request.GET.get('q', '')
            return super().get_context_data(**kwargs)
        kwargs.setdefault('q', self.request.GET.get('q', ''))
        kwargs.setdefault('estado', self.request.GET.get('estado', ''))
        return super().get_context_data(**kwargs)


class EmpresaBuscarView(LoginRequiredMixin, ListView):
    model = Empresa
    template_name = 'control/empresas/buscar.html'
    context_object_name = 'empresas'
    paginate_by = 20
    login_url = reverse_lazy('app_users:login')

    def dispatch(self, request, *args, **kwargs):
        if request.user.role == User.USUARIO_EMPRESA:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Empresa.objects.annotate(
            total_trabajadores=Count('trabajadores', distinct=True)
        ).order_by('-homologado', 'nombre')
        q = self.request.GET.get('q', '').strip()
        if q:
            queryset = queryset.filter(
                Q(nombre__icontains=q)
                | Q(ruc__icontains=q)
            )
        estado = self.request.GET.get('estado', '').strip()
        if estado in ('0', '1'):
            queryset = queryset.filter(activo=(estado == '1'))
        habilitado = self.request.GET.get('habilitado', '').strip()
        if habilitado in ('0', '1'):
            queryset = queryset.filter(homologado=(habilitado == '1'))
        return queryset

    def get_context_data(self, **kwargs):
        kwargs.setdefault('q', self.request.GET.get('q', ''))
        kwargs.setdefault('estado', self.request.GET.get('estado', ''))
        kwargs.setdefault('habilitado', self.request.GET.get('habilitado', ''))
        return super().get_context_data(**kwargs)


class EmpresaCreateView(AdministrarEmpresasMixin, CreateView):
    model = Empresa
    form_class = EmpresaForm
    template_name = 'control/empresas/form.html'
    success_url = reverse_lazy('app_control:empresa_lista')

    def form_valid(self, form):
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


class EmpresaDetailView(LoginRequiredMixin, DetailView):
    model = Empresa
    template_name = 'control/empresas/detalle.html'
    context_object_name = 'empresa'

    def dispatch(self, request, *args, **kwargs):
        if request.user.role == User.USUARIO_EMPRESA:
            return super().dispatch(request, *args, **kwargs)
        if request.user.role not in VerEmpresasMixin.required_roles and not request.user.is_superuser:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.role == User.USUARIO_EMPRESA:
            return queryset.filter(pk=self.request.user.empresa_id)
        return queryset

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if request.user.role != User.USUARIO_EMPRESA:
            raise PermissionDenied
        sctr = self.object.certificados.filter(tipo=Certificado.SCTR).first()
        form = SCTRForm(request.POST, request.FILES, instance=sctr, empresa=self.object)
        if form.is_valid():
            form.save()
            messages.success(request, 'SCTR actualizado correctamente.')
            return redirect('app_control:empresa_detalle', pk=self.object.pk)
        context = self.get_context_data(sctr_form=form)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        trabajadores = self.object.trabajadores.order_by('apellidos', 'nombres')
        kwargs.setdefault('total_trabajadores', trabajadores.count())
        kwargs.setdefault('total_usuarios', self.object.usuarios.count())
        kwargs.setdefault('sctr', self.object.certificados.filter(tipo=Certificado.SCTR).first())
        if self.request.user.role == User.USUARIO_EMPRESA:
            kwargs.setdefault('sctr_form', SCTRForm(instance=kwargs['sctr'], empresa=self.object))
        kwargs.setdefault('trabajadores', trabajadores)
        kwargs.setdefault(
            'trabajadores_por_estado',
            [
                {
                    'habilitado': grupo['habilitado'],
                    'total': grupo['total'],
                    'label': 'Habilitado' if grupo['habilitado'] else 'No habilitado',
                }
                for grupo in trabajadores.values('habilitado').annotate(total=Count('habilitado')).order_by('habilitado')
            ],
        )
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
    template_name = 'control/trabajadores/lista_empresa.html'
    context_object_name = 'trabajadores'
    paginate_by = 20
    sortable_columns = {
        'dni': ('dni',),
        'nombre': ('apellidos', 'nombres'),
        'empresa': ('empresa__nombre', 'apellidos', 'nombres'),
        'cargo': ('cargo', 'apellidos', 'nombres'),
        'induccion': ('tiene_induccion', 'apellidos', 'nombres'),
        'aptitud_medica': ('tiene_aptitud_medica', 'apellidos', 'nombres'),
        'estado': ('habilitado', 'apellidos', 'nombres'),
    }

    def get_queryset(self):
        certificados = Certificado.objects.filter(trabajador=OuterRef('pk'))
        queryset = Trabajador.objects.select_related('empresa').prefetch_related(
            Prefetch(
                'certificados',
                queryset=Certificado.objects.filter(tipo=Certificado.CURSOS),
                to_attr='cursos_lista',
            )
        ).annotate(
            tiene_induccion=Exists(certificados.filter(tipo=Certificado.INDUCCION)),
            tiene_aptitud_medica=Exists(certificados.filter(tipo=Certificado.APTITUD_MEDICA)),
            **{
                f'tiene_curso_{codigo.lower()}': Exists(
                    certificados.filter(tipo=Certificado.CURSOS, curso=codigo)
                )
                for codigo, label in Certificado.CURSO_CHOICES
            },
        ).order_by('habilitado', 'apellidos', 'nombres')
        if self.request.user.role == User.USUARIO_EMPRESA:
            queryset = queryset.filter(empresa=self.request.user.empresa)
        q = self.request.GET.get('q', '').strip()
        if q:
            queryset = queryset.filter(
                Q(dni__icontains=q)
                | Q(nombres__icontains=q)
                | Q(apellidos__icontains=q)
                | Q(cargo__icontains=q)
                | Q(empresa__nombre__icontains=q)
            )
        estado = self.request.GET.get('estado', '').strip()
        if estado in ('0', '1'):
            queryset = queryset.filter(habilitado=(estado == '1'))
        empresa_id = self.request.GET.get('empresa', '').strip()
        if self.request.user.role != User.USUARIO_EMPRESA and empresa_id.isdigit():
            queryset = queryset.filter(empresa_id=empresa_id)
        sort = self.request.GET.get('sort', '').strip()
        direction = self.request.GET.get('dir', 'asc').strip().lower()
        if direction not in ('asc', 'desc'):
            direction = 'asc'
        order_fields = self.sortable_columns.get(sort)
        if not order_fields:
            course_codes = {codigo.lower() for codigo, label in Certificado.CURSO_CHOICES}
            if sort in course_codes:
                order_fields = (f'tiene_curso_{sort}', 'apellidos', 'nombres')
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
        kwargs.setdefault('estado_choices', ((1, 'Habilitado'), (0, 'No habilitado')))
        kwargs.setdefault('sortable_columns', {
            'dni': 'DNI',
            'nombre': 'Nombre completo',
             'empresa': 'Empresa',
             'cargo': 'Cargo',
             'induccion': 'Inducción',
            'aptitud_medica': 'Aptitud médica',
        })
        kwargs['sortable_columns'].update({codigo.lower(): label for codigo, label in Certificado.CURSO_CHOICES})
        kwargs['sortable_columns']['estado'] = 'Estado'
        kwargs.setdefault('cursos_columnas', Certificado.CURSO_CHOICES)
        kwargs.setdefault('es_empresa', self.request.user.role == User.USUARIO_EMPRESA)
        if kwargs['es_empresa']:
            kwargs['sortable_columns'].pop('empresa', None)
        kwargs.setdefault('empresa', getattr(self.request.user, 'empresa', None))
        return super().get_context_data(**kwargs)


class TrabajadorBuscarView(VerTrabajadoresMixin, View):
    template_name = 'control/trabajadores/buscar.html'

    def get(self, request):
        q = request.GET.get('q', '').strip()
        trabajador = None
        resultados = 0
        if q:
            queryset = Trabajador.objects.select_related('empresa')
            if request.user.role == User.USUARIO_EMPRESA:
                queryset = queryset.filter(empresa=request.user.empresa)
            queryset = queryset.filter(
                Q(dni__icontains=q)
                | Q(nombres__icontains=q)
                | Q(apellidos__icontains=q)
            )
            resultados = queryset.count()
            if resultados == 1:
                trabajador = queryset.first()
        context = {
            'q': q,
            'trabajador': trabajador,
            'resultados': resultados,
            'es_empresa': request.user.role == User.USUARIO_EMPRESA,
            'puede_ver_detalle': request.user.role in (
                User.ADMINISTRADOR,
                User.BECA_AZUL,
                User.PLANTA,
                User.USUARIO_EMPRESA,
            ),
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


class TrabajadorDetailView(VerTrabajadorDetalleMixin, DetailView):
    model = Trabajador
    template_name = 'control/trabajadores/detalle.html'
    context_object_name = 'trabajador'

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.role == User.USUARIO_EMPRESA:
            queryset = queryset.filter(empresa=self.request.user.empresa)
        return queryset

    def get_context_data(self, **kwargs):
        certificados_lista = list(self.object.certificados.all().order_by('-fecha_emision'))
        certificados = {certificado.tipo: certificado for certificado in certificados_lista}
        cursos = {
            certificado.curso: certificado
            for certificado in certificados_lista
            if certificado.tipo == Certificado.CURSOS
        }
        kwargs.setdefault('certificados', certificados_lista)
        kwargs.setdefault('certificados_requeridos', [
            {'tipo': Certificado.INDUCCION, 'label': 'Inducción', 'objeto': certificados.get(Certificado.INDUCCION)},
            {'tipo': Certificado.APTITUD_MEDICA, 'label': 'Aptitud médica', 'objeto': certificados.get(Certificado.APTITUD_MEDICA)},
        ])
        kwargs.setdefault('cursos', [{'codigo': codigo, 'nombre': label, 'certificado': cursos.get(codigo)} for codigo, label in Certificado.CURSO_CHOICES])
        kwargs.setdefault('incidencias', self.object.incidencias.select_related('registrado_por'))
        kwargs.setdefault('es_empresa', self.request.user.role == User.USUARIO_EMPRESA)
        return super().get_context_data(**kwargs)


class TrabajadorHomologacionView(BecaAzulRequiredMixin, View):
    def post(self, request, pk):
        trabajador = get_object_or_404(Trabajador, pk=pk)
        estado = request.POST.get('estado')
        if estado not in ('0', '1'):
            messages.error(self.request, 'Estado no válido.')
            return redirect('app_control:trabajador_detalle', pk=trabajador.pk)
        trabajador.habilitado = estado == '1'
        trabajador.save(update_fields=['habilitado'])
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
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        self.trabajador = self.get_trabajador()
        form.instance.trabajador = self.trabajador
        with transaction.atomic():
            if form.cleaned_data.get('tipo') == Certificado.CURSOS:
                Certificado.objects.filter(
                    trabajador=self.trabajador,
                    tipo=Certificado.CURSOS,
                    curso=form.cleaned_data.get('curso'),
                ).delete()
            response = super().form_valid(form)
        messages.success(self.request, 'Certificado registrado correctamente.')
        return response

    def get_success_url(self):
        return reverse('app_control:trabajador_detalle', args=[self.trabajador.pk])


class CertificadoUpdateView(AdministrarTrabajadoresMixin, UpdateView):
    model = Certificado
    form_class = CertificadoForm
    template_name = 'control/certificados/form.html'

    def get_context_data(self, **kwargs):
        kwargs.setdefault('trabajador', self.object.trabajador)
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


class IncidenciaCreateView(GestionarIncidenciasMixin, CreateView):
    model = Incidencia
    form_class = IncidenciaForm
    template_name = 'control/incidencias/form.html'

    def get_trabajador(self):
        return get_object_or_404(Trabajador, pk=self.kwargs['trabajador_pk'])

    def get_context_data(self, **kwargs):
        kwargs.setdefault('trabajador', self.get_trabajador())
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        self.trabajador = self.get_trabajador()
        form.instance.trabajador = self.trabajador
        form.instance.registrado_por = self.request.user
        messages.success(self.request, 'Incidencia registrada correctamente.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('app_control:trabajador_detalle', args=[self.trabajador.pk])


class IncidenciaUpdateView(GestionarIncidenciasMixin, UpdateView):
    model = Incidencia
    form_class = IncidenciaForm
    template_name = 'control/incidencias/form.html'

    def get_context_data(self, **kwargs):
        kwargs.setdefault('trabajador', self.object.trabajador)
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, 'Incidencia actualizada correctamente.')
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('app_control:trabajador_detalle', args=[self.object.trabajador.pk])


class IncidenciaDeleteView(GestionarIncidenciasMixin, DeleteView):
    model = Incidencia
    template_name = 'control/incidencias/confirm_delete.html'

    def get_context_data(self, **kwargs):
        kwargs.setdefault('trabajador', self.object.trabajador)
        return super().get_context_data(**kwargs)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        trabajador_pk = self.object.trabajador.pk
        self.object.delete()
        messages.success(self.request, 'Incidencia eliminada correctamente.')
        return HttpResponseRedirect(reverse('app_control:trabajador_detalle', args=[trabajador_pk]))


class TrabajadorEmpresaListView(TrabajadorEmpresaPermisoMixin, ListView):
    model = Trabajador
    template_name = 'control/trabajadores/lista_empresa.html'
    context_object_name = 'trabajadores'
    paginate_by = 20

    def get_queryset(self):
        certificados = Certificado.objects.filter(trabajador=OuterRef('pk'))
        queryset = Trabajador.objects.filter(empresa=self.request.user.empresa).select_related(
            'empresa'
        ).prefetch_related(
            Prefetch(
                'certificados',
                queryset=Certificado.objects.filter(tipo=Certificado.CURSOS),
                to_attr='cursos_lista',
            )
        ).annotate(
            tiene_induccion=Exists(certificados.filter(tipo=Certificado.INDUCCION)),
            tiene_aptitud_medica=Exists(certificados.filter(tipo=Certificado.APTITUD_MEDICA)),
            **{
                f'tiene_curso_{codigo.lower()}': Exists(
                    certificados.filter(tipo=Certificado.CURSOS, curso=codigo)
                )
                for codigo, label in Certificado.CURSO_CHOICES
            },
        ).order_by('habilitado', 'apellidos', 'nombres')
        q = self.request.GET.get('q', '').strip()
        if q:
            queryset = queryset.filter(
                Q(dni__icontains=q)
                | Q(nombres__icontains=q)
                | Q(apellidos__icontains=q)
                | Q(cargo__icontains=q)
            )
        estado = self.request.GET.get('estado', '').strip()
        if estado in ('0', '1'):
            queryset = queryset.filter(habilitado=(estado == '1'))
        sort = self.request.GET.get('sort', '').strip()
        direction = self.request.GET.get('dir', 'asc').strip().lower()
        if direction not in ('asc', 'desc'):
            direction = 'asc'
        sortable_columns = {
            'dni': ('dni',),
            'nombre': ('apellidos', 'nombres'),
            'cargo': ('cargo', 'apellidos', 'nombres'),
            'induccion': ('tiene_induccion', 'apellidos', 'nombres'),
            'aptitud_medica': ('tiene_aptitud_medica', 'apellidos', 'nombres'),
            'estado': ('habilitado', 'apellidos', 'nombres'),
        }
        sortable_columns.update({
            codigo.lower(): (f'tiene_curso_{codigo.lower()}', 'apellidos', 'nombres')
            for codigo, label in Certificado.CURSO_CHOICES
        })
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
        kwargs.setdefault('estado_choices', ((1, 'Habilitado'), (0, 'No habilitado')))
        kwargs.setdefault('sortable_columns', {
            'dni': 'DNI',
            'nombre': 'Nombre completo',
            'cargo': 'Cargo',
            'induccion': 'Inducción',
            'aptitud_medica': 'Aptitud médica',
        })
        kwargs['sortable_columns'].update({codigo.lower(): label for codigo, label in Certificado.CURSO_CHOICES})
        kwargs['sortable_columns']['estado'] = 'Estado del trabajador'
        kwargs.setdefault('cursos_columnas', Certificado.CURSO_CHOICES)
        kwargs.setdefault('empresa', self.request.user.empresa)
        kwargs.setdefault('es_empresa', True)
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
        kwargs.setdefault('incidencias', self.object.incidencias.select_related('registrado_por'))
        kwargs.setdefault('es_empresa', True)
        return super().get_context_data(**kwargs)


class TrabajadorEmpresaCreateView(TrabajadorEmpresaBaseMixin, CreateView):
    model = Trabajador
    form_class = TrabajadorEmpresaForm
    template_name = 'control/trabajadores/form.html'
    success_url = reverse_lazy('app_control:trabajador_lista')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['empresa'] = self.request.user.empresa
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault(
            'certificado_formset',
            CertificadoCargaFormSet(
                initial=[{'tipo': Certificado.CURSOS, 'curso': curso} for curso, label in Certificado.CURSO_CHOICES],
                prefix='certificados',
            ),
        )
        return context

    def form_valid(self, form):
        formset = CertificadoCargaFormSet(self.request.POST, self.request.FILES, prefix='certificados')
        if not formset.is_valid():
            return self.render_to_response(self.get_context_data(form=form, certificado_formset=formset))
        form.instance.empresa = self.request.user.empresa
        with transaction.atomic():
            self.object = form.save()
            for certificado_form in formset:
                if certificado_form.cleaned_data and all(
                    certificado_form.cleaned_data.get(field)
                    for field in ('curso', 'archivo', 'fecha_emision', 'fecha_vencimiento')
                ):
                    certificado = certificado_form.save(commit=False)
                    certificado.trabajador = self.object
                    certificado.save()
        messages.success(self.request, 'Trabajador registrado correctamente.')
        return HttpResponseRedirect(self.get_success_url())


class TrabajadorEmpresaUpdateView(TrabajadorEmpresaBaseMixin, UpdateView):
    model = Trabajador
    form_class = TrabajadorEmpresaForm
    template_name = 'control/trabajadores/form.html'
    success_url = reverse_lazy('app_control:trabajador_lista')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['empresa'] = self.request.user.empresa
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        certificados = {
            certificado.curso: certificado
            for certificado in self.object.certificados.filter(tipo=Certificado.CURSOS)
        }
        initial = []
        for curso, label in Certificado.CURSO_CHOICES:
            certificado = certificados.get(curso)
            initial.append({
                'tipo': Certificado.CURSOS,
                'curso': curso,
                'fecha_emision': certificado.fecha_emision.isoformat() if certificado else '',
                'fecha_vencimiento': certificado.fecha_vencimiento.isoformat() if certificado else '',
                'archivo': certificado.archivo if certificado else '',
            })
        context.setdefault('certificado_formset', CertificadoCargaFormSet(initial=initial, prefix='certificados'))
        return context

    def form_valid(self, form):
        formset = CertificadoCargaFormSet(self.request.POST, self.request.FILES, prefix='certificados')
        if not formset.is_valid():
            return self.render_to_response(self.get_context_data(form=form, certificado_formset=formset))
        with transaction.atomic():
            self.object = form.save()
            cursos_existentes = {
                certificado.curso: certificado
                for certificado in self.object.certificados.filter(tipo=Certificado.CURSOS)
            }
            for certificado_form in formset:
                if certificado_form.cleaned_data:
                    curso = certificado_form.cleaned_data.get('curso')
                    if not curso or not all(certificado_form.cleaned_data.get(field) for field in ('fecha_emision', 'fecha_vencimiento')):
                        continue
                    certificado = cursos_existentes.get(curso, Certificado())
                    certificado.tipo = Certificado.CURSOS
                    certificado.curso = curso
                    certificado.fecha_emision = certificado_form.cleaned_data['fecha_emision']
                    certificado.fecha_vencimiento = certificado_form.cleaned_data['fecha_vencimiento']
                    archivo = certificado_form.cleaned_data.get('archivo')
                    if archivo:
                        certificado.archivo = archivo
                    elif not certificado.pk:
                        continue
                    certificado.trabajador = self.object
                    certificado.save()
        messages.success(self.request, 'Trabajador actualizado correctamente.')
        return HttpResponseRedirect(self.get_success_url())


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
    success_url = reverse_lazy('app_control:trabajador_lista')

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

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['tipo'].disabled = True
        return form

    def get_trabajador(self):
        return get_object_or_404(Trabajador, pk=self.kwargs['trabajador_pk'], empresa=self.request.user.empresa)

    def get_context_data(self, **kwargs):
        kwargs.setdefault('trabajador', self.get_trabajador())
        kwargs.setdefault('es_curso', True)
        return super().get_context_data(**kwargs)

    def get_initial(self):
        initial = super().get_initial()
        initial['tipo'] = Certificado.CURSOS
        initial['curso'] = self.request.GET.get('curso', '')
        return initial

    def form_valid(self, form):
        self.trabajador = self.get_trabajador()
        form.instance.trabajador = self.trabajador
        form.instance.tipo = Certificado.CURSOS
        with transaction.atomic():
            Certificado.objects.filter(
                trabajador=self.trabajador,
                tipo=Certificado.CURSOS,
                curso=form.cleaned_data.get('curso'),
            ).delete()
            response = super().form_valid(form)
        messages.success(self.request, 'Curso registrado correctamente.')
        return response

    def get_success_url(self):
        return reverse('app_control:trabajador_empresa_detalle', args=[self.trabajador.pk])


class CertificadoEmpresaUpdateView(TrabajadorEmpresaBaseMixin, UpdateView):
    model = Certificado
    form_class = CertificadoForm
    template_name = 'control/certificados/form.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        for field_name in ('tipo', 'curso'):
            form.fields[field_name].disabled = True
        form.initial['fecha_emision'] = self.object.fecha_emision.isoformat()
        form.initial['fecha_vencimiento'] = self.object.fecha_vencimiento.isoformat()
        return form

    def get_queryset(self):
        return Certificado.objects.filter(
            trabajador__empresa=self.request.user.empresa
        )

    def get_context_data(self, **kwargs):
        kwargs.setdefault('trabajador', self.object.trabajador)
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
