# Sistema de control Beca Azul

## 1. Propósito y alcance

Aplicación web interna para administrar empresas proveedoras y sus trabajadores, registrar y revisar documentación de seguridad y salud en el trabajo, determinar la habilitación del personal y dar seguimiento a homologaciones y vencimientos.

El sistema permite consultar paneles y reportes de cumplimiento, gestionar usuarios según su rol y mantener información de certificados e incidencias. Los archivos PDF de certificados se almacenan como archivos multimedia y se relacionan con una empresa o un trabajador.

## 2. Tecnologías y arquitectura

- **Backend:** Python y Django 4.2.25.
- **Base de datos:** PostgreSQL, conectado mediante `psycopg2-binary`.
- **Configuración:** `django-environ` carga variables desde `.env`.
- **Interfaz:** plantillas Django, HTML, hojas de estilo CSS y JavaScript. Los estilos se encuentran bajo `static/css`; hay estilos Tailwind compilados y estilos propios por componentes y páginas.
- **Gráficos:** Chart.js incluido localmente en `static/vendor/chartjs` y utilizado por los scripts del panel.
- **Archivos:** almacenamiento local de Django bajo `media/` para los documentos cargados. Los PDFs de demostración fuente están bajo `pdf/`.
- **Dependencias adicionales:** `django-model-utils` para campos de fecha de creación/modificación y Pillow para manejo de imágenes.

El proyecto Django se configura en `beca_azul2026/`. Las aplicaciones de negocio están en `applications/`, las plantillas globales en `templates/` y los recursos estáticos en `static/`. La configuración define español de Perú, zona horaria `America/Lima` y uso de fechas con zona horaria.

Las rutas principales se distribuyen así:

- `/`: redirige a la pantalla correspondiente según autenticación y rol.
- `/users/`: inicio de sesión, perfil, contraseña y administración de usuarios.
- `/panel/`, `/reportes/`, `/empresas/`, `/trabajadores/`, `/certificados/` e `/incidencias/`: operaciones del sistema de control.
- `/admin/`: administración de Django.

## 3. Aplicaciones y estructura del código

### `applications.users`

Contiene el modelo de usuario propio (`User`), el gestor de usuarios, autenticación, perfil, cambio de contraseña, administración de cuentas y mixins de autorización. El correo electrónico es el identificador de inicio de sesión.

### `applications.control`

Contiene los modelos y la lógica de empresas, trabajadores, certificados, cursos obligatorios, incidencias e historial de estados. Sus vistas implementan paneles, reportes, administración de empresas y trabajadores, validación de documentación y operaciones específicas para cada rol. Los archivos de URL están en `applications/control/urls.py`.

La aplicación incluye la señal de eliminación de archivos asociados a certificados y el comando `preparar_demo_certificados`, que instala documentos PDF de ejemplo y establece estados de demostración.

### `applications.home`

Resuelve la entrada al sistema redirigiendo a cada usuario a su área inicial y contiene la vista de acceso denegado.

### Recursos transversales

- `beca_azul2026/settings.py`: aplicaciones instaladas, base de datos, idioma, correo, estáticos y archivos multimedia.
- `beca_azul2026/urls.py`: rutas raíz y asociación de rutas de las aplicaciones.
- `templates/`: páginas HTML y fragmentos reutilizables.
- `static/`: estilos, JavaScript y librerías locales.
- `fixtures/seed.json`: datos iniciales de demostración.
- `pdf/`: archivos PDF fuente usados por la preparación de la demo.

## 4. Roles y acceso

Los permisos se comprueban en las vistas y mixins del backend, además de ocultar o mostrar opciones en la interfaz. Los superusuarios de Django tienen bypass de las comprobaciones por rol definidas en los mixins.

