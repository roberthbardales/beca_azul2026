from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('control', '0008_trabajador_habilitado'),
    ]

    operations = [
        migrations.AddField(
            model_name='trabajador',
            name='sctr',
            field=models.CharField(choices=[('APROBADO', 'Aprobado'), ('DESAPROBADO', 'Desaprobado'), ('RECHAZADO', 'Rechazado')], default='DESAPROBADO', max_length=15),
        ),
        migrations.AddField(
            model_name='trabajador',
            name='induccion',
            field=models.CharField(choices=[('APROBADO', 'Aprobado'), ('DESAPROBADO', 'Desaprobado'), ('RECHAZADO', 'Rechazado')], default='DESAPROBADO', max_length=15),
        ),
        migrations.AddField(
            model_name='trabajador',
            name='cursos',
            field=models.CharField(choices=[('APROBADO', 'Aprobado'), ('DESAPROBADO', 'Desaprobado'), ('RECHAZADO', 'Rechazado')], default='DESAPROBADO', max_length=15),
        ),
        migrations.AddField(
            model_name='trabajador',
            name='aptitud_medica',
            field=models.CharField(choices=[('APROBADO', 'Aprobado'), ('DESAPROBADO', 'Desaprobado'), ('RECHAZADO', 'Rechazado')], default='DESAPROBADO', max_length=15),
        ),
    ]
