# Funcionamiento del sistema

Guía paso a paso basada en las rutas, vistas, formularios y plantillas actuales. Las opciones visibles dependen del rol. Las acciones que no aparecen en la interfaz o no tienen una ruta disponible no se describen como funciones de usuario.

## 1. Inicio y navegación

### Acceso

1. Al abrir la raíz (`/`), el sistema comprueba la sesión.
2. Si no hay sesión, redirige al inicio de sesión (`/users/login/`).
3. Si ya hay sesión, redirige según rol: Administrador, Beca Azul y Planta al panel; Empresa al listado de trabajadores; Garita a la búsqueda de trabajadores.
4. Tras autenticarse, se aplican redirecciones equivalentes: Empresa va al listado de trabajadores y Garita a la búsqueda; los demás roles llegan al dashboard.

La barra lateral ofrece las opciones autorizadas para el rol: Dashboard, Buscar trabajador, Empresas, Trabajadores, Usuarios, Mi empresa y Reportes. El menú del usuario da acceso a Mi perfil y Cerrar sesión. En pantallas pequeñas, el botón de menú abre la barra lateral; el fondo/botón de cierre la oculta. Cerrar sesión es una acción POST desde el menú; termina la sesión y redirige a `/users/login/`.

### Acceso denegado

Cuando una vista rechaza el rol o el ámbito de empresa, el sistema responde con 403. No se realiza la operación solicitada. Las cuentas de empresa no pueden continuar si no tienen empresa asignada o esta está desactivada.

**Relación:** La navegación conduce a los módulos de Usuarios, Panel/Reportes, Empresas y Trabajadores; los permisos se aplican mediante los mixins de `applications/users/mixins.py` y verificaciones de cada vista.

## 2. Usuarios, autenticación y permisos

### Iniciar sesión

1. Abrir `/users/login/` (o seleccionar la raíz estando sin autenticar).
2. Introducir correo y contraseña y pulsar **Entrar**.
3. El botón de ojo solo muestra u oculta la contraseña en pantalla; no la cambia.
4. Si las credenciales no coinciden, se muestra el error correspondiente y se permanece en el formulario.
5. Si el rol es Empresa y la cuenta no tiene empresa activa, se cierra la sesión y se informa el motivo.
6. Si el acceso es válido, se crea la sesión y se redirige según rol.

Validaciones: formato de correo requerido y campos obligatorios; autenticación Django mediante correo/contraseña. No hay opción visible de recuperación pública de contraseña.

### Perfil propio

1. Abrir el menú superior y elegir **Mi perfil**.
2. Se muestran correo, nombres, apellidos, género, celular y fecha de nacimiento.
3. **Editar perfil** abre el formulario personal. Cambiar los campos deseados y pulsar **Guardar cambios**; **Cancelar** vuelve al perfil sin guardar.
4. Al guardar, el sistema actualiza el usuario de la sesión y confirma el éxito.

Validaciones: la fecha de nacimiento no puede ser futura. El formulario de perfil no permite cambiar correo, rol ni empresa.

### Cambiar la propia contraseña

1. Desde Mi perfil, pulsar **Cambiar contraseña**.
2. Introducir contraseña actual, nueva y confirmación.
3. Pulsar **Actualizar contraseña**. **Cancelar** retorna al perfil.
4. El sistema autentica nuevamente la contraseña actual. Si es incorrecta, muestra error.
5. La nueva contraseña debe pasar los validadores de Django, diferir de la contraseña actual y coincidir con la confirmación.
6. Si se acepta, se guarda la contraseña, se cierra la sesión y se solicita volver a iniciar sesión.

### Consultar usuarios

1. Usuarios con permiso abren **Usuarios** en la navegación (`/users/gestion/`).
2. Usar búsqueda por nombre o correo y/o filtros **Tipo de usuario** y **Estado**; pulsar **Buscar**.
3. **Limpiar** elimina filtros y vuelve al listado completo permitido al rol.
4. Usar **Anterior**, **Siguiente** o número de página para recorrer los resultados (20 por página).
5. Pulsar el icono de ver para abrir el detalle.

