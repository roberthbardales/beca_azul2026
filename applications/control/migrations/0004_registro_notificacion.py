from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('control', '0003_empresa_homologacion_certificado_aprobado'),
    ]

    operations = [
        migrations.CreateModel(
            name='RegistroNotificacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('evento', models.CharField(db_index=True, max_length=80)),
                ('asunto', models.CharField(max_length=255)),
                ('destinatarios', models.JSONField(default=list)),
                ('estado', models.CharField(choices=[('ENVIANDO', 'Enviando'), ('ENVIADO', 'Enviado'), ('FALLIDO', 'Fallido')], db_index=True, default='ENVIANDO', max_length=10)),
                ('error', models.TextField(blank=True)),
                ('creado', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('actualizado', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Registro de notificación',
                'verbose_name_plural': 'Registros de notificaciones',
                'ordering': ('-creado',),
            },
        ),
    ]
