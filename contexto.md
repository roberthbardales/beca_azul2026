# Contexto del proyecto

## Resumen

`beca_azul2026` es una aplicación web para gestionar empresas, trabajadores,
certificados y usuarios con permisos diferenciados por rol. Está construida
con Django 4.2, plantillas HTML del lado del servidor y PostgreSQL.

## Stack técnico

- Python `3.12.0` y Django `4.2.25`.
- PostgreSQL mediante `psycopg2-binary`.
- Configuración por variables de entorno con `django-environ`.
- Autenticación con un modelo de usuario propio (`users.User`) cuyo identificador
  es el correo electrónico.
- Archivos estáticos en `static/` y archivos subidos en `media/`.
- Imágenes mediante Pillow.
- Plantillas Django ubicadas en `templates/`.
- Gráficas del dashboard con Chart.js `4.4.7`, distribuido localmente desde
  `static/vendor/chartjs/` para no depender de un CDN.

## Estructura principal

```text
beca_azul2026/
├── applications/
│   ├── home/       # Página inicial
│   ├── users/      # Usuarios, autenticación, perfiles y permisos
│   └── control/    # Empresas, trabajadores y certificados
├── beca_azul2026/ # Configuración global del proyecto
├── templates/     # Plantillas HTML y componentes compartidos
│   ├── include/   # Layout, navegación y scripts compartidos
│   └── users/dashboard/ # Parciales del dashboard de usuarios
├── static/        # Recursos estáticos
│   ├── js/pages/dashboard.js # Inicialización de las gráficas
│   └── vendor/chartjs/       # Distribución local de Chart.js
├── media/         # Archivos cargados por usuarios
├── fixtures/      # Datos iniciales
├── manage.py
├── requirements.txt
└── .env           # Configuración local, no debe versionarse
```

## Rutas principales

- `/`: inicio.
- `/panel/`: dashboard general para roles autorizados.
- `/reportes/`: reportes de vencimientos, trabajadores y empresas para roles autorizados.
- `/users/`: login, registro, dashboard, perfil, cambio y restablecimiento de
  contraseña, además de la gestión de usuarios.
- `/empresas/`: listado y administración de empresas.
- `/empresas/<id>/`: detalle de empresa para Administrador, Beca Azul y Planta; el
  Usuario Empresa solo puede consultar la empresa asociada.
- `/empresas/<id>/sctr/editar/`: registro o consulta del SCTR de la empresa.
- `/empresas/<id>/homologacion/editar/`: registro o consulta del certificado de homologación de la empresa.
- `/trabajadores/`: listado, búsqueda y administración de trabajadores.
- `/empresas/<id>/trabajadores/`: listado de trabajadores de una empresa para el rol
  `GARITA`; permite consulta de la lista, sin acciones de detalle o edición.
- `/trabajadores/`: listado único de trabajadores. Los usuarios empresa ven solo
  los trabajadores de su empresa; los roles administrativos pueden filtrar por empresa.
- `/trabajadores/empresa/crear/`: creación de trabajadores exclusivamente para
  usuarios con rol `USUARIO_EMPRESA`.
- `/certificados/`: gestión de certificados.
- `/admin/`: administración nativa de Django.

Las rutas se registran en `beca_azul2026/urls.py`,
`applications/users/urls.py` y `applications/control/urls.py`.

La gestión de usuarios usa la ruta `/users/gestion/`; `/usuarios/gestion/` no es
una ruta válida del proyecto.

### Presentación de `/empresas/`

