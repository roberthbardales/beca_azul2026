# MANUAL DE FUNCIONAMIENTO DEL SISTEMA

## Sistema de control Beca Azul

**Guía de acceso y operación para los perfiles del sistema**

> **Versión:** 1.0  
> **Fecha:** ____________________  
> **Organización:** Beca Azul Ingenieros y Consultores

---

### Portada — espacio para captura

> **[Insertar captura de portada o pantalla de inicio del sistema]**
>
> Sugerencia: utilizar una imagen institucional o una captura sin datos personales reales.

---

## 1. Introducción

Este manual explica cómo utilizar el sistema de control de empresas, trabajadores y documentación. Está organizado por módulos y describe las operaciones que se encuentran disponibles en la interfaz, los pasos para ejecutarlas y las validaciones que pueden afectar el resultado.

El sistema permite administrar empresas, consultar y gestionar trabajadores, registrar certificados y revisar el cumplimiento de requisitos. También ofrece indicadores, reportes y notificaciones por correo vinculadas a determinadas operaciones.

### 1.1 Perfiles de acceso

Las opciones dependen del rol asignado a la cuenta:

- **Administrador:** acceso a vistas de control y herramientas de administración de acuerdo con los permisos asignados.
- **Beca Azul:** gestiona empresas, usuarios, aprobaciones documentales, requisitos y acciones de control.
- **Planta:** consulta paneles, empresas, trabajadores y reportes permitidos; no tiene las acciones de gestión restringidas a Beca Azul.
- **Usuario Empresa:** consulta su propia empresa y gestiona trabajadores de su empresa, además de registrar o actualizar documentación según las opciones habilitadas.
- **Garita:** consulta empresas y trabajadores, y utiliza principalmente la búsqueda rápida; no accede al detalle restringido de trabajadores.

La disponibilidad real puede variar según configuración y permisos. Si una opción no aparece, es posible que el rol no tenga permiso para ella.

### 1.2 Convenciones de esta guía

- **Pulsar** o **seleccionar** indica una acción en la interfaz.
- **Cancelar**, **Volver** o **Limpiar** no guarda los cambios del formulario/listado actual.
- Los controles de aprobación pueden estar deshabilitados mientras no se cumplan las condiciones requeridas.
- Las imágenes marcadas como espacios de captura deben sustituirse por capturas propias del entorno, evitando exponer datos personales.

---

## 2. Acceso al sistema

### 2.1 Iniciar sesión

1. Abrir la dirección web del sistema. Si no hay una sesión activa, aparecerá la pantalla de inicio de sesión.
2. Escribir el **correo electrónico** y la **contraseña** de la cuenta.
3. Pulsar **Entrar**.
4. Si los datos no son correctos, revisar el mensaje y volver a intentarlo.
5. Si la cuenta corresponde a una empresa desactivada o no tiene una empresa asignada, el sistema no permitirá continuar con el acceso de empresa.
6. Al ingresar correctamente, el sistema dirige a la pantalla inicial que corresponde al rol.

El icono de ojo en el campo de contraseña solo cambia su visibilidad en pantalla; no modifica la contraseña.

> **[Insertar captura 1: pantalla de inicio de sesión]**

### 2.2 Pantalla de inicio según perfil

Después de ingresar, el destino inicial depende del rol:

| Perfil | Destino inicial habitual |
|---|---|
| Administrador, Beca Azul, Planta | Dashboard / panel de control |
| Usuario Empresa | Listado de trabajadores de su empresa |
| Garita | Buscar trabajador |

### 2.3 Navegación y cierre de sesión

- La **barra lateral** contiene las secciones habilitadas para el perfil: Dashboard, Buscar trabajador, Empresas, Trabajadores, Usuarios, Mi empresa y Reportes.
- En dispositivos pequeños, usar el botón de menú para mostrar la barra lateral. Pulsar el fondo oscuro o el control de cierre para ocultarla.
- El menú superior muestra la cuenta y el rol. Desde allí se accede a **Mi perfil** o se elige **Cerrar sesión**.
- **Cerrar sesión** termina la sesión y regresa al formulario de acceso.

Cuando una operación no está autorizada, el sistema muestra una página de acceso denegado. No se completa la acción rechazada.

