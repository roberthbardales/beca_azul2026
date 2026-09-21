from django.db import migrations, models


def copiar_estado_a_habilitado(apps, schema_editor):
    Trabajador = apps.get_model('control', 'Trabajador')
    Trabajador.objects.filter(estado='HABILITADO').update(habilitado=True)
    Trabajador.objects.filter(estado='DESHABILITADO').update(habilitado=False)


class Migration(migrations.Migration):
    dependencies = [
        ('control', '0007_remove_trabajador_area_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='trabajador',
            name='habilitado',
            field=models.BooleanField(db_index=True, default=True),
        ),
        migrations.RunPython(copiar_estado_a_habilitado, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='trabajador',
            name='estado',
        ),
        migrations.RemoveField(
            model_name='empresa',
            name='direccion',
        ),
        migrations.RemoveField(
            model_name='empresa',
            name='telefono',
        ),
        migrations.RemoveField(
            model_name='empresa',
            name='email',
        ),
    ]
