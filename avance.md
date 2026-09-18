# Avance

## Permisos por roles implementados

### Reglas de acceso

| Rol | Gestión de usuarios | Empresas | Trabajadores |
|---|---|---|---|
| `ADMINISTRADOR` (`0`) | Crea/edita/elimina/ve usuarios `BECA_AZUL`, `PLANTA`, `GARITA` | Solo ver | Solo ver |
| `BECA_AZUL` (`1`) | Crea/edita/elimina/ve usuarios `USUARIO_EMPRESA` | Ver + administrar (crear, editar, activar/desactivar, eliminar) | Ver + administrar (crear, editar, estado, activar/desactivar, eliminar, certificados) |
| `USUARIO_EMPRESA` (`3`) | — | — | Ver + administrar trabajadores de SU empresa únicamente |
| `PLANTA` (`2`) / `GARITA` (`4`) | — | — | Sin acceso a paneles |

- `ADMINISTRADOR`: puede ver todos los paneles (usuarios, empresas, trabajadores) pero solo administra el panel de usuarios.
- `USUARIO_EMPRESA`: al entrar al panel general es redirigido a su lista de trabajadores.
- `USUARIO_EMPRESA` no puede ver usuarios ni empresas, y no puede ver ni modificar trabajadores de otras empresas (devuelve 404).

### Archivos modificados

- `applications/users/mixins.py`
  - Nuevos mixins: `VerEmpresasMixin`, `AdministrarEmpresasMixin`, `VerTrabajadoresMixin`, `AdministrarTrabajadoresMixin`, `TrabajadorEmpresaPermisoMixin`.
  - `GestionUsuariosPermisoMixin` (ADMINISTRADOR + BECA_AZUL) se conserva para el panel de usuarios.

- `applications/users/forms.py`
  - `UsuarioGestionForm` recibe `current_user` y limita las opciones de rol según quien crea/edita:
    - `BECA_AZUL` → solo `USUARIO_EMPRESA`.
    - `ADMINISTRADOR` → solo `BECA_AZUL`, `PLANTA`, `GARITA`.
    - Fallback → `PLANTA`, `USUARIO_EMPRESA`, `GARITA`.
  - La validación de `ChoiceField` rechaza roles fuera de las opciones permitidas.

- `applications/users/views.py`
  - Listados, detalle, edición, toggle, eliminación y reset de contraseña filtrados por rol:
    - `BECA_AZUL` ve solo `USUARIO_EMPRESA`.
    - `ADMINISTRADOR` ve solo `BECA_AZUL`, `PLANTA`, `GARITA`.
  - `UsuarioPasswordResetView` ahora usa `GestionUsuariosPermisoMixin` (antes solo ADMINISTRADOR).

- `applications/control/views.py`
  - Empresas: vistas de solo lectura para ADMINISTRADOR + BECA_AZUL (`VerEmpresasMixin`); CRUD solo BECA_AZUL (`AdministrarEmpresasMixin`).
  - Trabajadores: vistas de solo lectura (`VerTrabajadoresMixin`); CRUD + certificados solo BECA_AZUL (`AdministrarTrabajadoresMixin`).
  - Nuevas vistas para `USUARIO_EMPRESA` (restringidas a su empresa):
    - `TrabajadorEmpresaListView`, `TrabajadorEmpresaDetailView`, `TrabajadorEmpresaCreateView`, `TrabajadorEmpresaUpdateView`, `TrabajadorEmpresaEstadoView`, `TrabajadorEmpresaToggleView`, `TrabajadorEmpresaDeleteView`.
    - `CertificadoEmpresaCreateView`, `CertificadoEmpresaUpdateView`, `CertificadoEmpresaDeleteView`.
  - `DashboardView`: redirige a `USUARIO_EMPRESA` a su lista de trabajadores.

- `applications/control/forms.py`
  - Nuevo `TrabajadorEmpresaForm` con empresa fija.
  - `TrabajadorForm` sin cambios (BECA_AZUL/ver).

- `applications/control/urls.py`
  - Nuevas rutas bajo `/trabajadores/empresa/...` y `/certificados/empresa/...`.

- Templates:
  - `templates/include/sidebar.html`: secciones por rol (ADMINISTRADOR y BECA_AZUL ven Administración; USUARIO_EMPRESA ve solo sus Trabajadores).
  - `templates/control/trabajadores/detalle.html`: acciones según rol y rutas según `es_empresa`.
  - `templates/control/trabajadores/form.html`: enlaces de retorno según rol.
  - `templates/control/trabajadores/lista.html` y `templates/control/empresas/lista.html`: botones de creación solo para BECA_AZUL.
  - `templates/users/usuarios/detalle.html`: restablecer contraseña disponible para ADMINISTRADOR y BECA_AZUL.
  - `templates/control/trabajadores/lista_empresa.html`: nuevo, lista de trabajadores para USUARIO_EMPRESA.

### Verificación
- Usuario `BECA_AZUL`: 200 en usuarios/empresas/trabajadores y sus creaciones.
- Usuario `ADMINISTRADOR`: 200 en listados, 403 al crear/administrar empresas y trabajadores; no puede crear `USUARIO_EMPRESA` ni `ADMINISTRADOR`.
- Usuario `USUARIO_EMPRESA`: 200 en su panel de trabajadores, 403 en usuarios/empresas/panel global, 404 sobre trabajadores de otra empresa.
- `manage.py check` y `makemigrations --check` sin errores; no requiere migraciones.

### Pendiente / nota
- El registro público (`/users/register/`) sigue permitiendo elegir cualquier rol (incluido `ADMINISTRADOR`). Recomendado: restringirlo a un rol seguro o eliminar la ruta.