> **[Insertar captura 2: pantalla principal con navegación]**

---

## 3. Pantalla principal

### 3.1 Dashboard

El Dashboard es una vista de consulta para los perfiles autorizados. Presenta métricas y gráficos relacionados con:

- Empresas activas, inactivas y homologadas.
- Trabajadores habilitados y no habilitados.
- Estado de certificados de inducción, aptitud médica, SCTR y cursos.
- Documentos vencidos o próximos a vencer.
- Evolución mensual de estados de trabajadores y distribución por empresa.

El panel se actualiza al abrirlo. No es un formulario de edición. Parte de los datos depende de las fechas y de que el archivo del certificado esté disponible. La habilitación mostrada se calcula usando el estado de la empresa, las aprobaciones SCTR y homologación, y los requisitos personales del trabajador.

> **[Insertar captura 3: Dashboard completo]**

### 3.2 Mensajes y resultados

Después de guardar, activar, desactivar o enviar información, el sistema puede mostrar un mensaje de confirmación, advertencia o error. Conviene leerlo antes de repetir la operación, especialmente en acciones de aprobación, eliminación y envío de correos.

---

## 4. Módulo de usuarios, acceso y perfil

Este módulo administra cuentas, perfiles, sesiones y contraseñas. Las pantallas de gestión de usuarios requieren permisos; las acciones de gestión no están disponibles para todos los roles.

### 4.1 Consultar usuarios

1. Abrir **Usuarios** desde la barra lateral.
2. Para buscar, escribir nombre o correo en el campo de búsqueda.
3. Si se requiere, filtrar por **Tipo de usuario** y **Estado**.
4. Pulsar **Buscar** para aplicar los criterios.
5. Pulsar **Limpiar** para quitar los criterios y regresar al listado permitido.
6. Usar los controles de página para recorrer los resultados. El listado muestra hasta 20 cuentas por página.
7. Pulsar el icono de visualización en una fila para abrir el detalle.

El listado muestra nombre, correo, rol, empresa asociada, estado y último acceso. Las cuentas visibles dependen del perfil que consulta.

> **[Insertar captura 4: listado y filtros de usuarios]**

### 4.2 Crear una cuenta

1. Desde Usuarios, pulsar **Nuevo usuario** cuando esté disponible.
2. Seleccionar el **Tipo de usuario**.
3. Si se elige **Usuario Empresa**, seleccionar una empresa activa. Para otros roles no corresponde asignar empresa.
4. Introducir correo, nombres y apellidos.
5. En una cuenta nueva, introducir contraseña y confirmación. Los iconos de ojo muestran u ocultan el texto.
6. Pulsar **Crear usuario**. **Cancelar** o **Volver** regresa al listado sin guardar.

El sistema verifica que el correo no esté registrado, que el rol Empresa tenga empresa asignada y que los demás roles no tengan una empresa asociada. La contraseña debe coincidir con la confirmación y cumplir los validadores de contraseña configurados.

> **[Insertar captura 5: formulario de creación de usuario]**

### 4.3 Modificar o desactivar una cuenta

1. Abrir el detalle de la cuenta desde el listado.
2. Pulsar **Editar** para cambiar los datos de gestión disponibles y guardar.
3. En el detalle, pulsar **Desactivar** o **Activar** para cambiar el estado de la cuenta.
4. El sistema impide que una persona desactive su propia cuenta. También deniega acciones sobre una cuenta cuya empresa esté desactivada.

La acción de edición no es un cambio de contraseña. Para eso se usa el flujo de cambio o restablecimiento de contraseña.

### 4.4 Restablecer contraseña de otro usuario

1. En el detalle, pulsar **Restablecer contraseña** si la opción está disponible para el rol.
2. Escribir la contraseña nueva y repetirla en la confirmación.
3. Pulsar **Restablecer contraseña**.
4. El sistema valida coincidencia y política de contraseña, la guarda y vuelve al listado.

Este flujo no solicita la contraseña anterior del usuario.

### 4.5 Eliminar una cuenta

1. Abrir el detalle de la cuenta y pulsar **Eliminar**.
2. Revisar la pantalla de confirmación.
3. Confirmar para eliminar o regresar sin confirmar.

