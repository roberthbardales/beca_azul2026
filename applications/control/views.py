from datetime import timedelta
from unicodedata import combining, normalize

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.core.mail import EmailMultiAlternatives, send_mail
from django.db import transaction
from django.db.models import Count, Exists, Func, OuterRef, Prefetch, Q, Value
from django.db.models.functions import Concat, Lower
from django.http import FileResponse, Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils.html import escape
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView, View

from applications.users.mixins import (
    AdministrarEmpresasMixin,
    AdministrarTrabajadoresMixin,
    BecaAzulRequiredMixin,
    ConsultarTrabajadoresMixin,
    GestionarIncidenciasMixin,
    TrabajadorEmpresaPermisoMixin,
    UsuarioGaritaRequiredMixin,
    VerEmpresasMixin,
    VerTrabajadorDetalleMixin,
    VerTrabajadoresMixin,
)
from applications.users.models import User

from .forms import (
    CertificadoForm,
    EmpresaForm,
    IncidenciaForm,
    SCTRForm,
    SCTRSaludForm,
    HomologacionForm,
    TrabajadorEmpresaForm,
    TrabajadorForm,
)
from .models import Certificado, CursoObligatorio, Empresa, Incidencia, Trabajador


class TrabajadorActivoRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        trabajador = None
        if 'trabajador_pk' in kwargs:
            trabajador = Trabajador.objects.filter(pk=kwargs['trabajador_pk']).first()
        elif 'pk' in kwargs:
            if self.model is Trabajador:
                trabajador = Trabajador.objects.filter(pk=kwargs['pk']).first()
            elif self.model is Certificado:
                trabajador = Trabajador.objects.filter(certificados__pk=kwargs['pk']).first()
            elif self.model is Incidencia:
                trabajador = Trabajador.objects.filter(incidencias__pk=kwargs['pk']).first()
        if trabajador and (not trabajador.activo or not trabajador.empresa.activo):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class EmpresaActivaRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        empresa = None
        if 'trabajador_pk' in kwargs:
            empresa = Empresa.objects.filter(trabajadores__pk=kwargs['trabajador_pk']).first()
        elif 'pk' in kwargs:
            if getattr(self, 'model', None) is Empresa:
                empresa = Empresa.objects.filter(pk=kwargs['pk']).first()
            elif getattr(self, 'model', None) is Trabajador:
                empresa = Empresa.objects.filter(trabajadores__pk=kwargs['pk']).first()
            elif getattr(self, 'model', None) is Certificado:
                empresa = Empresa.objects.filter(
                    Q(certificados__pk=kwargs['pk']) | Q(trabajadores__certificados__pk=kwargs['pk'])
                ).first()
            elif getattr(self, 'model', None) is Incidencia:
                empresa = Empresa.objects.filter(trabajadores__incidencias__pk=kwargs['pk']).first()
        if empresa and not empresa.activo:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class DashboardView(LoginRequiredMixin, View):
    template_name = 'users/dashboard.html'

    def get(self, request):
        if not request.user.is_superuser and request.user.role not in (
            User.ADMINISTRADOR,
            User.BECA_AZUL,
            User.PLANTA,
        ):
            raise PermissionDenied
        Empresa.sincronizar_homologaciones()
        hoy = timezone.localdate()
        limite_30 = hoy + timedelta(days=30)
        limite_60 = hoy + timedelta(days=60)

        total_empresas = Empresa.objects.count()
        empresas_activas = Empresa.objects.filter(activo=True).count()
        empresas_habilitadas = Empresa.objects.filter(activo=True, homologacion=True).count()
        empresas_no_homologadas = Empresa.objects.filter(activo=True, homologacion=False).count()
        empresas_desactivadas = Empresa.objects.filter(activo=False).count()


        total_trabajadores = Trabajador.objects.count()
        inducciones = Certificado.objects.filter(tipo=Certificado.INDUCCION)
        inducciones_vigentes = sum(certificado.validacion_vigente for certificado in inducciones)
        inducciones_vencidas = inducciones.filter(fecha_vencimiento__lt=hoy).count()
        certificados_empresa = Certificado.objects.filter(
            tipo__in=(Certificado.SCTR_PENSION, Certificado.SCTR_SALUD, Certificado.HOMOLOGACION)
        )
        trabajadores = list(
            Trabajador.objects.select_related('empresa').prefetch_related(
                Prefetch(
                    'empresa__certificados',
                    queryset=certificados_empresa,
                    to_attr='certificados_habilitacion',
                )
            )
        )
        trabajadores_habilitados = sum(trabajador.habilitado_efectivo for trabajador in trabajadores)
        trabajadores_desactivados = sum(not trabajador.activo for trabajador in trabajadores)
        trabajadores_no_habilitados = sum(
            trabajador.activo and not trabajador.habilitado_efectivo
            for trabajador in trabajadores
        )
        trabajadores_sctr_salud = sum(trabajador.sctr_salud_efectivo for trabajador in trabajadores)
        trabajadores_sctr_pension = sum(trabajador.sctr_pension_efectivo for trabajador in trabajadores)
        sctr_salud_proximos_vencer = Certificado.objects.filter(
            empresa__isnull=False,
            tipo=Certificado.SCTR_SALUD,
            fecha_vencimiento__gte=hoy,
            fecha_vencimiento__lte=limite_30,
        ).count()
        sctr_pension_proximos_vencer = Certificado.objects.filter(
            empresa__isnull=False,
            tipo=Certificado.SCTR_PENSION,
            fecha_vencimiento__gte=hoy,
            fecha_vencimiento__lte=limite_30,
        ).count()
        cursos_vigentes = []
        for codigo, etiqueta in Certificado.CURSO_CHOICES:
            certificados_curso = Certificado.objects.filter(
                tipo=Certificado.CURSOS,
                curso=codigo,
            )
            cursos_vigentes.append(
                {
                    'codigo': codigo,
                    'nombre': etiqueta,
                    'total': sum(certificado.validacion_vigente for certificado in certificados_curso),
                }
            )


        total_certificados = Certificado.objects.count()
        certificados_sin_vencimiento = 0
        certificados_vencidos = Certificado.objects.filter(fecha_vencimiento__lt=hoy).count()
        certificados_proximos_30 = Certificado.objects.filter(
            fecha_vencimiento__gte=hoy, fecha_vencimiento__lte=limite_30
        ).count()
        certificados_proximos_60 = Certificado.objects.filter(
            fecha_vencimiento__gte=hoy, fecha_vencimiento__lte=limite_60
        ).count()

        trabajadores_por_estado = {
            'Habilitado': trabajadores_habilitados,
            'No habilitado': trabajadores_no_habilitados,
            'Desactivado': trabajadores_desactivados,
        }

        trabajadores_por_empresa = []
        for empresa in Empresa.objects.order_by('nombre'):
            trabajadores_empresa = [trabajador for trabajador in trabajadores if trabajador.empresa_id == empresa.pk]
            trabajadores_por_empresa.append(
                {
                    'nombre': empresa.nombre,
                    'habilitados': sum(trabajador.habilitado_efectivo for trabajador in trabajadores_empresa),
                    'inhabilitados': len(trabajadores_empresa) - sum(
                        trabajador.habilitado_efectivo for trabajador in trabajadores_empresa
                    ),
                }
            )

        certificados_vigentes = Certificado.objects.filter(
            fecha_vencimiento__gt=limite_30
        ).count()

        vencimientos_por_empresa = Empresa.objects.annotate(
            vigentes=Count(
                'certificados',
                filter=Q(certificados__fecha_vencimiento__gt=limite_30),
                distinct=True,
            ),
            proximos=Count(
                'certificados',
                filter=Q(
                    certificados__fecha_vencimiento__gte=hoy,
                    certificados__fecha_vencimiento__lte=limite_30,
                ),
                distinct=True,
            ),
            vencidos=Count(
                'certificados',
                filter=Q(certificados__fecha_vencimiento__lt=hoy),
                distinct=True,
            ),
        ).order_by('nombre')

        context = {
            'total_empresas': total_empresas,
            'empresas_activas': empresas_activas,
            'empresas_inactivas': total_empresas - empresas_activas,
            'empresas_habilitadas': empresas_habilitadas,
            'empresas_no_homologadas': empresas_no_homologadas,
            'empresas_desactivadas': empresas_desactivadas,
            'total_trabajadores': total_trabajadores,
            'inducciones_vigentes': inducciones_vigentes,
            'inducciones_vencidas': inducciones_vencidas,
            'trabajadores_habilitados': trabajadores_habilitados,
            'trabajadores_no_habilitados': trabajadores_no_habilitados,
            'trabajadores_desactivados': trabajadores_desactivados,
            'trabajadores_sctr_salud': trabajadores_sctr_salud,
            'trabajadores_sctr_pension': trabajadores_sctr_pension,
            'trabajadores_sin_sctr_salud': total_trabajadores - trabajadores_sctr_salud,
            'trabajadores_sin_sctr_pension': total_trabajadores - trabajadores_sctr_pension,
            'sctr_salud_proximos_vencer': sctr_salud_proximos_vencer,
            'sctr_pension_proximos_vencer': sctr_pension_proximos_vencer,
            'cursos_vigentes': cursos_vigentes,
            'total_certificados': total_certificados,
            'certificados_vencidos': certificados_vencidos,
            'certificados_sin_vencimiento': certificados_sin_vencimiento,
            'certificados_proximos_30': certificados_proximos_30,
            'certificados_proximos_60': certificados_proximos_60,
            'trabajadores_por_estado': trabajadores_por_estado,
            'dashboard_charts': {
                'estados_trabajadores': {
                    'labels': list(trabajadores_por_estado),
                    'data': list(trabajadores_por_estado.values()),
                },
                'trabajadores_empresa': {
                    'labels': [empresa['nombre'] for empresa in trabajadores_por_empresa],
                    'habilitados': [empresa['habilitados'] for empresa in trabajadores_por_empresa],
                    'inhabilitados': [empresa['inhabilitados'] for empresa in trabajadores_por_empresa],
                },
                'cumplimiento': [
                    certificados_vigentes,
                    certificados_proximos_30,
                    certificados_vencidos,
                ],
                'vencimientos_empresa': {
                    'labels': [empresa.nombre for empresa in vencimientos_por_empresa],
                    'vigentes': [empresa.vigentes for empresa in vencimientos_por_empresa],
                    'proximos': [empresa.proximos for empresa in vencimientos_por_empresa],
                    'vencidos': [empresa.vencidos for empresa in vencimientos_por_empresa],
                },
            },
        }
        return render(request, self.template_name, context)