El resultado muestra nombre, correo, rol, empresa, estado y último acceso. La búsqueda se combina con los filtros. El sistema restringe qué cuentas puede consultar cada rol: las vistas aceptan Administrador y Beca Azul, mientras que el conjunto de roles/objetos está limitado según el usuario autenticado.

### Crear usuario

1. Desde el listado, un usuario autorizado pulsa **Nuevo usuario** (la plantilla lo muestra a Beca Azul; la vista también verifica permiso).
2. Elegir tipo de usuario. Según el rol que crea, la lista de roles permitidos cambia.
3. Para tipo **Usuario Empresa**, seleccionar empresa activa; para otros tipos no corresponde asignar empresa.
4. Completar correo, nombres, apellidos y contraseña/confirmación. Los botones de ojo permiten revelar las contraseñas.
5. Pulsar **Crear usuario**. **Cancelar** o **Volver** descarta el formulario y regresa al listado.
6. Si es válido, se crea la cuenta y se muestra confirmación.

Validaciones: correo único (sin distinguir mayúsculas/minúsculas), rol Empresa requiere empresa, los otros roles no deben tener empresa, contraseña requerida en altas, coincidencia de contraseñas, y validadores de contraseña de Django.

### Editar, activar/desactivar, restablecer o eliminar

1. Abrir el detalle del usuario desde el listado.
2. **Editar** permite cambiar los campos de gestión disponibles; no presenta campos de contraseña. Guardar actualiza y vuelve al listado.
3. **Desactivar**/**Activar** alterna `is_active`. Se impide desactivar la propia cuenta. Si la empresa asociada está inactiva, la operación se deniega. La acción devuelve confirmación o, si es una solicitud dinámica, estado actualizado.
4. **Restablecer contraseña** (visible para superusuario, Administrador y Beca Azul) abre un formulario de nueva contraseña y confirmación. Al enviarlo, valida política de contraseña y coincidencia, actualiza la contraseña y vuelve al listado. No solicita contraseña actual.
5. **Eliminar** abre confirmación de Django; al confirmar, elimina la cuenta. El usuario no puede eliminar su propia cuenta. **Volver** desde el detalle retorna al listado.

El listado solo muestra una acción de ver detalle; no contiene botones directos de editar, activar/desactivar o eliminar. Estos controles se encuentran en el detalle. El detalle oculta edición, activación y eliminación al rol Planta. Las vistas vuelven a verificar permisos y el conjunto de roles gestionables, aunque se invoque una URL manualmente.

**Relación:** Usuarios Empresa está vinculado a una empresa del módulo Empresas. Desactivar una empresa desactiva sus cuentas asociadas y al reactivarla restaura el estado previo conservado por el sistema. Las cuentas gobiernan el acceso a todos los módulos.

## 3. Panel, indicadores y reportes

### Dashboard

1. Administrador, Beca Azul o Planta abre **Dashboard** en la barra lateral o llega mediante la redirección de acceso.
2. El panel carga métricas y gráficos de empresas, trabajadores, estados de habilitación y documentos/cursos por vigencia y vencimiento.
3. El panel registra los cambios de estado mensual de trabajadores para alimentar el histórico mostrado.
4. Durante la carga también sincroniza homologaciones y puede emitir avisos derivados de aprobaciones automáticas.

Es una vista de consulta; no ofrece formularios de edición. Si el rol no está autorizado, se responde 403. Los conteos de certificados distinguen documentos vigentes, vencidos y próximos a vencer según fechas y disponibilidad del archivo; la habilitación usa los requisitos calculados por el modelo Trabajador.

### Reportes

1. Elegir **Reportes** en la barra lateral. Está disponible para superusuario, Administrador, Beca Azul, Planta y Empresa.
2. Seleccionar una pestaña: **Aptitud médica e inducción**, **Homologación y SCTR**, **Trabajadores** o **Empresas**. El primer informe también incluye cursos.
3. Consultar los totales y filas presentadas. Las cuentas Empresa solo reciben datos de su empresa.
4. **Exportar a PDF** abre la impresión del navegador (hoja A4 horizontal; guardar como PDF permite generar el archivo). Para enviar por correo, Beca Azul pulsa **Enviar por correo**; el sistema genera la versión HTML y la envía a los destinatarios configurados.
5. Si el envío falla, se muestra un error y se registra el fallo; si se acepta, se muestra confirmación. Se vuelve al reporte seleccionado.

La selección inválida de reporte se sustituye por el informe de vencimientos. Los reportes de documentos muestran certificados vencidos o próximos a vencer que tengan archivo y fechas pertinentes; para personas se considera el estado activo según la consulta. El envío por correo se deniega a roles distintos de Beca Azul.

**Relación:** Consolida datos de Empresas, Trabajadores, Certificados y habilitación; los correos y sus resultados se registran en Notificaciones.

## 4. Gestión de empresas y homologación

### Consultar empresas

1. Elegir **Empresas** en la navegación. Garita puede consultar el listado; la administración y detalle dependen del rol.
2. En el listado, buscar por nombre o RUC y filtrar por estado activo/inactivo y homologación. Los filtros se aplican al actualizar el formulario.
3. Avanzar por páginas cuando corresponda. El resultado muestra empresas y datos agregados disponibles.
4. Seleccionar una empresa para abrir su ficha cuando el rol tenga permiso.

La lista sincroniza primero los estados de homologación. Para Garita se ordena priorizando homologadas; para otros perfiles, activas primero.

### Registrar una empresa

1. Desde el listado, Administrador o Beca Azul elige **Nueva empresa**.
2. Completar nombre, RUC, correo y representante legal.
3. Enviar el formulario; **Cancelar/Volver**, si se ofrece, retorna sin guardar.
4. El sistema valida los datos y, si son correctos, crea la empresa y muestra confirmación.

RUC debe contener exactamente 11 dígitos y ser único; correo también es único y debe tener formato de correo. La carga inicial de documentos empresariales se realiza desde las opciones específicas de SCTR/homologación, no se debe asumir que el formulario común siempre las muestra.

### Editar o consultar ficha

1. Desde el listado, Administrador/Beca Azul/Planta o una cuenta Empresa autorizada abre la ficha; Garita usa **Ver lista** y accede solo al listado de trabajadores de esa empresa.
2. La ficha muestra información y estado documental de SCTR pensión, SCTR salud y homologación, además de trabajadores y resúmenes. El detalle visible no muestra una lista de usuarios ni un botón de gestión de usuarios.
3. Beca Azul pulsa **Editar empresa** para modificar datos generales. Guardar actualiza la ficha; errores de validación se muestran junto al formulario. El enlace queda deshabilitado visualmente si la empresa está inactiva.
4. Una cuenta Empresa activa utiliza **Registrar/Editar SCTR pensión**, **Registrar/Editar SCTR salud** y **Registrar/Editar homologación** para cargar PDF y fechas y pulsar **Guardar cambios**. **Cancelar** regresa a la ficha.
5. Para consultar un PDF, pulsar **Ver certificado**/**Ver PDF** cuando el documento esté disponible. El archivo se sirve solo después de verificar sesión, rol, empresa y existencia del archivo. Los botones de aprobación SCTR se deshabilitan si falta vigencia o la empresa está inactiva, salvo para desaprobar un elemento ya aprobado.

