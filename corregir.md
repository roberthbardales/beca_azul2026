# Correcciones Pendientes

Ordenadas de más crítico a menos crítico.

## 1. Permisos inconsistentes en vistas administrativas

Las vistas de trabajadores y certificados usan permisos que no reflejan claramente los roles autorizados. Esto puede impedir operaciones a usuarios permitidos o permitir accesos incorrectos.

Archivos principales:

- `applications/control/views.py`
- `applications/users/mixins.py`

## 2. Eliminación del certificado anterior antes de guardar el nuevo

Al reemplazar un certificado, el anterior se elimina antes de confirmar que el nuevo archivo se guardó correctamente. Si ocurre un error, puede perderse el certificado anterior.

Vistas afectadas:

- `CertificadoCreateView`
- `CertificadoEmpresaCreateView`

## 3. Falta de transacción al reemplazar certificados

La eliminación y creación del certificado deben ejecutarse dentro de `transaction.atomic()` para evitar operaciones incompletas.

## 4. Posible `IntegrityError` al cambiar el curso

Si un trabajador ya tiene un certificado para el curso seleccionado, cambiar otro certificado a ese mismo curso puede violar la restricción única y producir un error 500.

## 5. Roles escritos como valores literales

Hay condiciones como:

```python
request.user.role == '3'
```

Deben usar las constantes del modelo:

```python
request.user.role == User.USUARIO_EMPRESA
```

## 6. Lógica repetida en las listas de trabajadores

`TrabajadorListView` y `TrabajadorEmpresaListView` repiten anotaciones, filtros y ordenamiento. Conviene extraer esta lógica a un queryset o mixin reutilizable.

## 7. Muchas consultas independientes en el dashboard

El dashboard realiza varias consultas separadas para contadores, trabajadores, empresas y certificados. Puede optimizarse agrupando agregaciones cuando aumente el volumen de datos.

## 8. `certificados_sin_vencimiento` fijo en cero

Actualmente se define así:

```python
certificados_sin_vencimiento = 0
```

Debe calcularse o eliminarse si el modelo siempre exige fecha de vencimiento.

## 9. Falta validar trabajadores inactivos

Algunas operaciones permiten editar trabajadores inactivos o agregarles certificados. Debe definirse si esto es correcto para el negocio.

## 10. `views.py` demasiado grande

El archivo contiene dashboard, empresas, trabajadores, certificados e incidencias. Conviene dividirlo por funcionalidad para facilitar su mantenimiento.
