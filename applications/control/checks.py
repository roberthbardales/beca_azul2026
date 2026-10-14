from email.utils import parseaddr

from django.conf import settings
from django.core.checks import Warning, register
from django.core.exceptions import ValidationError
from django.core.validators import validate_email


@register()
def check_email_configuration(app_configs, **kwargs):
    issues = []
    if settings.EMAIL_BACKEND != 'anymail.backends.brevo.EmailBackend':
        return issues

    if not settings.ANYMAIL.get('BREVO_API_KEY'):
        issues.append(Warning(
            'BREVO_API_KEY no está configurada; el envío de correos fallará.',
            hint='Configura la clave de API transaccional de Brevo en el entorno.',
            id='control.W001',
        ))

    _, sender = parseaddr(settings.DEFAULT_FROM_EMAIL)
    try:
        validate_email(sender)
    except ValidationError:
        issues.append(Warning(
            'DEFAULT_FROM_EMAIL no contiene una dirección válida.',
            hint='Usa el formato Nombre <correo@dominio> con un remitente validado en Brevo.',
            id='control.W002',
        ))

    if not settings.REPORTES_EMAILS:
        issues.append(Warning(
            'REPORTES_EMAILS está vacío; los reportes y avisos de nuevos trabajadores no tendrán destinatarios.',
            hint='Configura REPORTES_EMAILS con direcciones separadas por comas.',
            id='control.W003',
        ))
    else:
        for address in settings.REPORTES_EMAILS:
            try:
                validate_email(address)
            except ValidationError:
                issues.append(Warning(
                    f'Hay una dirección inválida en REPORTES_EMAILS: {address!r}.',
                    hint='Corrige la lista de destinatarios en el entorno.',
                    id='control.W004',
                ))
                break

    if settings.NOTIFICACIONES_EMAIL_ADICIONAL:
        try:
            validate_email(settings.NOTIFICACIONES_EMAIL_ADICIONAL)
        except ValidationError:
            issues.append(Warning(
                'NOTIFICACIONES_EMAIL_ADICIONAL no es una dirección válida.',
                hint='Corrige o elimina el destinatario adicional en el entorno.',
                id='control.W005',
            ))
    return issues
