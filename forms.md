# Cambios en los formularios

## Procesos modificados

1. **Crear certificados de trabajadores**
   - Se valida que no exista otro certificado del mismo tipo para el trabajador.
   - Aplica para inducción, aptitud médica y certificados no duplicables.

2. **Crear certificados desde una empresa**
   - El formulario recibe explícitamente el trabajador correspondiente.
   - También evita certificados duplicados.

3. **Editar certificados**
   - Se conserva la validación de duplicados.
   - El certificado que se está editando se excluye de la comprobación.

4. **Crear y editar SCTR**
   - Al editar solo las fechas, se conserva el archivo PDF existente.
   - Las fechas se actualizan correctamente.
   - Al crear un SCTR, el archivo continúa siendo obligatorio.

5. **Crear y editar homologación**
   - Se reutiliza la lógica común de `SCTRForm`.
   - Se mantiene el tipo de certificado y el mensaje específico de homologación.

6. **Validación de fechas**
   - Los certificados usan el mensaje:
     `La fecha de vencimiento no puede ser anterior a la fecha de emisión.`

7. **Formset de cursos**
   - Se mantiene el comportamiento actual.
   - La validación del modelo se omite durante `_post_clean()` porque el trabajador se asigna después, al guardar el formset.

## Comprobaciones manuales

- Crear dos certificados de inducción para el mismo trabajador.
- Crear dos certificados de aptitud médica para el mismo trabajador.
- Editar un certificado existente sin cambiar su tipo.
- Editar SCTR modificando solo las fechas.
- Editar SCTR subiendo un nuevo archivo.
- Crear una homologación sin archivo.
- Introducir una fecha de vencimiento anterior a la fecha de emisión.

## Verificación automatizada

- `python manage.py test`: 19 tests OK.
- `python manage.py check`: sin errores.
