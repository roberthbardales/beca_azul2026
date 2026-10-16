# Módulos y funcionalidades implementadas

Inventario basado en las apps propias del proyecto Django (`applications/home`, `applications/users` y `applications/control`) y sus rutas, vistas, modelos, formularios, servicios y plantillas. Se excluyen dependencias, datos de `media`, migraciones y archivos generados. No se genera aquí el manual de usuario.

## 1. Inicio y navegación

- **Para qué sirve:** Resolver la entrada a la aplicación según la sesión y el rol del usuario.
- **Funcionalidades disponibles:** Redirige usuarios autenticados al panel, al listado de trabajadores o a la búsqueda de garita; envía usuarios anónimos al inicio de sesión. Proporciona la respuesta de acceso denegado (403).
- **Archivos principales:** `applications/home/urls.py`, `applications/home/views.py`, `beca_azul2026/urls.py`, `templates/403.html`.

## 2. Usuarios, autenticación y permisos

- **Para qué sirve:** Gestionar cuentas, perfiles, sesiones y autorización basada en roles.
- **Funcionalidades disponibles:** Inicio y cierre de sesión; cambio y restablecimiento de contraseña; consulta y edición del perfil propio; alta, detalle, edición, activación/desactivación y eliminación de usuarios; filtros por texto, rol y estado; asignación de cuentas al ámbito de una empresa. Define roles Administrador, Beca Azul, Planta, Empresa y Garita, y protege vistas según el rol y el estado de la empresa.
- **Archivos principales:** `applications/users/urls.py`, `applications/users/views.py`, `applications/users/models.py`, `applications/users/forms.py`, `applications/users/managers.py`, `applications/users/services.py`, `applications/users/mixins.py`, `templates/users/`.

## 3. Panel, indicadores y reportes

- **Para qué sirve:** Dar visibilidad operativa sobre empresas, trabajadores, cumplimiento documental y vencimientos.
- **Funcionalidades disponibles:** Panel con métricas y gráficos de empresas y trabajadores, habilitación, cursos y certificados vigentes, vencidos o próximos a vencer; historial mensual de estados de trabajadores; reportes de vencimientos de trabajadores, documentos empresariales, trabajadores y empresas; envío por correo de reportes (restringido a Beca Azul).
- **Archivos principales:** `applications/control/urls.py`, `applications/control/views.py` (`DashboardView`, `ReportesView`), `applications/control/models.py` (`EstadoTrabajadorHistorico`), `applications/control/services/notificaciones.py`, `templates/users/dashboard/`, `templates/control/reportes.html`, `templates/control/reportes_email.html`.

## 4. Gestión de empresas y homologación

- **Para qué sirve:** Mantener empresas y controlar su habilitación documental.
- **Funcionalidades disponibles:** Listado paginado con búsqueda y filtros por estado y homologación; creación, edición, detalle, activación/desactivación y eliminación condicionada a que no existan trabajadores o usuarios asociados. Permite visualizar y administrar documentos SCTR pensión, SCTR salud y homologación, sus fechas, vigencia y aprobación. La homologación se sincroniza según las aprobaciones y vigencias requeridas; al desactivar una empresa se desactivan sus cuentas asociadas y se conserva su estado previo para restaurarlo al reactivar.
- **Archivos principales:** `applications/control/urls.py`, `applications/control/views.py` (vistas `Empresa*` y sincronización de homologaciones), `applications/control/forms.py` (`EmpresaForm`, `SCTRForm`, `SCTRSaludForm`, `HomologacionForm`), `applications/control/models.py` (`Empresa`), `templates/control/empresas/`.

## 5. Gestión y consulta de trabajadores

- **Para qué sirve:** Registrar personal por empresa y consultar sus datos y cumplimiento de requisitos.
- **Funcionalidades disponibles:** Listados paginados, ordenamiento y filtros por búsqueda, habilitación, estado y empresa; búsqueda tolerante a tildes por nombre y documento; vistas de detalle y edición; alta, actualización, activación/desactivación y eliminación (requiere desactivar antes). Usuarios de empresa pueden gestionar el personal de su propia empresa. Garita puede consultar listados y buscar trabajadores; el detalle se restringe a roles autorizados.
- **Archivos principales:** `applications/control/urls.py`, `applications/control/views.py` (vistas `Trabajador*` y `EmpresaTrabajadoresGaritaView`), `applications/control/forms.py` (`TrabajadorForm`, `TrabajadorEmpresaForm`), `applications/control/models.py` (`Trabajador`, `EstadoTrabajadorHistorico`), `applications/users/mixins.py`, `templates/control/trabajadores/`.