- `/empresas/` muestra el listado común de empresas para Administrador, Beca Azul y Planta, con búsqueda, filtro de estado y filtro de homologación.
- Administrador y Beca Azul pueden crear y administrar empresas; Planta solo puede consultar.
- El listado muestra RUC, estado del SCTR mediante icono, fechas de emisión y vencimiento, estado del certificado de homologación mediante icono, estado, trabajadores, homologación y acceso al detalle.
- El detalle muestra acciones de administración únicamente para Administrador y Beca Azul.
- La tabla utiliza las clases reutilizables `.app-table-wrap` y `.app-table`, definidas en `static/css/styles/components/tables.css`, con columnas adaptables al contenido y comportamiento responsive.
- La presentación visual mantiene la información y rutas existentes; los cambios de esta vista son de composición, tipografía, colores, bordes, iconos y comportamiento responsive.
- El detalle de empresa utiliza un panel compacto tipo tablero: encabezado con identidad y acciones, métricas horizontales y resumen documental del SCTR y la homologación.
- El badge de homologación usa iconos de estado y colores semánticos suaves. Para usuarios empresa se muestra en el área de acciones del encabezado.
- El detalle `/empresas/<id>/` permite `ADMINISTRADOR`, `BECA_AZUL`, `PLANTA` y `USUARIO_EMPRESA`. Usuario Empresa queda restringido por backend a su empresa asignada; Planta tiene acceso de solo lectura.
- Los formularios de SCTR y homologación usan una tarjeta documental compacta, separan el archivo actual de la carga de reemplazo y ofrecen un enlace `Ver PDF` cuando existe un archivo.

### Dashboard `/panel/`

- `applications.control.views.DashboardView` calcula las métricas y entrega los
  datos de las gráficas mediante `dashboard_charts`.
- `templates/users/dashboard.html` ensambla los parciales ubicados en
  `templates/users/dashboard/` y serializa los datos con `json_script`.
- Las cuatro tarjetas superiores resumen empresas homologadas, trabajadores
  autorizados, certificados próximos a vencer y certificados vencidos. Tienen
  dimensiones compactas y se adaptan a una sola columna en móviles.
- La gráfica circular clasifica certificados vigentes, próximos a vencer y
  vencidos. Los certificados sin vencimiento se excluyen de la dona y no se
  consideran vigentes.
- La gráfica de barras presenta las diez empresas con más trabajadores. Los
  trabajadores de las empresas restantes se agrupan bajo `Otros`.
- La gráfica lineal presenta las altas de trabajadores durante los últimos
  siete días.
- `static/js/pages/dashboard.js` valida el JSON y la presencia de cada elemento
  antes de crear las gráficas. Si Chart.js o los datos no están disponibles,
  presenta un mensaje dentro del contenedor en lugar de dejarlo vacío.
- El topbar tiene `z-index: 50` definido directamente en
  `static/css/styles/layout/topbar.css`, por lo que permanece por encima de los
  canvas durante el desplazamiento.
- Las pruebas del contexto y de la agrupación de datos se encuentran en
  `applications/control/tests/test_dashboard.py`.

## Sistema visual reutilizable

Los templates deben reutilizar las clases propias del sistema en lugar de repetir
combinaciones extensas de utilidades Tailwind.

### Botones

Las clases están definidas en `static/css/styles/components/buttons.css`:

- `.btn`: base común para botones y enlaces de acción.
- `.btn-primary`: acción principal, azul `#1557C0`.
- `.btn-secondary`: acción secundaria, azul `#1D7BF2`.
- `.btn-tertiary`: acción positiva o de consulta, verde `#53AC4D`.
- `.btn-quaternary`: acción alternativa, naranja `#FF7A29`.
- `.btn-quinary`: acción destructiva, rojo `#E53935`.
- `.btn-sm`: variante compacta.
- `.btn-icon`: botón cuadrado para acciones con icono.
- `.pagination-btn`: controles de paginación.

### Tablas

Las clases están definidas en `static/css/styles/components/tables.css`:

- `.app-table-wrap`: contenedor común con borde, sombra y radio `.4rem`.
- `.app-table`: tabla con encabezado, separadores, tipografía y hover unificados.

Todas las tablas de listados y detalles principales de usuarios, empresas y
trabajadores deben usar estas clases. La vista `/empresas/` conserva las clases
especializadas de trabajadores autorizados, pero sus tablas con `.app-table`
siguen el mismo estilo visual que `/trabajadores/`.

### Formularios

- `.form-control`, definido en `static/css/styles/components/forms.css`, unifica
  inputs y selects con el mismo borde, altura, foco y tipografía.
- `.worker-form-card`, definido en `static/css/styles/pages/control.css`, controla
  la tarjeta visual del formulario de creación/edición de trabajadores.

### Toasts

