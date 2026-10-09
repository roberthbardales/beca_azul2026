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
- `/trabajadores/empresa/<id>/`: detalle, edición y certificados de cursos para
  Usuario Empresa.
- `/certificados/crear/<trabajador_id>/`, `/certificados/<id>/editar/` y
  `/certificados/<id>/eliminar/`: gestión de certificados de trabajadores por
  Beca Azul.
- `/certificados/<id>/validar/`: aprobación o desaprobación de Inducción,
  Aptitud médica y cursos por Beca Azul.
- `/media/certificados/empresa_<id>/...`: descarga protegida de archivos según
  el rol y la empresa asociada.
- `/admin/`: administración nativa de Django.

La creación pública de usuarios está deshabilitada. La gestión se realiza desde
`/users/gestion/`.

El inicio de sesión redirige a cada usuario según su rol: dashboard para los
roles administrativos, lista de trabajadores para Usuario Empresa y búsqueda
de trabajadores para Usuario Garita. Cada usuario puede consultar y editar su
propio perfil y cambiar su contraseña.

El listado de `/trabajadores/` permite buscar por DNI completo o por palabras
del nombre y apellido, en cualquier orden y sin distinguir tildes. No permite
coincidencias parciales del DNI.

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

Una empresa tiene nombre, RUC, correo, representante legal, estado activo y
estado de homologación. También puede tener certificados SCTR de pensión, SCTR
de salud y homologación. La eliminación está protegida cuando existen
relaciones.

### Trabajador

Pertenece a una empresa y registra documento, nombres, apellidos y cargo.
También contiene:

- `activo`: controla si el registro está activo.
- `habilitado`: decisión manual de habilitación por Beca Azul.
- `habilitado_efectivo`: estado operativo calculado en tiempo real.

Los certificados SCTR no se cargan por trabajador. Se heredan de la empresa a
la que pertenece y sus fechas de emisión y vencimiento se toman de allí.

Un trabajador solo está efectivamente habilitado si está activo, su empresa está
activa, la habilitación manual está activa y la empresa tiene SCTR pensión, SCTR
salud y homologación aprobados, con archivo físico existente y vigente.
También debe tener Inducción y Aptitud médica validadas y vigentes, además de
todos los cursos obligatorios para ese trabajador validados y vigentes. Los
cursos que no son obligatorios no afectan la habilitación.
Desactivar un trabajador lo deja no habilitado. Reactivarlo no cambia la
decisión manual, pero el estado efectivo vuelve a calcularse con todos los
requisitos vigentes.

### Certificados

Los certificados registran tipo, fechas, archivo PDF cuando corresponde y estado
de validación. Los SCTR pensión, SCTR
salud y homologación pertenecen a la empresa. Los certificados de
Inducción y Aptitud médica pertenecen al trabajador y son independientes de los
cursos. Los cursos permiten un certificado por categoría y trabajador.

Inducción, Aptitud médica y cursos requieren un PDF para quedar completos. Al
crear un trabajador como Usuario Empresa se deben cargar los PDF y las fechas de
emisión y vencimiento de Inducción y Aptitud médica. En los formularios de SCTR,
homologación y certificados de trabajadores, las fechas se habilitan después de
seleccionar un PDF nuevo o cuando ya existe un archivo físico disponible. Beca
Azul valida explícitamente Inducción, Aptitud médica y cada curso obligatorio
mediante un checkbutton. Si falta el archivo o aún no se valida, queda
`Pendiente`; si vence, queda `Desaprobado`; solo un requisito validado, vigente y
con su archivo requerido queda `Vigente`.

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
- La habilitación efectiva exige que cada curso obligatorio tenga PDF, esté
  validado y vigente.
- Al desactivar la obligación, la constancia y sus datos se conservan.
- No existe todavía cálculo general de cumplimiento ni historial de cambios.

Los trabajadores inactivos no pueden modificar la obligatoriedad de cursos ni
validar certificados. Los interruptores y casillas de validación se muestran
deshabilitados y las vistas también rechazan los cambios enviados directamente.

