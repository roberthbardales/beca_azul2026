Quiero que implementes en este proyecto Django un sistema de control de empresas, usuarios, trabajadores y certificados.

IMPORTANTE:
- Antes de modificar código, inspecciona completamente la estructura actual del proyecto.
- Identifica las apps existentes, modelos, URLs, settings, templates, forms, managers, mixins, autenticación y migraciones.
- Ya existe un modelo User personalizado basado en AbstractBaseUser y PermissionsMixin. Debes adaptarlo, NO reemplazarlo sin necesidad.
- Respeta las convenciones y arquitectura existente del proyecto.
- No dupliques funcionalidades que ya existan.
- No elimines funcionalidades existentes.
- Si necesitas modificar modelos existentes, hazlo de forma compatible y crea las migraciones correspondientes.
- Usa Django Class Based Views (CBV) para TODAS las views nuevas.
- Usa buenas prácticas de Django.
- Implementa seguridad en backend, no solamente ocultando botones en templates.
- Al finalizar, ejecuta las migraciones y tests disponibles y corrige los errores que encuentres.

==================================================
1. ROLES DEL SISTEMA
==================================================

El sistema tendrá 4 tipos de usuarios:

1. BECA_AZUL
2. USUARIO_EMPRESA
3. USUARIO_PLANTA
4. USUARIO_GARITA

No utilizar "EMPLEADO" como rol de User.

IMPORTANTE:
Un trabajador registrado por una empresa NO es necesariamente un usuario del sistema.

Por lo tanto:

User = persona que utiliza el sistema.

Trabajador = persona registrada para efectos de control de acceso.

==================================================
2. MODELO USER
==================================================

El proyecto ya tiene un User similar a:

class User(AbstractBaseUser, PermissionsMixin):
    email
    first_name
    last_name
    occupation
    gender
    date_birth
    phone
    is_staff
    is_active
    objects = UserManager()
    USERNAME_FIELD = 'email'

Adáptalo para utilizar roles claros:

BECA_AZUL = 'BECA_AZUL'
USUARIO_EMPRESA = 'USUARIO_EMPRESA'
USUARIO_PLANTA = 'USUARIO_PLANTA'
USUARIO_GARITA = 'USUARIO_GARITA'

Crear ROLE_CHOICES.

Cambiar "occupation" por "role" si la arquitectura existente lo permite.

Si cambiar el nombre del campo genera problemas de migración o compatibilidad, analiza primero el proyecto y realiza la migración adecuada.

Agregar:

empresa = models.ForeignKey(
    Empresa,
    on_delete=models.PROTECT,
    null=True,
    blank=True,
    related_name='usuarios'
)

Reglas:

- BECA_AZUL normalmente no tiene empresa asignada.
- USUARIO_EMPRESA DEBE tener una empresa asignada.
- USUARIO_PLANTA no necesita empresa.
- USUARIO_GARITA no necesita empresa.

No permitas que un usuario pueda modificar su empresa arbitrariamente.

==================================================
3. MODELO EMPRESA
==================================================

Crear/adaptar modelo Empresa.

Campos mínimos:

- nombre
- ruc
- habilitada
- created_at
- updated_at

Ejemplo conceptual:

class Empresa(models.Model):
    nombre = models.CharField(max_length=150, unique=True)
    ruc = models.CharField(max_length=20, unique=True)
    habilitada = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

Usar on_delete=PROTECT cuando corresponda.

==================================================
4. MODELO TRABAJADOR
==================================================

Crear modelo Trabajador separado de User.

Campos mínimos:

- empresa
- dni
- nombres
- apellidos
- telefono
- cargo
- estado
- created_at
- updated_at

Estados:

PENDIENTE
HABILITADO
RECHAZADO

Ejemplo:

PENDIENTE = 'PENDIENTE'
HABILITADO = 'HABILITADO'
RECHAZADO = 'RECHAZADO'

ESTADO_CHOICES = (
    (PENDIENTE, 'Pendiente de revisión'),
    (HABILITADO, 'Habilitado'),
    (RECHAZADO, 'Rechazado'),
)

El estado inicial SIEMPRE debe ser:

PENDIENTE

Nunca debe crearse directamente como HABILITADO.

Agregar restricción:

DNI único por empresa.