## 6. Certificados, cursos obligatorios y habilitación

- **Para qué sirve:** Registrar y verificar documentación necesaria para la habilitación de trabajadores y empresas.
- **Funcionalidades disponibles:** Gestión de certificados empresariales (SCTR pensión, SCTR salud y homologación) y de trabajador (inducción, aptitud médica y cursos); carga, reemplazo, visualización y eliminación de PDF; validación de formato, tamaño máximo de 1 MB, firma PDF y coherencia de fechas. Seguimiento de vigencia y estados pendiente/vigente/próximo a vencer/vencido; aprobación de documentos, validación del SCTR del trabajador, configuración de cursos obligatorios y cálculo automático de habilitación efectiva a partir de requisitos vigentes. Los archivos se sirven mediante una ruta con control de acceso.
- **Archivos principales:** `applications/control/urls.py`, `beca_azul2026/urls.py` (ruta protegida de archivos de certificados), `applications/control/views.py` (vistas `Certificado*`, toggles y detalle del trabajador), `applications/control/forms.py` (formularios de certificados y formset), `applications/control/models.py` (`Certificado`, `CursoObligatorio`, `Empresa`, `Trabajador`), `applications/control/signals.py`, `templates/control/certificados/`, `templates/control/trabajadores/detalle.html`.

## 7. Incidencias

- **Para qué sirve:** Registrar observaciones asociadas a un trabajador.
- **Funcionalidades disponibles:** Crear, editar y eliminar incidencias; guardar quién la registró y mostrarlas en el detalle del trabajador. La descripción es obligatoria y la administración está sujeta a permisos.
- **Archivos principales:** `applications/control/urls.py`, `applications/control/views.py` (`Incidencia*`), `applications/control/forms.py` (`IncidenciaForm`), `applications/control/models.py` (`Incidencia`), `applications/users/mixins.py` (`GestionarIncidenciasMixin`), `templates/control/incidencias/`, `templates/control/trabajadores/detalle.html`.

## 8. Notificaciones por correo y registro de envíos

- **Para qué sirve:** Comunicar cambios relevantes y conservar el resultado de los envíos.
- **Funcionalidades disponibles:** Envío de avisos de habilitación/deshabilitación, homologación de empresas y nuevos trabajadores; envío de reportes HTML. Registra evento, asunto, destinatarios, estado y error; los fallos de correo se manejan sin revertir operaciones ya completadas.
- **Archivos principales:** `applications/control/services/notificaciones.py`, `applications/control/models.py` (`RegistroNotificacion`), `applications/control/views.py` (integración de eventos y reportes), `applications/control/checks.py` (comprobaciones de configuración de correo).

## 9. Administración y soporte del sistema

- **Para qué sirve:** Exponer modelos a la administración de Django y proporcionar tareas y validaciones operativas.
- **Funcionalidades disponibles:** Registro administrativo de modelos; comando de gestión para preparar certificados de demostración; comprobaciones de configuración del correo; eliminación del archivo almacenado al eliminar un certificado.
- **Archivos principales:** `applications/control/admin.py`, `applications/control/management/commands/preparar_demo_certificados.py`, `applications/control/checks.py`, `applications/control/signals.py`, `applications/control/apps.py`, `applications/users/admin.py`, `applications/home/admin.py`.

## Enrutamiento global

- **Para qué sirve:** Conectar las rutas de las apps y los endpoints transversales.
- **Funcionalidades disponibles:** Admin de Django; incluye rutas de inicio, usuarios y control; define una ruta protegida para servir PDFs de certificados y, en modo `DEBUG`, sirve archivos de media.
- **Archivos principales:** `beca_azul2026/urls.py`, `applications/home/urls.py`, `applications/users/urls.py`, `applications/control/urls.py`.
