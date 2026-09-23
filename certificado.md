# Certificados de requisitos del trabajador

## Objetivo

Permitir que el usuario registre un certificado para cada requisito:

- SCTR
- Inducción
- Cursos
- Aptitud médica

Cada certificado debe incluir su archivo PDF y la fecha de vigencia o vencimiento.

## Diseño recomendado

Reutilizar el modelo `Certificado` existente y agregarle un tipo de certificado. No es recomendable crear cuatro archivos y cuatro fechas directamente en `Trabajador`, porque cada documento puede tener información y ciclos de vigencia diferentes.

El modelo debería incluir un campo como el siguiente:

```python
class Certificado(TimeStampedModel):
    SCTR = 'SCTR'
    INDUCCION = 'INDUCCION'
    CURSOS = 'CURSOS'
    APTITUD_MEDICA = 'APTITUD_MEDICA'

    TIPO_CHOICES = (
        (SCTR, 'SCTR'),
        (INDUCCION, 'Inducción'),
        (CURSOS, 'Cursos'),
        (APTITUD_MEDICA, 'Aptitud médica'),
    )

    trabajador = models.ForeignKey(
        Trabajador,
        on_delete=models.CASCADE,
        related_name='certificados'
    )
    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES)
    nombre = models.CharField(max_length=200)
    fecha_emision = models.DateField()
    fecha_vencimiento = models.DateField()
    archivo = models.FileField(upload_to=certificado_upload_path)
```

## Un certificado por requisito

Para evitar que un trabajador tenga dos certificados del mismo tipo, agregar una restricción única:

```python
class Meta:
    constraints = [
        models.UniqueConstraint(
            fields=('trabajador', 'tipo'),
            name='un_certificado_por_tipo_trabajador'
        ),
    ]
```

## Formulario

El formulario debe incluir:

```python
fields = (
    'tipo',
    'nombre',
    'fecha_emision',
    'fecha_vencimiento',
    'archivo',
)
```

La pantalla debe mostrar:

- Tipo: SCTR, Inducción, Cursos o Aptitud médica.
- Nombre del certificado.
- Fecha de emisión.
- Fecha de vencimiento o vigencia.
- Archivo PDF.

El archivo y la fecha de vencimiento deberían ser obligatorios si todos los documentos tienen una fecha de expiración.

## Vista del trabajador

En el detalle del trabajador se puede mostrar una tabla como esta:

| Documento | Archivo | Vigencia | Estado |
|---|---|---|---|
| SCTR | Ver PDF | 30/09/2026 | Vigente |
| Inducción | Ver PDF | 15/10/2026 | Vigente |
| Cursos | Ver PDF | 01/08/2026 | Vencido |
| Aptitud médica | Ver PDF | 20/12/2026 | Vigente |

El estado puede calcularse comparando `fecha_vencimiento` con la fecha actual:

- Vigente: la fecha aún no venció.
- Vencido: la fecha ya pasó.
- Próximo a vencer: vence dentro del período configurado.

## Archivos que se deben modificar

- `applications/control/models.py`
- `applications/control/forms.py`
- `templates/control/certificados/form.html`
- `templates/control/trabajadores/detalle.html`
- Crear una nueva migración de Django.
- Actualizar las pruebas existentes.

## Ventajas

- Cada requisito tiene su propio certificado.
- Cada certificado puede tener una vigencia diferente.
- Se puede controlar fácilmente qué documentos están vencidos.
- Se evita duplicar campos dentro de `Trabajador`.
- Es posible reemplazar un certificado específico sin afectar los demás.
