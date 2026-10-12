# Roles y permisos del sistema

> Revisión del contenido: 12-10-2026. Resumen basado en el código actual; no identifica una versión publicada o desplegada.

Este documento resume los permisos definidos en el código actual. El acceso efectivo puede estar sujeto además al estado activo de la empresa o del trabajador y a que los registros pertenezcan a la empresa asociada al usuario.

## Roles

| Rol | Permisos y alcance principal |
|---|---|
| **Administrador** | Consulta empresas y trabajadores, acceso a paneles y gestión de usuarios conforme a las restricciones de cada vista. |
| **Beca Azul** | Administración de empresas y trabajadores; aprobación/validación de requisitos; gestión de incidencias y usuarios. |
| **Usuario Planta** | Consulta de panel, empresas, trabajadores y detalles permitidos. No cuenta con los permisos operativos reservados a Beca Azul. |
| **Usuario Empresa** | Acceso vinculado a una empresa activa. Consulta sus propios registros y puede registrar/actualizar trabajadores de su empresa y cargar o mantener documentos permitidos para esos trabajadores; no administra otras empresas. |
| **Usuario Garita** | Búsqueda y consulta de trabajadores para control de acceso. No tiene acceso general al detalle de trabajador ni a funciones de administración. |

Los superusuarios de Django reciben acceso privilegiado en los controles de permisos comunes. Algunas vistas aplican sus propias comprobaciones adicionales, por lo que el acceso no debe interpretarse como uniforme para todas las operaciones.

## Matriz resumida

| Funcionalidad | Administrador | Beca Azul | Planta | Empresa | Garita |
|---|:---:|:---:|:---:|:---:|:---:|
| Panel principal | Sí | Sí | Sí | No | No |
| Consultar empresas | Sí | Sí | Sí | Su empresa | Según vista |
| Crear/administrar empresas | Sí* | Sí | No | No | No |
| Consultar trabajadores | Sí | Sí | Sí | Su empresa | Búsqueda/listado permitido |
| Ver detalle de trabajador | Sí | Sí | Sí | Su empresa | No, salvo resultado de búsqueda limitado |
| Administrar trabajadores | No* | Sí | No | Operaciones limitadas a su empresa | No |
| Validar SCTR, certificados o cursos obligatorios | No* | Sí | No | No | No |
| Gestionar incidencias | No* | Sí | No | No | No |
| Gestionar usuarios | Sí* | Sí, con alcance restringido | No | No | No |

`*` Las vistas combinan roles y mixins específicos; los permisos concretos pueden variar por acción. El administrador no obtiene automáticamente todas las acciones reservadas explícitamente al rol Beca Azul. Los superusuarios tienen privilegios especiales en los mixins comunes.

## Restricciones importantes

- Cada cuenta de **Usuario Empresa** debe estar asociada a una empresa. La sesión y las operaciones de este rol se limitan a dicha empresa; si la empresa está inactiva, el acceso se deniega en las vistas protegidas.
- Las operaciones de la empresa no permiten modificar registros de otra empresa mediante el cambio de identificador en la URL.
- Las acciones que modifican datos se implementan en vistas específicas y, en general, mediante solicitudes POST.
- La validación de certificados está reservada a Beca Azul en las operaciones explícitas de aprobación. Los documentos deben estar disponibles y vigentes para su validación.
- Garita está orientado a búsqueda y consulta; ciertas vistas de resultados limitan la exposición del detalle.
- El inicio de sesión redirige a los roles administrativos y de planta al panel, a Usuario Empresa a su listado de trabajadores y a Garita a la búsqueda.

## Seguridad y datos

Los permisos se aplican en el servidor, además de los controles de navegación de la interfaz. No se deben compartir cuentas ni publicar datos personales, credenciales, tokens o información de conexión. Los certificados y datos de trabajadores deben tratarse como información restringida.

> La matriz es una guía resumida basada en los roles y controles de acceso del código. Para decisiones de acceso específicas, prevalecen las comprobaciones de cada vista.