- El componente global está en `templates/include/messages.html` y se incluye desde
  `templates/base.html`.
- Usa `django.contrib.messages` y soporta `success`, `error`, `warning` e `info`.
- Los toast aparecen arriba a la derecha, debajo del topbar para usuarios autenticados,
  incluyen cierre manual y desaparecen automáticamente después de cuatro segundos.
- Los mensajes de trabajadores tienen colores específicos: creación verde,
  actualización azul, activación/desactivación naranja y eliminación rojo.
- El comportamiento vanilla está integrado en `templates/include/layout_scripts.html` y
  los estilos en `static/css/styles/components/toasts.css`.

### Paleta

Los colores globales están centralizados en
`static/css/styles/variables.css`. Los colores semánticos principales son:

| Token | Color | Uso |
|---|---|---|
| `--primary-600` | `#1557C0` | Acción principal |
| `--secondary-500` | `#1D7BF2` | Acción secundaria |
| `--tertiary-500` | `#53AC4D` | Acción positiva |
| `--quaternary-500` | `#FF7A29` | Acción alternativa |
| `--quinary-500` | `#E53935` | Acción destructiva |

Los cambios de color deben hacerse preferentemente en `variables.css`, no
directamente dentro de cada template.

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

Los códigos numéricos de rol son valores establecidos del sistema y se mantienen
estables. Las plantillas pueden utilizarlos directamente para controlar la
visualización de acciones; cualquier cambio de estos códigos requiere actualizar
también las plantillas relacionadas.

### Empresa

Incluye nombre, RUC único, `homologado` y `activo`. La homologación se actualiza
automáticamente según el estado de sus trabajadores. No contiene datos de
contacto. No se puede eliminar una empresa que tenga relaciones protegidas.

### Trabajador

Pertenece a una empresa y contiene tipo de documento, DNI, nombres, apellidos,
cargo, `habilitado` y `activo`. El DNI/documento activo debe ser único dentro de
la empresa. Los requisitos documentales no se almacenan como estados en el
trabajador; se gestionan mediante la relación `certificados`.

 Al registrar un trabajador desde el portal de empresa se guardan sus datos básicos,
 un certificado obligatorio de Inducción y uno obligatorio de Aptitud médica. Los
 cursos son opcionales durante la creación; si se completa un curso, debe incluir
 archivo y fechas. Inducción y Aptitud médica admiten un certificado por trabajador
 y Cursos admite varios, uno por categoría. El SCTR y la homologación pertenecen a
 la empresa y existe un único certificado de cada tipo por empresa.

### Certificado

Pertenece a una empresa o a un trabajador y registra `tipo`, fecha de emisión,
fecha de vencimiento y archivo PDF. Los tipos disponibles son `SCTR`,
`HOMOLOGACION`, `INDUCCION`, `CURSOS` y `APTITUD_MEDICA`. SCTR y Homologación
admiten un solo certificado por empresa. Inducción y Aptitud médica admiten un
solo certificado por trabajador.
Cursos admite varios certificados, uno por cada categoría definida en `CursoTipo`.

Las categorías de cursos se definen mediante `CursoTipo` (`TextChoices`) en
`applications/control/models.py`; no existe un modelo `CategoriaCurso`. La
combinación trabajador/categoría es única para los certificados de cursos. Las fechas de
vencimiento no pueden ser anteriores a las fechas de emisión. El estado se
calcula como `Vigente`, `Próximo a vencer` (30 días) o `Vencido`.

Los archivos se almacenan bajo `media/certificados/`, se validan como PDF y se
eliminan al reemplazar o eliminar el certificado. El estado `habilitado` del
trabajador es independiente del estado de los certificados.

## Permisos por rol

| Rol | Usuarios | Empresas | Trabajadores |
|---|---|---|---|
| Administrador | Ve y gestiona usuarios permitidos, incluido crear usuarios | CRUD, igual que Beca Azul | Solo lectura; puede ver y descargar certificados |
| Beca Azul | Gestiona usuarios Planta, Empresa y Garita | CRUD | CRUD de trabajadores; puede ver y descargar certificados |
| Usuario Empresa | Sin acceso | Consulta de su empresa y gestión de su SCTR y homologación | CRUD solo de su empresa; puede cargar, editar, reemplazar y eliminar certificados |
| Planta | Consulta de usuarios, sin crear/editar/eliminar ni activar/desactivar | Solo lectura | Consulta trabajadores y certificados |
| Garita | Sin acceso | Búsqueda de empresas y consulta por empresa | Listas por empresa; sin detalle individual ni modificaciones |

