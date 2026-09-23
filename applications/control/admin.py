from django.contrib import admin

from .models import CategoriaCurso, Certificado, Empresa, Incidencia, Trabajador


@admin.register(CategoriaCurso)
class CategoriaCursoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre',)


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'ruc', 'homologado', 'activo')
    search_fields = ('nombre', 'ruc')
    list_filter = ('homologado', 'activo')
    readonly_fields = ('homologado',)
    list_per_page = 20


@admin.register(Trabajador)
class TrabajadorAdmin(admin.ModelAdmin):
    list_display = ('dni', 'nombres', 'apellidos', 'empresa', 'habilitado', 'activo')
    search_fields = ('dni', 'nombres', 'apellidos', 'cargo')
    list_filter = ('habilitado', 'activo', 'empresa')
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
    list_display = ('tipo', 'empresa', 'trabajador', 'fecha_emision', 'fecha_vencimiento')
    search_fields = ('empresa__nombre', 'trabajador__dni', 'trabajador__nombres', 'categoria__nombre')
    list_filter = ('tipo', 'categoria')
    list_per_page = 20
    list_select_related = ('empresa', 'trabajador', 'trabajador__empresa')
