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

### Presentación de `/empresas/`

- Para `PLANTA`, `/empresas/` muestra la consulta de empresas y trabajadores autorizados, con filtro por empresa, búsqueda de trabajador, DNI, estado y acceso al detalle.
- Para `ADMINISTRADOR` y `BECA_AZUL`, `/empresas/` mantiene el listado administrativo de empresas con RUC, estado, trabajadores y acciones.
- La tabla utiliza las clases reutilizables `.app-table-wrap` y `.app-table`, definidas en `static/css/styles/components/tables.css`, con columnas adaptables al contenido y comportamiento responsive.
- La presentación visual mantiene la información y rutas existentes; los cambios de esta vista son de composición, tipografía, colores, bordes, iconos y comportamiento responsive.

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

### Empresa

Incluye nombre, RUC único, `habilitado` y `activo`. No contiene datos de
contacto. No se puede eliminar una empresa que tenga relaciones protegidas.

### Trabajador

Pertenece a una empresa y contiene tipo de documento, DNI, nombres, apellidos,
cargo, `habilitado` y `activo`. El DNI/documento activo debe ser único dentro de
la empresa. Los requisitos documentales no se almacenan como estados en el
trabajador; se gestionan mediante la relación `certificados`.

 Al registrar un trabajador desde el portal de empresa se deben guardar únicamente
 sus datos básicos. Los certificados y cursos se agregan posteriormente desde el
 detalle del trabajador; SCTR, Inducción y Aptitud médica admiten un certificado
 por trabajador y Cursos admite varios.

### Certificado

Pertenece a un trabajador y registra `tipo`, fecha de emisión, fecha de
vencimiento y archivo PDF. Los tipos disponibles son `SCTR`, `INDUCCION`,
`CURSOS` y `APTITUD_MEDICA`. SCTR, Inducción y Aptitud médica admiten un solo
certificado por trabajador. Cursos admite varios certificados, uno por cada
`CategoriaCurso`.

`CategoriaCurso` contiene el nombre y el indicador `activo` de cada categoría.
Las categorías se crean, editan o desactivan desde Django Admin. La combinación
trabajador/categoría es única para los certificados de cursos. Las fechas de
vencimiento no pueden ser anteriores a las fechas de emisión. El estado se
calcula como `Vigente`, `Próximo a vencer` (30 días) o `Vencido`.

Los archivos se almacenan bajo `media/certificados/`, se validan como PDF y se
eliminan al reemplazar o eliminar el certificado. El estado `habilitado` del
trabajador es independiente del estado de los certificados.

## Permisos por rol

| Rol | Usuarios | Empresas | Trabajadores |
|---|---|---|---|
| Administrador | Gestiona usuarios de administración | Solo lectura | Solo lectura; puede ver y descargar certificados |
| Beca Azul | Gestiona usuarios empresa | CRUD | CRUD de trabajadores; puede ver y descargar certificados |
| Usuario Empresa | Sin acceso | Sin acceso | CRUD solo de su empresa; puede cargar, editar, reemplazar y eliminar certificados |
| Planta | Consulta de usuarios, sin crear/editar/eliminar ni activar/desactivar | Sin acceso | Consulta trabajadores y certificados |
| Garita | Sin acceso | Sin acceso | Sin acceso a paneles |

Las restricciones se implementan principalmente en
`applications/users/mixins.py` y en las vistas de `applications/users/` y
`applications/control/`. La autorización debe validarse siempre en backend;
ocultar botones en las plantillas no es suficiente.

### Restricciones específicas de certificados

- Solo `USUARIO_EMPRESA` puede crear, editar, reemplazar o eliminar certificados
  desde la aplicación, siempre dentro de su propia empresa.
- `ADMINISTRADOR`, `BECA_AZUL` y `PLANTA` pueden visualizar y descargar los
  certificados desde el detalle del trabajador.
- Las categorías de cursos solo se administran desde Django Admin.
- Estas restricciones se aplican tanto ocultando acciones en las plantillas como
  bloqueando las vistas mediante mixins y filtros por empresa.

### Detalle del trabajador

- El detalle muestra siempre filas para SCTR, Inducción, Aptitud médica y Cursos.
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
categorías de cursos, 43 certificados y cinco usuarios, uno por rol. Cada
trabajador de prueba tiene Inducción y Aptitud médica; el primer trabajador
también tiene SCTR y dos categorías de cursos. Las rutas de archivo de la
fixture son rutas de demostración y requieren que los PDFs existan en `media/`
para poder abrirlos.

En el entorno local usado para la última validación se utilizan Python `3.12.0` y
Django `4.2.25`. `manage.py check`, `makemigrations --check`, `manage.py test` y
`git diff --check` finalizaron correctamente. Las pruebas ejecutaron 3 casos y
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
