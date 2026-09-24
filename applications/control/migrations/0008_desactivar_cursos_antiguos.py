from django.db import migrations


def desactivar_cursos_antiguos(apps, schema_editor):
    Curso = apps.get_model('control', 'Curso')
    nombres = ('Caliente', 'Altura', 'Espacio confinado', 'Eléctrico', 'Excavación', 'Izaje')
    Curso.objects.exclude(nombre__in=nombres).update(activo=False)


class Migration(migrations.Migration):
    dependencies = [
        ('control', '0007_cursos_iniciales'),
    ]

    operations = [
        migrations.RunPython(desactivar_cursos_antiguos, migrations.RunPython.noop),
    ]
