# Documentación técnica

## Sistema de Control de Empresas y Trabajadores

**Estado del documento:** elaborado a partir del código fuente disponible. Describe la configuración y funcionalidades verificables en el repositorio; no certifica la configuración de un entorno productivo.

## 1. Arquitectura

Aplicación web monolítica construida con **Python 3 y Django 4.2.25**. La interfaz usa plantillas HTML de Django, CSS/Tailwind y JavaScript; incluye Chart.js. La persistencia está configurada para **PostgreSQL** mediante `psycopg2`. Los correos transaccionales se integran con Brevo mediante API HTTPS (django-anymail). Los certificados PDF se almacenan en el sistema de archivos configurado en `MEDIA_ROOT`.

| Componente | Interacción |
|---|---|
| Usuario / navegador | Se comunica por HTTP(S) con la aplicación Django. |
| Django (vistas, formularios y plantillas) | Recibe solicitudes y utiliza los módulos funcionales. |
| `users`, `control`, `home` | Implementan autenticación, gestión del sistema y páginas generales. |
| PostgreSQL | Persistencia consultada mediante el ORM de Django. |
| Almacenamiento de medios | Lectura y escritura de certificados PDF. |
| Recursos estáticos | CSS, JavaScript e imágenes servidos al navegador. |
| Brevo | Envío de correo transaccional mediante API HTTPS. |

**Flujo resumido:** Navegador → Django → módulos de la aplicación → PostgreSQL y almacenamiento de medios. Las notificaciones que correspondan se envían desde la aplicación a Brevo; la interfaz carga los recursos estáticos.

No se identificó una API separada ni una arquitectura de microservicios. El servidor web, proxy TLS, almacenamiento externo, monitoreo y topología de producción no están definidos en el repositorio.

## 2. Diseño, módulos y funcionamiento

- `beca_azul2026/`: configuración, rutas raíz y puntos de entrada WSGI/ASGI.
- `applications/users/`: modelo de usuario propio con inicio/cierre de sesión, perfil, administración y permisos basados en rol.
- `applications/control/`: empresas, trabajadores, cursos/requisitos, certificados, incidencias, reportes, paneles y notificaciones.
- `applications/home/`: redirección/páginas generales, incluida la respuesta de acceso denegado.
- `templates/`, `static/`: presentación, estilos, scripts y recursos de interfaz.
- `media/`: destino configurado para archivos cargados; debe tratarse como dato sensible.
- `fixtures/`: datos de inicialización/prueba presentes en el repositorio.

Los formularios validan datos antes de persistirlos. Django ORM realiza consultas a PostgreSQL. El estado efectivo de habilitación combina estado activo de empresa y trabajador, aprobaciones y vigencia de SCTR/homologación, inducción, aptitud médica y cursos obligatorios. La aplicación registra historial de cambios de estado y puede enviar notificaciones y reportes por correo.

| Etapa | Funcionamiento |
|---|---|
| 1. Solicitud | El navegador realiza una solicitud a Django. |
| 2. Acceso | Se comprueba autenticación y permiso; si falla, se solicita inicio de sesión o se deniega el acceso. |
| 3. Validación | La vista procesa los datos mediante formularios y validaciones. |
| 4. Persistencia | Los cambios válidos se guardan con el ORM y, cuando aplica, dentro de transacciones. |
| 5. Archivos | Los PDF se guardan en `MEDIA_ROOT`. |
| 6. Reglas de negocio | Se calculan vigencias y habilitación a partir de los requisitos aplicables. |
| 7. Respuesta | Se presenta la página, panel o reporte; cuando corresponde, se envía una notificación por Brevo. |

## 3. Seguridad, validaciones, roles y permisos

### Controles observados