Las restricciones se implementan principalmente en
`applications/users/mixins.py` y en las vistas de `applications/users/` y
`applications/control/`. La autorización debe validarse siempre en backend;
ocultar botones en las plantillas no es suficiente.

### Consulta de trabajadores para Garita

- Garita puede buscar empresas en `/empresas/buscar/`.
- La tabla muestra la columna `Acciones` únicamente para Garita, con un botón
  compacto `Ver lista` que dirige a `/empresas/<id>/trabajadores/`.
- La lista por empresa reutiliza `templates/control/trabajadores/lista_empresa.html`
  y muestra trabajadores activos e inactivos.
- En esa lista Garita no ve la columna `Acciones`.
- El acceso directo a `/trabajadores/<id>/` devuelve `403 Forbidden` para Garita.

### Gestión de usuarios

- En `/users/gestion/`, los usuarios con rol `BECA_AZUL` visualizan usuarios de
  tipo `PLANTA`, `USUARIO_EMPRESA` y `GARITA`.
- En `/users/gestion/`, `ADMINISTRADOR` puede consultar y gestionar usuarios de
  todos los roles permitidos por las vistas, incluido crear usuarios.
- El filtro `usuarios-rol` muestra únicamente `PLANTA`, `USUARIO_EMPRESA` y
  `GARITA` para evitar seleccionar `BECA_AZUL` o `ADMINISTRADOR`.
- En `/users/gestion/crear/`, el combo `id_role` de un usuario Beca Azul permite
  crear únicamente usuarios Planta, Empresa y Garita.
- `ADMINISTRADOR` no se ofrece como tipo seleccionable y `superuser` no es un
  rol del modelo, sino una condición separada (`is_superuser`); ninguno puede
  ser creado desde este formulario.

### Reportes

- `/reportes/` está disponible para `ADMINISTRADOR`, `BECA_AZUL`, `PLANTA` y
  `USUARIO_EMPRESA`.
- Usuario Empresa recibe únicamente información de su empresa y sus trabajadores.
- Garita no tiene acceso a reportes ni al dashboard.

### Restricciones específicas de certificados

- Solo `USUARIO_EMPRESA` puede crear, editar, reemplazar o eliminar certificados
  desde la aplicación, siempre dentro de su propia empresa.
- `ADMINISTRADOR`, `BECA_AZUL` y `PLANTA` pueden visualizar y descargar los
  certificados desde el detalle del trabajador.
- Las categorías de cursos se mantienen en código mediante `CursoTipo`; no se
  administran desde Django Admin.
- Estas restricciones se aplican tanto ocultando acciones en las plantillas como
  bloqueando las vistas mediante mixins y filtros por empresa.

### Detalle de empresa y trabajador

- El detalle de empresa muestra métricas, el estado independiente `Empresa.homologado` y el estado/vigencia del SCTR y la homologación, sin listar trabajadores.
  El usuario empresa puede acceder únicamente a su propia empresa y consultar o editar ambos certificados desde
  `/empresas/<id>/sctr/editar/` y `/empresas/<id>/homologacion/editar/`. El detalle del trabajador muestra filas para
  Inducción, Aptitud médica y Cursos.
- Los cursos registrados aparecen como filas adicionales; si no existe ninguno,
  se muestra una fila vacía con la acción para añadirlo.
- Los certificados faltantes se muestran como filas vacías con una acción `Añadir`
  para crear el tipo correspondiente.
- Solo el usuario empresa ve las acciones de añadir, editar y eliminar; el resto
  de roles puede consultar y descargar los certificados.

### Restricciones específicas de Planta

- `PLANTA` puede acceder al listado y detalle de usuarios en modo consulta.
- `PLANTA` no puede crear, editar, eliminar, restablecer contraseñas ni
  activar/desactivar usuarios.
