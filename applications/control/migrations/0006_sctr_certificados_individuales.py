from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):
    dependencies = [('control', '0005_trabajador_sctr_validaciones')]

    operations = [
        migrations.RemoveConstraint(model_name='certificado', name='certificado_unico_empresa_tipo'),
        migrations.RemoveConstraint(model_name='certificado', name='certificado_propietario_segun_tipo'),
        migrations.AddConstraint(
            model_name='certificado',
            constraint=models.UniqueConstraint(fields=('empresa', 'tipo'), condition=Q(empresa__isnull=False, tipo='HOMOLOGACION'), name='certificado_unico_empresa_tipo'),
        ),
        migrations.AddConstraint(
            model_name='certificado',
            constraint=models.UniqueConstraint(fields=('trabajador', 'tipo'), condition=Q(trabajador__isnull=False, tipo__in=('SCTR_PENSION', 'SCTR_SALUD')), name='certificado_unico_trabajador_sctr_tipo'),
        ),
        migrations.AddConstraint(
            model_name='certificado',
            constraint=models.CheckConstraint(
                check=(
                    Q(tipo='HOMOLOGACION', empresa__isnull=False, trabajador__isnull=True, curso__isnull=True)
                    | Q(tipo__in=('SCTR_PENSION', 'SCTR_SALUD'), empresa__isnull=True, trabajador__isnull=False, curso__isnull=True)
                    | Q(tipo__in=('INDUCCION', 'APTITUD_MEDICA'), empresa__isnull=True, trabajador__isnull=False, curso__isnull=True)
                    | Q(tipo='CURSOS', empresa__isnull=True, trabajador__isnull=False, curso__isnull=False)
                ),
                name='certificado_propietario_segun_tipo',
            ),
        ),
    ]
