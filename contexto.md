# Contexto del proyecto

## Resumen

`beca_azul2026` es una aplicación Django para administrar empresas,
trabajadores, certificados, incidencias y usuarios con permisos por rol. Usa
plantillas HTML del lado del servidor y PostgreSQL.

## Stack y estructura

- Python 3.12 y Django 4.2.
- PostgreSQL con `psycopg2-binary`.
- Usuario personalizado `applications.users.models.User`, autenticado por correo.
- Archivos subidos en `media/` y recursos estáticos en `static/`.
- Chart.js local para las gráficas del dashboard.
- `applications/users/`: autenticación, usuarios y permisos.
- `applications/control/`: empresas, trabajadores, certificados e incidencias.
- `templates/`: interfaz HTML.

## Rutas principales

- `/`: inicio.
- `/panel/`: dashboard para Administrador, Beca Azul y Planta.
- `/reportes/`: reportes para Administrador, Beca Azul, Planta y Usuario Empresa.
- `/users/`: autenticación, perfil y gestión protegida de usuarios.
- `/empresas/`: consulta y administración de empresas.
- `/trabajadores/`: listado y búsqueda de trabajadores.
- `/trabajadores/<id>/`: detalle general del trabajador.
- `/trabajadores/empresa/<id>/`: detalle del trabajador para su empresa.
- `/certificados/crear/`, `/certificados/<id>/editar/` y `/certificados/<id>/eliminar/`:
  creación, edición y eliminación de certificados según el rol.
- `/admin/`: administración nativa de Django.

La creación pública de usuarios está deshabilitada. La gestión se realiza desde
`/users/gestion/`.

## Usuarios y roles

| Código | Rol |
|---|---|
| `0` | Administrador |
| `1` | Beca Azul |
| `2` | Usuario Planta |
| `3` | Usuario Empresa |
| `4` | Usuario Garita |

Un superusuario de Django puede superar los mixins basados únicamente en rol.
Esto es independiente del valor guardado en `User.role`.

## Modelo de datos

### Empresa

Una empresa tiene nombre, RUC, correo, fecha de fundación, estado activo y
estado de homologación. También puede tener un certificado SCTR y uno de
homologación. La eliminación está protegida cuando existen relaciones.

### Trabajador

Pertenece a una empresa y registra documento, nombres, apellidos y cargo.
También contiene:

- `activo`: controla si el registro está activo.
- `habilitado`: estado operativo, independiente de `activo`.
- `sctr`: aprobación del SCTR del trabajador por Beca Azul.

Desactivar un trabajador también lo deja no habilitado. Reactivarlo no cambia
automáticamente su estado de habilitación.

### Certificados

Los certificados registran tipo, fechas y archivo PDF. Los certificados de
Inducción y Aptitud médica pertenecen al trabajador y son independientes de los
cursos. Los cursos permiten un certificado por categoría y trabajador.

Los seis cursos fijos son:

- Caliente (`CALIENTE`).
- Altura (`ALTURA`).
- Espacio confinado (`ESPACIO_CONFINADO`).
- Eléctrico (`ELECTRICO`).
- Excavación (`EXCAVACION`).
- Izaje (`IZAJE`).

La fecha de vencimiento no puede ser anterior a la fecha de emisión. El estado
del certificado puede ser `Vigente`, `Próximo a vencer` o `Vencido`.

### Cursos obligatorios por trabajador

`CursoObligatorio` relaciona individualmente un trabajador con cualquiera de
los seis cursos fijos. No crea ni modifica certificados.

- Los seis cursos comienzan como no obligatorios si no existe una relación.
- Beca Azul puede activar o desactivar cada curso manualmente desde el detalle.
- El cambio se guarda mediante `POST` inmediatamente.
- Inducción y Aptitud médica no usan esta configuración y no fueron modificados.
- Un curso puede ser obligatorio aunque todavía no tenga PDF.
- Si es obligatorio y no existe constancia, el detalle muestra `Falta subir`.
- Si ya existe una constancia, conserva sus fechas y estado documental.
- Al desactivar la obligación, la constancia y sus datos se conservan.
- No existe todavía cálculo general de cumplimiento ni historial de cambios.

La ruta de configuración es:

`POST /trabajadores/<id>/cursos/<curso>/obligatorio/`

Solo acepta los seis valores definidos en `CursoTipo` y no permite modificar
trabajadores inactivos.

## Certificados y carga de archivos

Usuario Empresa carga y administra los certificados de su empresa y sus
trabajadores. Puede cargar cursos aunque todavía no sean obligatorios. Beca Azul,
Administrador y Planta pueden consultar los certificados desde los detalles
permitidos, sin gestionar su contenido mediante las vistas normales.

Antes de mostrar o descargar documentos de empresa se comprueba que el archivo
físico exista en el storage. Un registro sin archivo físico puede conservarse
para permitir reemplazarlo.

## Estados y homologación

La habilitación del trabajador se alterna desde un botón protegido de Beca Azul.
El SCTR del trabajador es independiente del certificado SCTR de su empresa.

Beca Azul puede homologar una empresa solo si el SCTR y la homologación tienen
archivo físico y ambos están vigentes. Puede deshomologarla posteriormente sin
volver a cumplir esa validación.

## Dashboard y reportes

El dashboard presenta métricas de empresas, trabajadores y certificados, además
de gráficas de estados y vencimientos. Los reportes permiten consultar datos
globales a los roles administrativos y datos limitados a su empresa a Usuario
Empresa.

## Configuración y comprobaciones

La configuración local se realiza mediante `.env`. No deben publicarse claves,
contraseñas, archivos reales de `media/` ni datos de producción.

Comandos habituales:

```text
python manage.py migrate
python manage.py check
python manage.py makemigrations --check
python manage.py test
```

Las autorizaciones se validan siempre en backend mediante mixins, querysets
restringidos y comprobaciones explícitas; ocultar botones no es una medida de
seguridad suficiente.
