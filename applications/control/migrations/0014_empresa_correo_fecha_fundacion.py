from django.db import migrations, models
from django.utils.text import slugify


def generar_correos(apps, schema_editor):
    Empresa = apps.get_model('control', 'Empresa')
    usados = set()
    for empresa in Empresa.objects.order_by('pk'):
        base = slugify(empresa.nombre).replace('-', '') or f'empresa{empresa.pk}'
        correo = f'{base}@gmail.com'
        sufijo = 2
        while correo in usados:
            correo = f'{base}{sufijo}@gmail.com'
            sufijo += 1
        empresa.correo = correo
        empresa.save(update_fields=('correo',))
        usados.add(correo)


class Migration(migrations.Migration):
    dependencies = [('control', '0013_remove_certificado_certificado_unico_sctr_empresa_and_more')]

    operations = [
        migrations.AddField(
            model_name='empresa', name='correo',
            field=models.EmailField(max_length=254, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='empresa', name='fecha_fundacion',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.RunPython(generar_correos, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='empresa', name='correo',
            field=models.EmailField(max_length=254, unique=True),
        ),
    ]
