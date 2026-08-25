# Brújula Municipal v1.5 · Overlay de producción

Este paquete **NO sustituye** el repositorio completo. Se copia encima del repositorio actual para conservar:

- catálogos y JSON;
- 175/200 proyectos según tu rama;
- 27 obligaciones;
- BDNS/BOE;
- 222 fichas SEO;
- 38.161 localidades generadas;
- herramientas, comparables, playbooks y demás módulos.

## Qué corrige

### Fallo fatal de validación
El log demuestra que `validar_sitio.py` y la auditoría de accesibilidad están tratando `tools/cache/repos/osm-validador-ine-tmp/index.html` como una página pública. Eso provoca los tres errores finales y aborta el commit.

El parche envuelve temporalmente `validar_sitio.py` y `generar_accesibilidad.py`: durante esas fases mueve `tools/cache` fuera de la raíz del repositorio, ejecuta la herramienta y restaura la caché al terminar.

También garantiza que `sincronizar_repositorios.py` borre cualquier carpeta `*-tmp` al finalizar.

## Qué mejora visualmente

- capa global `agency-ultra-v15.css`;
- capa global `agency-ultra-v15.js`;
- hero oscuro editorial y más contundente;
- mapa de España en Inicio/Mi localidad/Inteligencia/Cockpit/Ejecutivo cuando corresponde;
- pin calculado con latitud/longitud si el perfil las aporta;
- Command Center visual con prioridades, micrográfico y red de dependencias;
- jerarquía de producto enterprise, menos estética de portal;
- aviso premium de copia local;
- acceso `Ctrl/Cmd + K` al buscador cuando existe.

## Cómo aplicarlo desde GitHub

1. Descomprime el paquete.
2. Sube su contenido **encima** de tu repositorio actual, sin borrar los demás archivos.
3. Haz commit.
4. En Actions aparecerá `Aplicar Brújula v1.5 visual + hotfix`.
5. Ejecuta ese workflow una sola vez.
6. Después ejecuta tu workflow normal `Actualizar datos de Brújula Municipal` con `full`.

## Importante
No subas una carpeta exterior `brujula-v15-overlay/`; sube su contenido directamente a la raíz del repositorio.
