from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='user',
            constraint=models.CheckConstraint(
                check=~models.Q(role='3', empresa__isnull=True),
                name='usuario_empresa_requiere_empresa',
            ),
        ),
    ]