| Rol | Alcance general |
|---|---|
| **Administrador** | Administración general de usuarios y acceso a las funciones administrativas que permiten las vistas. |
| **Beca Azul** | Gestión operativa central: empresas, trabajadores, revisiones y aprobaciones de certificados, homologaciones, incidencias y envío de reportes por correo. |
| **Usuario Planta** | Consulta del panel e información de empresas y trabajadores según los permisos de cada vista. |
| **Usuario Empresa** | Acceso limitado a su propia empresa y sus trabajadores; puede registrar y gestionar trabajadores de su empresa y aportar su documentación. |
| **Usuario Garita** | Consulta y búsqueda de trabajadores para verificar su información operativa, sin acceso a la administración completa. |

Las sesiones de Usuario Empresa requieren que exista una empresa asociada y que esta se encuentre activa. Las vistas de trabajadores aplican filtros por empresa para impedir que ese rol opere sobre registros de otras empresas.

## 5. Modelos y reglas de negocio

### Usuario (`applications.users.User`)

Extiende la autenticación de Django y los permisos (`PermissionsMixin`). Incluye correo único, nombres, apellidos, rol, género, fecha de nacimiento, teléfono y estados de actividad. Un Usuario Empresa debe tener empresa asignada; los demás roles no deben asociarse a una empresa mediante el formulario de gestión.

### Empresa

Registra nombre, RUC de 11 dígitos, correo, representante legal, actividad y estados de aprobación de SCTR y homologación. Mantiene certificados de empresa y trabajadores relacionados.

La empresa solo puede estar homologada si cuenta con certificados vigentes de homologación, SCTR pensión y SCTR salud, y ambos SCTR están aprobados. Cuando falta un archivo o vence un documento que sustentaba una aprobación, la lógica puede invalidar la aprobación y la homologación.

### Trabajador

Pertenece a una empresa y registra tipo y número de documento, nombres, apellidos, cargo, estado activo y validaciones individuales de SCTR pensión y salud. Para DNI se exige un número de ocho dígitos. No se permiten documentos duplicados entre trabajadores activos de la misma empresa.

El estado **habilitado efectivo** requiere conjuntamente:

1. Que el trabajador y su empresa estén activos.
2. Que la empresa esté homologada y tenga aprobados y vigentes los SCTR de pensión y salud.
3. Que los dos SCTR estén validados para el trabajador.
4. Que haya certificados de inducción y aptitud médica vigentes, con archivo disponible y validados.
5. Que cada curso obligatorio para ese trabajador tenga su certificado vigente, con archivo disponible y validado.

El historial conserva transiciones de estado del trabajador: habilitado, no habilitado o desactivado.

### Certificado

Puede pertenecer a una empresa o a un trabajador, según el tipo. Los tipos incluyen SCTR pensión, SCTR salud, homologación, inducción, aptitud médica y cursos. Registra fechas de emisión y vencimiento, archivo PDF y marca de validación.

Un certificado está vigente cuando existe su archivo y la fecha actual cae entre emisión y vencimiento. La validación vigente también exige que haya sido aprobado. La emisión no puede ser posterior al vencimiento. El sistema aplica restricciones para que los tipos de certificado tengan el propietario y, cuando corresponda, el curso adecuados.

Los PDFs cargados deben tener extensión `.pdf`, firma inicial `%PDF-` y tamaño máximo de 1 MB. Las rutas de almacenamiento se organizan por empresa, año y mes; los archivos demo usan `certificados/demo/`.

### Cursos obligatorios

Se configuran por trabajador, sin duplicar el mismo curso. Las categorías disponibles son trabajo en caliente, trabajo en altura, espacios confinados, trabajo eléctrico, excavación/perforación e izaje. Un curso obligatorio requiere un certificado válido para que el trabajador pueda quedar habilitado.

### Incidencias

Registran una descripción asociada a un trabajador y, opcionalmente, el usuario que la reportó. Su gestión está restringida al rol Beca Azul.

## 6. Flujos funcionales

### Empresas y homologación

