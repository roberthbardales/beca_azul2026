from django.urls import path

from . import views

app_name = 'app_control'

urlpatterns = [
    # Dashboard y reportes
    path('panel/', views.DashboardView.as_view(), name='dashboard'),
    path('reportes/', views.ReportesView.as_view(), name='reportes'),

    # Empresas
    path('empresas/', views.EmpresaListView.as_view(), name='empresa_lista'),
    path('empresas/crear/', views.EmpresaCreateView.as_view(), name='empresa_crear'),
    path('empresas/<int:pk>/sctr/editar/', views.EmpresaSCTRUpdateView.as_view(), name='empresa_sctr_editar'),
    path('empresas/<int:pk>/sctr-salud/editar/', views.EmpresaSCTRSaludUpdateView.as_view(), name='empresa_sctr_salud_editar'),
    path('empresas/<int:pk>/homologacion/editar/', views.EmpresaHomologacionUpdateView.as_view(), name='empresa_homologacion_editar'),
    path('empresas/<int:pk>/', views.EmpresaDetailView.as_view(), name='empresa_detalle'),
    path('empresas/<int:pk>/trabajadores/', views.EmpresaTrabajadoresGaritaView.as_view(), name='empresa_trabajadores_garita'),
    path('empresas/<int:pk>/editar/', views.EmpresaUpdateView.as_view(), name='empresa_editar'),
    path('empresas/<int:pk>/toggle/', views.EmpresaToggleView.as_view(), name='empresa_toggle'),
    path('empresas/<int:pk>/sctr/<str:tipo>/toggle/', views.EmpresaSCTRToggleView.as_view(), name='empresa_sctr_toggle'),
    path('empresas/<int:pk>/homologacion/toggle/', views.EmpresaHomologacionToggleView.as_view(), name='empresa_homologacion_toggle'),
    path('empresas/certificados/<int:pk>/ver/', views.EmpresaCertificadoView.as_view(), name='empresa_certificado_ver'),
    path('empresas/<int:pk>/eliminar/', views.EmpresaDeleteView.as_view(), name='empresa_eliminar'),

    # Trabajadores
    path('trabajadores/', views.TrabajadorListView.as_view(), name='trabajador_lista'),
    path('trabajadores/buscar/', views.TrabajadorBuscarView.as_view(), name='trabajador_buscar'),
    path('trabajadores/empresa/crear/', views.TrabajadorEmpresaCreateView.as_view(), name='trabajador_empresa_crear'),
    path('trabajadores/empresa/<int:pk>/', views.TrabajadorEmpresaDetailView.as_view(), name='trabajador_empresa_detalle'),
    path('trabajadores/empresa/<int:pk>/editar/', views.TrabajadorEmpresaUpdateView.as_view(), name='trabajador_empresa_editar'),
    path('trabajadores/empresa/<int:pk>/toggle/', views.TrabajadorEmpresaToggleView.as_view(), name='trabajador_empresa_toggle'),
    path('trabajadores/empresa/<int:pk>/eliminar/', views.TrabajadorEmpresaDeleteView.as_view(), name='trabajador_empresa_eliminar'),
    path('trabajadores/<int:pk>/', views.TrabajadorDetailView.as_view(), name='trabajador_detalle'),
    path('trabajadores/<int:pk>/editar/', views.TrabajadorUpdateView.as_view(), name='trabajador_editar'),
    path('trabajadores/<int:pk>/habilitado/toggle/', views.TrabajadorHabilitadoToggleView.as_view(), name='trabajador_habilitado_toggle'),
    path('trabajadores/<int:pk>/cursos/<str:curso>/obligatorio/', views.TrabajadorCursoObligatorioToggleView.as_view(), name='trabajador_curso_obligatorio_toggle'),
    path('trabajadores/<int:pk>/sctr/', views.TrabajadorSCTRView.as_view(), name='trabajador_sctr'),
    path('trabajadores/<int:pk>/toggle/', views.TrabajadorToggleView.as_view(), name='trabajador_toggle'),
    path('trabajadores/<int:pk>/eliminar/', views.TrabajadorDeleteView.as_view(), name='trabajador_eliminar'),

    # Certificados
    path('certificados/empresa/crear/<int:trabajador_pk>/', views.CertificadoEmpresaCreateView.as_view(), name='certificado_empresa_crear'),
    path('certificados/empresa/<int:pk>/editar/', views.CertificadoEmpresaUpdateView.as_view(), name='certificado_empresa_editar'),
    path('certificados/empresa/<int:pk>/eliminar/', views.CertificadoEmpresaDeleteView.as_view(), name='certificado_empresa_eliminar'),
    path('certificados/crear/<int:trabajador_pk>/', views.CertificadoCreateView.as_view(), name='certificado_crear'),
    path('certificados/<int:pk>/editar/', views.CertificadoUpdateView.as_view(), name='certificado_editar'),
    path('certificados/<int:pk>/eliminar/', views.CertificadoDeleteView.as_view(), name='certificado_eliminar'),

    # Incidencias
    path('trabajadores/<int:trabajador_pk>/incidencias/crear/', views.IncidenciaCreateView.as_view(), name='incidencia_crear'),
    path('incidencias/<int:pk>/editar/', views.IncidenciaUpdateView.as_view(), name='incidencia_editar'),
    path('incidencias/<int:pk>/eliminar/', views.IncidenciaDeleteView.as_view(), name='incidencia_eliminar'),
]