- `PLANTA` no puede activar/desactivar trabajadores ni modificar certificados.
- Todos los usuarios autenticados pueden utilizar `/trabajadores/buscar/`. Los
  usuarios de empresa se limitan a trabajadores de su propia empresa.
- `Usuario Empresa` utiliza `/trabajadores/` y queda limitado automáticamente a su
  empresa. El botón de creación solo aparece para este rol; los roles administrativos
  consultan el mismo template sin esa acción.

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
py -3.12 -m venv venv
venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata fixtures/seed.json
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
trabajadores y permisos por roles. El dashboard está implementado con métricas,
tres gráficas Chart.js, trabajadores recientes y certificados por vencer. Sus
componentes están divididos en parciales y Chart.js se sirve localmente. Los
scripts comunes del layout se cargan desde `templates/include/layout_scripts.html`.
El fixture `fixtures/seed.json` contiene 10 empresas, 20 trabajadores, tres
categorías de cursos, 43 certificados y 14 usuarios: un administrador, un
usuario Beca Azul, un usuario Planta, un usuario Garita y diez usuarios de
empresa, asociados a las empresas de prueba. En el entorno de desarrollo, todos
los usuarios del fixture utilizan la contraseña `admin`; debe cambiarse al
cargar los datos en cualquier entorno compartido o de producción. Cada
trabajador de prueba tiene Inducción y Aptitud médica; las empresas pueden
tener SCTR y los trabajadores tienen además categorías de cursos. Las rutas de
archivo de la fixture son rutas de demostración y requieren que los PDFs existan
en `media/` para poder abrirlos.

En el entorno local usado para la última validación se utilizan Python `3.12.0` y
Django `4.2.25`. `manage.py check`, `manage.py test applications.control.tests`
y `git diff --check` finalizaron correctamente. Las pruebas ejecutaron 17 casos y
terminaron en estado OK. Si `psycopg2-binary` presenta un error de módulo nativo,
reinstalarlo dentro del entorno virtual con:

```bash
python -m pip install --force-reinstall --no-cache-dir psycopg2-binary==2.9.9
```

`check --deploy` mantiene advertencias esperables para desarrollo: `DEBUG=True`,
HTTPS no forzado y cookies seguras desactivadas. Deben configurarse antes de
publicar en producción.

Pendientes documentados en `mejoras.md`:

- Exportación e importación masiva en CSV/Excel/PDF.
- Historial de cambios.
- Flujo guiado para vincular o crear el usuario de una empresa.
- Vista previa de documentos PDF.
- Alertas de DNI duplicado entre empresas.
- Ampliación de pruebas automatizadas para reglas de negocio.

Correcciones técnicas pendientes documentadas en `corregir.md`:

- Revisar y unificar los permisos de las vistas administrativas de trabajadores
  y certificados.
- Hacer seguro el reemplazo de certificados: conservar el archivo anterior si
  falla el guardado del nuevo y usar `transaction.atomic()`.
- Validar conflictos de categoría antes de cambiar un certificado de curso.
- Sustituir comparaciones literales de roles por las constantes de `User`.
- Reducir la lógica repetida de las listas de trabajadores.
- Revisar la cantidad de consultas independientes del dashboard cuando crezca
  el volumen de datos.
- Definir el tratamiento de trabajadores inactivos al editar o agregar
  certificados.
- Dividir `applications/control/views.py` si continúa creciendo.

El registro público `/users/register/` solo permite crear usuarios con rol
`USUARIO_EMPRESA`; los roles privilegiados se gestionan desde el módulo protegido
de usuarios.

## Archivos de referencia

- `README.md`: actualmente contiene solo el nombre del proyecto.
- `avance.md`: detalle de permisos implementados y verificaciones realizadas.
- `mejoras.md`: plan de mejoras y funcionalidades implementadas.
- `corregir.md`: correcciones técnicas pendientes, ordenadas por prioridad.
- `beca_azul2026/settings.py`: configuración, base de datos y seguridad.
- `applications/users/models.py`: usuarios y roles.
- `applications/control/models.py`: empresas, trabajadores y certificados.
