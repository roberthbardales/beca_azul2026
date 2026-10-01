from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('control', '0014_empresa_correo_fecha_fundacion'),
    ]

    operations = [
        migrations.AddField(
            model_name='trabajador',
            name='sctr',
            field=models.BooleanField(default=False),
        ),
    ]
