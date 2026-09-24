from datetime import date, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.hashers import make_password
from django.db import transaction

from applications.users.models import User
from applications.control.models import Certificado, Empresa, Trabajador


class Command(BaseCommand):
    help = 'Carga datos demo con cinco trabajadores por empresa.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear', action='store_true',
            help='Elimina empresas, trabajadores y usuarios asociados antes de cargar los datos demo.',
        )

    def handle(self, *args, **options):
        if not options['clear']:
            raise CommandError('Esta operación elimina datos. Ejecuta el comando con --clear para confirmar.')
        empresas_nombres = ('Apple', 'Google', 'Microsoft', 'Amazon', 'Tesla', 'Samsung', 'Toyota', 'Adobe', 'Oracle', 'Netflix')
        nombres = ('Ana', 'Luis', 'Marta', 'Jose', 'Rosa')
        apellidos = ('Perez', 'Garcia', 'Lopez', 'Ramos', 'Torres')
        cursos = ('CALIENTE', 'ALTURA', 'ESPACIO_CONFINADO', 'ELECTRICO', 'EXCAVACION', 'IZAJE')
        password = make_password('admin')
        hoy = date.today()

        with transaction.atomic():
            Certificado.objects.all().delete()
            Trabajador.objects.all().delete()
            User.objects.all().update(password=password)
            User.objects.filter(empresa__isnull=False).delete()
            Empresa.objects.all().delete()

            for empresa_index, empresa_nombre in enumerate(empresas_nombres, start=1):
                empresa = Empresa.objects.create(nombre=empresa_nombre, ruc=f'201000000{empresa_index:02d}')
                User.objects.create(
                    email=f'{empresa_nombre.lower()}@gmail.com', password=password,
                    first_name='Usuario', last_name=empresa_nombre, role=User.USUARIO_EMPRESA,
                    empresa=empresa,
                )
                distribucion = (6, 3, 1, 0, 2)
                for trabajador_index, cantidad_cursos in enumerate(distribucion):
                    trabajador = Trabajador.objects.create(
                        empresa=empresa, tipo_documento=Trabajador.DNI,
                        dni=f'700{empresa_index:02d}{trabajador_index + 1:02d}',
                        nombres=nombres[trabajador_index],
                        apellidos=f'{apellidos[trabajador_index]} {empresa_index:02d}',
                        cargo=('Operario', 'Tecnico', 'Supervisora', 'Analista', 'Supervisor')[trabajador_index],
                        habilitado=trabajador_index != 3, activo=trabajador_index != 4,
                    )
                    Certificado.objects.create(
                        trabajador=trabajador, tipo=Certificado.INDUCCION,
                        fecha_emision=hoy - timedelta(days=30), fecha_vencimiento=hoy + timedelta(days=180),
                        archivo=f'certificados/demo/induccion_{empresa_index}_{trabajador_index}.pdf',
                    )
                    Certificado.objects.create(
                        trabajador=trabajador, tipo=Certificado.APTITUD_MEDICA,
                        fecha_emision=hoy - timedelta(days=30), fecha_vencimiento=hoy + timedelta(days=10 if trabajador_index == 3 else 180),
                        archivo=f'certificados/demo/aptitud_{empresa_index}_{trabajador_index}.pdf',
                    )
                    for curso in cursos[:cantidad_cursos]:
                        vencimiento = hoy - timedelta(days=5) if trabajador_index == 2 else hoy + timedelta(days=15 if trabajador_index == 1 else 180)
                        Certificado.objects.create(
                            trabajador=trabajador, tipo=Certificado.CURSOS, curso=curso,
                            fecha_emision=hoy - timedelta(days=30), fecha_vencimiento=vencimiento,
                            archivo=f'certificados/demo/curso_{empresa_index}_{trabajador_index}_{curso.lower()}.pdf',
                        )
                Certificado.objects.create(
                    empresa=empresa, tipo=Certificado.SCTR,
                    fecha_emision=hoy - timedelta(days=30), fecha_vencimiento=hoy + timedelta(days=180),
                    archivo=f'certificados/demo/sctr_{empresa_index}.pdf',
                )
        self.stdout.write(self.style.SUCCESS('Datos demo cargados correctamente.'))