No se puede eliminar la cuenta propia. La operación elimina el usuario y no debe confundirse con desactivarlo.

### 4.6 Consultar y editar el perfil propio

1. Abrir el menú superior y seleccionar **Mi perfil**.
2. Revisar correo y datos personales.
3. Pulsar **Editar perfil**.
4. Actualizar nombres, apellidos, género, teléfono o fecha de nacimiento.
5. Pulsar **Guardar cambios**. **Cancelar** vuelve al perfil sin guardar.

La fecha de nacimiento no puede ser futura. El formulario de perfil no permite cambiar correo, rol ni empresa.

### 4.7 Cambiar la propia contraseña

1. Desde Mi perfil, pulsar **Cambiar contraseña**.
2. Escribir contraseña actual, nueva contraseña y confirmación.
3. Pulsar **Actualizar contraseña**.
4. Si la contraseña actual es incorrecta, corregirla y volver a enviar.
5. La contraseña nueva debe coincidir con la confirmación, cumplir la política y no ser igual a la actual.
6. Tras guardar, el sistema cierra la sesión; volver a iniciar sesión con la contraseña nueva.

> **[Insertar captura 6: perfil personal y opciones de contraseña]**

---

## 5. Módulo de empresas y homologación

Este módulo mantiene la información de las empresas y sus documentos habilitantes. La homologación depende de las aprobaciones y vigencia de los certificados requeridos.

### 5.1 Buscar y consultar empresas

1. Abrir **Empresas**.
2. Escribir nombre o RUC en el campo de búsqueda.
3. Usar los filtros **Estado** y **Homologación** según se necesite.
4. Pulsar **Buscar**. Para limpiar los criterios, pulsar **Limpiar**.
5. Revisar en la tabla los estados de SCTR pensión, SCTR salud, certificado de homologación, cantidad de trabajadores, estado de empresa y homologación.
6. Pulsar la acción de visualización para abrir la ficha. Garita usa **Ver lista** para consultar los trabajadores de esa empresa.

La ficha de empresa está disponible únicamente para roles autorizados y para la propia empresa cuando accede como Usuario Empresa.

> **[Insertar captura 7: listado de empresas con filtros]**

### 5.2 Registrar una empresa

1. En el listado, Administrador o Beca Azul pulsa **Nueva empresa**.
2. Completar nombre, RUC, correo y representante legal (si corresponde).
3. Pulsar **Crear empresa**.
4. Si la información pasa las validaciones, el sistema crea la empresa y confirma el resultado.

El RUC debe tener exactamente 11 dígitos y ser único. El correo debe tener formato válido y no estar asociado a otra empresa. Los documentos SCTR y de homologación se registran desde sus opciones en la ficha, no desde el formulario general.

> **[Insertar captura 8: formulario de empresa]**

### 5.3 Consultar la ficha y los certificados

La ficha presenta los datos generales, el estado de documentos empresariales, totales de trabajadores y resumen de habilitación.

- **Editar empresa** permite a Beca Azul modificar los datos generales.
- **Ver certificado** o **Ver PDF** abre el documento, si existe y el perfil puede consultarlo.
- La cuenta Empresa consulta únicamente la ficha de su propia empresa.

Los archivos se sirven después de verificar que la sesión, el rol y la empresa correspondan al documento solicitado.

> **[Insertar captura 9: ficha de empresa con SCTR y homologación]**

### 5.4 Registrar o actualizar SCTR y homologación

1. En la ficha, elegir **Registrar/Editar SCTR pensión**, **Registrar/Editar SCTR salud** o **Registrar/Editar homologación**. Estas opciones de carga corresponden a la cuenta Empresa activa.
2. Seleccionar el archivo PDF.
3. Completar fecha de emisión y fecha de vencimiento.
4. Si el documento ya existe, puede conservarse el archivo actual o reemplazarse por otro.
5. Pulsar **Guardar cambios**. **Cancelar** vuelve a la ficha.

El archivo es obligatorio cuando no existe un documento disponible. El vencimiento no puede ser anterior a la emisión. Si un documento se reemplaza o deja de estar vigente, algunas aprobaciones pueden invalidarse.

### 5.5 Aprobar documentos y completar homologación