class ReportesView(LoginRequiredMixin, View):
    template_name = 'control/reportes.html'
    reportes = ('vencimientos', 'vencimientos_empresa', 'trabajadores', 'empresas')

    def get(self, request):
        context = self._get_context(request)
        return render(request, self.template_name, context)

    def post(self, request):
        if request.user.role != User.BECA_AZUL:
            raise PermissionDenied

        context = self._get_context(request)
        titulo = dict((clave, titulo) for clave, titulo, _ in context['reportes'])[context['reporte_actual']]
        html = render_to_string('control/reportes_email.html', context, request=request)
        email = EmailMultiAlternatives(
            subject=f'Reporte: {titulo}',
            body=f'Reporte: {titulo}. Este correo contiene una versión HTML del reporte.',
            from_email=None,
            to=settings.REPORTES_EMAILS,
        )
        email.attach_alternative(html, 'text/html')
        try:
            email.send()
        except Exception:
            messages.error(request, 'No se pudo enviar el reporte por correo.')
        else:
            messages.success(request, 'Reporte enviado correctamente por correo.')
        return redirect(f'{reverse("app_control:reportes")}?reporte={context["reporte_actual"]}')

    def _get_context(self, request):
        if not request.user.is_superuser and request.user.role not in (
            User.ADMINISTRADOR, User.BECA_AZUL, User.PLANTA, User.USUARIO_EMPRESA
        ):
            raise PermissionDenied
        Empresa.sincronizar_homologaciones()

        reporte = request.POST.get('reporte') or request.GET.get('reporte', 'vencimientos')
        if reporte not in self.reportes:
            reporte = 'vencimientos'

        hoy = timezone.localdate()
        limite_30 = hoy + timedelta(days=30)
        certificados = Certificado.objects.select_related('empresa', 'trabajador__empresa')
        trabajadores = Trabajador.objects.select_related('empresa')
        empresas = Empresa.objects.annotate(total_trabajadores=Count('trabajadores', distinct=True)).prefetch_related(
            Prefetch(
                'certificados',
                queryset=Certificado.objects.filter(
                    tipo__in=(Certificado.SCTR_PENSION, Certificado.SCTR_SALUD, Certificado.HOMOLOGACION)
                ),
                to_attr='certificados_habilitacion',
            )
        )

        if request.user.role == User.USUARIO_EMPRESA:
            certificados = certificados.filter(
                Q(empresa_id=request.user.empresa_id) | Q(trabajador__empresa_id=request.user.empresa_id)
            )
            trabajadores = trabajadores.filter(empresa_id=request.user.empresa_id)
            empresas = empresas.filter(id=request.user.empresa_id)

        trabajadores_lista = list(trabajadores)

        if reporte == 'vencimientos':
            certificados = certificados.filter(
                tipo__in=(Certificado.INDUCCION, Certificado.APTITUD_MEDICA)
            )
        elif reporte == 'vencimientos_empresa':
            certificados = certificados.filter(
                empresa__isnull=False,
                tipo__in=(Certificado.HOMOLOGACION, Certificado.SCTR_PENSION, Certificado.SCTR_SALUD),
            )

        context = {
            'reporte_actual': reporte,
            'reportes': (
                ('vencimientos', 'Aptitud médica e inducción', 'Vencimientos de aptitud médica e inducción'),
                ('vencimientos_empresa', 'Homologación y SCTR', 'Vencimientos de homologación y SCTR'),
                ('trabajadores', 'Trabajadores', 'Estado del personal registrado'),
                ('empresas', 'Empresas', 'Empresas y cantidad de trabajadores'),
            ),
            'total_trabajadores': trabajadores.count(),
            'total_empresas': empresas.count(),
            'total_certificados': certificados.count(),
            'vencidos': certificados.filter(fecha_vencimiento__lt=hoy).count(),
            'por_vencer': certificados.filter(
                fecha_vencimiento__gte=hoy, fecha_vencimiento__lte=limite_30
            ).count(),
            'trabajadores_no_habilitados': sum(
                not trabajador.habilitado_efectivo for trabajador in trabajadores_lista
            ),
            'empresas_pendientes': empresas.filter(homologacion=False).count(),
        }

        if reporte in ('vencimientos', 'vencimientos_empresa'):
            filas = list(certificados.order_by('fecha_vencimiento'))
            context['filas'] = [
                certificado for certificado in filas
                if certificado.estado in ('Vencido', 'Próximo a vencer')
            ]
        elif reporte == 'trabajadores':
            context['filas'] = trabajadores.order_by('empresa__nombre', 'apellidos', 'nombres')
        elif reporte == 'empresas':
            context['filas'] = empresas.order_by('nombre')
        return context