- Middleware Django de sesión, autenticación, CSRF, seguridad y prevención de framing (`XFrameOptionsMiddleware`).
- En `DEBUG=False`: redirección a HTTPS, HSTS por 31.536.000 segundos con subdominios y preload, cookies de sesión/CSRF seguras, `X-Content-Type-Options: nosniff` y `X-Frame-Options: DENY`.
- `ALLOWED_HOSTS` y `CSRF_TRUSTED_ORIGINS` se leen de entorno; los hosts permitidos no tienen valores predeterminados.
- Validaciones de formularios y restricciones de base de datos: RUC de 11 dígitos, DNI de 8 dígitos cuando corresponde, unicidad condicionada, formatos/fechas coherentes y propietario/tipo de certificado compatible.
- PDF limitado a 1 MiB; se comprueba extensión `.pdf` y firma inicial `%PDF-`. Esto no equivale a análisis antimalware ni valida exhaustivamente el contenido del archivo.
- Acceso a vistas restringido mediante login, mixins y comprobaciones de rol. Los usuarios de empresa requieren empresa asociada activa; las vistas de trabajador aplican controles de rol/empresa según su caso.
- Descarga de certificados de empresa pasa por una vista dedicada. En modo desarrollo, Django sirve medios; en producción debe configurarse el servidor de medios de forma segura.

### Roles

Roles definidos en `applications/users/models.py`: **Administrador**, **Beca Azul**, **Usuario Planta**, **Usuario Empresa** y **Usuario Garita**. Los permisos se aplican por vista mediante mixins y filtrado de registros. En particular, Usuario Empresa está vinculado obligatoriamente a una empresa y el acceso a su ámbito depende del control de empresa activa. Superusuario Django puede superar ciertos controles de rol.

No se encontró una matriz central única de permisos; el alcance concreto depende de cada vista y queryset. No se documenta aquí una garantía de aislamiento para cada endpoint más allá del código comprobable. No se verificaron controles de rate limiting, CAPTCHA, antivirus de cargas ni política externa de auditoría/retención.

## 4. Inicio de sesión y sesiones

- El identificador de autenticación es el correo electrónico; las vistas llaman a `django.contrib.auth.authenticate`, `login` y `logout`.
- Contraseñas se establecen/cambian mediante `set_password` de Django y no se guardan en texto plano por la lógica observada. Django aplica su mecanismo de hash configurable.
- Validadores configurados: similitud con atributos del usuario, longitud mínima predeterminada de Django, contraseña común y solo numérica.
- Mensaje genérico para credenciales incorrectas. El cierre de sesión se procesa mediante POST y requiere usuario autenticado.
- Gestión de sesión y CSRF delegadas al middleware Django. En producción, cookie de sesión y CSRF marcadas `Secure`; el valor predeterminado estándar de `HttpOnly` para cookie de sesión depende de Django.
- No se encontró configuración explícita de caducidad/rotación de sesión, bloqueo por intentos, segundo factor ni limitación de solicitudes. La protección frente a fuerza bruta no pudo verificarse como control implementado.

## 5. Base de datos SQL

La configuración declara PostgreSQL (`django.db.backends.postgresql_psycopg2`), con nombre, usuario y contraseña de conexión suministrados por entorno. Las migraciones de Django describen el esquema. No se inspeccionó un servidor SQL activo ni se verificaron parámetros del servidor.

### Entidades principales

| Tabla/modelo | Propósito y relaciones |
|---|---|
| `users_user` (`User`) | Cuenta, correo único, contraseña gestionada por Django, rol, estado y FK opcional protegida a `Empresa`; Usuario Empresa exige empresa por validación y constraint. |
| `control_empresa` (`Empresa`) | Empresa, RUC/correo únicos, datos y aprobaciones; relaciones con trabajadores, certificados y usuarios. |
| `control_trabajador` (`Trabajador`) | Persona/documento y estado; FK protegida a Empresa; unicidad condicionada de documento por empresa para trabajadores activos. |
| `control_certificado` (`Certificado`) | Tipo, fechas, archivo, aprobación; FK opcional a Empresa o Trabajador, cuya combinación válida depende del tipo. |
| `control_cursoobligatorio` (`CursoObligatorio`) | Curso requerido por trabajador; único por trabajador y curso. |
| `control_incidencia` (`Incidencia`) | Incidencia asociada a trabajador; registrador asociado opcionalmente a usuario. |
| `control_estadotrabajadorhistorico` (`EstadoTrabajadorHistorico`) | Historial de estado relacionado con trabajador. |
| `control_registronotificacion` (`RegistroNotificacion`) | Evento, destinatarios, estado y error de notificación; no tiene FK declarada a usuario/empresa. |