Beca Azul utiliza las acciones de aprobación que aparecen junto a cada requisito:

- **Aprobar/Desaprobar SCTR pensión**.
- **Aprobar/Desaprobar SCTR salud**.
- **Aprobar/Desaprobar Cert. homologación**.

Antes de aprobar, comprobar que el archivo esté disponible y vigente. No se aprueba un SCTR sin certificado empresarial vigente ni la homologación sin su certificado vigente. La homologación efectiva se sincroniza cuando están aprobados y vigentes ambos SCTR y el certificado de homologación.

Cuando se completa la homologación automáticamente, el sistema intenta enviar una notificación a la empresa. Un fallo de correo no cancela la aprobación.

> **[Insertar captura 10: botones de aprobación y estados documentales]**

### 5.6 Activar, desactivar o eliminar una empresa

1. Beca Azul pulsa **Desactivar empresa** o **Activar empresa**.
2. Al desactivar, el sistema también desactiva las cuentas asociadas y conserva cuál era su estado anterior.
3. Al reactivar, restaura las cuentas que estaban activas antes de la desactivación; las que ya estaban inactivas permanecen así.
4. **Eliminar empresa** abre una confirmación. La eliminación se bloquea si la empresa tiene trabajadores o usuarios asociados.

> **[Insertar captura 11: acciones de estado y eliminación de empresa]**

---

## 6. Módulo de trabajadores y búsqueda

Este módulo permite consultar trabajadores y, a usuarios Empresa, registrar y actualizar los trabajadores de su organización. La habilitación es distinta del estado activo: un trabajador activo puede seguir sin estar habilitado si le faltan requisitos.

### 6.1 Consultar el listado

1. Abrir **Trabajadores**.
2. Escribir nombre, documento o el término permitido en el campo de búsqueda.
3. Filtrar por habilitación, estado o empresa según las opciones visibles al perfil.
4. Pulsar **Buscar** para aplicar filtros; **Limpiar** los elimina.
5. Usar la paginación para recorrer resultados.
6. Pulsar el icono de detalle para consultar al trabajador, si el rol tiene permiso.

La búsqueda por nombre tolera diferencias de tildes y varios términos. Usuario Empresa solo consulta su organización. Garita consulta trabajadores desde **Empresas** > **Ver lista**; su vista no incluye acciones de detalle.

> **[Insertar captura 12: listado de trabajadores y filtros]**

### 6.2 Buscar rápidamente un trabajador

1. Abrir **Buscar trabajador**.
2. Escribir nombre o número de documento.
3. Pulsar **Buscar**.
4. Revisar el resultado o la lista de coincidencias. La pantalla muestra documento, empresa, cargo y estado de habilitación.
5. Si aparece **Ver detalle**, pulsarlo para abrir la ficha completa. Garita puede consultar coincidencias, pero no accede al detalle restringido.

Las cuentas Empresa realizan la búsqueda dentro de su propia empresa. Si no hay coincidencias, se muestra un aviso indicando que no se encontró el trabajador.

> **[Insertar captura 13: pantalla de búsqueda de trabajador]**

### 6.3 Registrar un trabajador desde una cuenta Empresa

1. Desde **Trabajadores**, pulsar **Nuevo trabajador**.
2. Completar tipo y número de documento, nombres, apellidos y cargo.
3. La empresa se asigna automáticamente desde la cuenta; no se selecciona otra empresa.
4. Adjuntar los certificados requeridos de **Inducción** y **Aptitud médica**, con fecha de emisión y vencimiento para cada documento.
5. Pulsar **Registrar trabajador**. **Cancelar** vuelve al listado sin guardar.
6. Si los datos son válidos, el sistema crea el trabajador y los certificados. También intenta notificar el alta por correo.
7. Si el correo falla, el trabajador permanece registrado y se muestra una advertencia.

Validaciones: el DNI debe tener ocho dígitos si se eligió DNI; no debe existir un trabajador activo con el mismo documento en esa empresa; el archivo debe ser PDF de hasta 1 MB y tener firma PDF válida; no se admite vencimiento anterior a emisión. El alta genérica para personal administrador no está disponible como flujo público enlazado en la interfaz actual.

