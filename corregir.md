# Registro de correcciones

## Certificados con propietario inconsistente - Corregido

Las restricciones `CheckConstraint` del modelo impiden que un certificado tenga un propietario incompatible con su tipo, incluso si se inserta mediante `bulk_create()`.

Se agrego una prueba que confirma que una insercion masiva invalida es rechazada por la base de datos.

## Validaciones de Empresa - Corregido

`Empresa` ahora valida el formato del RUC, exige certificados vigentes para aprobar SCTR y exige certificados vigentes de ambos SCTR y homologacion para aprobar la homologacion.

Las vistas mantienen sus validaciones para evitar que las operaciones administrativas que usan `update_fields` puedan omitir `clean()`.

## Estado temporal de usuarios

`User.is_active_before_empresa_deactivation` guarda intencionalmente el estado previo del usuario para restaurarlo cuando la empresa vuelva a activarse. No requiere correccion.
