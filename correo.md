# Envío de reportes por correo

El proyecto usa Django. Actualmente el botón **Exportar a PDF** solo imprime el reporte desde el navegador; para enviarlo como archivo adjunto se necesita generar el PDF desde Django y enviarlo por SMTP.

## 1. Cuenta remitente

Se recomienda usar una cuenta exclusiva para el sistema, por ejemplo:

```text
reportes@tudominio.com
```

Se necesitarán estos datos del proveedor de correo:

- Correo remitente
- Contraseña o contraseña de aplicación
- Servidor SMTP
- Puerto SMTP
- Tipo de seguridad: TLS o SSL

Ejemplo para Gmail:

```text
Servidor: smtp.gmail.com
Puerto: 587
Seguridad: TLS
Usuario: tu_correo@gmail.com
Contraseña: contraseña de aplicación
```

Gmail requiere activar la verificación en dos pasos y crear una contraseña de aplicación.

## 2. Variables en `.env`

```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=tu_correo@gmail.com
EMAIL_HOST_PASSWORD=tu_contraseña_de_aplicacion
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
DEFAULT_FROM_EMAIL=tu_correo@gmail.com
REPORTES_EMAILS=correo1@ejemplo.com,correo2@ejemplo.com
```

La contraseña no debe escribirse directamente en `settings.py` ni subirse al repositorio.

## 3. Configuración de Django

En `beca_azul2026/settings.py` se deben conectar las variables del `.env` con estas opciones:

- `EMAIL_BACKEND`
- `EMAIL_HOST`
- `EMAIL_PORT`
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`
- `EMAIL_USE_TLS` o `EMAIL_USE_SSL`
- `DEFAULT_FROM_EMAIL`

## 4. Generación del PDF

Para enviar el reporte como adjunto hay que:

- Generar el reporte en el servidor.
- Convertir la plantilla HTML a PDF.
- Adjuntar el PDF al correo.
- Enviar el correo al destinatario configurado.

El proyecto ya tiene `xhtml2pdf` instalado, por lo que probablemente no se necesita otra librería.

## 5. Decisiones funcionales

Hay que definir si se quiere:

- Enviar siempre al correo fijo configurado.
- Permitir escribir el correo antes de enviar.
- Permitir varios destinatarios.
- Enviar el reporte seleccionado: vencimientos, trabajadores o empresas.
- Enviar el reporte filtrado según el usuario y su empresa.

## 6. Seguridad

La funcionalidad debe validar que:

- Solo los roles autorizados puedan enviar reportes.
- Un usuario empresa no pueda enviar información de otra empresa.
- El destinatario tenga un formato válido.
- La contraseña SMTP no quede expuesta.
- Se controle el tamaño del archivo adjunto.
- Se muestre un mensaje cuando el envío sea exitoso o falle.

La opción recomendada es usar una cuenta SMTP exclusiva, configurar las variables en `.env`, generar el PDF desde Django y añadir un botón **Enviar por correo** junto al botón actual de exportación.