> **[Insertar captura 14: alta de trabajador con certificados]**

### 6.4 Editar, desactivar, activar y eliminar

- **Editar trabajador:** abrir el detalle y pulsar **Editar trabajador** cuando esté disponible. Cambiar los datos permitidos y guardar. Usuario Empresa solo puede editar trabajadores activos; si está desactivado, el sistema muestra un aviso en lugar de abrir el formulario.
- **Desactivar trabajador / Activar trabajador:** Beca Azul o superusuario alterna el estado activo desde el detalle. La acción no sustituye la validación documental.
- **Eliminar trabajador:** Beca Azul o superusuario puede eliminar desde el detalle, pero primero debe desactivarlo. Si sigue activo, el sistema bloquea la eliminación y lo devuelve a la ficha. Al confirmar sobre un trabajador inactivo, se elimina el registro y los datos dependientes según las relaciones del sistema.

Si alguno de estos cambios modifica la habilitación efectiva, el sistema intenta notificar a la empresa.

> **[Insertar captura 15: detalle del trabajador y acciones disponibles]**

---

## 7. Certificados, cursos obligatorios y habilitación

Los requisitos se dividen entre documentación de empresa y documentación individual. Los documentos de empresa aplican a sus trabajadores; los documentos individuales pertenecen a cada trabajador.

### 7.1 Revisar documentos en el detalle

1. Abrir el detalle de un trabajador.
2. Revisar los documentos empresariales heredados: **SCTR pensión** y **SCTR salud**.
3. Revisar los certificados propios: **Inducción**, **Aptitud médica** y cursos.
4. Consultar emisión, vencimiento, estado, validación y acceso al PDF cuando esté disponible.
5. Revisar qué cursos están marcados como obligatorios. Los cursos no requeridos no bloquean la habilitación.

El estado de vigencia se calcula con las fechas y la existencia del archivo. Para que la habilitación personal resulte efectiva, se requiere que trabajador y empresa estén activos, que la empresa esté homologada y cuente con SCTR aprobado/vigente, que el SCTR del trabajador esté validado y que los certificados personales requeridos estén vigentes y validados.

> **[Insertar captura 16: detalle de documentos y estado de habilitación]**

### 7.2 Añadir o editar certificados de cursos como Usuario Empresa

1. En el detalle, localizar **Cursos**.
2. Para añadir un curso, primero debe estar marcado como obligatorio por el flujo de gestión correspondiente. Pulsar **Añadir**.
3. Para reemplazar o actualizar un archivo existente, pulsar **Editar PDF**.
4. Seleccionar el PDF y completar o actualizar fechas.
5. Pulsar el botón de guardar del formulario. **Cancelar** vuelve al detalle.

El formulario comprueba el formato PDF, la disponibilidad del documento y la coherencia entre fechas. El curso no se puede añadir si no figura como requisito obligatorio. El detalle visible no ofrece un botón genérico para que Beca Azul cree cualquier certificado individual, aunque existen vistas de certificado en el sistema.

### 7.3 Configurar cursos obligatorios

1. En el detalle del trabajador, Beca Azul localiza la columna **Obligatorio** en la tabla de cursos.
2. Pulsar el interruptor del curso para activarlo como requisito.
3. Pulsarlo otra vez para retirar la obligatoriedad.
4. Si el curso pasa a ser obligatorio, se requiere un certificado vigente y validado para que cuente en la habilitación.

Solo se admiten los cursos ofrecidos por el sistema. No se permite cambiar la obligatoriedad cuando el trabajador o su empresa están inactivos.

### 7.4 Validar certificados personales y SCTR del trabajador

**Certificados de inducción, aptitud médica y cursos**

1. Beca Azul revisa el documento y su fecha de vencimiento.
2. Si el certificado está disponible, vigente y corresponde a un requisito aplicable, usar el control de validación que aparece en el detalle.
3. El sistema alterna la validación y vuelve a calcular la habilitación.
4. Si el archivo falta, el certificado está vencido o el trabajador/empresa está inactivo, el control se bloquea o la operación se rechaza.

**SCTR del trabajador**