class EmpresaListView(VerEmpresasMixin, ListView):
    model = Empresa
    template_name = 'control/empresas/lista.html'
    context_object_name = 'empresas'
    paginate_by = 20

    def get_queryset(self):
        Empresa.sincronizar_homologaciones()
        queryset = Empresa.objects.annotate(
            total_trabajadores=Count('trabajadores', distinct=True),
            total_usuarios=Count('usuarios', distinct=True),
        ).prefetch_related(
            Prefetch('certificados', queryset=Certificado.objects.filter(tipo=Certificado.SCTR_PENSION), to_attr='sctr_pension_certificados'),
            Prefetch('certificados', queryset=Certificado.objects.filter(tipo=Certificado.SCTR_SALUD), to_attr='sctr_salud_certificados'),
            Prefetch('certificados', queryset=Certificado.objects.filter(tipo=Certificado.HOMOLOGACION), to_attr='homologacion_certificados'),
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
        homologacion = self.request.GET.get('homologacion', '').strip()
        if homologacion in ('0', '1'):
            queryset = queryset.filter(homologacion=(homologacion == '1'))
        return queryset

    def get_context_data(self, **kwargs):
        kwargs.setdefault('q', self.request.GET.get('q', ''))
        kwargs.setdefault('estado', self.request.GET.get('estado', ''))
        kwargs.setdefault('homologacion', self.request.GET.get('homologacion', ''))
        kwargs.setdefault('es_garita', self.request.user.role == User.GARITA)
        context = super().get_context_data(**kwargs)
        for empresa in context['empresas']:
            empresa.invalidar_homologacion_si_corresponde()
        return context


class EmpresaCreateView(AdministrarEmpresasMixin, CreateView):
    model = Empresa
    form_class = EmpresaForm
    template_name = 'control/empresas/form.html'
    success_url = reverse_lazy('app_control:empresa_lista')

    def form_valid(self, form):
        messages.success(self.request, 'Empresa creada correctamente.')
        return super().form_valid(form)


class EmpresaUpdateView(EmpresaActivaRequiredMixin, BecaAzulRequiredMixin, UpdateView):
    model = Empresa
    form_class = EmpresaForm
    template_name = 'control/empresas/form.html'
    success_url = reverse_lazy('app_control:empresa_lista')

    def form_valid(self, form):
        messages.success(self.request, 'Empresa actualizada correctamente.')
        return super().form_valid(form)


class EmpresaToggleView(BecaAzulRequiredMixin, View):
    def post(self, request, pk):
        empresa = get_object_or_404(Empresa, pk=pk)
        with transaction.atomic():
            empresa.activo = not empresa.activo
            if empresa.activo:
                usuarios = empresa.usuarios.filter(is_active_before_empresa_deactivation=True)
                usuarios.update(is_active=True, is_active_before_empresa_deactivation=None)
                empresa.usuarios.filter(is_active_before_empresa_deactivation=False).update(
                    is_active_before_empresa_deactivation=None
                )
            else:
                for usuario in empresa.usuarios.all():
                    usuario.is_active_before_empresa_deactivation = usuario.is_active
                    usuario.is_active = False
                    usuario.save(update_fields=['is_active', 'is_active_before_empresa_deactivation'])
            empresa.save(update_fields=['activo'])
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'activo': empresa.activo, 'nombre': empresa.nombre})
        estado = 'activada' if empresa.activo else 'desactivada'
        messages.success(self.request, f'La empresa "{empresa.nombre}" fue {estado}.')
        return redirect('app_control:empresa_detalle', pk=empresa.pk)


class EmpresaSCTRToggleView(EmpresaActivaRequiredMixin, BecaAzulRequiredMixin, View):
    def post(self, request, pk, tipo):
        empresa = get_object_or_404(Empresa, pk=pk)
        estados = {
            'pension': ('sctr_pension_aprobado', Certificado.SCTR_PENSION, 'sctr_pension_validado'),
            'salud': ('sctr_salud_aprobado', Certificado.SCTR_SALUD, 'sctr_salud_validado'),
        }
        try:
            field_name, certificate_type, worker_validation_field = estados[tipo]
        except KeyError:
            raise Http404

        aprobado = not getattr(empresa, field_name)
        if aprobado and not empresa.sctr_empresa_vigente(certificate_type):
            messages.error(request, f'No se puede aprobar el SCTR {tipo} sin un certificado empresarial vigente.')
            return redirect('app_control:empresa_detalle', pk=empresa.pk)

        with transaction.atomic():
            setattr(empresa, field_name, aprobado)
            empresa.save(update_fields=[field_name])
            if not aprobado:
                empresa.trabajadores.filter(**{worker_validation_field: True}).update(
                    **{worker_validation_field: False}
                )
        estado = 'aprobado' if aprobado else 'desaprobado'
        messages.success(request, f'El SCTR {tipo} de "{empresa.nombre}" fue {estado} para sus trabajadores.')
        return redirect('app_control:empresa_detalle', pk=empresa.pk)


class EmpresaHomologacionToggleView(EmpresaActivaRequiredMixin, BecaAzulRequiredMixin, View):
    def post(self, request, pk):
        empresa = get_object_or_404(Empresa, pk=pk)
        empresa.invalidar_homologacion_si_corresponde()
        if not empresa.homologacion:
            certificados = {
                certificado.tipo: certificado
                for certificado in empresa.certificados.filter(
                    tipo__in=(Certificado.SCTR_PENSION, Certificado.SCTR_SALUD, Certificado.HOMOLOGACION)
                )
            }
            sctr_pension = certificados.get(Certificado.SCTR_PENSION)
            sctr_salud = certificados.get(Certificado.SCTR_SALUD)
            homologacion = certificados.get(Certificado.HOMOLOGACION)
            tiene_sctr_pension = bool(sctr_pension and sctr_pension.esta_vigente)
            tiene_sctr_salud = bool(sctr_salud and sctr_salud.esta_vigente)
            tiene_homologacion = bool(homologacion and homologacion.esta_vigente)
            if not tiene_sctr_pension:
                messages.error(request, 'Falta subir el SCTR pensión o no está vigente.')
            elif not empresa.sctr_pension_aprobado:
                messages.error(request, 'El SCTR pensión debe estar aprobado.')
            if not tiene_sctr_salud:
                messages.error(request, 'Falta subir el SCTR salud o no está vigente.')
            elif not empresa.sctr_salud_aprobado:
                messages.error(request, 'El SCTR salud debe estar aprobado.')
            if not tiene_homologacion:
                messages.error(request, 'Falta subir el certificado de homologación.')
            if (
                not tiene_sctr_pension
                or not empresa.sctr_pension_aprobado
                or not tiene_sctr_salud
                or not empresa.sctr_salud_aprobado
                or not tiene_homologacion
            ):
                return redirect('app_control:empresa_detalle', pk=empresa.pk)
        empresa.homologacion = not empresa.homologacion
        empresa.save(update_fields=['homologacion'])
        estado = 'aprobada' if empresa.homologacion else 'desaprobada'
        messages.success(request, f'La homologación de "{empresa.nombre}" fue {estado}.')
        return redirect('app_control:empresa_detalle', pk=empresa.pk)


class EmpresaCertificadoView(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.role not in (User.BECA_AZUL, User.USUARIO_EMPRESA):
            raise PermissionDenied
        if request.user.role == User.USUARIO_EMPRESA and (
            not request.user.empresa or not request.user.empresa.activo
        ):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, pk):
        certificado = get_object_or_404(
            Certificado,
            pk=pk,
            empresa__isnull=False,
            tipo__in=(Certificado.SCTR_PENSION, Certificado.SCTR_SALUD, Certificado.HOMOLOGACION),
        )
        if request.user.role == User.USUARIO_EMPRESA and certificado.empresa_id != request.user.empresa_id:
            raise PermissionDenied
        if not certificado.archivo or not certificado.archivo.storage.exists(certificado.archivo.name):
            raise Http404
        return FileResponse(certificado.archivo.open('rb'), content_type='application/pdf')