La empresa usuaria solo puede consultar su propia ficha y actualizar sus documentos de SCTR y homologación. El formulario de documentos exige el archivo cuando no existe uno disponible y no permite vencimiento anterior a emisión.

### Aprobaciones y estados

- Beca Azul utiliza **Aprobar/Desaprobar SCTR pensión**, **Aprobar/Desaprobar SCTR salud** o **Aprobar/Desaprobar Cert. homologación** en la ficha; cada botón cambia la aprobación indicada.
- No se permite aprobar SCTR sin certificado empresarial vigente ni homologación sin certificado vigente.
- La homologación efectiva se sincroniza cuando están aprobados y vigentes SCTR pensión, SCTR salud y el certificado de homologación. Al quedar homologada automáticamente, el sistema intenta notificar a la empresa; un fallo de correo no revierte la aprobación.
- Si un documento deja de estar vigente o se modifica, pueden invalidarse aprobaciones asociadas; la habilitación de trabajadores se recalcula conforme a los requisitos actuales.

### Activar/desactivar y eliminar

1. Beca Azul pulsa **Desactivar empresa** o **Activar empresa**. Al desactivar, las cuentas asociadas quedan inactivas y se guarda su estado anterior; al reactivar, se restauran las que estaban activas antes. Las que ya estaban inactivas siguen así.
2. **Eliminar** solicita confirmación. La operación se bloquea si hay trabajadores o usuarios asociados y se redirige a la ficha con un mensaje. Si no hay asociaciones, se elimina y vuelve al listado.