1. Revisar primero en la ficha de empresa que el SCTR correspondiente esté aprobado y vigente.
2. En el detalle del trabajador, Beca Azul marca la casilla de validación de SCTR pensión o salud.
3. El sistema solo acepta la validación si existe aprobación empresarial y certificado vigente.
4. Si cambia la habilitación efectiva, se intenta notificar a la empresa.

> **[Insertar captura 17: validación de curso y SCTR en el detalle]**

La tabla del detalle inspeccionada no muestra una acción de eliminar certificado; las vistas de eliminación existen, pero no se describen aquí como botón normal de interfaz.

---

## 8. Incidencias

Las incidencias son observaciones asociadas a un trabajador y se muestran en su detalle.

### Registrar una incidencia

1. Beca Azul abre el detalle del trabajador.
2. En la sección **Incidencias**, pulsar **Agregar incidencia**.
3. Escribir la descripción.
4. Pulsar **Guardar incidencia**. **Cancelar** vuelve al detalle sin guardar.
5. El sistema registra automáticamente quién la creó y la muestra en la tabla con fecha, descripción y autor.

La descripción es obligatoria y no puede quedar vacía después de quitar espacios al inicio y al final. La gestión requiere que el trabajador y la empresa estén activos. La tabla normal de detalle no incluye botones para editar o eliminar incidencias, aunque existen vistas para esas operaciones.

> **[Insertar captura 18: sección de incidencias y formulario]**

---

## 9. Reportes

El módulo presenta informes de vencimientos, trabajadores y empresas. Usuario Empresa solo ve datos de su empresa; el envío por correo está restringido a Beca Azul.

### Consultar un reporte

1. Abrir **Reportes** desde la barra lateral.
2. Seleccionar una pestaña:
   - **Aptitud médica e inducción** (incluye cursos).
   - **Homologación y SCTR**.
   - **Trabajadores**.
   - **Empresas**.
3. Revisar el detalle tabular y los totales mostrados.

Los informes de documentos incluyen registros vencidos o próximos a vencer que tienen archivo y fechas aplicables. La selección de informe se conserva al navegar y al volver desde el envío.

### Exportar o enviar

- **Exportar a PDF:** pulsar el botón para abrir la impresión del navegador; seleccionar la opción de guardar como PDF si se necesita un archivo. El diseño de impresión está configurado en A4 horizontal.
- **Enviar por correo:** Beca Azul pulsa el botón correspondiente. El sistema envía una versión HTML a los destinatarios configurados y muestra confirmación o error. El resultado del envío queda registrado.

> **[Insertar captura 19: selección de reporte y acciones de exportación/envío]**

---

## 10. Notificaciones automáticas

Las notificaciones no constituyen una pantalla de operación independiente. Se ejecutan después de ciertos eventos:

- Registro de un nuevo trabajador desde una cuenta Empresa.
- Cambio de habilitación efectiva de un trabajador.
- Aprobación automática de homologación de empresa.
- Envío de reportes por Beca Azul.

El sistema registra asunto, evento, destinatarios y resultado. Si el envío falla, el cambio que lo originó no se revierte; según el caso, se muestra una advertencia o error y queda información del fallo para soporte.

---

## 11. Administración y tareas de soporte

### 11.1 Administración Django

La consola administrativa se encuentra en `/admin/` y requiere una cuenta autorizada por Django. Está destinada a personal con responsabilidades de administración técnica. Las opciones concretas dependen de los modelos y permisos configurados.

### 11.2 Herramientas de demostración

Existe un comando de gestión denominado `preparar_demo_certificados`, que se ejecuta desde el entorno del proyecto, no desde las pantallas normales. Está destinado a preparar archivos/estados de demostración. No ejecutarlo en un entorno con información real sin que el equipo técnico confirme previamente su propósito y alcance.

La eliminación física de archivos de certificados y las comprobaciones de configuración de correo se ejecutan automáticamente como tareas de soporte.

---

## 12. Procesos completos recomendados

### 12.1 Incorporar una empresa hasta habilitarla

