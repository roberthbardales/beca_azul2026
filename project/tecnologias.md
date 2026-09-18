# Tecnologias del Proyecto

## Stack principal

- **React 18.3.1:** biblioteca para construir la interfaz de usuario.
- **TypeScript 5.5.3:** tipado estatico para JavaScript.
- **Vite 5.4.2:** servidor de desarrollo y herramienta de compilacion.
- **Tailwind CSS 3.4.1:** framework de estilos basado en clases utilitarias.

## Librerias

- **Lucide React 0.446.0:** iconos para la interfaz.
- **Supabase JS 2.57.4:** cliente para servicios de Supabase. Esta instalado, pero no se utiliza actualmente en el codigo.
- **PostCSS 8.4.35** y **Autoprefixer 10.4.18:** procesamiento y compatibilidad de CSS.

## Calidad de codigo

- **ESLint 9.9.1:** analisis estatico de codigo.
- **typescript-eslint 8.3.0:** reglas de ESLint para TypeScript.
- **eslint-plugin-react-hooks:** validacion de reglas de hooks de React.
- **eslint-plugin-react-refresh:** soporte para React Fast Refresh durante el desarrollo.

## Datos actuales

La aplicacion utiliza datos de ejemplo definidos localmente en `src/data/mockData.ts`, incluyendo empleados, departamentos, puestos, certificaciones y actividad reciente.

## Comandos disponibles

```bash
npm run dev       # Inicia el servidor de desarrollo
npm run build     # Genera la version de produccion
npm run preview   # Previsualiza la compilacion de produccion
npm run lint      # Ejecuta ESLint
npm run typecheck # Verifica los tipos de TypeScript
```
