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

8. **Cursos obligatorios por trabajador**
   - La obligatoriedad no se configura desde los formularios de certificados.
   - Beca Azul la activa o desactiva desde el detalle del trabajador mediante un interruptor.
   - Activar la obligación no crea un certificado ni un PDF.
   - Si falta la constancia de un curso obligatorio, el detalle muestra `Falta subir`.

## Comprobaciones manuales

- Crear dos certificados de inducción para el mismo trabajador.
- Crear dos certificados de aptitud médica para el mismo trabajador.
- Editar un certificado existente sin cambiar su tipo.
- Editar SCTR modificando solo las fechas.
- Editar SCTR subiendo un nuevo archivo.
- Crear una homologación sin archivo.
- Introducir una fecha de vencimiento anterior a la fecha de emisión.

## Verificación automatizada

- Las pruebas automatizadas disponibles deben ejecutarse con `python manage.py test`.
- `python manage.py check`: sin errores.
