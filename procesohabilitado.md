# Proceso de habilitación del trabajador

## Estado inicial

Todo trabajador se crea como **HABILITADO** por defecto (`applications/control/models.py`, valor por defecto de `estado`). BECA_AZUL puede deshabilitarlo manualmente cuando corresponda.

## Regla de habilitación

El estado del trabajador es **100 % manual**: solo el usuario **BECA_AZUL** puede habilitarlo o deshabilitarlo desde el detalle del trabajador ("Cambiar estado" → `TrabajadorEstadoView`, `applications/control/views.py`). El permiso se controla con `AdministrarTrabajadoresMixin` (`applications/users/mixins.py`).

Estados posibles:

- **HABILITADO** = Habilitado
- **DESHABILITADO** = Deshabilitado

## Qué ya NO existe

- **Sin recalculación automática**: se eliminó `Trabajador.actualizar_estado()` y el signal `post_save` de `Certificado` (`applications/control/signals.py` ya no existe). Guardar o aprobar certificados **no cambia** el estado del trabajador.
- **Sin estados PENDIENTE ni RECHAZADO**: fueron reemplazados por un único estado negativo `DESHABILITADO`. La migración de datos mapea `PENDIENTE` → `DESHABILITADO` y `RECHAZADO` → `DESHABILITADO`.
- **El Usuario Empresa no puede cambiar estado**: se eliminó `TrabajadorEmpresaEstadoView` y su URL `trabajador_empresa_estado`.

## Cabos sueltos pendientes

- `aprobado_por` y `fecha_aprobacion` existen en el modelo `Certificado` pero todavía **no se asignan en ningún flujo** (solo son rellenables en el admin de Django manualmente).
- El superusuario conserva el bypass de los mixins, por lo que también puede cambiar el estado.