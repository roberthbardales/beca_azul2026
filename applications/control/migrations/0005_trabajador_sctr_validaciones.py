from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('control', '0004_alter_empresa_ruc'),
    ]

    operations = [
        migrations.AddField(
            model_name='trabajador',
            name='sctr_pension_validado',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='trabajador',
            name='sctr_salud_validado',
            field=models.BooleanField(default=False),
        ),
    ]
