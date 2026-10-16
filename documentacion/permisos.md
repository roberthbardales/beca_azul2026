# Permisos del sistema

## Alcance

Este documento describe las capacidades asociadas a los cinco roles de negocio definidos en la aplicación. Se basa en las vistas, mixins y filtros de datos presentes en el código; el acceso puede variar por pantalla, estado de empresa/trabajador y reglas de negocio. “Consultar” no implica permiso para modificar.

## Permisos por rol y módulo

### Administrador

- **Panel y reportes:** consulta el panel y los reportes. El envío de reportes por correo no está concedido explícitamente al rol Administrador en la vista revisada.
- **Empresas y trabajadores:** consulta listados y detalles según las reglas de cada vista; no tiene las operaciones exclusivas asignadas a Beca Azul.
- **Certificados e incidencias:** sin permiso de aprobación, validación o gestión explícito en las vistas de negocio revisadas.
- **Usuarios:** puede consultar cuentas y crear/editar cuentas de Beca Azul, Planta, Empresa o Garita, según las restricciones de cada acción; no puede crear ni editar Administradores. Puede cambiar contraseñas, activar/desactivar y eliminar cuentas, con limitaciones por acción.
- **Cuenta propia:** puede consultar/editar su perfil y cambiar su contraseña.

### Beca Azul

- **Panel y reportes:** consulta panel y reportes; puede enviar reportes por correo.
- **Empresas:** crea, edita, activa/desactiva y elimina empresas; administra aprobaciones de SCTR y homologación. La carga de documentos empresariales se realiza desde pantallas habilitadas para este rol.
- **Trabajadores:** crea, edita, activa/desactiva y elimina trabajadores; configura cursos obligatorios.
- **Certificados:** crea, edita, elimina y valida certificados de trabajadores; valida SCTR por trabajador. La edición de documentación empresarial no corresponde a las pantallas de carga propias de Usuario Empresa.
- **Incidencias:** crea, edita y elimina incidencias.
- **Usuarios:** consulta cuentas y crea cuentas de Planta, Empresa y Garita; actualiza, restablece contraseñas, activa/desactiva y elimina cuentas dentro de los roles objetivo permitidos por cada vista. No puede crear ni editar Administradores o usuarios Beca Azul.
- **Cuenta propia:** puede consultar/editar su perfil y cambiar su contraseña.

### Usuario Planta

- **Panel y reportes:** consulta el panel y los reportes; puede consultar reportes, pero el código no le concede el envío por correo.
- **Empresas y trabajadores:** consulta listados y detalles autorizados; no administra registros.
- **Archivos:** puede consultar determinados archivos de trabajadores. La descarga de certificados empresariales está restringida en las vistas de descarga observadas.
- **Usuarios, incidencias y aprobaciones:** no tiene permisos de gestión en las vistas revisadas.
- **Cuenta propia:** puede consultar/editar su perfil y cambiar su contraseña.

### Usuario Empresa

- **Alcance de datos:** requiere una empresa vinculada y activa; sus consultas de trabajadores, empresa y reportes se limitan a esa empresa.
- **Reportes:** consulta reportes filtrados a su empresa; no envía reportes por correo.
- **Empresa y certificados empresariales:** consulta su empresa y carga/actualiza SCTR y homologación de su propia empresa; no aprueba documentos.
- **Trabajadores:** crea y edita trabajadores de su empresa; no administra su activación ni los elimina mediante las vistas revisadas.
- **Certificados de trabajadores:** carga, actualiza o elimina documentación dentro de su empresa y de los requisitos permitidos. Para cursos, solo gestiona certificados de cursos previamente configurados como obligatorios. No valida certificados ni configura cursos obligatorios.
- **Incidencias:** consulta información desde el detalle del trabajador, sin gestionarlas.
- **Cuenta propia:** puede consultar/editar su perfil y cambiar su contraseña.

### Usuario Garita

- **Empresas:** consulta el listado orientado a garita; no accede al detalle empresarial de las vistas revisadas.
- **Trabajadores:** busca y consulta información de verificación; no accede al detalle completo ni modifica registros.
- **Panel y reportes:** sin acceso en las vistas revisadas. **Certificados, incidencias y usuarios:** sin permisos de gestión ni consulta de gestión.
- **Cuenta propia:** puede consultar/editar su perfil y cambiar su contraseña.

## Gestión de usuarios

La consulta y gestión de cuentas está protegida por permisos de rol. Beca Azul crea cuentas de Planta, Empresa y Garita y opera sobre esos roles; Administrador puede crear y editar cuentas de Beca Azul, Planta, Empresa y Garita. Las acciones de actualización, restablecimiento de contraseña, activación/desactivación y eliminación aplican filtros propios por rol objetivo. Las vistas impiden que un usuario se desactive o elimine a sí mismo. También existe cambio de contraseña propio.

## Reglas importantes de alcance

- Si una empresa se desactiva, sus usuarios se desactivan temporalmente; el sistema conserva su estado previo para restaurarlo al reactivarla.
- Los usuarios Empresa no acceden a empresas ajenas y las vistas de trabajadores filtran los resultados por la empresa vinculada.
- La carga de certificados por una empresa depende de que el requisito esté habilitado cuando se trata de cursos obligatorios.
- La aprobación de documentos exige archivos disponibles y vigentes, de acuerdo con las validaciones de negocio.
- Las restricciones se aplican en las vistas del servidor, no solo ocultando controles de interfaz.

## Notas y límites

- Los permisos se definen distribuidos entre mixins, vistas y filtros de consulta; no existe una matriz central editable.
- Esta guía es una síntesis funcional, no una especificación exhaustiva endpoint por endpoint. Antes de asignar cuentas reales, validar los flujos exactos requeridos por la organización.
- Un superusuario de Django puede superar controles de algunos mixins. Debe tratarse como acceso técnico privilegiado y gestionarse por separado de los cinco roles de negocio.
