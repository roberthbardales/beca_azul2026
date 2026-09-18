# Como funciona el sistema

## 1. Entrada al sistema

El usuario ingresa desde `/users/login/` usando su correo electrónico y
contraseña. Django autentica las credenciales, crea una sesión y redirige al
usuario al panel principal.

También existen rutas para:

- Registro: `/users/register/`
- Cerrar sesión: `/users/logout/`
- Perfil: `/users/perfil/`
- Cambio de contraseña: `/users/update/`

## 2. Panel principal

Después del login, el usuario entra al dashboard mediante `/users/` y es
redirigido a `/panel/`.

El panel muestra:

- Total de empresas y empresas activas o inactivas.
- Total de trabajadores por estado.
- Total de certificados.
- Certificados vencidos y próximos a vencer.
- Cantidad de trabajadores por empresa.

Los usuarios con rol `USUARIO_EMPRESA` son enviados directamente a la lista de
trabajadores de su empresa.

## 3. Roles y permisos

| Rol | Permisos principales |
|---|---|
| `ADMINISTRADOR` | Gestiona determinados usuarios y consulta empresas y trabajadores |
| `BECA_AZUL` | Administra usuarios empresa, empresas, trabajadores y certificados |
| `USUARIO_EMPRESA` | Administra únicamente trabajadores de su empresa |
| `PLANTA` | Sin acceso a los paneles principales |
| `GARITA` | Sin acceso a los paneles principales |

Los permisos se controlan en el backend mediante mixins. Si un usuario intenta
entrar a una sección no autorizada, Django rechaza la solicitud.

## 4. Gestión de usuarios

Se encuentra en `/users/gestion/`.

Los usuarios autorizados pueden:

- Listar, buscar y filtrar usuarios.
- Crear y editar usuarios.
- Activar o desactivar cuentas.
- Eliminar usuarios.
- Restablecer contraseñas.

El rol `ADMINISTRADOR` gestiona usuarios `BECA_AZUL`, `PLANTA` y `GARITA`.
El rol `BECA_AZUL` gestiona usuarios `USUARIO_EMPRESA`.

El sistema impide que un usuario desactive o elimine su propia cuenta.

## 5. Gestión de empresas

Las empresas se administran desde `/empresas/`.

Una empresa contiene nombre, RUC único, dirección, teléfono, correo y estado
activo o inactivo.

El rol `BECA_AZUL` puede crear, editar, activar, desactivar y eliminar
empresas. El rol `ADMINISTRADOR` puede consultarlas, pero no administrarlas.

Una empresa no puede eliminarse si tiene trabajadores o usuarios asociados.

## 6. Gestión de trabajadores

Los trabajadores se gestionan desde `/trabajadores/`.

Cada trabajador pertenece a una empresa y contiene tipo de documento, DNI o
documento equivalente, nombres, apellidos, fecha de nacimiento, teléfono,
cargo, área y estado.

El sistema permite buscar, filtrar, ordenar, paginar, crear, editar, eliminar,
activar, desactivar y cambiar el estado de los trabajadores.

El documento activo debe ser único dentro de la misma empresa.

## 7. Usuarios de empresa

Los usuarios con rol `USUARIO_EMPRESA` acceden mediante
`/trabajadores/empresa/`.

Solo pueden consultar y modificar los trabajadores asociados a su propia
empresa. El backend verifica esta relación incluso si el usuario modifica
manualmente el identificador incluido en la URL.

## 8. Certificados

Los certificados pertenecen a un trabajador y se crean desde rutas como
`/trabajadores/<id>/certificados/crear/`.

Cada certificado registra nombre, descripción, fecha de emisión, fecha de
vencimiento, archivo PDF, aprobación, usuario aprobador y fecha de aprobación.

Los archivos se almacenan en `media/certificados/`. La configuración acepta
archivos PDF de hasta 5 MB.

## 9. Estado automático del trabajador

Cada vez que se guarda un certificado, una señal de Django actualiza el estado
del trabajador.

El trabajador pasa a `HABILITADO` cuando tiene al menos dos certificados
aprobados. De lo contrario, permanece en `PENDIENTE`.

Los estados disponibles son:

- `PENDIENTE`
- `HABILITADO`
- `RECHAZADO`

## 10. Base de datos y configuración

La aplicación utiliza PostgreSQL. Los datos de conexión se leen desde el
archivo `.env`:

```env
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=
```

También se configuran allí `SECRET_KEY`, `DEBUG` y `ALLOWED_HOSTS`.

Django administra los cambios de estructura mediante migraciones.

## 11. Flujo general

1. El usuario inicia sesión.
2. Django identifica su rol.
3. El sistema muestra únicamente las opciones autorizadas.
4. El usuario consulta o administra empresas y trabajadores.
5. Los trabajadores reciben certificados.
6. Los certificados determinan automáticamente el estado del trabajador.
7. El dashboard muestra los totales y alertas importantes.
