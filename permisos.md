# Tipos de usuarios y permisos

Este documento describe los permisos efectivos implementados actualmente en el backend.
Los permisos no dependen únicamente de los botones visibles en las plantillas: las vistas
validan el rol y, cuando corresponde, restringen el conjunto de datos consultable.

## Tipos de usuarios

| Rol | Código | Alcance general |
|---|---:|---|
| **Administrador** | `0` | Administración de empresas y usuarios, además de consulta amplia del sistema. Puede crear usuarios, pero no modificar trabajadores, certificados o incidencias desde las vistas normales. |
| **Beca Azul** | `1` | Administración general de usuarios, empresas, trabajadores, certificados e incidencias. |
| **Usuario Planta** | `2` | Consulta de usuarios, empresas, trabajadores y certificados. También puede acceder al dashboard. No tiene operaciones de modificación. |
| **Usuario Empresa** | `3` | Administración exclusivamente sobre la empresa asignada, sus trabajadores y sus certificados. |
| **Usuario Garita** | `4` | Búsqueda de empresas y consulta de listas de trabajadores por empresa. No administra información ni accede al detalle individual. |

Los códigos de rol son identificadores estables definidos por el modelo `User`.
Las plantillas que comparan estos códigos forman parte del comportamiento actual;
si se modifican, deben actualizarse de forma coordinada.

## Rutas principales

| Funcionalidad | Ruta base |
|---|---|
| Dashboard | `/panel/` |
| Búsqueda de empresas | `/empresas/buscar/` |
| Trabajadores de una empresa para Garita | `/empresas/<id>/trabajadores/` |
| Gestión de empresas | `/empresas/` |
| Listado de trabajadores | `/trabajadores/` |
| Búsqueda de trabajadores | `/trabajadores/buscar/` |
| Gestión de usuarios | `/users/gestion/` |
| Creación de usuarios protegida | `/users/gestion/crear/` |
| Reportes | `/reportes/` |

La ruta `/users/register/` fue deshabilitada y devuelve `404 Not Found`. La creación de
usuarios se realiza únicamente desde la gestión protegida.

Las rutas de gestión de trabajadores y certificados tienen dos variantes: una para
Beca Azul y otra específica para Usuario Empresa. Las vistas específicas de empresa
comprueban que el registro pertenezca a la empresa asignada al usuario.

## Administrador

### Usuarios

- Puede acceder al listado de usuarios.
- Puede ver en el listado usuarios de todos los roles, incluidos Administradores y Beca Azul.
- Puede consultar el detalle, editar, activar, desactivar, eliminar y restablecer la contraseña de usuarios permitidos por la vista.
- Puede crear usuarios desde la gestión normal.
- No puede editar ni eliminar cuentas con rol Administrador desde las vistas normales de detalle, edición y eliminación.
- Puede gestionar usuarios de los roles permitidos por las vistas, incluidos Beca Azul, Planta, Empresa y Garita.

### Empresas

- Puede consultar el listado de empresas.
- Puede buscar empresas por nombre, RUC, estado y homologación.
- Puede ver el detalle de cualquier empresa.
- Puede crear empresas.
- Puede editar empresas.
- Puede activar o desactivar empresas.
- Puede eliminar empresas cuando no tengan trabajadores ni usuarios asociados.

### Trabajadores, certificados e incidencias

- Puede consultar el listado de trabajadores de todas las empresas.
- Puede buscar trabajadores por DNI, nombres, apellidos o cargo.
- Puede consultar el detalle de cualquier trabajador.
- No puede crear, editar, activar, desactivar ni eliminar trabajadores.
- No puede crear, editar ni eliminar certificados.
- No puede crear, editar ni eliminar incidencias.
- La homologación o habilitación del trabajador tampoco está disponible para este rol.

### Dashboard

- Puede acceder al dashboard general.
- El dashboard muestra métricas globales de empresas, trabajadores y certificados.

### Reportes

- Puede acceder a `/reportes/` y consultar los reportes globales.

## Beca Azul

### Usuarios

- Puede acceder al listado de usuarios.
- Puede crear usuarios.
- Puede editar, activar, desactivar, eliminar y restablecer la contraseña de usuarios.
- En las vistas normales, puede gestionar usuarios Planta, Empresa y Garita.
- No puede gestionar Administradores desde las vistas normales.
- Al crear o editar un Usuario Empresa, puede asignarle una empresa.
- Los usuarios de otros roles no pueden conservar una empresa asignada.

### Empresas

- Puede consultar el listado de empresas.
- Puede buscar empresas por nombre, RUC, estado y homologación.
- Puede ver el detalle de cualquier empresa.
- Puede crear, editar, activar, desactivar y eliminar empresas.
- La eliminación se bloquea cuando existen trabajadores o usuarios asociados.

