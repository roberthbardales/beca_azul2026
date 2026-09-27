# Tipos de usuarios y permisos

## Tipos de usuarios

| Rol | Código | Permisos principales |
|---|---:|---|
| **Administrador** | `0` | Puede ver y gestionar todos los usuarios existentes. Tiene los mismos permisos que Beca Azul en empresas. |
| **Beca Azul** | `1` | Administración general del sistema. |
| **Usuario Planta** | `2` | Consulta de información, sin modificar datos. |
| **Usuario Empresa** | `3` | Gestiona únicamente la información de su empresa. |
| **Usuario Garita** | `4` | Consulta trabajadores para control de acceso. |

## Administrador

- Puede acceder a la gestión de usuarios.
- Puede ver todos los tipos de usuarios, incluidos Administradores y Beca Azul.
- Puede consultar, crear, editar, activar, desactivar y eliminar empresas.
- Puede acceder al detalle de cualquier empresa.
- Puede consultar trabajadores y certificados.
- No tiene permisos de modificación sobre trabajadores, según las reglas actuales.
- No puede registrar o editar usuarios nuevos desde la vista normal si el permiso de creación está reservado a Beca Azul.

## Beca Azul

- Puede gestionar usuarios Planta, Empresa y Garita.
- Puede crear usuarios.
- Puede editar usuarios permitidos.
- Puede consultar empresas.
- Puede crear, editar, activar, desactivar y eliminar empresas.
- Puede ver el detalle de cualquier empresa.
- Puede gestionar trabajadores.
- Puede gestionar certificados e incidencias.
- Tiene acceso al dashboard general.
- Tiene permisos completos de administración operativa.

## Usuario Planta

- Puede consultar usuarios permitidos.
- Puede acceder a `/empresas/`.
- Puede buscar y filtrar empresas por nombre, RUC, estado y homologación.
- Puede ver el detalle de cualquier empresa.
- Solo tiene acceso de lectura en empresas.
- No puede crear, editar, activar, desactivar ni eliminar empresas.
- Puede consultar trabajadores y certificados.
- No puede modificar trabajadores ni certificados.

## Usuario Empresa

- Solo puede acceder a la empresa asignada a su usuario.
- Puede consultar el detalle de su empresa.
- Puede ver el estado de homologación y el SCTR.
- Puede registrar, editar o reemplazar el SCTR de su empresa.
- Puede gestionar trabajadores de su empresa: crear, editar, activar, desactivar y eliminar.
- Puede cargar y gestionar certificados de sus trabajadores.
- No puede consultar ni modificar otras empresas.
- No puede crear ni gestionar otros usuarios.

## Usuario Garita

- Puede buscar empresas homologadas mediante la búsqueda de empresas.
- Puede buscar trabajadores.
- Puede consultar el detalle de trabajadores.
- Está orientado al control de acceso.
- No tiene acceso al dashboard administrativo.
- No puede administrar empresas, trabajadores, usuarios ni certificados.

## Reglas importantes

- Los permisos se validan en el backend, no solo ocultando botones en los templates.
- Si un usuario intenta acceder directamente a una URL no permitida, recibe un error `403`.
- El Usuario Empresa queda limitado mediante `request.user.empresa_id`.
- Planta puede ver empresas, pero no tiene acciones de modificación.
- Administrador y Beca Azul tienen permisos equivalentes para administrar empresas.