1. Administrador o Beca Azul registra la empresa con nombre, RUC, correo y representante.
2. La cuenta Empresa (si corresponde) se crea desde el módulo Usuarios y se vincula a esa empresa activa.
3. El usuario Empresa ingresa, abre **Mi empresa** y carga SCTR pensión, SCTR salud y certificado de homologación con sus fechas.
4. Beca Azul revisa cada archivo y aprueba SCTR pensión, SCTR salud y homologación cuando los documentos están vigentes.
5. El sistema sincroniza la homologación efectiva cuando se cumplen los requisitos y puede enviar una notificación a la empresa.
6. Revisar la ficha y el Dashboard para confirmar los estados.

### 12.2 Registrar un trabajador de una empresa

1. La cuenta Empresa abre **Trabajadores** y pulsa **Nuevo trabajador**.
2. Completa datos personales y documento; la empresa queda asignada por el sistema.
3. Adjunta Inducción y Aptitud médica con emisión y vencimiento.
4. Envía el formulario y revisa el mensaje de resultado.
5. Beca Azul revisa el detalle y valida los certificados personales.
6. Beca Azul configura, si corresponde, cursos obligatorios y valida el SCTR del trabajador, después de confirmar la aprobación empresarial.
7. Revisar la etiqueta de habilitación y los estados documentales. Si el trabajador alcanza o pierde habilitación efectiva, el sistema intenta notificar a la empresa.

### 12.3 Mantener vigente la documentación

1. Consultar Dashboard o Reportes para detectar certificados vencidos o próximos a vencer.
2. Abrir la ficha de la empresa o el detalle del trabajador correspondiente.
3. Reemplazar el archivo o actualizar los datos desde las opciones disponibles para el rol.
4. Confirmar que la emisión y el vencimiento sean correctos y que el PDF se pueda abrir.
5. Volver a aprobar/validar el documento cuando el flujo lo requiera.
6. Confirmar que la habilitación se haya recalculado.

### 12.4 Gestionar la salida temporal de una empresa o trabajador

- **Empresa:** Beca Azul desactiva la empresa desde la ficha. El sistema desactiva sus cuentas asociadas, conserva el estado previo de cada cuenta y bloquea el acceso de empresa. Al reactivar, restaura las cuentas que estaban activas.
- **Trabajador:** Beca Azul desactiva al trabajador desde su ficha. La desactivación es distinta de la eliminación. Para eliminarlo, primero debe quedar desactivado y luego confirmarse la acción de eliminación.

---

## 13. Validaciones y recomendaciones generales

- Revisar que se está usando la empresa correcta antes de registrar trabajadores o documentos.
- El RUC debe tener 11 dígitos; el DNI debe tener 8 dígitos cuando se selecciona ese tipo documental.
- No se permiten documentos duplicados activos para el mismo trabajador dentro de la empresa.
- Los certificados deben ser PDF válido y de hasta 1 MB según validación del servidor.
- La fecha de vencimiento no puede ser anterior a la fecha de emisión.
- La vigencia depende de las fechas y de que el archivo esté efectivamente disponible.
- No intentar validar documentos vencidos ni aprobar SCTR/homologación sin certificado vigente.
- La habilitación requiere cumplir requisitos empresariales y personales; activar un registro no equivale a habilitarlo documentalmente.
- Antes de repetir una operación, leer los mensajes para evitar duplicados o acciones no deseadas.
- Si el correo falla, comprobar el estado de la operación principal: en altas, aprobaciones y cambios de habilitación, el fallo del correo no suele deshacer la operación.

---

## 14. Conclusiones

El sistema centraliza la gestión de empresas, trabajadores, certificados y requisitos de habilitación. Para obtener información fiable, es importante mantener actualizados los documentos, fechas y aprobaciones, así como verificar la habilitación efectiva después de cada cambio.

Los permisos dependen del perfil y del estado de la empresa. Las acciones de aprobación y eliminación están protegidas por validaciones para reducir operaciones incompatibles con la vigencia o con las relaciones existentes. Los indicadores y reportes facilitan el seguimiento y las notificaciones informan ciertos cambios, pero no reemplazan la revisión de los datos en las fichas correspondientes.

### Capturas pendientes de incorporar

Este manual incluye marcadores desde **[Insertar captura 1]** hasta **[Insertar captura 19]**. Reemplazar cada marcador por una imagen del entorno real, asegurándose de ocultar correos, documentos, nombres y cualquier otro dato personal o confidencial.
