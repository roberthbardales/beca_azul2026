from django.db import migrations, models
import django.db.models.deletion
from django.db.models import Q
from django.db.models import F
import model_utils.fields
import django.utils.timezone
import applications.control.models


class Migration(migrations.Migration):
    dependencies = [('control', '0002_initial')]

    operations = [
        migrations.RemoveField(model_name='trabajador', name='sctr'),
        migrations.RemoveField(model_name='trabajador', name='induccion'),
        migrations.RemoveField(model_name='trabajador', name='cursos'),
        migrations.RemoveField(model_name='trabajador', name='aptitud_medica'),
        migrations.CreateModel(
            name='CategoriaCurso',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('nombre', models.CharField(max_length=150, unique=True)),
                ('activo', models.BooleanField(default=True)),
            ],
            options={'ordering': ('nombre',), 'verbose_name': 'Categoría de curso', 'verbose_name_plural': 'Categorías de cursos'},
        ),
        migrations.RemoveField(model_name='certificado', name='nombre'),
        migrations.RemoveField(model_name='certificado', name='descripcion'),
        migrations.RemoveField(model_name='certificado', name='aprobado'),
        migrations.RemoveField(model_name='certificado', name='aprobado_por'),
        migrations.RemoveField(model_name='certificado', name='fecha_aprobacion'),
        migrations.AddField(
            model_name='certificado', name='tipo',
            field=models.CharField(choices=[('SCTR', 'SCTR'), ('INDUCCION', 'Inducción'), ('CURSOS', 'Cursos'), ('APTITUD_MEDICA', 'Aptitud médica')], max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='certificado', name='categoria',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='certificados', to='control.categoriacurso'),
        ),
        migrations.AlterField(model_name='certificado', name='fecha_vencimiento', field=models.DateField()),
        migrations.AlterField(model_name='certificado', name='archivo', field=models.FileField(upload_to=applications.control.models.certificado_upload_path)),
        migrations.AlterField(model_name='certificado', name='tipo', field=models.CharField(choices=[('SCTR', 'SCTR'), ('INDUCCION', 'Inducción'), ('CURSOS', 'Cursos'), ('APTITUD_MEDICA', 'Aptitud médica')], max_length=20)),
        migrations.AddConstraint(model_name='certificado', constraint=models.UniqueConstraint(condition=Q(('categoria__isnull', True)), fields=('trabajador', 'tipo'), name='certificado_unico_tipo_trabajador')),
        migrations.AddConstraint(model_name='certificado', constraint=models.UniqueConstraint(condition=Q(('tipo', 'CURSOS')), fields=('trabajador', 'categoria'), name='certificado_unico_categoria_curso_trabajador')),
        migrations.RemoveConstraint(model_name='certificado', name='certificado_fecha_vencimiento_no_antes_de_emision'),
        migrations.AddConstraint(model_name='certificado', constraint=models.CheckConstraint(check=Q(('fecha_vencimiento__gte', F('fecha_emision'))), name='certificado_fecha_vencimiento_no_antes_de_emision')),
    ]
