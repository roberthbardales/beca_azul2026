# Correcciones pendientes

Este archivo contiene únicamente temas técnicos que todavía no forman parte de
las funcionalidades actuales. No sustituye las reglas de `contexto.md` ni
`permisos.md`.

## Reemplazo seguro de certificados

Revisar el flujo de reemplazo de archivos para conservar el archivo anterior si
falla el guardado del nuevo. Las operaciones deben mantener consistencia entre
base de datos y storage.

## Conflictos de cursos

Validar de forma explícita los conflictos cuando se cambia la categoría de un
certificado y ya existe otro certificado para la misma combinación trabajador y
curso.

## Consultas del dashboard

Revisar la cantidad de consultas independientes cuando aumente el volumen de
empresas, trabajadores y certificados.

## Organización del código

`applications/control/views.py` concentra dashboard, empresas, trabajadores,
certificados e incidencias. Puede dividirse por funcionalidad si continúa
creciendo.

## Pruebas pendientes

Ampliar las pruebas automatizadas para cubrir específicamente:

- Activación y desactivación de cursos obligatorios.
- Restricción de la operación a Beca Azul.
- Rechazo de cursos no pertenecientes al catálogo fijo.
- Mensaje `Falta subir` cuando falta una constancia obligatoria.
- Conservación del certificado al desactivar la obligación.
