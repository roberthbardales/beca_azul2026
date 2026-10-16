from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.template.loader import render_to_string
from django.utils import timezone

from applications.control.models import Certificado, CertificadoTipo
from applications.control.services.notificaciones import enviar_reporte


class Command(BaseCommand):
    help = 'Envía por correo el reporte semanal de certificados vencidos o próximos a vencer.'

    def handle(self, *args, **options):
        destinatarios = settings.REPORTES_EMAILS
        if not destinatarios:
            raise CommandError('No hay destinatarios configurados en REPORTES_EMAILS.')

        hoy = timezone.localdate()
        limite = hoy + timedelta(days=30)
        base = Certificado.objects.filter(
            fecha_emision__isnull=False,
            fecha_vencimiento__isnull=False,
            fecha_emision__lte=hoy,
        ).select_related('empresa', 'trabajador__empresa')

        certificados_trabajadores = base.filter(
            trabajador__isnull=False,
            trabajador__activo=True,
            tipo__in=(CertificadoTipo.INDUCCION, CertificadoTipo.APTITUD_MEDICA, CertificadoTipo.CURSOS),
            fecha_vencimiento__lte=limite,
        ).order_by('fecha_vencimiento', 'trabajador__empresa__nombre', 'trabajador__apellidos', 'trabajador__nombres')

        certificados_empresas = base.filter(
            empresa__isnull=False,
            tipo__in=(CertificadoTipo.SCTR_PENSION, CertificadoTipo.SCTR_SALUD, CertificadoTipo.HOMOLOGACION),
            fecha_vencimiento__lte=limite,
        ).order_by('fecha_vencimiento', 'empresa__nombre')

        html = render_to_string('control/reporte_semanal_certificados_email.html', {
            'fecha_generacion': hoy,
            'certificados_trabajadores': certificados_trabajadores,
            'certificados_empresas': certificados_empresas,
            'total_trabajadores': certificados_trabajadores.count(),
            'total_empresas': certificados_empresas.count(),
        })

        try:
            enviar_reporte('Semanal de certificados', html, destinatarios)
        except Exception as error:
            raise CommandError(f'No se pudo enviar el reporte: {error}') from error

        self.stdout.write(self.style.SUCCESS(
            'Reporte enviado a {} destinatario(s): {} certificados de trabajadores y {} de empresas.'.format(
                len(destinatarios), certificados_trabajadores.count(), certificados_empresas.count(),
            )
        ))
