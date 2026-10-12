# Documentación del sistema

> Esta guía describe el sistema tal como se encuentra actualmente en el proyecto. Se basa en el código, las plantillas y la configuración presentes en el árbol de trabajo; no representa una revisión histórica de Git.
>
> Revisión del contenido: 12-10-2026. No se especifica una versión publicada o desplegada.

## 1. Introducción

El sistema es una aplicación web para administrar empresas y trabajadores, revisar sus documentos de seguridad y determinar su estado de habilitación. Centraliza información empresarial, certificados y requisitos laborales para facilitar su seguimiento y consulta.

Sus funciones principales incluyen la gestión de empresas, trabajadores y usuarios; la carga y validación de certificados; el control de vigencias y requisitos obligatorios; el registro de incidencias; paneles y reportes; y la búsqueda de trabajadores para consulta en garita.

## 2. Tecnologías utilizadas

| Área | Tecnología identificada en el proyecto |
|---|---|
| Lenguaje y backend | Python, Django 4.2.25 |
| Interfaz | Plantillas Django, HTML, Tailwind CSS, CSS y JavaScript |
| Gráficos | Chart.js |
| Base de datos | PostgreSQL (`psycopg2`) |
| Configuración | Variables de entorno mediante `django-environ` |
| Archivos | Almacenamiento de medios de Django, incluyendo certificados PDF |

Las versiones de dependencias Python están declaradas en `requirements.txt`.

## 3. Estructura del proyecto

| Carpeta/archivo | Responsabilidad |
|---|---|
| `beca_azul2026/` | Configuración del proyecto, rutas y aplicación WSGI. |
| `applications/users/` | Usuarios, autenticación, perfiles y controles de acceso por rol. |
| `applications/control/` | Empresas, trabajadores, certificados, incidencias, paneles y reportes. |
| `applications/home/` | Enrutamiento inicial de usuarios y respuesta de acceso denegado. |
| `templates/` | Páginas y componentes HTML organizados por módulo. |
| `static/` | CSS, JavaScript, recursos gráficos, fuentes y librerías del frontend. |
| `media/` | Archivos cargados por el sistema; los certificados se agrupan por empresa y fecha. |
| `fixtures/` | Fixtures de datos configurados para el proyecto. |
| `manage.py` | Utilidad de administración de Django. |

## 4. Módulos y funcionalidades

- **Empresas:** alta, consulta, actualización y desactivación; administración de certificados de SCTR pensión, SCTR salud y homologación; visualización de trabajadores y usuarios asociados.
- **Trabajadores:** registro y consulta de trabajadores vinculados a empresas, búsqueda, detalle, actualización y control de estado activo. La aplicación mantiene un historial de estados.
- **Documentación y cumplimiento:** carga de certificados de empresa y trabajador, validación, seguimiento de emisión/vencimiento y aviso de documentos próximos a vencer. Se contemplan homologación, SCTR, inducción, aptitud médica y cursos de seguridad: trabajos en caliente, altura, espacios confinados, eléctricos, excavación e izaje.
- **Habilitación:** el estado se calcula considerando actividad de empresa y trabajador, homologación y SCTR empresarial aprobados y vigentes, validaciones SCTR del trabajador y certificados vigentes de inducción, aptitud médica y cursos obligatorios configurados. El código contempla notificaciones por correo cuando un trabajador pasa a habilitado.
- **Incidencias:** registro, consulta y mantenimiento de incidencias ligadas a trabajadores.
- **Usuarios:** inicio/cierre de sesión, perfil, cambio y restablecimiento de contraseña, alta y gestión de cuentas.
- **Paneles y reportes:** indicadores y gráficos de empresas, trabajadores y cumplimiento. El código incluye vistas de reportes y configuración SMTP para el envío por correo.
- **Garita:** búsqueda de trabajadores para consultar resultados de habilitación, con acceso de consulta según el rol.

Los cursos son configurables como obligatorios por trabajador. Las reglas de validación impiden aprobar documentación que no esté vigente o cuyo archivo no esté disponible.

## 5. Base de datos

El motor definido en la configuración es **PostgreSQL**. El acceso se parametriza mediante variables de entorno.

