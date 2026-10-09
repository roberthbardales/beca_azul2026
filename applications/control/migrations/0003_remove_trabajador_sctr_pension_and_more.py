from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('control', '0002_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='trabajador',
            name='sctr_pension',
        ),
        migrations.RemoveField(
            model_name='trabajador',
            name='sctr_salud',
        ),
    ]
