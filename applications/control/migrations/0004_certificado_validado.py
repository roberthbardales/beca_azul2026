from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('control', '0003_empresa_sctr_pension_aprobado_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='certificado',
            name='validado',
            field=models.BooleanField(default=False),
        ),
    ]
