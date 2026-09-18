from django.urls import path

from . import views

app_name = 'app_control'

urlpatterns = [
    path('panel/', views.DashboardView.as_view(), name='dashboard'),
    path('empresas/', views.EmpresaListView.as_view(), name='empresa_lista'),
    path('empresas/crear/', views.EmpresaCreateView.as_view(), name='empresa_crear'),
    path('empresas/<int:pk>/', views.EmpresaDetailView.as_view(), name='empresa_detalle'),
    path('empresas/<int:pk>/editar/', views.EmpresaUpdateView.as_view(), name='empresa_editar'),
    path('empresas/<int:pk>/toggle/', views.EmpresaToggleView.as_view(), name='empresa_toggle'),
    path('empresas/<int:pk>/eliminar/', views.EmpresaDeleteView.as_view(), name='empresa_eliminar'),
    path('trabajadores/', views.TrabajadorListView.as_view(), name='trabajador_lista'),
    path('trabajadores/buscar/', views.TrabajadorBuscarView.as_view(), name='trabajador_buscar'),
    path('trabajadores/empresa/', views.TrabajadorEmpresaListView.as_view(), name='trabajador_empresa_lista'),
    path('trabajadores/empresa/crear/', views.TrabajadorEmpresaCreateView.as_view(), name='trabajador_empresa_crear'),
    path('trabajadores/empresa/<int:pk>/', views.TrabajadorEmpresaDetailView.as_view(), name='trabajador_empresa_detalle'),
    path('trabajadores/empresa/<int:pk>/editar/', views.TrabajadorEmpresaUpdateView.as_view(), name='trabajador_empresa_editar'),
    path('trabajadores/empresa/<int:pk>/estado/', views.TrabajadorEmpresaEstadoView.as_view(), name='trabajador_empresa_estado'),
    path('trabajadores/empresa/<int:pk>/toggle/', views.TrabajadorEmpresaToggleView.as_view(), name='trabajador_empresa_toggle'),
    path('trabajadores/empresa/<int:pk>/eliminar/', views.TrabajadorEmpresaDeleteView.as_view(), name='trabajador_empresa_eliminar'),
    path('trabajadores/empresa/<int:trabajador_pk>/certificados/crear/', views.CertificadoEmpresaCreateView.as_view(), name='certificado_empresa_crear'),
    path('certificados/empresa/<int:pk>/editar/', views.CertificadoEmpresaUpdateView.as_view(), name='certificado_empresa_editar'),
    path('certificados/empresa/<int:pk>/eliminar/', views.CertificadoEmpresaDeleteView.as_view(), name='certificado_empresa_eliminar'),
    path('trabajadores/crear/', views.TrabajadorCreateView.as_view(), name='trabajador_crear'),
    path('trabajadores/<int:pk>/', views.TrabajadorDetailView.as_view(), name='trabajador_detalle'),
    path('trabajadores/<int:pk>/editar/', views.TrabajadorUpdateView.as_view(), name='trabajador_editar'),
    path('trabajadores/<int:pk>/estado/', views.TrabajadorEstadoView.as_view(), name='trabajador_estado'),
    path('trabajadores/<int:pk>/toggle/', views.TrabajadorToggleView.as_view(), name='trabajador_toggle'),
    path('trabajadores/<int:pk>/eliminar/', views.TrabajadorDeleteView.as_view(), name='trabajador_eliminar'),
    path('trabajadores/<int:trabajador_pk>/certificados/crear/', views.CertificadoCreateView.as_view(), name='certificado_crear'),
    path('certificados/<int:pk>/editar/', views.CertificadoUpdateView.as_view(), name='certificado_editar'),
    path('certificados/<int:pk>/eliminar/', views.CertificadoDeleteView.as_view(), name='certificado_eliminar'),
]

