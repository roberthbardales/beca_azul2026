# Plan: Mejoras a los módulos Empresa y Trabajador

## Contexto
El sistema hoy tiene CRUD completo de Empresa y Trabajador (con Certificados mediante
formset inline), todo con permisos de Administrador. Ya hay: búsqueda, filtros por
estado/empresa, paginación, validación de RUC, DNI único por empresa, validación de
archivos PDF/tamaño.

## A. Mejoras al módulo Empresa
1. **Más campos de identificación/contacto**: razon_social, representante_legal,
   rubro/giro, fecha_inicio_contrato, fecha_fin_contrato, correo_alternativo.
   Validación del RUC con dígito de verificación (SUNAT).
2. **Vigencia de contrato** [IMPLEMENTADO]: campos fecha_inicio/fecha_fin, aviso de
   contratos por vencer (30 días) y vencidos en el dashboard.
3. **Trabajadores por estado en el detalle** [IMPLEMENTADO]: tabla resumen por estado
   + lista de trabajadores en empresa_detalle.
4. **Reporte/exportación**: exportar empresas y reportes por empresa a Excel/CSV/PDF.
5. **Usuario empresa al crear empresa**: flujo guiado para vincular/crear el
   usuario_empresa al momento de crear la empresa.
6. **Historial de cambios**: registrar quién/cuándo activó/desactivó/editó cada empresa.
7. **Estadísticas en el listado**: columnas con número de trabajadores y estado agregado.

## B. Mejoras al módulo Trabajador
1. **Más datos personales/laborales** [IMPLEMENTADO]: fecha_nacimiento, genero,
   correo, tipo_documento (DNI/CE/Pasaporte), fecha_ingreso, tipo_contrato,
   area/turno, foto. Validaciones: DNI de 8 dígitos, fechas no futuras.
2. **Gestión de Certificados mejorada** [IMPLEMENTADO]: límite máx. 3 (backend +
   JS), estado_vigencia (Vigente/Vencido/Próximo a vencer/Sin vencimiento),
   alertas de vencimiento en dashboard (30/60 días), CRUD individual de
   certificados tras crear el trabajador.
3. **Estado automático / semáforo** [IMPLEMENTADO]: semaforo del trabajador
   derivado de sus certificados (rojo/amarillo/verde/gris) mostrado en listado,
   detalle y admin.
4. **Búsqueda avanzada** [IMPLEMENTADO]: filtros por texto (DNI, nombre, cargo,
   área, empresa), estado, tipo de documento, empresa, rango de fechas de ingreso
   y alerta de certificados (vencidos / 30 / 60 días), con paginación que
   conserva los filtros.
5. **Importación masiva**: CSV/Excel con validaciones y detección de duplicados.
6. **Exportación**: CSV/Excel/PDF de trabajadores filtrados.
7. **Vista previa de documentos**: visualizar PDFs en línea.
8. **Alertas de duplicados entre empresas**: mismo DNI en otra empresa.

## C. Mejoras transversales
- CRUD de Certificado independiente (crear/editar/eliminar) además del formset. [IMPLEMENTADO]
- Mensajes/validaciones más claros.
- Testing de las nuevas reglas (límite 3 certificados, RUC, vencimientos).
- Proteger cambios de estado con reglas de negocio en backend.

## Nota de implementación
- Sección A: ítems 2 y 3 implementados (vigencia de contrato y trabajadores por
  estado en detalle de empresa). Migración `control.0003` aplicada.
- Sección B: ítems 1, 2, 3 y 4 implementados (datos laborales, gestión de
  certificados, semáforo y búsqueda avanzada). Migración `control.0004`
  aplicada (campos nuevos del trabajador).
- Sección C: CRUD independiente de certificado implementado
  (certificado_crear/editar/eliminar).