Es decir, una misma persona no puede tener el mismo DNI dos veces dentro de la misma empresa.

No asumir necesariamente que el DNI es único globalmente si el negocio actual no lo exige.

==================================================
5. MODELO CERTIFICADO
==================================================

Crear modelo Certificado relacionado con Trabajador.

Un trabajador puede tener MÁXIMO 3 certificados.

Campos:

- trabajador
- archivo
- nombre
- estado
- observacion
- created_at
- updated_at si es necesario

Estados:

PENDIENTE
APROBADO
RECHAZADO

Ejemplo:

PENDIENTE = 'PENDIENTE'
APROBADO = 'APROBADO'
RECHAZADO = 'RECHAZADO'

Cada certificado comienza como PENDIENTE.

El archivo debe utilizar FileField con un upload_to organizado.

Por ejemplo:

certificados/%Y/%m/

Validar correctamente los archivos.

Si es posible, implementar validación de extensiones permitidas y tamaño máximo usando una configuración razonable y fácil de modificar.

NO permitir más de 3 certificados por trabajador.

Esta validación debe existir en backend, no solamente en JavaScript/HTML.

==================================================
6. FLUJO DE BECA AZUL
==================================================

El usuario BECA_AZUL es el administrador del negocio.

Puede:

- Crear empresas.
- Editar empresas.
- Habilitar/deshabilitar empresas.
- Crear usuarios de empresa.
- Asignar cada usuario de empresa a una empresa.
- Ver todas las empresas.
- Ver todos los usuarios de empresa.
- Ver todos los trabajadores.
- Revisar trabajadores.
- Revisar certificados.
- Aprobar/rechazar certificados.
- Habilitar/rechazar trabajadores según las reglas de validación.

IMPORTANTE:

Beca Azul NO debe editar arbitrariamente los datos básicos del trabajador desde la vista de revisión.

Su función respecto al trabajador es revisar la documentación y determinar si corresponde habilitarlo o rechazarlo.

==================================================
7. CREAR USUARIO EMPRESA
==================================================

Solo BECA_AZUL puede crear usuarios de empresa.

Cuando Beca Azul crea un usuario empresa debe seleccionar/asignar una empresa.

Ejemplo:

Empresa:
ABC SAC

Usuario:
Juan Pérez
juan@abc.com

Role:
USUARIO_EMPRESA

Empresa:
ABC SAC

El usuario debe quedar asociado a esa empresa.

Un usuario empresa NO puede cambiarse a otra empresa desde el frontend.

Tampoco debe poder manipular el empresa_id mediante POST para acceder a otra empresa.

==================================================
8. USUARIO EMPRESA
==================================================

USUARIO_EMPRESA solo puede trabajar con su propia empresa.

Puede:

- Ver su empresa.
- Ver trabajadores de su empresa.
- Crear trabajadores.
- Editar trabajadores de su empresa.
- Registrar/subir certificados de trabajadores de su empresa.
- Ver estado de los trabajadores.
- Ver certificados.

NO puede:

- Ver trabajadores de otras empresas.
- Crear trabajadores para otra empresa.
- Editar trabajadores de otra empresa.
- Subir certificados a trabajadores de otra empresa.
- Habilitar trabajadores.
- Deshabilitar trabajadores.
- Aprobar/rechazar certificados.
- Habilitar/deshabilitar empresas.
- Crear usuarios de empresa.

IMPORTANTE:

Nunca confiar en un empresa_id enviado desde el formulario.

La empresa debe determinarse siempre desde:

request.user.empresa

Ejemplo:

trabajador.empresa = request.user.empresa

Para obtener trabajadores:

Trabajador.objects.filter(
    empresa=request.user.empresa
)

Para obtener un trabajador específico:

Trabajador.objects.get(
    pk=pk,
    empresa=request.user.empresa
)

Implementar esto correctamente en los querysets de las CBV.

==================================================
9. REGISTRO DE TRABAJADOR
==================================================

USUARIO_EMPRESA registra:

- DNI
- Nombres
- Apellidos
- Teléfono
- Cargo

La empresa se asigna automáticamente según:

request.user.empresa

Nunca mostrar la empresa como campo editable obligatorio.

Al crear el trabajador:

estado = PENDIENTE

Después de crear el trabajador, permitir subir hasta 3 certificados.