class EmpresaCertificadoArchivoView(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.role in (User.BECA_AZUL, User.PLANTA, User.USUARIO_EMPRESA):
            if request.user.role == User.USUARIO_EMPRESA and (
                not request.user.empresa or not request.user.empresa.activo
            ):
                raise PermissionDenied
            return super().dispatch(request, *args, **kwargs)
        raise PermissionDenied

    def get(self, request, empresa_id, path):
        certificado = get_object_or_404(
            Certificado,
            archivo=f'certificados/empresa_{empresa_id}/{path}',
        )
        certificado_empresa_id = certificado.empresa_id or certificado.trabajador.empresa_id
        if certificado_empresa_id != int(empresa_id):
            raise Http404
        if request.user.role == User.PLANTA and certificado.empresa_id:
            raise PermissionDenied
        if request.user.role == User.USUARIO_EMPRESA and request.user.empresa_id != certificado_empresa_id:
            raise PermissionDenied
        if not certificado.archivo or not certificado.archivo.storage.exists(certificado.archivo.name):
            raise Http404
        return FileResponse(certificado.archivo.open('rb'), content_type='application/pdf')


class EmpresaDetailView(LoginRequiredMixin, DetailView):
    model = Empresa
    template_name = 'control/empresas/detalle.html'
    context_object_name = 'empresa'

    def dispatch(self, request, *args, **kwargs):
        if request.user.role not in (User.ADMINISTRADOR, User.BECA_AZUL, User.PLANTA, User.USUARIO_EMPRESA):
            raise PermissionDenied
        if request.user.role == User.USUARIO_EMPRESA and not request.user.empresa:
            raise PermissionDenied
        if request.user.role == User.USUARIO_EMPRESA and not request.user.empresa.activo:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.role == User.USUARIO_EMPRESA:
            return queryset.filter(pk=self.request.user.empresa_id)
        return queryset

    def get_context_data(self, **kwargs):
        self.object.invalidar_homologacion_si_corresponde()
        trabajadores = self.object.trabajadores.order_by('apellidos', 'nombres')
        sctr_pension = self.object.certificados.filter(tipo=Certificado.SCTR_PENSION).first()
        sctr_salud = self.object.certificados.filter(tipo=Certificado.SCTR_SALUD).first()
        homologacion = self.object.certificados.filter(tipo=Certificado.HOMOLOGACION).first()
        def certificado_valido(certificado):
            return bool(certificado and certificado.esta_vigente)

        sctr_pension_valido = certificado_valido(sctr_pension)
        sctr_salud_valido = certificado_valido(sctr_salud)
        sctr_pension_archivo_existe = bool(
            sctr_pension
            and sctr_pension.archivo
            and sctr_pension.archivo.storage.exists(sctr_pension.archivo.name)
        )
        sctr_salud_archivo_existe = bool(
            sctr_salud
            and sctr_salud.archivo
            and sctr_salud.archivo.storage.exists(sctr_salud.archivo.name)
        )
        homologacion_vigente = bool(homologacion and homologacion.esta_vigente)
        homologacion_archivo_existe = bool(
            homologacion
            and homologacion.archivo
            and homologacion.archivo.storage.exists(homologacion.archivo.name)
        )
        homologacion_valida = homologacion_vigente
        kwargs.setdefault('total_trabajadores', trabajadores.count())
        kwargs.setdefault(
            'empresa_trabajadores_chart',
            {
                    'labels': ['Habilitado', 'No habilitado'],
                    'data': [
                    sum(trabajador.habilitado_efectivo for trabajador in trabajadores),
                    sum(not trabajador.habilitado_efectivo for trabajador in trabajadores),
                ],
            },
        )
        kwargs.setdefault('total_usuarios', self.object.usuarios.count())
        kwargs.setdefault('sctr', sctr_pension)
        kwargs.setdefault('sctr_pension', sctr_pension)
        kwargs.setdefault('sctr_salud', sctr_salud)
        kwargs.setdefault('sctr_pension_valido', sctr_pension_valido)
        kwargs.setdefault('sctr_salud_valido', sctr_salud_valido)
        kwargs.setdefault('sctr_pension_archivo_existe', sctr_pension_archivo_existe)
        kwargs.setdefault('sctr_salud_archivo_existe', sctr_salud_archivo_existe)
        kwargs.setdefault('sctr_pension_aprobado', self.object.sctr_pension_aprobado)
        kwargs.setdefault('sctr_salud_aprobado', self.object.sctr_salud_aprobado)
        kwargs.setdefault('sctr_valido', sctr_pension_valido and sctr_salud_valido)
        kwargs.setdefault('homologacion', homologacion)
        kwargs.setdefault('homologacion_valida', homologacion_valida)
        kwargs.setdefault('homologacion_archivo_existe', homologacion_archivo_existe)
        kwargs.setdefault(
            'trabajadores_por_estado',
            [
                {'estado': 'HABILITADO', 'total': sum(trabajador.habilitado_efectivo for trabajador in trabajadores), 'label': 'Habilitado'},
                {'estado': 'NO_HABILITADO', 'total': sum(not trabajador.habilitado_efectivo for trabajador in trabajadores), 'label': 'No habilitado'},
            ],
        )
        return super().get_context_data(**kwargs)


class EmpresaSCTRUpdateView(LoginRequiredMixin, UpdateView):
    certificate_type = Certificado.SCTR_PENSION
    model = Certificado
    form_class = SCTRForm
    template_name = 'control/empresas/sctr_form.html'
    context_object_name = 'sctr'

    def dispatch(self, request, *args, **kwargs):
        if (
            request.user.role != User.USUARIO_EMPRESA
            or not request.user.empresa
            or not request.user.empresa.activo
        ):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Certificado.objects.filter(
            empresa=self.request.user.empresa,
            tipo=self.certificate_type,
        )

    def get_object(self, queryset=None):
        queryset = queryset or self.get_queryset()
        return queryset.filter(empresa_id=self.kwargs['pk']).first()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['empresa'] = self.request.user.empresa
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['empresa'] = self.request.user.empresa
        context['sctr_titulo'] = 'SCTR pensión'
        return context

    def form_valid(self, form):
        if not form.instance.pk:
            form.instance.empresa = self.request.user.empresa
        response = super().form_valid(form)
        messages.success(self.request, 'SCTR actualizado correctamente.')
        return response

    def get_success_url(self):
        return reverse('app_control:empresa_detalle', args=[self.request.user.empresa.pk])


class EmpresaSCTRSaludUpdateView(EmpresaSCTRUpdateView):
    form_class = SCTRSaludForm
    certificate_type = Certificado.SCTR_SALUD

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sctr_titulo'] = 'SCTR salud'
        return context


class EmpresaHomologacionUpdateView(EmpresaSCTRUpdateView):
    form_class = HomologacionForm
    template_name = 'control/empresas/homologacion_form.html'
    context_object_name = 'homologacion'

    def get_queryset(self):
        return Certificado.objects.filter(
            empresa=self.request.user.empresa,
            tipo=Certificado.HOMOLOGACION,
        )

    def form_valid(self, form):
        if not form.instance.pk:
            form.instance.empresa = self.request.user.empresa
        response = super(EmpresaSCTRUpdateView, self).form_valid(form)
        messages.success(self.request, 'Homologación actualizada correctamente.')
        return response


class EmpresaDeleteView(EmpresaActivaRequiredMixin, BecaAzulRequiredMixin, DeleteView):
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


class TrabajadorListBaseView(ListView):
    model = Trabajador
    template_name = 'control/trabajadores/lista_empresa.html'
    context_object_name = 'trabajadores'
    paginate_by = 20
    sortable_columns = {
        'dni': ('dni',),
        'nombre': ('apellidos', 'nombres'),
        'empresa': ('empresa__nombre', 'apellidos', 'nombres'),
        'induccion': ('tiene_induccion', 'apellidos', 'nombres'),
        'aptitud_medica': ('tiene_aptitud_medica', 'apellidos', 'nombres'),
    }

    def get_paginate_by(self, queryset):
        if self.request.user.role == User.GARITA:
            return None
        return self.paginate_by

    def get_queryset(self):
        certificados = Certificado.objects.filter(trabajador=OuterRef('pk'))
        queryset = Trabajador.objects.select_related('empresa').prefetch_related(
            Prefetch(
                'empresa__certificados',
                queryset=Certificado.objects.filter(
                    tipo__in=(Certificado.SCTR_PENSION, Certificado.SCTR_SALUD, Certificado.HOMOLOGACION)
                ),
                to_attr='certificados_habilitacion',
            ),
            Prefetch(
                'certificados',
                queryset=Certificado.objects.filter(
                    tipo__in=(Certificado.INDUCCION, Certificado.APTITUD_MEDICA, Certificado.CURSOS)
                ),
                to_attr='certificados_lista',
            ),
            Prefetch(
                'cursos_obligatorios',
                to_attr='cursos_obligatorios_lista',
            ),
        ).annotate(
            tiene_induccion=Exists(certificados.filter(tipo=Certificado.INDUCCION)),
            tiene_aptitud_medica=Exists(certificados.filter(tipo=Certificado.APTITUD_MEDICA)),
            **{
                f'tiene_curso_{codigo.lower()}': Exists(
                    certificados.filter(tipo=Certificado.CURSOS, curso=codigo)
                )
                for codigo, label in Certificado.CURSO_CHOICES
            },
        ).order_by('-created', '-pk')
        if self.request.user.role == User.USUARIO_EMPRESA:
            queryset = queryset.filter(empresa=self.request.user.empresa)
        q = self.request.GET.get('q', '').strip()
        if q:
            sin_tildes = Func(
                Lower(Concat('nombres', Value(' '), 'apellidos')),
                Value('áéíóúüñ'),
                Value('aeiouun'),
                function='TRANSLATE',
            )
            termino = ''.join(
                char for char in normalize('NFKD', q.casefold())
                if not combining(char)
            )
            queryset = queryset.annotate(nombre_completo_sin_tildes=sin_tildes)
            dni_queryset = queryset.filter(dni__iexact=q)
            tokens = termino.split()
            for token in tokens:
                queryset = queryset.filter(nombre_completo_sin_tildes__icontains=token)
            queryset = queryset | dni_queryset
        habilitacion = self.request.GET.get('habilitacion', '').strip()
        if habilitacion in ('1', '0'):
            esperado = habilitacion == '1'
            ids = [trabajador.pk for trabajador in queryset if trabajador.habilitado_efectivo == esperado]
            queryset = queryset.filter(pk__in=ids)
        estado = self.request.GET.get('estado', '').strip()
        if estado in ('1', '0'):
            queryset = queryset.filter(activo=(estado == '1'))
        empresa_id = self.request.GET.get('empresa', '').strip()
        if self.request.user.role != User.USUARIO_EMPRESA and empresa_id.isdigit():
            queryset = queryset.filter(empresa_id=empresa_id)
        return queryset

    def get_context_data(self, **kwargs):
        query_params = self.request.GET.copy()
        query_params.pop('page', None)
        kwargs.setdefault('q', self.request.GET.get('q', ''))
        kwargs.setdefault('habilitacion', self.request.GET.get('habilitacion', ''))
        kwargs.setdefault('estado', self.request.GET.get('estado', ''))
        kwargs.setdefault('empresa_id', self.request.GET.get('empresa', ''))
        kwargs.setdefault('query_string', query_params.urlencode())
        kwargs.setdefault('empresas', Empresa.objects.order_by('nombre'))
        kwargs.setdefault('habilitacion_choices', (('1', 'Habilitado'), ('0', 'No habilitado')))
        kwargs.setdefault('estado_choices', (('1', 'Activo'), ('0', 'Desactivado')))
        kwargs.setdefault('sortable_columns', {
            'dni': 'DNI',
            'nombre': 'Nombre completo',
             'empresa': 'Empresa',
             'sctr_pension': 'SCTR pensión',
             'sctr_salud': 'SCTR salud',
             'induccion': 'Inducción',
            'aptitud_medica': 'Aptitud médica',
        })
        kwargs['sortable_columns'].update({codigo.lower(): label for codigo, label in Certificado.CURSO_CHOICES})
        kwargs['sortable_columns']['estado'] = 'Estado'
        kwargs['sortable_columns']['habilitacion'] = 'Habilitación'
        kwargs.setdefault('cursos_columnas', Certificado.CURSO_CHOICES)
        kwargs.setdefault('es_empresa', self.request.user.role == User.USUARIO_EMPRESA)
        kwargs.setdefault('es_garita', self.request.user.role == User.GARITA)
        kwargs.setdefault('es_beca_azul', self.request.user.role == User.BECA_AZUL)
        if kwargs['es_empresa']:
            kwargs['sortable_columns'].pop('empresa', None)
        kwargs.setdefault('empresa', getattr(self.request.user, 'empresa', None))
        context = super().get_context_data(**kwargs)
        for trabajador in context['trabajadores']:
            trabajador.limpiar_validaciones_sctr_invalidas()
        return context


class TrabajadorListView(VerTrabajadoresMixin, TrabajadorListBaseView):
    pass


class EmpresaTrabajadoresGaritaView(UsuarioGaritaRequiredMixin, TrabajadorListBaseView):
    def get_queryset(self):
        return super().get_queryset().filter(empresa_id=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        kwargs.setdefault('empresa', get_object_or_404(Empresa, pk=self.kwargs['pk']))
        return super().get_context_data(**kwargs)


class TrabajadorBuscarView(ConsultarTrabajadoresMixin, View):
    template_name = 'control/trabajadores/buscar.html'
    login_url = reverse_lazy('app_users:login')

    def get(self, request):
        q = request.GET.get('q', '').strip()
        trabajador = None
        resultados = 0
        trabajadores = []
        if q:
            sin_tildes = Func(
                Lower(Concat('nombres', Value(' '), 'apellidos')),
                Value('áéíóúüñ'),
                Value('aeiouun'),
                function='TRANSLATE',
            )
            dni_sin_tildes = Func(
                Lower('dni'),
                Value('áéíóúüñ'),
                Value('aeiouun'),
                function='TRANSLATE',
            )
            queryset = Trabajador.objects.select_related('empresa').annotate(
                nombre_completo_sin_tildes=sin_tildes,
                dni_sin_tildes=dni_sin_tildes,
            )
            if request.user.role == User.USUARIO_EMPRESA:
                queryset = queryset.filter(empresa=request.user.empresa)
            tokens = [
                ''.join(
                    char for char in normalize('NFKD', token.casefold())
                    if not combining(char)
                )
                for token in q.split()
            ]
            for token in tokens:
                queryset = queryset.filter(
                    Q(dni_sin_tildes__icontains=token)
                    | Q(nombre_completo_sin_tildes__icontains=token)
                )
            queryset = queryset.order_by('apellidos', 'nombres', 'dni')
            trabajadores = list(queryset)
            resultados = queryset.count()
            if resultados == 1:
                trabajador = trabajadores[0]
        context = {
            'q': q,
            'trabajador': trabajador,
            'trabajadores': trabajadores,
            'resultados': resultados,
            'es_empresa': request.user.role == User.USUARIO_EMPRESA,
            'puede_ver_detalle': request.user.is_superuser or request.user.role in (
                User.ADMINISTRADOR,
                User.BECA_AZUL,
                User.PLANTA,
                User.USUARIO_EMPRESA,
            ),
        }
        return render(request, self.template_name, context)


class TrabajadorUpdateView(EmpresaActivaRequiredMixin, TrabajadorActivoRequiredMixin, AdministrarTrabajadoresMixin, UpdateView):
    model = Trabajador
    form_class = TrabajadorForm
    template_name = 'control/trabajadores/form.html'
    success_url = reverse_lazy('app_control:trabajador_lista')

    def form_valid(self, form):
        self.object = form.save()
        messages.success(
            self.request,
            f'El trabajador "{self.object}" fue actualizado correctamente.',
            extra_tags='worker-updated',
        )
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
        Certificado.objects.filter(
            trabajador=self.object,
            tipo__in=(Certificado.INDUCCION, Certificado.APTITUD_MEDICA, Certificado.CURSOS),
            validado=True,
            fecha_vencimiento__lt=timezone.localdate(),
        ).update(validado=False)
        self.object.limpiar_validaciones_sctr_invalidas()
        certificados_lista = list(self.object.certificados.all().order_by('-fecha_emision'))
        certificados = {certificado.tipo: certificado for certificado in certificados_lista}
        certificados_empresa = {
            certificado.tipo: certificado
            for certificado in self.object.empresa.certificados.filter(
                tipo__in=(Certificado.SCTR_PENSION, Certificado.SCTR_SALUD)
            )
        }
        for certificado in certificados_lista + list(certificados_empresa.values()):
            certificado.archivo_existe = bool(
                certificado.archivo
                and certificado.archivo.storage.exists(certificado.archivo.name)
            )
        cursos = {
            certificado.curso: certificado
            for certificado in certificados_lista
            if certificado.tipo == Certificado.CURSOS
        }
        obligatorios = set(self.object.cursos_obligatorios.values_list('curso', flat=True))
        kwargs.setdefault('certificados', certificados_lista)
        certificados_validables = [
            certificado for certificado in certificados_lista
            if certificado.tipo in (Certificado.INDUCCION, Certificado.APTITUD_MEDICA)
            or (certificado.tipo == Certificado.CURSOS and certificado.curso in obligatorios)
        ]
        kwargs.setdefault('certificados_validables', certificados_validables)
        for certificado in certificados_validables:
            certificado.puede_validarse = bool(
                certificado.esta_vigente and certificado.archivo_existe
            )
            certificado.validacion_bloqueada_por_vencimiento = (
                certificado.fecha_vencimiento < timezone.localdate()
            )
        kwargs.setdefault('certificados_requeridos', [
            {'tipo': Certificado.SCTR_PENSION, 'label': 'SCTR pensión', 'objeto': certificados_empresa.get(Certificado.SCTR_PENSION), 'heredado': True, 'campo_validacion': 'pension', 'validado': self.object.sctr_pension_validado},
            {'tipo': Certificado.SCTR_SALUD, 'label': 'SCTR salud', 'objeto': certificados_empresa.get(Certificado.SCTR_SALUD), 'heredado': True, 'campo_validacion': 'salud', 'validado': self.object.sctr_salud_validado},
            {'tipo': Certificado.INDUCCION, 'label': 'Inducción', 'objeto': certificados.get(Certificado.INDUCCION)},
            {'tipo': Certificado.APTITUD_MEDICA, 'label': 'Aptitud médica', 'objeto': certificados.get(Certificado.APTITUD_MEDICA)},
        ])
        for fila in kwargs['certificados_requeridos'][:2]:
            fila['puede_validarse'] = bool(
                fila['objeto'] and fila['objeto'].esta_vigente
            )
        kwargs.setdefault('sctr_pension_vigente', self.object.sctr_pension_efectivo)
        kwargs.setdefault('sctr_salud_vigente', self.object.sctr_salud_efectivo)
        kwargs.setdefault('sctr_pension_certificado', certificados_empresa.get(Certificado.SCTR_PENSION))
        kwargs.setdefault('sctr_salud_certificado', certificados_empresa.get(Certificado.SCTR_SALUD))
        kwargs.setdefault(
            'sctr_pension_archivo_existe',
            bool(
                certificados_empresa.get(Certificado.SCTR_PENSION)
                and certificados_empresa[Certificado.SCTR_PENSION].archivo
                and certificados_empresa[Certificado.SCTR_PENSION].archivo.storage.exists(
                    certificados_empresa[Certificado.SCTR_PENSION].archivo.name
                )
            ),
        )
        kwargs.setdefault(
            'sctr_salud_archivo_existe',
            bool(
                certificados_empresa.get(Certificado.SCTR_SALUD)
                and certificados_empresa[Certificado.SCTR_SALUD].archivo
                and certificados_empresa[Certificado.SCTR_SALUD].archivo.storage.exists(
                    certificados_empresa[Certificado.SCTR_SALUD].archivo.name
                )
            ),
        )
        kwargs.setdefault('cursos', [
            {'codigo': codigo, 'nombre': label, 'certificado': cursos.get(codigo), 'obligatorio': codigo in obligatorios}
            for codigo, label in Certificado.CURSO_CHOICES
        ])
        kwargs.setdefault('puede_configurar_cursos', self.request.user.is_superuser or self.request.user.role == User.BECA_AZUL)
        kwargs.setdefault('puede_validar_sctr_trabajador', self.request.user.is_superuser or self.request.user.role == User.BECA_AZUL)
        kwargs.setdefault('fecha_hoy', timezone.localdate())
        kwargs.setdefault('incidencias', self.object.incidencias.select_related('registrado_por'))
        kwargs.setdefault('es_empresa', self.request.user.role == User.USUARIO_EMPRESA)
        return super().get_context_data(**kwargs)


class TrabajadorSCTRValidacionToggleView(BecaAzulRequiredMixin, View):
    CAMPOS = {
        'pension': ('sctr_pension_validado', Certificado.SCTR_PENSION, 'sctr_pension_aprobado'),
        'salud': ('sctr_salud_validado', Certificado.SCTR_SALUD, 'sctr_salud_aprobado'),
    }

    def post(self, request, pk, tipo):
        trabajador = get_object_or_404(Trabajador.objects.select_related('empresa'), pk=pk)
        if tipo not in self.CAMPOS:
            raise Http404
        campo, tipo_certificado, campo_aprobacion_empresa = self.CAMPOS[tipo]
        certificado = trabajador.empresa.certificados.filter(tipo=tipo_certificado).first()

        if not trabajador.activo or not trabajador.empresa.activo:
            raise PermissionDenied

        validado_actual = getattr(trabajador, campo)
        validado = request.POST.get('validado') == '1'
        if validado == validado_actual:
            return redirect('app_control:trabajador_detalle', pk=trabajador.pk)

        certificado_vigente = bool(certificado and certificado.esta_vigente)
        aprobado_empresa = getattr(trabajador.empresa, campo_aprobacion_empresa)
        if validado and not aprobado_empresa:
            nombre = 'SCTR pensión' if tipo == 'pension' else 'SCTR salud'
            messages.error(
                request,
                f'Primero se requiere que el {nombre} en el panel de la empresa esté aprobado.',
            )
            return redirect('app_control:trabajador_detalle', pk=trabajador.pk)
        if validado and not certificado_vigente:
            messages.error(request, 'No se puede validar el SCTR porque el certificado no está vigente o falta el archivo.')
            return redirect('app_control:trabajador_detalle', pk=trabajador.pk)

        setattr(trabajador, campo, validado)
        trabajador.save(update_fields=[campo])
        nombre = 'SCTR pensión' if tipo == 'pension' else 'SCTR salud'
        estado = 'aprobado' if validado else 'desaprobado'
        messages.success(request, f'{nombre} del trabajador: {estado}.')
        return redirect('app_control:trabajador_detalle', pk=trabajador.pk)


class CertificadoValidacionToggleView(BecaAzulRequiredMixin, View):
    def post(self, request, pk):
        certificado = get_object_or_404(
            Certificado,
            pk=pk,
            trabajador__isnull=False,
            tipo__in=(Certificado.INDUCCION, Certificado.APTITUD_MEDICA, Certificado.CURSOS),
        )
        if not certificado.trabajador.empresa.activo:
            raise PermissionDenied
        if not certificado.trabajador.activo:
            messages.error(request, 'No se puede modificar la validación porque el trabajador está desactivado.')
            return redirect('app_control:trabajador_detalle', pk=certificado.trabajador_id)
        if certificado.tipo == Certificado.CURSOS and not certificado.trabajador.cursos_obligatorios.filter(
            curso=certificado.curso
        ).exists():
            messages.error(request, 'Solo se pueden validar cursos habilitados previamente.')
            return redirect('app_control:trabajador_detalle', pk=certificado.trabajador_id)
        if not certificado.archivo or not certificado.archivo.storage.exists(certificado.archivo.name):
            certificado.validado = False
            certificado.save(update_fields=['validado'])
            messages.error(request, 'No se puede validar el certificado porque falta el archivo PDF.')
            return redirect('app_control:trabajador_detalle', pk=certificado.trabajador_id)
        if not certificado.esta_vigente:
            certificado.validado = False
            certificado.save(update_fields=['validado'])
            messages.error(request, 'No se puede validar un certificado que todavía no está vigente o ya venció.')
        else:
            certificado.validado = not certificado.validado
            certificado.save(update_fields=['validado'])
            estado = 'aprobado' if certificado.validado else 'desaprobado'
            requisito = (
                certificado.get_curso_display()
                if certificado.tipo == Certificado.CURSOS
                else certificado.get_tipo_display()
            )
            messages.success(request, f'{requisito}: {estado}.')
        return redirect('app_control:trabajador_detalle', pk=certificado.trabajador_id)


class TrabajadorHabilitadoToggleView(BecaAzulRequiredMixin, View):
    def post(self, request, pk):
        trabajador = get_object_or_404(Trabajador, pk=pk)
        if not trabajador.empresa.activo:
            raise PermissionDenied
        if not trabajador.activo:
            messages.error(
                request,
                f'No se puede modificar la habilitación porque el trabajador "{trabajador}" está desactivado.',
            )
            return redirect('app_control:trabajador_detalle', pk=trabajador.pk)
        if not trabajador.habilitado:
            trabajador.limpiar_validaciones_sctr_invalidas()
            mensajes = []
            empresa = trabajador.empresa
            if not empresa.activo:
                mensajes.append('la empresa está inactiva')
            if not empresa.sctr_pension_aprobado or not empresa.sctr_pension_vigente:
                mensajes.append('SCTR pensión aprobado y vigente')
            if not empresa.sctr_salud_aprobado or not empresa.sctr_salud_vigente:
                mensajes.append('SCTR salud aprobado y vigente')
            if not trabajador.sctr_pension_validado:
                mensajes.append('validación individual del SCTR pensión')
            if not trabajador.sctr_salud_validado:
                mensajes.append('validación individual del SCTR salud')
            if not empresa.homologacion or not empresa.homologacion_vigente:
                mensajes.append('homologación aprobada y vigente')
            certificados_trabajador = {
                certificado.tipo: certificado
                for certificado in trabajador.certificados.all()
            }
            for tipo, etiqueta in (
                (Certificado.INDUCCION, 'Inducción validada y vigente'),
                (Certificado.APTITUD_MEDICA, 'Aptitud médica validada y vigente'),
            ):
                certificado = certificados_trabajador.get(tipo)
                if not certificado or not certificado.validacion_vigente:
                    mensajes.append(etiqueta)
            cursos = {
                certificado.curso: certificado
                for certificado in trabajador.certificados.all()
                if certificado.tipo == Certificado.CURSOS
            }
            for curso in trabajador.cursos_obligatorios.values_list('curso', flat=True):
                if not cursos.get(curso) or not cursos[curso].validacion_vigente:
                    mensajes.append(f'curso {dict(Certificado.CURSO_CHOICES).get(curso, curso)} validado y vigente')
            if mensajes:
                messages.error(request, f'No se puede habilitar: falta cumplir con {", ".join(mensajes)}.')
                return redirect('app_control:trabajador_detalle', pk=trabajador.pk)
        trabajador.habilitado = not trabajador.habilitado
        trabajador.save(update_fields=['habilitado'])
        estado = 'habilitado' if trabajador.habilitado else 'no habilitado'
        messages.success(request, f'El trabajador "{trabajador}" ahora está {estado}.')
        return redirect('app_control:trabajador_detalle', pk=trabajador.pk)


class TrabajadorCursoObligatorioToggleView(BecaAzulRequiredMixin, View):
    def post(self, request, pk, curso):
        trabajador = get_object_or_404(Trabajador, pk=pk)
        if not trabajador.empresa.activo:
            raise PermissionDenied
        if not trabajador.activo:
            messages.error(request, 'No se puede modificar la obligatoriedad de cursos porque el trabajador está desactivado.')
            return redirect('app_control:trabajador_detalle', pk=trabajador.pk)
        if curso not in dict(Certificado.CURSO_CHOICES):
            raise PermissionDenied
        requisito, creado = CursoObligatorio.objects.get_or_create(trabajador=trabajador, curso=curso)
        if not creado:
            requisito.delete()
        return redirect('app_control:trabajador_detalle', pk=trabajador.pk)


class TrabajadorToggleView(AdministrarTrabajadoresMixin, View):
    def post(self, request, pk):
        trabajador = get_object_or_404(Trabajador, pk=pk)
        if not trabajador.empresa.activo:
            raise PermissionDenied
        trabajador.activo = not trabajador.activo
        if not trabajador.activo:
            trabajador.habilitado = False
            trabajador.save(update_fields=['activo', 'habilitado'])
        else:
            trabajador.save(update_fields=['activo'])
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'activo': trabajador.activo, 'nombre': str(trabajador)})
        estado = 'activado' if trabajador.activo else 'desactivado'
        messages.success(request, f'El trabajador "{trabajador}" fue {estado}.', extra_tags='worker-toggled')
        return redirect('app_control:trabajador_detalle', pk=trabajador.pk)


