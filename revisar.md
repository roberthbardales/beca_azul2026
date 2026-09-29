# Revisión general del sistema

## 1. Flujos principales

Comprobar manualmente cada rol:

- Administrador.
- Beca Azul.
- Planta.
- Usuario de empresa.
- Garita.
- Usuario no autenticado.

Probar login, logout, permisos, creación, edición, activación, desactivación y eliminación de empresas y trabajadores. También probar certificados, incidencias, búsquedas, alertas, SCTR y homologación.

Verificar que un usuario no pueda acceder a una URL prohibida pegándola directamente en el navegador.

## 2. Seguridad

- Verificar permisos en las vistas, no solo ocultar botones.
- Comprobar protección CSRF.
- Restringir archivos subidos.
- Impedir que una empresa acceda a PDFs o trabajadores de otra empresa.
- Confirmar autorización para eliminaciones.
- Usar `DEBUG=False` en producción.
- Mantener `SECRET_KEY` y credenciales fuera del repositorio.
- Configurar cookies seguras y HTTPS.

## 3. Integridad de datos

Revisar DNI único por empresa, RUC único, certificados únicos por requisito y fechas válidas.

También comprobar qué ocurre al eliminar o desactivar empresas y trabajadores, y qué sucede con sus certificados y archivos asociados.

Las reglas importantes deberían estar protegidas con restricciones de base de datos, no únicamente con validaciones de formularios.

## 4. Pruebas automatizadas

Ampliar las pruebas para cubrir:

- Permisos por rol.
- URLs importantes.
- Creación, edición y eliminación.
- Acceso entre empresas.
- Archivos inválidos, grandes o falsos PDF.
- Registros duplicados.
- Fechas inválidas.
- Formularios incompletos.
- Respuestas `403` y `404`.

## 5. Rendimiento

- Buscar consultas repetidas dentro de ciclos.
- Usar `select_related()` y `prefetch_related()` donde corresponda.
- Mantener paginación en listados.
- Revisar índices para DNI, RUC, fechas de vencimiento y estados.
- Revisar las consultas independientes del dashboard.

## 6. Archivos y almacenamiento

- Verificar límites de tamaño en aplicación y servidor.
- Validar realmente el contenido de los archivos.
- Usar nombres seguros.
- Comprobar reemplazo y eliminación de PDFs antiguos.
- Restringir el acceso a documentos sensibles.
- Incluir `MEDIA_ROOT` en los backups.

## 7. Experiencia de usuario

- Mensajes de error claros.
- Confirmación antes de eliminar.
- Mensajes de éxito después de guardar.
- Conservación de datos cuando un formulario falla.
- Estados vacíos para búsquedas sin resultados.
- Diseño responsive.
- Navegación consistente.
- Enlaces de retorno correctos según el rol.

## 8. Mantenimiento

Revisar vistas demasiado grandes, lógica duplicada, nombres inconsistentes, líneas largas, textos repetidos y separación entre permisos, consultas y presentación.

Documentar las reglas de negocio importantes.

## 9. Producción

Antes de publicar:

- Ejecutar `python manage.py check --deploy`.
- Configurar `DEBUG=False`.
- Configurar `ALLOWED_HOSTS`.
- Configurar HTTPS.
- Configurar archivos estáticos y multimedia.
- Configurar backups de base de datos y documentos.
- Configurar logs y monitoreo.
- Probar la restauración de un backup.

## Prioridad recomendada

1. Permisos por rol.
2. Acceso seguro a documentos PDF.
3. Integridad de certificados.
4. Pruebas de autorización.
5. Backups y restauración.