| Modelo principal | Uso y relaciones |
|---|---|
| `Empresa` | Identificación y estado de la empresa, aprobaciones de SCTR y homologación. Se relaciona con trabajadores, certificados y usuarios. |
| `Trabajador` | Datos de identidad y cargo; pertenece a una empresa y se relaciona con certificados, cursos obligatorios, incidencias e historial de estados. |
| `Certificado` | Tipo, archivo, fechas y validación. Según el tipo pertenece a una empresa o a un trabajador; los certificados de cursos especifican además el curso. |
| `CursoObligatorio` | Cursos requeridos definidos para un trabajador. |
| `Incidencia` | Descripción asociada a un trabajador y, opcionalmente, al usuario que la registró. |
| `EstadoTrabajadorHistorico` | Registro temporal de los estados habilitado, no habilitado o desactivado. |
| `User` | Cuenta autenticable con rol y asociación a empresa cuando corresponde. |

Las relaciones principales son empresa–trabajadores, empresa/trabajador–certificados y trabajador–cursos/incidencias/historial. El modelo declara restricciones de integridad y unicidad para varios registros.

## 6. Usuarios y permisos

El modelo define los siguientes roles:

| Rol | Alcance general observado en los controles de acceso |
|---|---|
| Administrador | Gestión general y gestión de usuarios. |
| Beca Azul | Administración operativa de empresas, trabajadores, validaciones e incidencias; gestión de usuarios según los permisos definidos. |
| Usuario Planta | Consulta de panel, empresas y trabajadores en las vistas permitidas. |
| Usuario Empresa | Debe estar asociado a una empresa; consulta y operaciones limitadas a los datos de esa empresa. |
| Usuario Garita | Consulta y búsqueda de trabajadores. |

Las vistas verifican sesión y rol, y algunas operaciones tienen restricciones adicionales. Los superusuarios de Django reciben acceso privilegiado en los controles comunes. La asociación de usuario de empresa requiere una empresa y el acceso se bloquea si esta está inactiva.

## 7. Arquitectura del sistema

La aplicación utiliza el patrón web de Django con renderizado en servidor. Las URL dirigen solicitudes a vistas; estas aplican permisos, consultan o actualizan modelos mediante el ORM y renderizan plantillas. El navegador recibe HTML y recursos estáticos (CSS y JavaScript). PostgreSQL almacena los datos estructurados y `media/` almacena archivos. La configuración SMTP se utiliza para las notificaciones y reportes que envía la aplicación.

## 8. Instalación y ejecución

Requisitos identificados: Python compatible con las dependencias y PostgreSQL. Django está fijado en la versión 4.2.25. La instalación de dependencias, configuración de entorno y comandos de ejecución se describen en el [README](README.md). Las credenciales y la configuración específica deben proporcionarse fuera de la documentación y mantenerse privadas.

## 9. Seguridad

- Autenticación de Django con correo como identificador y validadores de contraseña configurados.
- Protección de vistas mediante sesión y permisos por rol; usuarios de empresa quedan limitados a su empresa activa.
- Middleware de sesiones, CSRF, seguridad y protección contra clickjacking.
- Clave secreta, base de datos y correo configurados mediante variables de entorno.
- Con `DEBUG` desactivado, se configuran redirección HTTPS, HSTS, cookies seguras de sesión/CSRF y `X-Frame-Options: DENY`.
- Los formularios de certificados verifican la extensión PDF, el tamaño máximo de 1 MB y la firma del archivo. Las vistas de descarga de certificados requieren autenticación y aplican restricciones por rol y empresa.

La seguridad final también depende de mantener las variables y servicios del entorno de producción correctamente configurados.

## 10. Observaciones

- La base de datos debe ser PostgreSQL; las funciones de correo requieren una configuración SMTP válida.
- En modo de desarrollo Django sirve los medios según la configuración local. Para producción se debe configurar el servicio que servirá los archivos estáticos y medios.
- El README contiene instrucciones generales de instalación y ejecución; la configuración concreta depende del entorno de despliegue.
- El repositorio contiene cambios locales respecto de su último commit; este documento describe el contenido actual del proyecto y no afirma que esos cambios estén publicados o desplegados.
- El estado de despliegue, respaldos y operación productiva no puede verificarse únicamente con el código disponible y debe confirmarse con el responsable del sistema.
