Actúa como un desarrollador senior especializado en Django, Python, Tailwind CSS y aplicaciones web mantenibles.

Tengo una aplicación Django que ya está funcionando. Quiero que revises el código antes de realizar cambios.

Mi objetivo es mantener una arquitectura Django limpia, utilizar vistas basadas en clases (Class-Based Views / CBV) correctamente y seguir buenas prácticas de seguridad, mantenibilidad, rendimiento y reutilización.

## 1. Primero analiza, no modifiques

Antes de proponer código nuevo, revisa la estructura y detecta:

- Errores reales.
- Malas prácticas.
- Código duplicado.
- Código innecesario.
- Problemas de seguridad.
- Problemas de rendimiento.
- Consultas N+1.
- Responsabilidades mal ubicadas.
- Lógica de negocio dentro de views o templates.
- URLs hardcodeadas.
- Validaciones insuficientes.
- Problemas de autorización o permisos.
- Código difícil de mantener.
- Uso incorrecto o innecesario de vistas basadas en funciones.

No cambies código únicamente por preferencia personal. Si el código actual es correcto, mantenible y sigue buenas prácticas, indícalo y no lo reescribas innecesariamente.

## 2. Revisa la arquitectura Django

Comprueba:

- models.py
- views.py
- urls.py
- forms.py
- admin.py
- templates
- static
- configuración
- servicios/utilidades si existen
- tests

Evalúa si cada responsabilidad está ubicada correctamente.

No agregues capas como services.py, repositories, managers, mixins o utilities salvo que solucionen un problema concreto de diseño o reutilización.

## 3. Revisa las vistas

Quiero utilizar Class-Based Views siempre que sean apropiadas.

Prioriza las vistas genéricas de Django:

- ListView
- DetailView
- CreateView
- UpdateView
- DeleteView
- FormView
- TemplateView

Utiliza LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin u otros mixins cuando sean apropiados.

Evita utilizar View directamente si una Generic Class-Based View resuelve mejor el problema.

Verifica correctamente:

- model
- form_class
- template_name
- context_object_name
- success_url
- get_queryset()
- get_context_data()
- form_valid()
- get_object()

No sobreescribas métodos si Django ya proporciona el comportamiento necesario.

Si encuentras una Function-Based View, determina primero si convertirla a CBV realmente mejora el código. Si no aporta una ventaja clara, explícalo.

## 4. Revisa models.py

Comprueba:

- tipos de campos
- ForeignKey
- OneToOneField
- ManyToManyField
- on_delete
- related_name
- null y blank
- choices
- defaults
- constraints
- índices
- Meta
- __str__()
- validaciones

Identifica posibles problemas de integridad de datos.

## 5. Revisa consultas y rendimiento

Busca especialmente:

- consultas N+1
- consultas repetidas
- acceso innecesario a la base de datos
- filtros ineficientes

Evalúa cuándo corresponde utilizar:

- select_related()
- prefetch_related()
- exists()
- count()
- annotate()
- aggregate()

No realices optimizaciones prematuras; explica qué problema resuelve cada optimización.

## 6. Revisa forms.py

Comprueba:

- ModelForm
- fields / exclude
- widgets
- clean()
- clean_<field>()
- validaciones
- mensajes de error

La seguridad y validación no deben depender únicamente de HTML, JavaScript o Tailwind.

## 7. Revisa seguridad

Busca:

- problemas de autorización
- acceso a objetos pertenecientes a otros usuarios
- endpoints sin protección
- CSRF
- datos enviados por el usuario sin validar
- exposición de información sensible
- secretos hardcodeados
- configuración insegura
- DEBUG inapropiado para producción

Diferencia claramente autenticación de autorización.

## 8. Revisa templates y Tailwind CSS

Comprueba que los templates:

- utilicen herencia correctamente
- tengan un base.html coherente
- reutilicen componentes cuando tenga sentido
- utilicen {% url %} en lugar de URLs hardcodeadas
- no contengan lógica de negocio
- mantengan una estructura clara

Para Tailwind CSS:

- conserva el diseño existente salvo que exista un problema
- evita duplicación excesiva
- mantén consistencia visual
- no introduzcas CSS personalizado si Tailwind resuelve adecuadamente el caso
- no cambies clases únicamente por preferencia estética

## 9. Revisa configuración

Comprueba:

- SECRET_KEY
- DEBUG
- ALLOWED_HOSTS
- variables de entorno
- STATIC_URL / STATIC_ROOT
- MEDIA_URL / MEDIA_ROOT
- configuración de base de datos
- logging
- configuración de producción

No muestres ni copies secretos reales.

## 10. Revisa calidad del código

Comprueba:

- PEP 8
- nombres descriptivos
- imports
- responsabilidades
- duplicación
- complejidad innecesaria
- manejo de excepciones
- type hints cuando aporten claridad
- comentarios innecesarios
- documentación necesaria

Prioriza código Django idiomático y simple sobre abstracciones innecesarias.

## Formato de respuesta

Primero dame un diagnóstico.

Clasifica cada hallazgo como:

CRÍTICO — seguridad, pérdida de datos o fallo grave.

IMPORTANTE — arquitectura, rendimiento, mantenibilidad o comportamiento incorrecto.

MEJORA — refactorización recomendable pero no necesaria.

CORRECTO — código que está bien y debería mantenerse.

Para cada problema indica:

1. Archivo.
2. Código o sección afectada.
3. Problema encontrado.
4. Por qué es un problema.
5. Solución recomendada.
6. Código corregido, cuando corresponda.

No reescribas archivos completos si solamente es necesario cambiar una parte.

Mantén el comportamiento actual de la aplicación salvo que ese comportamiento sea incorrecto o inseguro.

Cuando no tengas suficiente contexto para determinar si algo es un error, indícalo en lugar de asumir.

Al terminar, proporciona un orden recomendado de implementación de las correcciones, empezando por seguridad y errores funcionales, seguido de arquitectura, rendimiento y finalmente mejoras de estilo.