La ruta de configuración es:

`POST /trabajadores/<id>/cursos/<curso>/obligatorio/`

Solo acepta los seis valores definidos en `CursoTipo` y no permite modificar
trabajadores inactivos.

## Certificados y carga de archivos

Usuario Empresa carga, administra y consulta en PDF el SCTR y la homologación de
su empresa, así como los certificados de sus trabajadores dentro de los límites
de sus vistas. En el alta de trabajador debe adjuntar Inducción y Aptitud médica
con sus fechas. En los formularios de SCTR y homologación, primero selecciona el
PDF para habilitar las fechas de emisión y vencimiento. Puede consultar sus
certificados empresariales aunque estén vencidos, si el archivo físico existe.
Beca Azul puede gestionar y validar certificados de trabajadores desde las
vistas permitidas. Administrador y Planta pueden consultarlos desde los detalles
permitidos, sin gestionar su contenido.

Las vistas específicas de certificados de cursos para Usuario Empresa solo
permiten cursos marcados como obligatorios. El formulario de alta o edición de
trabajadores también permite cargar los cursos del trabajador, y la empresa solo
puede operar sobre trabajadores de su propia empresa.

Antes de mostrar o descargar documentos de empresa se comprueba que el archivo
físico exista en el storage. Un registro sin archivo físico puede conservarse
para permitir reemplazarlo.

## Estados y homologación

La habilitación manual del trabajador se alterna desde un botón protegido de
Beca Azul. El estado operativo se obtiene mediante `habilitado_efectivo` y
considera trabajador activo, empresa activa, aprobaciones, archivos y vigencias.
El SCTR que se utiliza para habilitar al trabajador corresponde a los
certificados de su empresa.

Beca Azul puede homologar una empresa solo si los SCTR de pensión y salud están
aprobados, tienen archivo físico vigente, y el certificado de homologación
también tiene archivo físico vigente. Si cualquiera de esas aprobaciones o
vigencias deja de cumplirse, la homologación se invalida automáticamente.

## Dashboard y reportes

El dashboard presenta métricas de empresas, trabajadores y certificados, además
de gráficas de estados y vencimientos. Los reportes permiten consultar datos
globales a los roles administrativos y datos limitados a su empresa a Usuario
Empresa.

La consulta está disponible para Administrador, Beca Azul, Planta y Usuario
Empresa. Solo Beca Azul puede enviar reportes por correo mediante `POST`.

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

## Carga inicial en VPS

El proyecto utiliza un único fixture de datos iniciales:

`fixtures/seed.json`

Este archivo contiene empresas, trabajadores, usuarios, certificados y cursos
obligatorios. No se debe cargar un segundo fixture para completar esos datos.

`preparar_demo_certificados` instala los PDFs de ejemplo y calcula fechas y
aprobaciones relativas al día de ejecución. Se ejecuta después del fixture y
no crea ni reemplaza empresas, trabajadores o usuarios.

En una base de datos nueva, el orden es:

```text
python manage.py migrate
python manage.py loaddata seed
python manage.py preparar_demo_certificados
python manage.py check
```

El fixture no reemplaza las migraciones. Los archivos de migración de todas las
aplicaciones deben estar desplegados antes de ejecutar `migrate`.

`preparar_demo_certificados` copia los PDFs fuente disponibles en `pdf/` a las
rutas `certificados/demo/` registradas en el fixture y deja estados variados
de vigencia, validación y homologación. Puede volver a ejecutarse sin borrar
registros; solo cambia los certificados demo y los estados de las empresas
asociadas. No sustituye las migraciones ni la carga del fixture.

Para reiniciar la demo se recrea la base de datos y se repite la secuencia de
comandos anterior; no ejecutar esa secuencia sobre datos reales.

Las autorizaciones se validan siempre en backend mediante mixins, querysets
restringidos y comprobaciones explícitas; ocultar botones no es una medida de
seguridad suficiente.
