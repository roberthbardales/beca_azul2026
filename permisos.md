# Permisos del sistema

Los permisos efectivos se validan en backend. Las acciones ocultas en las
plantillas también están protegidas por vistas y mixins.

## Roles

| Rol | Código | Alcance |
|---|---:|---|
| Administrador | `0` | Gestión de usuarios y empresas; consulta amplia. |
| Beca Azul | `1` | Administración operativa completa del sistema. |
| Usuario Planta | `2` | Consulta de información y acceso al dashboard. |
| Usuario Empresa | `3` | Gestión limitada a su empresa y sus trabajadores. |
| Usuario Garita | `4` | Búsqueda de empresas y consulta de listas de trabajadores. |

El superusuario de Django supera los controles generales basados en rol cuando
la vista no añade una restricción específica.

## Administrador

- Gestiona usuarios permitidos: consultar, crear, editar, activar, desactivar, eliminar y restablecer contraseñas según las vistas.
- Consulta empresas y sus detalles.
- Consulta trabajadores, certificados e incidencias.
- No crea, edita, activa, desactiva ni elimina empresas, trabajadores, certificados o incidencias desde las vistas normales.
- No activa ni desactiva cursos obligatorios ni estados de trabajadores.
- Accede al dashboard y a reportes globales.

## Beca Azul

- Gestiona usuarios Planta, Empresa y Garita.
- Gestiona empresas, incluyendo activación, desactivación y homologación.
- Una homologación solo se mantiene aprobada si SCTR pensión y salud están
  aprobados y vigentes, y el certificado de homologación tiene archivo vigente.
  Si falla cualquiera de esas condiciones, se invalida automáticamente.
- Consulta trabajadores de todas las empresas.
- En `/trabajadores/` puede buscar por DNI completo o por palabras del nombre y
  apellido, sin distinguir tildes. El DNI no admite coincidencias parciales.
- Crea, edita, activa, desactiva y elimina trabajadores.
- Crea, edita y elimina certificados de trabajadores de Inducción, Aptitud
  médica y cursos.
- Valida o desaprueba explícitamente Inducción, Aptitud médica y cada curso
  obligatorio mediante `POST` en `/certificados/<id>/validar/`.
- No puede validar ni desaprobar certificados de un trabajador inactivo. Las
  casillas aparecen deshabilitadas y el backend rechaza igualmente el `POST`.
- Inducción, Aptitud médica y cursos requieren PDF para quedar completos. En el
  formulario de alta de trabajador de Usuario Empresa son obligatorios los PDF y
  las fechas de emisión y vencimiento de Inducción y Aptitud médica.
- En los formularios de SCTR, homologación y certificados de trabajadores, las
  fechas de emisión y vencimiento se habilitan al seleccionar un PDF, o si ya
  existe un archivo físico disponible. El backend también exige PDF y fechas
  válidas para guardar certificados nuevos.
- Si falta el PDF requerido o aún no fueron validados, quedan pendientes; al
  vencer, quedan desaprobados.
- Cambia la habilitación manual del trabajador. La habilitación efectiva además
  exige trabajador y empresa activos, SCTR pensión y salud aprobados con archivo
  físico vigente, homologación aprobada con archivo físico vigente, Inducción y
  Aptitud médica validadas y vigentes, y todos los cursos obligatorios validados
  y vigentes.
- Crea, edita y elimina incidencias.
- Consulta certificados desde los detalles permitidos.
- Activa o desactiva manualmente cada uno de los seis cursos para cada trabajador.
- Puede modificar esa obligatoriedad solo en trabajadores activos.
- Las validaciones de Inducción, Aptitud médica y cursos también quedan
  bloqueadas para trabajadores inactivos: las casillas se muestran
  deshabilitadas y el backend rechaza el `POST`.
- Puede hacerlo mediante `POST` en `/trabajadores/<id>/cursos/<curso>/obligatorio/`.
- No modifica Inducción ni Aptitud médica mediante esta configuración.
- Accede al dashboard y a reportes globales.
- Puede enviar reportes por correo mediante `POST`.

Al activar un curso obligatorio no se crea automáticamente una constancia. Si
falta el PDF, Usuario Empresa verá `Falta subir` y deberá cargarlo.

## Usuario Planta

- Consulta empresas, trabajadores y certificados.
- Accede al dashboard.
- Accede a reportes según el alcance implementado.
- No gestiona usuarios, empresas, trabajadores, certificados ni incidencias.
- No modifica estados de trabajadores, SCTR ni cursos obligatorios.
- Puede consultar la configuración de obligatoriedad visible en el detalle.
- No envía reportes por correo.

## Usuario Empresa

- Debe tener una empresa asignada y activa.
- Solo accede a su propia empresa y a sus trabajadores.
- Consulta su empresa y administra los certificados SCTR y homologación de ella.
- Para registrar o actualizar SCTR y homologación, selecciona primero el PDF; el
  formulario habilita después las fechas de emisión y vencimiento. Un certificado
  nuevo no se guarda sin archivo y fechas válidas.