**Relación:** Empresa es el ámbito de usuarios Empresa y trabajadores; aloja documentos empresariales, define parte de la habilitación y es fuente de reportes y notificaciones.

## 5. Gestión y consulta de trabajadores

### Listado y búsqueda

1. Abrir **Trabajadores** para ver el listado autorizado. Empresa ve únicamente trabajadores de su organización; otras cuentas autorizadas pueden filtrar por empresa. Garita llega a **Empresas** y desde una fila usa **Ver lista** para ver los trabajadores de esa empresa; no dispone de acciones de detalle.
2. Buscar por nombre completo o documento. La búsqueda de nombres ignora diferencias de tildes y admite términos separados.
3. Usar filtros de habilitación (habilitado/no habilitado), estado (activo/desactivado) y empresa, según el rol.
4. Utilizar encabezados/opciones de ordenamiento disponibles y la paginación. Para Garita el listado de su vista específica no se pagina.
5. Abrir el detalle mediante la acción/enlace del trabajador.

### Búsqueda rápida (Garita y otros roles habilitados)

1. Elegir **Buscar trabajador**.
2. Escribir nombre o documento y ejecutar la búsqueda.
3. Revisar resultados: el sistema presenta coincidencias ordenadas por apellidos/nombres/documento y tolera tildes.
4. Un resultado único se muestra directamente como trabajador seleccionado para roles distintos de Garita; Garita conserva resultados de consulta y no obtiene acceso al detalle por esta vía.

Las cuentas Empresa solo buscan en su propio ámbito. Para consultas sin término, la pantalla queda sin resultados.

### Alta de trabajador por personal administrador

La vista/formulario genérico de alta está definido en el código, pero no tiene una ruta pública configurada en `applications/control/urls.py`. Por ello, no se documenta un procedimiento utilizable desde la interfaz para que personal administrador registre trabajadores.

### Alta por usuario de empresa

1. En **Trabajadores**, pulsar **Nuevo trabajador**.
2. Completar tipo y número de documento, nombres, apellidos y cargo. La empresa se asigna automáticamente a la empresa de la cuenta.
3. En el alta se requieren certificados PDF de inducción y aptitud médica, sus fechas de emisión y vencimiento.
4. Pulsar **Registrar trabajador**. **Cancelar** vuelve al listado. Si los datos/documentos son válidos, se crea el trabajador junto con esos certificados y se intenta enviar aviso de nuevo trabajador.
5. Si falla el correo, el trabajador permanece creado y se muestra aviso; no se revierte el alta.

Se aplica la comprobación de DNI y duplicidad activa. El formulario valida los archivos como PDF de hasta 1 MB con firma `%PDF-`; las fechas de vencimiento no pueden preceder a emisión. La plantilla contiene además una comprobación de cliente de 2 MB, pero la validación del servidor del formulario es de 1 MB.

### Editar, activar/desactivar y eliminar

