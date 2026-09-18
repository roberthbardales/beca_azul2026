from django.contrib import admin

from .models import Certificado, Empresa, Incidencia, Trabajador


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'ruc', 'habilitado', 'activo')
    search_fields = ('nombre', 'ruc', 'email', 'direccion')
    list_filter = ('habilitado', 'activo')
    readonly_fields = ('habilitado',)
    list_per_page = 20


@admin.register(Trabajador)
class TrabajadorAdmin(admin.ModelAdmin):
    list_display = ('dni', 'nombres', 'apellidos', 'empresa', 'estado', 'activo')
    search_fields = ('dni', 'nombres', 'apellidos', 'cargo', 'area')
    list_filter = ('estado', 'activo', 'empresa')
    list_per_page = 20
    list_select_related = ('empresa',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'empresa':
            kwargs['queryset'] = Empresa.objects.filter(activo=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Incidencia)
class IncidenciaAdmin(admin.ModelAdmin):
    list_display = ('id', 'trabajador', 'descripcion_corta', 'registrado_por', 'created')
    search_fields = ('descripcion', 'trabajador__dni', 'trabajador__nombres', 'trabajador__apellidos')
    list_filter = ('trabajador__empresa',)
    list_select_related = ('trabajador', 'trabajador__empresa', 'registrado_por')
    list_per_page = 20

    @admin.display(description='Descripción')
    def descripcion_corta(self, obj):
        return obj.descripcion[:60] + ('…' if len(obj.descripcion) > 60 else '')


@admin.register(Certificado)
class CertificadoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'trabajador', 'fecha_emision', 'fecha_vencimiento', 'aprobado')
    search_fields = ('nombre', 'trabajador__dni', 'trabajador__nombres')
    list_filter = ('aprobado',)
    list_per_page = 20
    list_select_related = ('trabajador', 'trabajador__empresa')