- Puede ver en PDF los certificados de su propia empresa, aunque estén vencidos,
  siempre que el archivo físico exista.
- Crea y edita trabajadores de su empresa.
- Al crear un trabajador, debe adjuntar los PDF y completar las fechas de emisión
  y vencimiento de Inducción y Aptitud médica.
- No puede activar ni desactivar trabajadores; esa operación está reservada a
  Beca Azul.
- Puede cargar, editar y eliminar certificados de sus trabajadores dentro de los
  límites de las vistas de empresa.
- Puede cargar cualquiera de los seis cursos al crear o editar un trabajador.
- Las vistas específicas de cursos solo permiten cursos marcados como
  obligatorios.
- Si Beca Azul marcó un curso como obligatorio y no existe PDF, el detalle muestra
  `Falta subir`.
- Puede consultar si un curso está marcado como obligatorio, pero no puede cambiarlo.
- No modifica Inducción, Aptitud médica ni la obligatoriedad de cursos.
- No aprueba SCTR ni homologa/deshomologa empresas.
- No accede al dashboard general.
- Sus reportes se limitan a su empresa y trabajadores.
- No puede enviar reportes por correo.

## Usuario Garita

- Busca empresas.
- Consulta la lista de trabajadores de una empresa.
- Puede ver trabajadores activos e inactivos en esa lista.
- Puede buscar trabajadores, pero no consultar su detalle individual.
- No accede al detalle individual del trabajador.
- No administra empresas, trabajadores, certificados, incidencias, estados ni
  cursos obligatorios.
- No accede a usuarios, dashboard ni reportes.

## Reglas de cursos obligatorios

- Solo aplican a los seis cursos fijos del catálogo.
- La configuración es individual por trabajador.
- Cada interruptor realiza una activación o desactivación manual.
- La operación se guarda inmediatamente mediante `POST` y requiere CSRF.
- Un curso obligatorio puede no tener certificado todavía.
- Sin certificado se muestra `Falta subir`.
- Con certificado se muestran sus fechas y estado normal.
- Un curso obligatorio sin PDF, sin validación o vencido no permite habilitar al
  trabajador.
- Desactivar la obligación no elimina el certificado ni sus fechas.
- No se registra auditoría de quién cambió la obligación.
- No se calcula un porcentaje ni estado general de cumplimiento.

## Reglas de seguridad

- Los cambios usan solicitudes `POST`.
- Las vistas comprueban el rol antes de ejecutar operaciones.
- Usuario Empresa queda restringido por `request.user.empresa`.
- Los trabajadores inactivos no pueden recibir modificaciones en las vistas que
  usan `TrabajadorActivoRequiredMixin`.
- Los cursos enviados a la ruta de obligatoriedad deben pertenecer a
  `Certificado.CURSO_CHOICES`.
- La existencia de una ruta de archivo en la base de datos no garantiza que el
  PDF exista físicamente; las vistas documentales comprueban el storage.

## Habilitación efectiva

- `habilitado` conserva la decisión manual de Beca Azul.
- `habilitado_efectivo` es el estado operativo calculado en tiempo real.
- Un trabajador solo está efectivamente habilitado si está activo, su empresa
  está activa, cumple todos los requisitos empresariales de SCTR y homologación,
  y tiene Inducción, Aptitud médica y todos sus cursos obligatorios validados y
  vigentes.
- Si falta un archivo, una aprobación o una vigencia, se considera no habilitado
  sin necesidad de una tarea programada.
- La acción de habilitar vuelve a validar todos los requisitos y muestra el
  motivo cuando alguno no se cumple.

## Datos iniciales y despliegue

- La carga inicial usa únicamente `fixtures/seed.json`.
- El fixture incluye los usuarios de los cinco roles, empresas, trabajadores,
  certificados y cursos obligatorios.
- Las migraciones se ejecutan antes del fixture; `loaddata` no crea tablas ni
  reemplaza migraciones.
- En una base nueva, el orden recomendado es:

```text
python manage.py migrate
python manage.py loaddata seed
python manage.py preparar_demo_certificados
python manage.py check
```

- `preparar_demo_certificados` copia los PDFs fuente de `pdf/` a las rutas demo
  declaradas en el fixture, actualiza las fechas relativas al día de ejecución
  y establece estados variados de vigencia y aprobación. Es repetible y solo
  modifica certificados bajo `certificados/demo/` y empresas asociadas a esos
  certificados; no borra trabajadores, empresas ni usuarios.
- El comando no reemplaza `loaddata`: primero carga el fixture y luego prepara
  los archivos y estados demo.
- Las credenciales contenidas en el fixture son datos de desarrollo y deben
  cambiarse antes de usar el entorno en producción.