class TrabajadorDeleteView(TrabajadorActivoRequiredMixin, AdministrarTrabajadoresMixin, DeleteView):
    model = Trabajador
    template_name = 'control/trabajadores/confirm_delete.html'
    context_object_name = 'trabajador'
    success_url = reverse_lazy('app_control:trabajador_lista')

    def form_valid(self, form):
        nombre = str(self.object)
        self.object.delete()
        messages.success(
            self.request,
            f'El trabajador "{nombre}" fue eliminado.',
            extra_tags='worker-deleted',
        )
        return HttpResponseRedirect(self.get_success_url())


class CertificadoCreateView(TrabajadorActivoRequiredMixin, AdministrarTrabajadoresMixin, CreateView):
    model = Certificado
    form_class = CertificadoForm
    template_name = 'control/certificados/form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['trabajador'] = get_object_or_404(
            Trabajador,
            pk=self.kwargs['trabajador_pk'],
        )
        return kwargs

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


class CertificadoUpdateView(TrabajadorActivoRequiredMixin, AdministrarTrabajadoresMixin, UpdateView):
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


class CertificadoDeleteView(TrabajadorActivoRequiredMixin, AdministrarTrabajadoresMixin, DeleteView):
    model = Certificado
    template_name = 'control/certificados/confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        trabajador_pk = self.object.trabajador.pk
        self.object.delete()
        messages.success(self.request, 'Certificado eliminado correctamente.')
        return HttpResponseRedirect(reverse('app_control:trabajador_detalle', args=[trabajador_pk]))