Una empresa registra sus datos y carga certificados de SCTR pensión, SCTR salud y homologación. Beca Azul revisa los documentos y aprueba los SCTR. La homologación se puede aprobar únicamente cuando están disponibles y vigentes los tres certificados y ambos SCTR están aprobados. Las actualizaciones de documentos pueden retirar aprobaciones anteriores para exigir una nueva revisión.

### Registro y habilitación de trabajadores

Usuario Empresa registra trabajadores de su propia empresa y adjunta inicialmente documentación requerida de inducción y aptitud médica. Beca Azul administra la documentación y revisa las validaciones individuales y los cursos obligatorios. La habilitación se calcula con las condiciones anteriores; no es solo un campo manual.

### Panel y reportes

El panel presenta indicadores de empresas, trabajadores, habilitaciones, cumplimiento y vencimientos. La página de reportes ofrece cuatro vistas: certificados de trabajador por vencer, certificados empresariales por vencer, situación de trabajadores y resumen de empresas. Los reportes pueden imprimirse/exportarse desde el navegador como PDF. Beca Azul puede enviar por correo una versión HTML del reporte seleccionado.

## 7. Correos, configuración e instalación

### Notificaciones por correo

El envío usa `django-anymail` con el backend de Brevo por API HTTPS; no utiliza SMTP. La clave se obtiene de `BREVO_API_KEY` en `.env` mediante `django-environ`. El remitente predeterminado es `CheckID <notificaciones@envios.beca-azul.com>`.

- **Alta de trabajador:** envía una notificación con nombre, apellido, tipo y número de documento, cargo y empresa a `REPORTES_EMAILS`.
- **Habilitación:** al pasar de no habilitado a habilitado, envía los datos del trabajador —incluido tipo y número de documento—, empresa, cargo y estado. Los destinatarios son el correo de la empresa, `noreply.beca.azul@gmail.com` y el valor opcional `NOTIFICACIONES_EMAIL_ADICIONAL`.
- **Homologación:** al aprobarla, envía la empresa, RUC y los certificados empresariales —SCTR pensión, SCTR salud y homologación— con fechas y estado, a los mismos destinatarios de las notificaciones de habilitación.
- **Reporte:** Beca Azul envía el reporte seleccionado como HTML a `REPORTES_EMAILS`. Configura esa variable con una lista de destinatarios separados por comas.

Los correos de alta, habilitación y homologación tienen una versión HTML en tabla y un cuerpo de texto alternativo.

### Configuración e inicialización de un entorno

La configuración local requiere Python, las dependencias fijadas en `requirements.txt` y una instancia de PostgreSQL accesible. El archivo `.env` debe contener la clave secreta, el modo `DEBUG`, hosts permitidos, nombre/usuario/contraseña/host/puerto de la base de datos y, si se enviarán correos, `BREVO_API_KEY` y los destinatarios configurados arriba. Los valores concretos son propios del entorno y no forman parte de este documento.

El esquema de la base se administra mediante migraciones de Django. Para una base nueva, se generan las migraciones de las aplicaciones propias a partir de sus modelos y luego se aplican junto con las migraciones integradas de Django. Los datos de demostración se cargan desde `fixtures/seed.json`; después se ejecuta `preparar_demo_certificados`, que copia los PDF fuente de `pdf/` a las rutas demo y calcula fechas relativas a la fecha de ejecución.

El fixture actual contiene cinco empresas —Apple, Google, Microsoft, Amazon y Tesla— con cinco trabajadores cada una, cursos obligatorios y certificados demo. Al preparar la demo, Apple, Google y Microsoft quedan homologadas y diez trabajadores de esas tres empresas quedan con los documentos necesarios preparados para habilitarse. El comando es repetible para los archivos y estados demo; no crea ni reemplaza los registros principales del fixture.

La configuración multimedia usa `MEDIA_ROOT=media/` y `MEDIA_URL=/media/`. En modo `DEBUG`, Django sirve los archivos multimedia localmente; el acceso a certificados empresariales también está conectado a una vista con control de acceso.
