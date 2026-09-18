# Contexto del proyecto

## Resumen

`beca_azul2026` es una aplicación web para gestionar empresas, trabajadores,
certificados y usuarios con permisos diferenciados por rol. Está construida
con Django 3.2, plantillas HTML del lado del servidor y PostgreSQL.

## Stack técnico

- Python y Django `3.2.25`.
- PostgreSQL mediante `psycopg2-binary`.
- Configuración por variables de entorno con `django-environ`.
- Autenticación con un modelo de usuario propio (`users.User`) cuyo identificador
  es el correo electrónico.
- Archivos estáticos en `static/` y archivos subidos en `media/`.
- Imágenes mediante Pillow.
- Plantillas Django ubicadas en `templates/`.

## Estructura principal

```text
beca_azul2026/
├── applications/
│   ├── home/       # Página inicial
│   ├── users/      # Usuarios, autenticación, perfiles y permisos
│   └── control/    # Empresas, trabajadores y certificados
├── beca_azul2026/ # Configuración global del proyecto
├── templates/     # Plantillas HTML y componentes compartidos
├── static/        # Recursos estáticos
├── media/         # Archivos cargados por usuarios
├── fixtures/      # Datos iniciales
├── manage.py
├── requirements.txt
└── .env           # Configuración local, no debe versionarse
```

## Rutas principales

- `/`: inicio.
- `/users/`: login, registro, dashboard, perfil, cambio y restablecimiento de
  contraseña, además de la gestión de usuarios.
- `/empresas/`: listado y administración de empresas.
- `/trabajadores/`: listado, búsqueda y administración de trabajadores.
- `/trabajadores/empresa/`: vista restringida a los trabajadores de la empresa
  asociada al usuario.
- `/certificados/`: gestión de certificados.
- `/admin/`: administración nativa de Django.

Las rutas se registran en `beca_azul2026/urls.py`,
`applications/users/urls.py` y `applications/control/urls.py`.

## Modelo de datos

### Usuario

El modelo `applications.users.models.User` extiende `AbstractBaseUser` y
`PermissionsMixin`. Usa `email` como `USERNAME_FIELD` y puede estar asociado a
una `Empresa`.

Roles disponibles:

| Código | Rol |
|---|---|
| `0` | `ADMINISTRADOR` |
| `1` | `BECA_AZUL` |
| `2` | `PLANTA` |
| `3` | `USUARIO_EMPRESA` |
| `4` | `GARITA` |

### Empresa

Incluye nombre, RUC único, datos de contacto y estado activo. No se puede
eliminar una empresa que tenga relaciones protegidas.

### Trabajador

Pertenece a una empresa y contiene documento, nombres, apellidos, datos
personales, cargo, área y estado. El DNI/documento activo debe ser único dentro
de la empresa. Sus estados son `PENDIENTE`, `HABILITADO` y `RECHAZADO`.

### Certificado

Pertenece a un trabajador, registra emisión, vencimiento, aprobación y archivo.
Los archivos se almacenan bajo `media/certificados/`, deben ser PDF y tienen un
límite configurado de 5 MB. Un trabajador pasa a `HABILITADO` cuando tiene al
menos dos certificados aprobados.

## Permisos por rol

| Rol | Usuarios | Empresas | Trabajadores |
|---|---|---|---|
| Administrador | Gestiona usuarios de administración | Solo lectura | Solo lectura |
| Beca Azul | Gestiona usuarios empresa | CRUD | CRUD y certificados |
| Usuario Empresa | Sin acceso | Sin acceso | CRUD solo de su empresa |
| Planta | Sin acceso | Sin acceso | Sin acceso a paneles |
| Garita | Sin acceso | Sin acceso | Sin acceso a paneles |

Las restricciones se implementan principalmente en
`applications/users/mixins.py` y en las vistas de `applications/users/` y
`applications/control/`. La autorización debe validarse siempre en backend;
ocultar botones en las plantillas no es suficiente.

## Configuración requerida

Crear un archivo `.env` en la raíz con valores equivalentes a:

```env
SECRET_KEY=clave-local
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=nombre_base
DB_USER=usuario_base
DB_PASSWORD=contrasena_base
DB_HOST=localhost
DB_PORT=5432
```

No publicar el `.env`, contraseñas, claves secretas ni archivos de `media/` que
contengan información real.

## Puesta en marcha

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata seed
python manage.py runserver
```

Comprobaciones habituales:

```bash
python manage.py check
python manage.py makemigrations --check
python manage.py test
```

## Convenciones de desarrollo

- Mantener la lógica de autorización en mixins y vistas, no solo en templates.
- Usar formularios Django para validación de entrada y mensajes claros al
  usuario.
- Crear migraciones después de modificar modelos.
- Mantener las URLs agrupadas por aplicación y usar namespaces existentes.
- Usar `get_object_or_404` y filtros por empresa/rol para evitar exposición de
  datos entre organizaciones.
- No agregar secretos ni datos de producción al repositorio.

## Estado y pendientes conocidos

El sistema ya cuenta con CRUD de empresas, trabajadores y certificados,
búsqueda avanzada, paginación, filtros, validaciones de documentos, estados de
trabajadores y permisos por roles.

Pendientes documentados en `mejoras.md`:

- Exportación e importación masiva en CSV/Excel/PDF.
- Historial de cambios.
- Flujo guiado para vincular o crear el usuario de una empresa.
- Vista previa de documentos PDF.
- Alertas de DNI duplicado entre empresas.
- Ampliación de pruebas automatizadas para reglas de negocio.

El registro público `/users/register/` todavía permite seleccionar roles
privilegiados. Antes de producción debe restringirse a un rol seguro o
eliminarse la posibilidad de crear cuentas administrativas desde esa ruta.

## Archivos de referencia

- `README.md`: actualmente contiene solo el nombre del proyecto.
- `avance.md`: detalle de permisos implementados y verificaciones realizadas.
- `mejoras.md`: plan de mejoras y funcionalidades implementadas.
- `beca_azul2026/settings.py`: configuración, base de datos y seguridad.
- `applications/users/models.py`: usuarios y roles.
- `applications/control/models.py`: empresas, trabajadores y certificados.