class IncidenciaCreateView(TrabajadorActivoRequiredMixin, GestionarIncidenciasMixin, CreateView):
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


class IncidenciaUpdateView(TrabajadorActivoRequiredMixin, GestionarIncidenciasMixin, UpdateView):
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


class IncidenciaDeleteView(TrabajadorActivoRequiredMixin, GestionarIncidenciasMixin, DeleteView):
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


class TrabajadorEmpresaBaseMixin(TrabajadorEmpresaPermisoMixin):
    def get_queryset(self):
        return Trabajador.objects.filter(empresa=self.request.user.empresa)


class TrabajadorEmpresaDetailView(TrabajadorEmpresaBaseMixin, DetailView):
    model = Trabajador
    template_name = 'control/trabajadores/detalle.html'
    context_object_name = 'trabajador'

    def get_context_data(self, **kwargs):
        certificados_lista = list(self.object.certificados.all().order_by('-fecha_emision'))
        certificados = {certificado.tipo: certificado for certificado in certificados_lista}
        certificados_empresa = {
            certificado.tipo: certificado
            for certificado in self.object.empresa.certificados.filter(
                tipo__in=(Certificado.SCTR_PENSION, Certificado.SCTR_SALUD)
            )
        }
        cursos = {
            certificado.curso: certificado
            for certificado in certificados_lista
            if certificado.tipo == Certificado.CURSOS
        }
        obligatorios = set(self.object.cursos_obligatorios.values_list('curso', flat=True))
        kwargs.setdefault('certificados', certificados_lista)
        kwargs.setdefault('certificados_requeridos', [
            {'tipo': Certificado.SCTR_PENSION, 'label': 'SCTR pensión', 'objeto': certificados_empresa.get(Certificado.SCTR_PENSION), 'heredado': True},
            {'tipo': Certificado.SCTR_SALUD, 'label': 'SCTR salud', 'objeto': certificados_empresa.get(Certificado.SCTR_SALUD), 'heredado': True},
            {'tipo': Certificado.INDUCCION, 'label': 'Inducción', 'objeto': certificados.get(Certificado.INDUCCION)},
            {'tipo': Certificado.APTITUD_MEDICA, 'label': 'Aptitud médica', 'objeto': certificados.get(Certificado.APTITUD_MEDICA)},
        ])
        kwargs.setdefault('sctr_pension_vigente', self.object.sctr_pension_efectivo)
        kwargs.setdefault('sctr_salud_vigente', self.object.sctr_salud_efectivo)
        kwargs.setdefault('cursos', [
            {'codigo': codigo, 'nombre': label, 'certificado': cursos.get(codigo), 'obligatorio': codigo in obligatorios}
            for codigo, label in Certificado.CURSO_CHOICES
        ])
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

    def form_valid(self, form):
        form.instance.empresa = self.request.user.empresa
        self.object = form.save()
        try:
            enviados = send_mail(
                subject='Nuevo trabajador registrado',
                message=(
                    'Se ha creado un nuevo trabajador.\n\n'
                    f'Nombre: {self.object.nombres}\n'
                    f'Apellido: {self.object.apellidos}\n'
                    f'Empresa: {self.object.empresa.nombre}'
                ),
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[settings.EMAIL_HOST_USER],
                fail_silently=False,
                html_message=(
                    '<p>Se ha creado un nuevo trabajador:</p>'
                    '<table style="border-collapse: collapse; width: 100%; max-width: 600px;">'
                    '<tbody>'
                    f'<tr><th style="border: 1px solid #d1d5db; padding: 8px; text-align: left;">Nombre</th><td style="border: 1px solid #d1d5db; padding: 8px;">{escape(self.object.nombres)}</td></tr>'
                    f'<tr><th style="border: 1px solid #d1d5db; padding: 8px; text-align: left;">Apellido</th><td style="border: 1px solid #d1d5db; padding: 8px;">{escape(self.object.apellidos)}</td></tr>'
                    f'<tr><th style="border: 1px solid #d1d5db; padding: 8px; text-align: left;">Empresa</th><td style="border: 1px solid #d1d5db; padding: 8px;">{escape(self.object.empresa.nombre)}</td></tr>'
                    '</tbody></table>'
                ),
            )
            if not enviados:
                raise RuntimeError('El correo no fue aceptado para envío.')
        except Exception:
            messages.warning(
                self.request,
                'El trabajador fue registrado, pero no se pudo enviar la notificación por correo.',
            )
        messages.success(
            self.request,
            f'El trabajador "{self.object}" fue registrado correctamente.',
            extra_tags='worker-created',
        )
        return HttpResponseRedirect(self.get_success_url())