### Trabajadores

- Puede consultar trabajadores de todas las empresas.
- Puede filtrar trabajadores por empresa, estado y datos personales.
- Puede buscar trabajadores.
- Puede consultar el detalle de cualquier trabajador.
- Puede editar trabajadores.
- Puede activar o desactivar trabajadores.
- Puede eliminar trabajadores.
- Puede modificar el estado de habilitación u homologación del trabajador.
- Puede aprobar o desaprobar el SCTR del trabajador desde su página de detalle.
- El estado SCTR del trabajador inicia como desaprobado y no cambia automáticamente
  por el vencimiento del certificado SCTR de la empresa.

### Certificados e incidencias

- Puede crear, editar y eliminar certificados de trabajadores.
- Puede gestionar certificados de inducción, aptitud médica y cursos.
- Puede crear, editar y eliminar incidencias.
- Las incidencias quedan registradas con el usuario que las creó.

### Dashboard

- Puede acceder al dashboard general con información global del sistema.

### Reportes

- Puede acceder a `/reportes/` y consultar los reportes globales.

## Usuario Planta

### Usuarios

- Puede consultar el listado de usuarios.
- Puede ver los usuarios permitidos por el sistema: Beca Azul, Planta y Garita.
- No puede consultar ni gestionar Administradores desde la gestión normal.
- No puede crear, editar, activar, desactivar, eliminar ni restablecer contraseñas de usuarios.

### Empresas

- Puede acceder al listado de empresas en `/empresas/`.
- Puede buscar y filtrar empresas por nombre, RUC, estado y homologación.
- Puede ver el detalle de cualquier empresa.
- Solo tiene permisos de lectura.
- No puede crear, editar, activar, desactivar ni eliminar empresas.
- No puede editar el SCTR.

### Trabajadores, certificados e incidencias

- Puede consultar trabajadores de todas las empresas.
- Puede buscar trabajadores.
- Puede consultar el detalle de cualquier trabajador.
- Puede consultar certificados asociados a los trabajadores.
- No puede crear, editar, activar, desactivar ni eliminar trabajadores.
- No puede crear, editar ni eliminar certificados.
- No puede crear, editar ni eliminar incidencias.
- No puede modificar la homologación o habilitación de trabajadores.
- No puede aprobar ni desaprobar el SCTR de los trabajadores.

### Dashboard

- Puede acceder al dashboard general.
- El dashboard se muestra con información global, no limitada a una empresa.

### Reportes

- Puede acceder a `/reportes/`.
- Los reportes se limitan a su empresa y a sus trabajadores.

## Usuario Empresa

### Alcance de datos

- Debe tener una empresa asignada.
- Solo puede consultar y administrar trabajadores cuya empresa sea la asignada mediante `request.user.empresa` o `request.user.empresa_id`.
- Si no tiene empresa asignada, las vistas específicas de empresa rechazan el acceso.
- El acceso a un trabajador, certificado o empresa perteneciente a otra empresa se rechaza; según la vista, se devuelve `403` o `404` al no encontrar el objeto dentro del queryset autorizado.

### Empresa y SCTR

- Puede consultar el detalle de su empresa.
- Puede consultar el estado de homologación y el SCTR de su empresa.
- Puede crear, editar o reemplazar el SCTR de su empresa.
- Puede crear, editar o reemplazar el certificado de homologación de su empresa.
- No puede consultar el detalle de otras empresas.
- No puede crear, editar, activar, desactivar ni eliminar empresas.

### Trabajadores

- Puede consultar el listado de trabajadores de su empresa.
- Puede buscar trabajadores de su empresa.
- Puede consultar el detalle de sus trabajadores.
- Puede crear trabajadores para su empresa.
- Puede editar trabajadores de su empresa.
- Puede activar o desactivar trabajadores de su empresa.
- Puede eliminar trabajadores de su empresa.
- Al crear o editar un trabajador, la empresa se establece desde el usuario autenticado; no puede elegir otra empresa.
- No puede aprobar ni desaprobar el SCTR del trabajador; esa acción corresponde exclusivamente a Beca Azul.

### Certificados

- Puede cargar certificados de sus trabajadores.
- Puede crear, editar y eliminar certificados de sus trabajadores.
- Puede gestionar certificados de inducción, aptitud médica y cursos.
- Puede cargar certificados durante el alta o edición de un trabajador.
- No puede gestionar certificados de trabajadores de otras empresas.

### Incidencias y dashboard

- No puede crear, editar ni eliminar incidencias.
- No accede al dashboard general.
- Un acceso directo a `/panel/` o a la ruta alternativa del dashboard devuelve `403`.
- Al iniciar sesión es redirigido al listado de trabajadores de su empresa.

