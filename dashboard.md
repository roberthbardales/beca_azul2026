# Opciones para el dashboard por tipo de usuario

Actualmente existen estos roles:

- **Administrador**
- **Beca Azul**
- **Usuario Planta**
- **Usuario Empresa**
- **Usuario Garita**

El dashboard actual es global para Administrador, Beca Azul y Planta. Usuario Empresa es enviado directamente a sus trabajadores y Garita no tiene dashboard.

## Opción 1: Dashboard por rol

| Rol | Información común | Información adicional |
|---|---|---|
| Administrador | Resumen general | Empresas, usuarios, trabajadores, certificados e incidencias |
| Beca Azul | Resumen general | Gestión completa, alertas, incidencias y estadísticas |
| Usuario Planta | Resumen operativo | Trabajadores, certificados e incidencias de empresas activas |
| Usuario Empresa | Resumen de su empresa | Sus trabajadores, certificados vencidos y próximos a vencer |
| Usuario Garita | Acceso operativo | Búsqueda/verificación de trabajadores y estado de habilitación |

Elementos comunes:

- Nombre del usuario y empresa asociada.
- Alertas importantes.
- Certificados vencidos o próximos a vencer.
- Accesos rápidos.
- Estado general de trabajadores visibles para ese usuario.

La información debe filtrarse en el servidor según el usuario. No basta con ocultar tarjetas en la plantilla.

## Opción 2: Un solo dashboard configurable

Se mantiene una sola plantilla, pero cada rol recibe diferentes tarjetas.

```text
Administrador:
[Empresas] [Trabajadores] [Certificados] [Incidencias]

Usuario Empresa:
[Mis trabajadores] [Certificados vencidos] [Trabajadores habilitados]

Garita:
[Trabajadores habilitados] [Búsqueda rápida]
```

Ventajas:

- Menos duplicación de código.
- Más fácil mantener el diseño.
- Permite agregar o quitar módulos por rol.

## Opción 3: Dashboard con permisos granulares

Además del rol, se definen permisos específicos:

- Ver empresas.
- Ver todos los trabajadores.
- Ver trabajadores de su empresa.
- Ver certificados.
- Gestionar incidencias.
- Administrar usuarios.
- Ver estadísticas globales.

Es la opción más flexible si posteriormente habrá nuevos tipos de usuario, pero requiere más trabajo inicial.

## Recomendación

Usar la **Opción 2 con permisos de la Opción 3**:

- Una estructura visual común.
- Tarjetas y módulos diferentes por rol.
- Filtros obligatorios por empresa.
- Permisos controlados en las vistas y consultas, no solo en HTML.

### Distribución propuesta

#### Administrador y Beca Azul

- Resumen global.
- Empresas.
- Trabajadores.
- Certificados.
- Incidencias.
- Usuarios.

#### Usuario Planta

- Trabajadores de empresas activas.
- Certificados próximos a vencer.
- Incidencias.
- Estadísticas operativas.

#### Usuario Empresa

- Trabajadores de su empresa.
- Estado de habilitación.
- Certificados vencidos.
- Certificados próximos a vencer.
- Incidencias de su empresa.

#### Usuario Garita

- Búsqueda de trabajador.
- Estado habilitado/deshabilitado.
- Validación rápida de certificados.

## Decisiones pendientes

1. ¿Usuario Planta debe ver datos de todas las empresas o solo algunas?
2. ¿Garita debe tener un dashboard o únicamente una pantalla de búsqueda?
3. ¿Usuario Empresa podrá crear o editar trabajadores, o solo consultarlos?
4. ¿Las incidencias serán visibles para todos los roles o solo para Beca Azul y Planta?
5. ¿Administrador y Beca Azul tendrán exactamente los mismos datos?