class TrabajadorEmpresaUpdateView(TrabajadorActivoRequiredMixin, TrabajadorEmpresaBaseMixin, UpdateView):
    model = Trabajador
    form_class = TrabajadorEmpresaForm
    template_name = 'control/trabajadores/form.html'
    success_url = reverse_lazy('app_control:trabajador_lista')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['empresa'] = self.request.user.empresa
        return kwargs

    def form_valid(self, form):
        self.object = form.save()
        messages.success(
            self.request,
            f'El trabajador "{self.object}" fue actualizado correctamente.',
            extra_tags='worker-updated',
        )
        return HttpResponseRedirect(self.get_success_url())


class TrabajadorEmpresaToggleView(EmpresaActivaRequiredMixin, BecaAzulRequiredMixin, View):
    def post(self, request, pk):
        trabajador = get_object_or_404(Trabajador, pk=pk)
        trabajador.activo = not trabajador.activo
        if not trabajador.activo:
            trabajador.habilitado = False
            trabajador.save(update_fields=['activo', 'habilitado'])
        else:
            trabajador.save(update_fields=['activo'])
        estado = 'activado' if trabajador.activo else 'desactivado'
        messages.success(request, f'El trabajador "{trabajador}" fue {estado}.', extra_tags='worker-toggled')
        return redirect('app_control:trabajador_detalle', pk=trabajador.pk)


