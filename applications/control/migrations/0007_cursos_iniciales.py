from django.db import migrations


def crear_cursos(apps, schema_editor):
    Curso = apps.get_model('control', 'Curso')
    nombres = ('Caliente', 'Altura', 'Espacio confinado', 'Eléctrico', 'Excavación', 'Izaje')
    Curso.objects.exclude(nombre__in=nombres).update(activo=False)
    for nombre in nombres:
        Curso.objects.update_or_create(nombre=nombre, defaults={'activo': True})


def eliminar_cursos(apps, schema_editor):
    Curso = apps.get_model('control', 'Curso')
    Curso.objects.filter(nombre__in=('Caliente', 'Altura', 'Espacio confinado', 'Eléctrico', 'Excavación', 'Izaje')).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('control', '0006_rename_categoriacurso_curso_alter_curso_options_and_more'),
    ]

    operations = [
        migrations.RunPython(crear_cursos, eliminar_cursos),
    ]
