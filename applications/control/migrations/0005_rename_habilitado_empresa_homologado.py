from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('control', '0004_remove_certificado_certificado_unico_tipo_trabajador_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='empresa',
            old_name='habilitado',
            new_name='homologado',
        ),
    ]
