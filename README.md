# Sistema de Control de Empresas y Trabajadores

> Guía de instalación y uso técnico basada en el contenido actual del proyecto. No identifica una versión publicada o desplegada.

Aplicación web para gestionar empresas, trabajadores y la documentación requerida para consultar y controlar su habilitación. Permite dar seguimiento a certificados, requisitos de seguridad, incidencias y estados de cumplimiento desde una interfaz con acceso según el rol del usuario.

## Funcionalidades principales

- Gestión de empresas y sus certificados SCTR de pensión, SCTR de salud y homologación.
- Registro y administración de trabajadores asociados a empresas.
- Carga y seguimiento de certificados de inducción, aptitud médica y cursos de seguridad.
- Configuración de cursos obligatorios y validación de documentos vigentes.
- Cálculo del estado de habilitación del trabajador según los requisitos aplicables.
- Paneles, reportes, registro de incidencias y búsqueda para consulta en garita.
- Administración de usuarios con roles diferenciados.

## Tecnologías

- Python y Django 4.2.25.
- HTML, plantillas Django, Tailwind CSS, CSS y JavaScript.
- Chart.js para gráficos.
- PostgreSQL como base de datos.
- `django-environ` para leer la configuración desde variables de entorno.

Las dependencias Python están listadas en `requirements.txt`.

## Organización

```text
applications/
  control/       Empresas, trabajadores, certificados, incidencias y reportes
  home/          Redirección inicial y página de acceso denegado
  users/         Usuarios, autenticación, perfiles y permisos
beca_azul2026/   Configuración y rutas del proyecto Django
fixtures/        Fixtures de datos
media/           Archivos cargados por la aplicación
static/          CSS, JavaScript, imágenes y otros recursos estáticos
templates/       Plantillas HTML
manage.py        Comandos administrativos de Django
  requirements.txt Dependencias Python
```

Documentos complementarios: [`DOCUMENTACION_TECNICA.md`](DOCUMENTACION_TECNICA.md) describe la arquitectura, seguridad, base de datos, respaldo y despliegue; [`permisos.md`](permisos.md) resume los permisos por rol, también disponible en [`permisos.pdf`](permisos.pdf).

## Requisitos

- Python compatible con las versiones de `requirements.txt`.
- PostgreSQL disponible y una base de datos preparada para la aplicación.
- Variables de entorno configuradas para la aplicación.

## Configuración local

La aplicación lee un archivo `.env` en la raíz del proyecto. Crea ese archivo localmente y configura los valores necesarios. **No agregues `.env` ni credenciales al repositorio.**

Variables requeridas para iniciar la configuración:

| Variable | Uso |
|---|---|
| `SECRET_KEY` | Clave secreta de Django. |
| `DB_NAME` | Nombre de la base PostgreSQL. |
| `DB_USER` | Usuario de la base de datos. |
| `DB_PASSWORD` | Contraseña de la base de datos. |

Variables opcionales de base de datos y aplicación:

| Variable | Valor predeterminado/uso |
|---|---|
| `DB_HOST` | `localhost` |
| `DB_PORT` | `5432` |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | Lista separada por comas de hosts permitidos. |

El correo transaccional se envía mediante la API HTTPS de Brevo (no SMTP). Define `BREVO_API_KEY` en el archivo `.env` y configura allí los destinatarios de reportes y notificaciones. El remitente predeterminado es `CheckID <notificaciones@envios.beca-azul.com>`. No guardes credenciales en el repositorio.

## Instalación y ejecución

Desde la raíz del repositorio:

1. Crear y activar un entorno virtual:

   ```bash
   python -m venv .venv
   ```

   En Windows PowerShell:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   En macOS/Linux:

   ```bash
   source .venv/bin/activate
   ```

2. Instalar dependencias:

   ```bash
   pip install -r requirements.txt
   ```

3. Crear y configurar el archivo `.env` según la sección anterior.
4. Preparar el esquema de la base de datos y una cuenta administrativa:

   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. Iniciar el servidor de desarrollo:

   ```bash
   python manage.py runserver
   ```

Abrir `http://127.0.0.1:8000/` en el navegador. El servidor de desarrollo no está destinado a producción.

`BREVO_API_KEY` solo es necesaria si se van a utilizar las funciones de notificación y envío de reportes por correo.

## Solución de problemas básicos

- **Error al iniciar por configuración incompleta:** confirma que el archivo `.env` existe en la raíz y que contiene las variables requeridas, sin compartir sus valores.
- **No conecta con PostgreSQL:** verifica que el servicio esté activo y que el nombre de base, usuario, contraseña, host y puerto coincidan con la configuración de tu entorno.
- **Faltan dependencias:** activa el entorno virtual del proyecto e instala los paquetes con `pip install -r requirements.txt`.
- **No se envían correos:** revisa `BREVO_API_KEY`, los destinatarios y la configuración de Brevo.
- **Archivos estáticos o certificados no se muestran en producción:** comprueba la configuración del servidor para entregar archivos estáticos y medios; `runserver` es solo para desarrollo.

## Usuarios y permisos

El sistema contempla los roles Administrador, Beca Azul, Usuario Planta, Usuario Empresa y Usuario Garita. Los permisos se aplican en las vistas y pueden depender de la operación y del estado de la empresa o trabajador. Las cuentas de Usuario Empresa están vinculadas a una empresa y las consultas de ese rol se limitan a ella en las vistas correspondientes. Consulta [`permisos.md`](permisos.md) para el resumen detallado; también está disponible en [`permisos.pdf`](permisos.pdf).

## Seguridad y archivos

- La autenticación, sesiones, validación de contraseñas y protección CSRF se implementan mediante Django.
- Los certificados se aceptan como PDF con un tamaño máximo configurado de 1 MB.
- La configuración activa opciones adicionales de HTTPS, HSTS y cookies seguras cuando `DEBUG` está desactivado.
- Los certificados y archivos de medios pueden contener información sensible: protege su almacenamiento y evita publicarlos o incluirlos en el control de versiones.
- No publiques claves, contraseñas, direcciones privadas ni datos personales en este README, en el repositorio o en registros compartidos.
- No se verificó una política automatizada de respaldos; el operador del despliegue debe definir y probar la copia y recuperación de PostgreSQL y de `MEDIA_ROOT`.

## Notas de despliegue

En producción se requiere configurar correctamente PostgreSQL, variables de entorno, HTTPS, correo transaccional por API HTTPS de Brevo y la entrega segura de archivos estáticos y medios. El repositorio no define servidor WSGI/ASGI, proxy, monitoreo ni política de copias; esos componentes deben definirse para el entorno de despliegue. No usar `runserver` en producción. Para el detalle técnico, consultar [`DOCUMENTACION_TECNICA.md`](DOCUMENTACION_TECNICA.md).