Las tablas auxiliares de autenticación/sesión/permisos de Django (incluidas `django_session`, `auth_group` y tablas de permisos) también forman parte del esquema migrado. Los nombres físicos de tablas derivan del app label/modelo salvo personalización de Django.

| Entidad origen | Relación | Entidad destino | Notas |
|---|---|---|---|
| Empresa | 1 a muchos | Trabajador | Un trabajador pertenece a una empresa. |
| Empresa | 1 a muchos | Certificado | Incluye certificados empresariales, como SCTR y homologación. |
| Trabajador | 1 a muchos | Certificado | Incluye inducción, aptitud médica y cursos. |
| Trabajador | 1 a muchos | Curso obligatorio | Un requisito de curso pertenece a un trabajador. |
| Trabajador | 1 a muchos | Incidencia | Cada incidencia se asocia a un trabajador. |
| Trabajador | 1 a muchos | Historial de estado | Conserva estados históricos del trabajador. |
| Empresa | 1 a muchos | Usuario | La FK de empresa del usuario es opcional; los usuarios con rol Empresa deben tenerla. |
| Usuario | 1 a muchos (opcional) | Incidencia | Una incidencia puede guardar quién la registró. |
| Registro de notificación | Sin FK declarada | — | Guarda evento, estado, destinatarios y error; no tiene relación declarada con usuario o empresa. |

**Seguridad e integridad SQL:** ORM parametrizado de Django para consultas habituales; claves foráneas, unicidad, check constraints y validación de modelos/formularios según los casos descritos. La seguridad de red, cifrado en reposo, privilegios del usuario SQL, auditoría, parchado y copias dependen de la infraestructura y no se verificaron. Las credenciales SQL se obtienen del entorno; no se incluyen en esta documentación.

## 6. Backup y recuperación

No se identificaron scripts, tareas programadas, política de retención ni configuración de backup/restauración en el código/documentación analizados. Por tanto, **no puede confirmarse que existan respaldos ni asignarles frecuencia**.

Procedimiento operativo recomendado, a definir y probar por el responsable de infraestructura:

1. Respaldar PostgreSQL con herramientas nativas (`pg_dump`/`pg_restore`) y preservar de forma coordinada el directorio de medios (`MEDIA_ROOT`), que contiene certificados.
2. Cifrar los respaldos, limitar accesos y almacenarlos fuera del servidor de aplicación; definir frecuencia, retención, RPO/RTO y responsable.
3. Para recuperar, aprovisionar PostgreSQL y almacenamiento, restaurar base y medios de un punto temporal compatible, instalar la misma versión de aplicación, configurar secretos por entorno y ejecutar verificaciones/migraciones pertinentes.
4. Probar periódicamente la restauración en un entorno aislado y validar relaciones y acceso a archivos antes de habilitar el servicio.

Estos pasos son recomendaciones operativas, no funcionalidades verificadas del proyecto.

## 7. Despliegue, requisitos e instalación

### Requisitos observables

- Python compatible con las dependencias fijadas en `requirements.txt` (Django 4.2.25).
- PostgreSQL accesible; driver `psycopg2-binary` incluido.
- Variables de entorno: `SECRET_KEY`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`. También se configuran `DB_HOST` (predeterminado `localhost`), `DB_PORT` (predeterminado `5432`), `DEBUG` (predeterminado `False`), `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS` y configuración opcional de Brevo/destinatarios.
- Directorios con permisos adecuados para medios y recursos estáticos.

### Instalación local

```bash
python -m venv .venv
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
# Crear .env local y establecer variables requeridas sin versionar secretos
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

En `DEBUG=False`, HTTPS, proxy y `ALLOWED_HOSTS` deben estar correctamente configurados. El comando `runserver` es solo para desarrollo. Para producción hace falta definir un servidor WSGI/ASGI adecuado, terminación TLS, entrega segura de estáticos/medios, gestión de secretos, registros, monitoreo y proceso de backup. Esos componentes y sus parámetros no están especificados en el repositorio; no se afirma un despliegue productivo existente.

La integración de correo utiliza API HTTPS de Brevo y requiere `BREVO_API_KEY`; destinatarios se configuran en entorno. `python manage.py check --deploy` puede ayudar a detectar configuraciones Django incompletas, pero no sustituye una revisión de infraestructura.
