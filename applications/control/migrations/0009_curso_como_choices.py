from django.db import migrations, models
from django.db.models import Q


def copiar_cursos(apps, schema_editor):
    Certificado = apps.get_model('control', 'Certificado')
    for certificado in Certificado.objects.select_related('curso').all():
        if certificado.curso_id:
            certificado.curso_codigo = certificado.curso.nombre.upper().replace(' ', '_').replace('É', 'E')
            certificado.save(update_fields=('curso_codigo',))


class Migration(migrations.Migration):
    dependencies = [('control', '0008_desactivar_cursos_antiguos')]

    operations = [
        migrations.RemoveConstraint(model_name='certificado', name='certificado_unico_tipo_trabajador'),
        migrations.RemoveConstraint(model_name='certificado', name='certificado_unico_categoria_curso_trabajador'),
        migrations.RemoveConstraint(model_name='certificado', name='certificado_propietario_segun_tipo'),
        migrations.AddField(
            model_name='certificado', name='curso_codigo',
            field=models.CharField(max_length=30, null=True, blank=True),
        ),
        migrations.RunPython(copiar_cursos, migrations.RunPython.noop),
        migrations.RemoveField(model_name='certificado', name='curso'),
        migrations.RenameField(model_name='certificado', old_name='curso_codigo', new_name='curso'),
        migrations.AlterField(
            model_name='certificado', name='curso',
            field=models.CharField(blank=True, choices=[
                ('CALIENTE', 'Caliente'), ('ALTURA', 'Altura'),
                ('ESPACIO_CONFINADO', 'Espacio confinado'), ('ELECTRICO', 'Eléctrico'),
                ('EXCAVACION', 'Excavación'), ('IZAJE', 'Izaje')], max_length=30, null=True),
        ),
        migrations.DeleteModel(name='Curso'),
        migrations.AddConstraint(
            model_name='certificado',
            constraint=models.UniqueConstraint(condition=Q(trabajador__isnull=False, curso__isnull=True), fields=('trabajador', 'tipo'), name='certificado_unico_tipo_trabajador'),
        ),
        migrations.AddConstraint(
            model_name='certificado',
            constraint=models.UniqueConstraint(condition=Q(trabajador__isnull=False, tipo='CURSOS', curso__isnull=False), fields=('trabajador', 'curso'), name='certificado_unico_categoria_curso_trabajador'),
        ),
        migrations.AddConstraint(
            model_name='certificado',
            constraint=models.CheckConstraint(check=(Q(tipo='SCTR', empresa__isnull=False, trabajador__isnull=True, curso__isnull=True) | Q(tipo__in=('INDUCCION', 'APTITUD_MEDICA'), trabajador__isnull=False, empresa__isnull=True, curso__isnull=True) | Q(tipo='CURSOS', trabajador__isnull=False, empresa__isnull=True, curso__isnull=False)), name='certificado_propietario_segun_tipo'),
        ),
    ]