==================================================
10. CERTIFICADOS
==================================================

El usuario empresa puede subir hasta 3 certificados.

Ejemplo:

Trabajador:
Carlos Pérez

Certificados:

1. Certificado médico.pdf
2. Curso seguridad.pdf
3. Antecedentes.pdf

Cada certificado empieza:

estado = PENDIENTE

El usuario empresa NO puede cambiar el estado del certificado.

Solo BECA_AZUL puede:

- aprobar certificado
- rechazar certificado
- agregar observación

==================================================
11. REGLA PARA HABILITAR TRABAJADOR
==================================================

Esta es una regla CRÍTICA.

Beca Azul NO debe poder habilitar manualmente a un trabajador si la documentación no está correctamente revisada.

Implementar una función/método de dominio similar a:

trabajador.puede_habilitar()

Reglas mínimas:

- Debe existir al menos un certificado.
- Ningún certificado puede estar en PENDIENTE.
- Ningún certificado puede estar RECHAZADO.
- Todos los certificados existentes deben estar APROBADOS.
- Los datos básicos del trabajador deben estar completos según las validaciones del formulario.

Si todo está correcto:

trabajador.estado = HABILITADO

Si existe algún certificado rechazado:

trabajador.estado = RECHAZADO

Si existe algún certificado pendiente:

trabajador.estado = PENDIENTE

IMPORTANTE:

La cantidad máxima de certificados es 3, pero NO necesariamente deben existir 3.

Puede tener 1, 2 o 3 certificados.

==================================================
12. REVISIÓN DE BECA AZUL
==================================================

Crear una interfaz de revisión para Beca Azul.

Debe mostrar:

- Empresa
- DNI
- Nombres
- Apellidos
- Cargo
- Estado del trabajador
- Lista de certificados
- Nombre del certificado
- Archivo
- Estado del certificado
- Observación

Ejemplo conceptual:

TRABAJADOR
Carlos Pérez

Empresa:
ABC SAC

DNI:
12345678

Estado:
PENDIENTE

CERTIFICADOS

1. Certificado médico
   Estado: PENDIENTE
   [VER ARCHIVO]
   [APROBAR]
   [RECHAZAR]

2. Curso seguridad
   Estado: PENDIENTE
   [VER ARCHIVO]
   [APROBAR]
   [RECHAZAR]

Luego, cuando todos estén aprobados:

[HABILITAR TRABAJADOR]

La vista de habilitación debe volver a validar las condiciones en backend.

NO confiar en que el frontend haya ocultado el botón.

==================================================
13. SEGURIDAD DE HABILITACIÓN
==================================================

Solo un usuario con:

request.user.role == User.BECA_AZUL

puede modificar:

Trabajador.estado

y Certificado.estado.

USUARIO_EMPRESA nunca debe poder cambiar estos campos mediante POST, PUT, PATCH, formularios manipulados o URLs directas.

No exponer estos campos en los ModelForms del usuario empresa.

Si un usuario empresa intenta acceder directamente a una URL de habilitación/revisión:

responder con PermissionDenied / 403.

Usar mixins reutilizables, por ejemplo:

BecaAzulRequiredMixin
UsuarioEmpresaRequiredMixin
UsuarioPlantaRequiredMixin
UsuarioGaritaRequiredMixin

O una estructura equivalente acorde al proyecto.

==================================================
14. USUARIO PLANTA
==================================================

USUARIO_PLANTA será principalmente de consulta.

Puede:

- Ver dashboard.
- Ver empresas.
- Ver empresas habilitadas.
- Ver trabajadores.
- Filtrar trabajadores por empresa.
- Ver estado del trabajador.
- Ver estado de la empresa.
- Consultar información general.

NO puede:

- Crear empresas.
- Crear usuarios empresa.
- Crear trabajadores.
- Editar trabajadores.
- Aprobar certificados.
- Habilitar trabajadores.
- Deshabilitar trabajadores.

==================================================
15. USUARIO GARITA
==================================================

Crear una interfaz sencilla de consulta.

Debe permitir:

- Buscar empresa.
- Buscar trabajador por DNI u otro identificador definido por el proyecto.
- Mostrar si la empresa está habilitada.
- Mostrar si el trabajador está habilitado.
- Mostrar si puede ingresar.

La regla final para permitir ingreso debe ser:

trabajador.empresa.habilitada == True
AND
trabajador.estado == HABILITADO

Crear una propiedad/método de dominio como:

trabajador.esta_autorizado

que encapsule esta regla.

Ejemplo:

if trabajador.esta_autorizado:
    # AUTORIZADO
else:
    # NO AUTORIZADO

Garita NO debe poder modificar absolutamente nada.

Solo consultar.

==================================================
16. CLASS BASED VIEWS
==================================================

Todas las vistas nuevas deben utilizar CBV.

Utilizar apropiadamente:

- ListView
- DetailView
- CreateView
- UpdateView
- DeleteView si realmente es necesario
- View para acciones POST específicas

No implementar vistas funcionales para estas funcionalidades.

Ejemplos esperados:

EmpresaListView
EmpresaCreateView
EmpresaUpdateView
EmpresaToggleStatusView

UsuarioEmpresaListView
UsuarioEmpresaCreateView
UsuarioEmpresaUpdateView

TrabajadorListView
TrabajadorCreateView
TrabajadorUpdateView
TrabajadorDetailView

TrabajadorRevisionListView
TrabajadorRevisionView
TrabajadorHabilitarView
TrabajadorRechazarView

CertificadoCreateView
CertificadoRevisionView
CertificadoAprobarView
CertificadoRechazarView

GaritaConsultaView

Adapta los nombres a la arquitectura existente.

==================================================
17. FORMS
==================================================

Crear ModelForms apropiados.

Importante:

El formulario de Trabajador para USUARIO_EMPRESA NO debe incluir:

- empresa
- estado

El formulario de Certificado para USUARIO_EMPRESA NO debe incluir:

- trabajador editable
- estado
- observacion de aprobación

El formulario de revisión de Beca Azul sí puede permitir:

- estado del certificado
- observación

pero siempre protegido por backend.

==================================================
18. URLs
==================================================

Organizar las URLs por aplicación.

Ejemplo conceptual:

/empresas/
/empresas/crear/
/empresas/<pk>/
/empresas/<pk>/editar/
/empresas/<pk>/habilitar/
/empresas/<pk>/deshabilitar/

/usuarios-empresa/
/usuarios-empresa/crear/

/trabajadores/
/trabajadores/crear/
/trabajadores/<pk>/
/trabajadores/<pk>/editar/

/revision/
/revision/<pk>/
/revision/<pk>/habilitar/
/revision/<pk>/rechazar/

/trabajadores/<pk>/certificados/
/trabajadores/<pk>/certificados/subir/

/garita/
/garita/consultar/

Adaptar a las URLs existentes.

Las acciones que cambien datos deben utilizar POST y CSRF.

NO usar GET para acciones como:

- habilitar
- deshabilitar
- aprobar
- rechazar
- eliminar

==================================================
19. TEMPLATES
==================================================

Crear templates limpios y reutilizables utilizando el base template existente.

Necesito como mínimo:

Beca Azul:

- dashboard
- empresas/lista
- empresas/form
- usuarios_empresa/lista
- usuarios_empresa/form
- trabajadores/revision_lista
- trabajadores/revision_detail

Usuario Empresa:

- dashboard
- trabajadores/lista
- trabajadores/form
- trabajadores/detail
- certificados/form

Planta:

- dashboard
- empresas/lista
- trabajadores/lista

Garita:

- consulta
- resultado de consulta

No necesito un diseño visual excesivamente complejo.

Priorizar funcionalidad, claridad y responsive básico.

==================================================
20. DASHBOARD
==================================================

Crear dashboard según el rol.

BECA_AZUL:

Mostrar:

- Total empresas
- Empresas habilitadas
- Empresas deshabilitadas
- Total trabajadores
- Trabajadores pendientes
- Trabajadores habilitados
- Trabajadores rechazados
- Certificados pendientes

USUARIO_EMPRESA:

Mostrar:

- Empresa
- Total trabajadores
- Trabajadores pendientes
- Trabajadores habilitados
- Trabajadores rechazados

USUARIO_PLANTA:

Mostrar estadísticas generales.

USUARIO_GARITA:

Mostrar directamente la interfaz de consulta.

==================================================
21. PERMISOS Y SEGURIDAD
==================================================

No depender solamente del role en templates.

Toda acción debe estar protegida en backend.