class TrabajadorEmpresaDeleteView(EmpresaActivaRequiredMixin, BecaAzulRequiredMixin, DeleteView):
    model = Trabajador
    template_name = 'control/trabajadores/confirm_delete.html'
    context_object_name = 'trabajador'
    success_url = reverse_lazy('app_control:trabajador_lista')

    def form_valid(self, form):
        nombre = str(self.object)
        self.object.delete()
        messages.success(
            self.request,
            f'El trabajador "{nombre}" fue eliminado.',
            extra_tags='worker-deleted',
        )
        return HttpResponseRedirect(self.get_success_url())


class CertificadoEmpresaCreateView(TrabajadorActivoRequiredMixin, TrabajadorEmpresaBaseMixin, CreateView):
    model = Certificado
    form_class = CertificadoForm
    template_name = 'control/certificados/form.html'

    def dispatch(self, request, *args, **kwargs):
        if request.method == 'GET':
            trabajador = self.get_trabajador()
            curso = request.GET.get('curso')
            if request.GET.get('tipo') != Certificado.CURSOS or not curso or not CursoObligatorio.objects.filter(
                trabajador=trabajador,
                curso=curso,
            ).exists():
                raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['trabajador'] = self.get_trabajador()
        return kwargs

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Model validation needs the worker assigned before form.is_valid().
        form.instance.trabajador = self.get_trabajador()
        form.instance.tipo = Certificado.CURSOS
        form.fields['tipo'].disabled = True
        form.fields['curso'].disabled = True
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
        if not CursoObligatorio.objects.filter(
            trabajador=self.trabajador,
            curso=form.cleaned_data.get('curso'),
        ).exists():
            raise PermissionDenied
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
        return reverse('app_control:trabajador_detalle', args=[self.trabajador.pk])


class CertificadoEmpresaUpdateView(TrabajadorActivoRequiredMixin, TrabajadorEmpresaBaseMixin, UpdateView):
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
        queryset = Certificado.objects.filter(
            trabajador__empresa=self.request.user.empresa
        )
        obligatorios = CursoObligatorio.objects.filter(
            trabajador_id=OuterRef('trabajador_id'),
            curso=OuterRef('curso'),
        )
        return queryset.annotate(curso_obligatorio=Exists(obligatorios)).filter(
            Q(tipo=Certificado.CURSOS, curso_obligatorio=True) | ~Q(tipo=Certificado.CURSOS)
        )

    def get_context_data(self, **kwargs):
        kwargs.setdefault('trabajador', self.object.trabajador)
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        certificado_original = Certificado.objects.only(
            'fecha_emision', 'fecha_vencimiento'
        ).get(pk=self.object.pk)
        certificado_modificado = bool(
            form.files.get('archivo')
            or form.cleaned_data.get('fecha_emision') != certificado_original.fecha_emision
            or form.cleaned_data.get('fecha_vencimiento') != certificado_original.fecha_vencimiento
        )
        if certificado_modificado:
            form.instance.validado = False
        self.object = form.save()
        messages.success(self.request, 'Certificado actualizado correctamente.')
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('app_control:trabajador_detalle', args=[self.object.trabajador.pk])


class CertificadoEmpresaDeleteView(TrabajadorActivoRequiredMixin, TrabajadorEmpresaBaseMixin, DeleteView):
    model = Certificado
    template_name = 'control/certificados/confirm_delete.html'

    def get_queryset(self):
        queryset = Certificado.objects.filter(
            trabajador__empresa=self.request.user.empresa
        )
        obligatorios = CursoObligatorio.objects.filter(
            trabajador_id=OuterRef('trabajador_id'),
            curso=OuterRef('curso'),
        )
        return queryset.annotate(curso_obligatorio=Exists(obligatorios)).filter(
            Q(tipo=Certificado.CURSOS, curso_obligatorio=True) | ~Q(tipo=Certificado.CURSOS)
        )

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        trabajador_pk = self.object.trabajador.pk
        self.object.delete()
        messages.success(self.request, 'Certificado eliminado correctamente.')
        return HttpResponseRedirect(reverse('app_control:trabajador_detalle', args=[trabajador_pk]))
