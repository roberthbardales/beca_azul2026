import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, send_mail
from django.utils.html import escape

from ..models import RegistroNotificacion

logger = logging.getLogger(__name__)


def _enviar_y_registrar(evento, asunto, destinatarios, envio):
    registro = RegistroNotificacion.objects.create(
        evento=evento,
        asunto=asunto,
        destinatarios=list(destinatarios),
    )
    try:
        enviados = envio()
    except Exception as error:
        registro.estado = RegistroNotificacion.Estado.FALLIDO
        registro.error = f'{type(error).__name__}: {error}'[:10000]
        registro.save(update_fields=('estado', 'error', 'actualizado'))
        logger.exception(
            'Falló el envío de notificación id=%s evento=%s', registro.pk, evento,
        )
        raise

    if enviados:
        registro.estado = RegistroNotificacion.Estado.ENVIADO
    else:
        registro.estado = RegistroNotificacion.Estado.FALLIDO
        registro.error = 'El backend de correo no aceptó ningún destinatario.'
        logger.warning(
            'El backend no aceptó el envío de notificación id=%s evento=%s',
            registro.pk, evento,
        )
    registro.save(update_fields=('estado', 'error', 'actualizado'))
    return enviados

def tabla_notificacion_html(titulo, filas):
    filas_html = ''.join(
        '<tr>'
        f'<th style="border: 1px solid #d1d5db; padding: 8px; text-align: left">{escape(etiqueta)}</th>'
        f'<td style="border: 1px solid #d1d5db; padding: 8px">{escape(valor or "-")}</td>'
        '</tr>'
        for etiqueta, valor in filas
    )
    return (
        f'<h2>{escape(titulo)}</h2>'
        '<table border="1" cellpadding="6" cellspacing="0" '
        'style="border-collapse: collapse; width: 100%; max-width: 600px">'
        f'<tbody>{filas_html}</tbody></table>'
    )


def enviar_notificacion_habilitacion(asunto, mensaje, destinatario_empresa, datos, evento='habilitacion'):
    destinatarios = list(dict.fromkeys(filter(None, (
        destinatario_empresa,
        'noreply.beca.azul@gmail.com',
        settings.NOTIFICACIONES_EMAIL_ADICIONAL,
    ))))
    return _enviar_y_registrar(
        evento, asunto, destinatarios,
        lambda: send_mail(
            subject=asunto,
            message=mensaje,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=destinatarios,
            fail_silently=False,
            html_message=tabla_notificacion_html(asunto, datos),
        ),
    )


def enviar_reporte(titulo, html, destinatarios):
    email = EmailMultiAlternatives(
        subject=f'Reporte: {titulo}',
        body=f'Reporte: {titulo}. Este correo contiene una versión HTML del reporte.',
        from_email=None,
        to=destinatarios,
    )
    email.attach_alternative(html, 'text/html')
    return _enviar_y_registrar(
        'reporte', f'Reporte: {titulo}', destinatarios, email.send,
    )


def notificar_nuevo_trabajador(trabajador):
    return _enviar_y_registrar(
        'nuevo_trabajador', 'Nuevo trabajador registrado', settings.REPORTES_EMAILS,
        lambda: send_mail(
            subject='Nuevo trabajador registrado',
            message=(
                'Se ha creado un nuevo trabajador.\n\n'
                f'Nombre: {trabajador.nombres}\n'
                f'Apellido: {trabajador.apellidos}\n'
                f'Empresa: {trabajador.empresa.nombre}'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=settings.REPORTES_EMAILS,
            fail_silently=False,
            html_message=tabla_notificacion_html(
                'Nuevo trabajador registrado',
                (
                    ('Nombre', trabajador.nombres),
                    ('Apellido', trabajador.apellidos),
                    ('Documento', trabajador.get_tipo_documento_display()),
                    ('Número de documento', trabajador.dni),
                    ('Cargo', trabajador.cargo),
                    ('Empresa', trabajador.empresa.nombre),
                ),
            ),
        ),
    )