Por ejemplo:

class BecaAzulRequiredMixin:

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if request.user.role != User.BECA_AZUL:
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)

Crear equivalentes para los demás roles.

Además:

- LoginRequiredMixin donde corresponda.
- PermissionDenied para acceso indebido.
- Filtrar siempre por empresa para USUARIO_EMPRESA.
- No confiar en IDs recibidos del cliente.
- No permitir Mass Assignment de campos sensibles.
- Usar POST para mutaciones.
- CSRF.
- Validar archivos.
- Validar tamaño de archivos.
- Evitar IDOR (Insecure Direct Object Reference).

==================================================
22. AUDITORÍA
==================================================

Como el sistema controla autorizaciones, implementar si la arquitectura lo permite un pequeño historial de acciones.

Registrar al menos:

- quién aprobó un certificado
- quién rechazó un certificado
- quién habilitó un trabajador
- quién rechazó un trabajador
- fecha/hora
- trabajador
- empresa
- observación cuando corresponda

Puedes crear un modelo:

Auditoria

con:

usuario
empresa
trabajador
certificado nullable
accion
observacion
created_at

Acciones:

CERTIFICADO_APROBADO
CERTIFICADO_RECHAZADO
TRABAJADOR_HABILITADO
TRABAJADOR_RECHAZADO
EMPRESA_HABILITADA
EMPRESA_DESHABILITADA

No es necesario construir un frontend completo para auditoría inicialmente, pero sí dejar el modelo y registrar las acciones críticas.

==================================================
23. REGLAS IMPORTANTES DE NEGOCIO
==================================================

Implementar estas reglas exactamente:

1. Solo BECA_AZUL crea empresas.

2. Solo BECA_AZUL crea USUARIO_EMPRESA.

3. Todo USUARIO_EMPRESA debe pertenecer a una Empresa.

4. USUARIO_EMPRESA solo puede trabajar con su empresa.

5. USUARIO_EMPRESA puede crear trabajadores.

6. Al crear un trabajador, su estado es PENDIENTE.

7. Un trabajador puede tener máximo 3 certificados.

8. Cada certificado comienza PENDIENTE.

9. Solo BECA_AZUL puede aprobar/rechazar certificados.

10. Solo BECA_AZUL puede cambiar el estado del trabajador.

11. Un trabajador solo puede quedar HABILITADO cuando todos sus certificados existentes estén APROBADOS y exista al menos un certificado.

12. Si existe un certificado RECHAZADO, el trabajador no puede estar HABILITADO.

13. Si existe un certificado PENDIENTE, el trabajador no puede estar HABILITADO.

14. Garita solamente consulta.

15. Planta solamente consulta.

16. Para ingresar, deben cumplirse ambas condiciones:

empresa.habilitada == True
trabajador.estado == HABILITADO

==================================================
24. TESTS
==================================================

Crear tests automatizados para las reglas críticas.

Como mínimo probar:

USER:

- Beca Azul puede crear empresa.
- Usuario empresa no puede crear empresa.
- Beca Azul puede crear usuario empresa.
- Usuario empresa queda asociado a empresa correcta.

TRABAJADORES:

- Usuario empresa puede crear trabajador.
- Trabajador queda asociado automáticamente a la empresa del usuario.
- Usuario empresa no puede crear trabajador para otra empresa.
- Usuario empresa no puede ver trabajadores de otra empresa.
- Usuario empresa no puede modificar estado.

CERTIFICADOS:

- Se puede subir certificado.
- No se pueden subir más de 3.
- Certificado comienza PENDIENTE.
- Usuario empresa no puede aprobar/rechazar certificado.
- Beca Azul sí puede aprobar/rechazar.

HABILITACIÓN:

- No se puede habilitar trabajador sin certificados.
- No se puede habilitar trabajador con certificados PENDIENTES.
- No se puede habilitar trabajador con certificados RECHAZADOS.
- Se puede habilitar cuando todos los certificados existentes están APROBADOS.
- Usuario empresa no puede habilitar trabajador.
- Planta no puede habilitar trabajador.
- Garita no puede modificar trabajador.

GARITA:

- Empresa deshabilitada => NO AUTORIZADO.
- Empresa habilitada + trabajador pendiente => NO AUTORIZADO.
- Empresa habilitada + trabajador rechazado => NO AUTORIZADO.
- Empresa habilitada + trabajador habilitado => AUTORIZADO.