## Usuario Garita

### Empresas

- Puede acceder a la búsqueda de empresas mediante `/empresas/buscar/`.
- Puede buscar empresas por nombre, RUC, estado y homologación.
- Actualmente el backend no restringe esta búsqueda a empresas homologadas: puede devolver empresas homologadas y no homologadas.
- No puede crear, editar, activar, desactivar ni eliminar empresas.
- No puede acceder a la gestión normal de empresas ni modificar el SCTR.
- Puede abrir la lista de trabajadores de una empresa desde el botón `Ver lista`.
- Esta acción dirige a la lista de
  trabajadores de la empresa seleccionada.
- La búsqueda no conserva filtros ni paginación al abrir dicha lista.

### Trabajadores

- Puede consultar la lista de trabajadores activos e inactivos de una empresa mediante
  `/empresas/<id>/trabajadores/`.
- No puede consultar el detalle individual mediante `/trabajadores/<id>/`; esa ruta
  devuelve `403 Forbidden`.
- En la lista por empresa no se muestra la columna `Acciones`.
- La lista queda limitada a la empresa indicada en la URL.
- Actualmente el backend no exige que el trabajador pertenezca a una empresa homologada.
- No puede crear, editar, activar, desactivar ni eliminar trabajadores.
- No puede modificar la homologación o habilitación del trabajador.
- No puede aprobar ni desaprobar el SCTR del trabajador.

### Usuarios, certificados, incidencias y dashboard

- No puede acceder a la gestión de usuarios.
- No puede crear, editar ni eliminar certificados.
- No puede crear, editar ni eliminar incidencias.
- No puede acceder al dashboard administrativo.
- Un acceso directo a `/panel/` o a la ruta alternativa del dashboard devuelve `403`.
- Después del inicio de sesión es redirigido a la búsqueda de trabajadores.

## Reglas de autorización del backend

- Las autorizaciones se validan en las vistas mediante mixins de rol y comprobaciones explícitas.
- El ocultamiento de botones en las plantillas no constituye el control de seguridad principal.
- Un rol sin autorización para una vista recibe `403 Forbidden` mediante `PermissionDenied`.
- Las operaciones sobre empresas, trabajadores, certificados e incidencias tienen controles separados.
- Los querysets se filtran por empresa para Usuario Empresa antes de devolver objetos.
- Un usuario Empresa no puede cambiar el alcance modificando parámetros de la URL o del formulario.
- Las operaciones de modificación usan solicitudes `POST` en las vistas de activación, desactivación y eliminación lógica.
- La eliminación de empresas se bloquea si existen trabajadores o usuarios relacionados.
- La eliminación de un trabajador elimina también sus certificados relacionados según las reglas de los modelos.

## Superusuario de Django

- El superusuario de Django puede superar los controles de los mixins basados únicamente en `role`.
- Este comportamiento es independiente del código de rol almacenado en `User.role`.
- Las vistas con validaciones manuales adicionales pueden aplicar restricciones basadas en el rol aunque el usuario sea superusuario.
- Por seguridad operativa, el superusuario debe tener un rol y una empresa coherentes con las operaciones que vaya a realizar.

## Resumen por operación

| Operación | Admin. | Beca Azul | Planta | Empresa | Garita |
|---|---:|---:|---:|---:|---:|
| Dashboard general | Sí | Sí | Sí | No | No |
| Listar usuarios | Sí | Sí | Sí | No | No |
| Crear usuarios | Sí | Sí | No | No | No |
| Gestionar empresas | Sí | Sí | No | No | No |
| Consultar empresas | Todas | Todas | Todas | Asignada | Búsqueda general |
| Consultar trabajadores | Todas | Todas | Todas | Propios | Búsqueda general |
| Modificar trabajadores | No | Sí | No | Propios | No |
| Gestionar certificados | No | Sí | No | Propios | No |
| Gestionar incidencias | No | Sí | No | No | No |
| Gestionar SCTR | No | No | No | Propio | No |
| Consultar reportes | Sí | Sí | Sí | Propios | No |

El dashboard está disponible exclusivamente para Administrador, Beca Azul y Usuario Planta.
Usuario Empresa y Usuario Garita reciben `403` tanto en la ruta principal `/panel/` como en
la ruta alternativa del dashboard. El superusuario de Django conserva el acceso, aunque su
rol almacenado sea distinto, porque los controles de dashboard permiten explícitamente a los
superusuarios.

En la fila de empresas, “Búsqueda general” refleja el comportamiento actual: Garita puede
encontrar empresas homologadas y no homologadas porque todavía no existe un filtro backend
que limite los resultados a `homologado=True`.