1. Abrir el detalle y elegir **Editar** cuando el rol tenga permiso. Cambiar los datos disponibles y guardar; el sistema vuelve al listado con confirmación.
2. Beca Azul o superusuario pulsa **Desactivar trabajador**/**Activar trabajador** para alternar la marca de actividad. La habilitación documental es distinta: puede seguir como no habilitado aunque el trabajador esté activo. El cambio puede disparar notificación si altera la habilitación efectiva.
3. **Eliminar trabajador** desde el detalle está disponible a Beca Azul o superusuario. La eliminación requiere que el trabajador ya esté desactivado. Si sigue activo, se bloquea y se devuelve al detalle. Si está inactivo, la confirmación elimina al trabajador y datos relacionados según las relaciones configuradas.

Los usuarios Empresa pueden editar un trabajador solo si está activo. Si está desactivado, el control **Editar trabajador** muestra un aviso en lugar de abrir el formulario. No tienen acción para activar/desactivar o eliminar trabajadores en esta pantalla.

**Relación:** El detalle combina documentos empresariales y personales, cursos obligatorios, estado de habilitación e incidencias. Los cambios documentales pueden alterar habilitación y disparar notificaciones.

## 6. Certificados, cursos obligatorios y habilitación

### Consultar requisitos

1. Abrir el detalle del trabajador desde Trabajadores.
2. Revisar documentos propios (inducción, aptitud médica y cursos) y documentos heredados de la empresa (SCTR pensión y salud). En cada certificado se muestra su estado/fechas y, cuando existe, el acceso al archivo.
3. El detalle distingue cursos configurados como obligatorios de los que no aplican. La habilitación efectiva requiere trabajador y empresa activos, homologación y SCTR empresariales aprobados/vigentes, validaciones SCTR del trabajador y certificados válidos de inducción, aptitud y cursos obligatorios.

Estados de vigencia dependen de fechas y existencia del archivo. Para la validación de trabajadores, el certificado debe estar vigente y tener el PDF disponible.

### Registrar o editar certificado de trabajador

1. En el detalle, Empresa puede añadir o editar certificados de cursos que ya estén configurados como obligatorios, mediante los controles **Añadir** o **Editar PDF**. Beca Azul puede validar certificados existentes; el alta/edición general de certificados personales tiene rutas y vistas, pero el detalle inspeccionado no ofrece botón genérico de registro.
2. Para un certificado general, elegir tipo; si es Cursos, elegir también curso. Completar fechas y cargar PDF.
3. Enviar. Se exige PDF disponible, coherencia de fechas y, para cursos, curso indicado. No se puede repetir un requisito individual no basado en curso.
4. Para editar, abrir el certificado y cambiar archivo o fechas; guardar. Si cambia el contenido/fechas de un certificado personal, el sistema invalida la validación existente.
5. La vista de eliminación de certificado está implementada para roles autorizados, pero no aparece un botón de eliminar en la tabla del detalle inspeccionada. Si se accede a la pantalla de confirmación por una ruta disponible, confirmar elimina el registro y el archivo almacenado y retorna al detalle.

El sistema almacena los certificados bajo una ruta organizada por empresa, año y mes, con nombre aleatorio basado en documento de trabajador o RUC. La visualización del archivo comprueba permiso y pertenencia al ámbito.

### Configurar cursos obligatorios

1. En el detalle del trabajador, un usuario Beca Azul usa el interruptor **Obligatorio** junto al curso.
2. Activarlo añade el curso como requisito; volver a pulsarlo lo quita.
3. Si el curso queda obligatorio, debe existir un certificado válido y aprobado para que contribuya a la habilitación. Si se cambia el requisito, el sistema vuelve a comparar el estado de habilitación y puede notificar una transición.

Solo se aceptan cursos de las opciones definidas en el sistema y no se permite gestionar este requisito para trabajador o empresa inactivos.

### Validar certificados y SCTR

- **Certificado personal:** Beca Azul usa el control de validar/desaprobar en el detalle. El sistema comprueba empresa y trabajador activos, archivo presente, vigencia y, para cursos, que el curso sea obligatorio. Si no cumple, no valida (y puede retirar validación vencida/archivo ausente); si cumple, alterna la marca y compara habilitación antes/después.
- **SCTR del trabajador:** Beca Azul selecciona validar para pensión o salud. Primero debe estar aprobado el SCTR empresarial correspondiente y su certificado vigente. Si se intenta validar sin ellos, la operación se rechaza con mensaje. Al aprobar o retirar validación, el estado efectivo puede cambiar.
- **SCTR y homologación empresariales:** se administran desde ficha de empresa como se describe en el módulo anterior; sus aprobaciones y vigencia condicionan a todos los trabajadores asociados.

Cuando cambia efectivamente la habilitación, el sistema intenta enviar correo a la empresa y destinatarios adicionales configurados. El fallo del correo no deshace la validación.

**Relación:** Los certificados son la base de los indicadores/reportes y están relacionados con Empresas o Trabajadores. Cursos obligatorios enlazan requisitos al trabajador; la habilitación efectiva reúne documentos y aprobaciones de ambos niveles.

## 7. Incidencias

### Consultar, registrar, editar y eliminar

1. Abrir el detalle del trabajador y localizar la sección de incidencias.
2. Para registrar, Beca Azul elige **Agregar incidencia**, escribe la descripción y envía el formulario.
3. El sistema asocia automáticamente trabajador y usuario que registra; guarda la incidencia y vuelve al detalle con confirmación.
4. La incidencia se consulta en la tabla del detalle. Las vistas de edición y eliminación existen, pero la tabla no muestra botones **Editar** ni **Eliminar**; por ello, no se incluyen esos pasos como opciones de la interfaz normal.

La descripción, tras quitar espacios al inicio/final, no puede quedar vacía. La gestión requiere permiso Beca Azul y trabajador/empresa activos; el contenido registrado se muestra en el detalle.

**Relación:** Cada incidencia pertenece a un trabajador; el detalle y las consultas de trabajadores la muestran junto con el estado documental.

## 8. Notificaciones por correo y registro de envíos

Este módulo opera automáticamente como consecuencia de otras acciones, no como una pantalla con botones de usuario identificada en las rutas.

1. Al crear trabajador desde la cuenta de empresa, el sistema intenta avisar a los destinatarios configurados.
2. Al cambiar la habilitación efectiva de un trabajador, intenta notificar a la empresa y direcciones adicionales configuradas.
3. Al completar homologación empresarial automáticamente, intenta notificar a la empresa con información documental.
4. Al enviar un reporte (Beca Azul), se remite el HTML a `REPORTES_EMAILS`.
5. Cada intento registra evento, asunto, destinatarios, estado y, si falla, mensaje de error. El servicio marca enviado si el backend acepta destinatarios y fallido si no acepta ninguno o lanza excepción.

Un problema de envío no revierte el registro, aprobación o cambio de habilitación que lo originó. Según el flujo, el usuario recibe advertencia/error o la excepción se registra en logs. Las direcciones, backend y clave de API se configuran en el entorno; las comprobaciones de sistema avisan si faltan o no son válidos.

**Relación:** Se integra con alta de trabajadores, habilitación, homologación y reportes. El historial queda en `RegistroNotificacion`.

## 9. Administración y soporte del sistema

### Administración Django

El acceso se realiza por `/admin/` con una cuenta autorizada por Django. Allí se exponen los modelos registrados por las apps. Las opciones concretas de edición dependen de cada `admin.py`; esta guía no atribuye botones o acciones que no se hayan definido en la interfaz administrativa.

### Preparar certificados de demostración

Existe el comando Django `preparar_demo_certificados`, ubicado en `applications/control/management/commands/preparar_demo_certificados.py`. Se ejecuta desde el entorno de desarrollo/operación mediante `manage.py`; no es una acción de la interfaz web. Sus efectos y parámetros se deben consultar en la ayuda del comando antes de ejecutarlo en un entorno con datos reales.

### Comprobaciones y limpieza

En las comprobaciones de Django se revisan valores de configuración de correo y destinatarios. Al eliminar un certificado, una señal elimina el archivo físico asociado si existe. Estas tareas son automáticas; no requieren acción del usuario en las pantallas normales.

**Relación:** La administración opera sobre los modelos de Usuarios y Control; las comprobaciones y señales respaldan el envío y almacenamiento de certificados.

## 10. Enrutamiento global y archivos

El enrutamiento conecta `/`, `/users/` y las rutas de control, además del administrador. La ruta de certificados valida la sesión, rol, empresa propietaria y existencia del archivo antes de servir el PDF. Las cuentas Planta no pueden usar esa ruta para documentos empresariales; Empresa solo accede a archivos de su propia empresa. En modo `DEBUG`, Django sirve archivos desde `MEDIA_URL` según configuración.

Las rutas no constituyen una función operativa separada para el usuario: son el mecanismo que permite navegar entre los módulos y acceder de forma controlada a los documentos.
