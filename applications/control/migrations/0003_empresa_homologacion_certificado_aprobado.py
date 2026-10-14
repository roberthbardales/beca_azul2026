from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('control', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='empresa',
            name='homologacion_certificado_aprobado',
            field=models.BooleanField(default=False),
        ),
    ]