SEGURIDAD:

- Intentar acceder a trabajadores de otra empresa debe devolver 404 o 403 según la implementación.
- Intentar ejecutar endpoints protegidos con otro rol debe devolver 403.
- Las acciones mutables deben requerir POST.

==================================================
25. MIGRACIONES
==================================================

Después de implementar modelos:

- Crear migraciones.
- Revisarlas.
- Ejecutarlas.

No borrar la base de datos.

No utilizar comandos destructivos como:

flush
reset_db
DROP DATABASE

No eliminar datos existentes.

Si existe información previa en occupation y hay que migrarla a role, crea una migración de datos apropiada.

==================================================
26. ADMIN
==================================================

Registrar los modelos en Django Admin:

- Empresa
- Trabajador
- Certificado
- Auditoria

Configurar list_display, search_fields, list_filter y readonly_fields donde corresponda.

El Admin no debe convertirse en la única forma de administrar el sistema; las funcionalidades principales deben existir mediante las vistas del sistema.

==================================================
27. ARCHIVOS
==================================================

Verificar settings para:

MEDIA_URL
MEDIA_ROOT

Configurar correctamente la gestión de archivos en desarrollo.

En urls.py principal, configurar media serving solamente para DEBUG si corresponde.

No almacenar archivos subidos directamente dentro de static.

==================================================
28. CALIDAD DEL CÓDIGO
==================================================

Quiero código limpio y mantenible.

Evitar:

- lógica de negocio duplicada
- consultas repetidas innecesariamente
- lógica sensible únicamente en templates
- empresa_id recibido del formulario para usuarios empresa
- estados modificables desde formularios que no correspondan
- vistas funcionales
- código innecesario

Usar:

- select_related
- prefetch_related
- get_queryset()
- mixins reutilizables
- métodos de dominio como puede_habilitar() y esta_autorizado
- transacciones cuando una operación modifique varias entidades
- mensajes de Django para feedback al usuario

==================================================
29. ORDEN DE IMPLEMENTACIÓN
==================================================

Implementa en este orden:

FASE 1
Analizar proyecto existente.

FASE 2
Adaptar User.

FASE 3
Crear/adaptar Empresa.

FASE 4
Crear Trabajador.

FASE 5
Crear Certificado.

FASE 6
Crear Auditoria.

FASE 7
Crear Forms.

FASE 8
Crear mixins de permisos.

FASE 9
Crear CBVs.

FASE 10
Crear URLs.

FASE 11
Crear templates.

FASE 12
Crear dashboards.

FASE 13
Crear consulta de Garita.

FASE 14
Crear tests.

FASE 15
Ejecutar migraciones.

FASE 16
Ejecutar tests.

FASE 17
Corregir todos los errores.

==================================================
30. MUY IMPORTANTE: ANTES DE CODIFICAR
==================================================

Primero inspecciona:

- estructura de carpetas
- settings.py
- INSTALLED_APPS
- AUTH_USER_MODEL
- User actual
- UserManager
- urls.py
- templates existentes
- modelos existentes
- forms existentes
- views existentes
- dependencias instaladas
- sistema de autenticación actual

Después explícame brevemente:

1. Qué encontraste.
2. Qué archivos vas a modificar.
3. Qué archivos vas a crear.
4. Si detectaste conflictos con el modelo User actual.

Luego implementa.

NO te quedes solamente en el análisis: después del análisis debes realizar la implementación completa.

==================================================
RESULTADO ESPERADO
==================================================

Al terminar debo tener un sistema funcional donde:

BECA AZUL
    ↓
crea Empresa
    ↓
crea Usuario Empresa
    ↓
Usuario Empresa registra Trabajador
    ↓
sube hasta 3 certificados
    ↓
Trabajador queda PENDIENTE
    ↓
Beca Azul revisa certificados
    ↓
aprueba/rechaza certificados
    ↓
si todo está correcto
    ↓
Trabajador HABILITADO
    ↓
Garita consulta
    ↓
Empresa habilitada + Trabajador habilitado
    ↓
AUTORIZADO

La seguridad de este flujo debe estar implementada en backend con Django CBV y no depender solamente de la interfaz.