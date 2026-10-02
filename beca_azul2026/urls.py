from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path

from applications.control.views import EmpresaCertificadoArchivoView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('applications.home.urls')),
    path('users/', include('applications.users.urls')),
    path('', include('applications.control.urls')),
    re_path(
        r'^media/certificados/empresa_(?P<empresa_id>[0-9]+)/(?P<path>.+)$',
        EmpresaCertificadoArchivoView.as_view(),
        name='empresa_certificado_archivo',
    ),
]

handler403 = 'applications.home.views.permission_denied'

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
