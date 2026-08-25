# Brújula Municipal v1.5 · Agency Ultra + Production Hotfix

## Por qué esta entrega es un overlay
El repositorio que está fallando en GitHub ya contiene la versión funcional completa: catálogos, radares, fichas SEO, localidades, herramientas y pipeline. Para no perder nada, v1.5 se aplica **encima** de ese repositorio.

## Rediseño visual
- Hero oscuro editorial, con mayor contraste y presencia de producto premium.
- Mapa de España contextual en Inicio/Mi localidad/Inteligencia/Cockpit/Ejecutivo.
- Pin exacto cuando el perfil aporta latitud/longitud; si no, se indica que la posición es aproximada.
- Command Center con prioridades, micrográfico y red de dependencias.
- Módulos de datos con jerarquía enterprise, menos repetición de tarjetas genéricas.
- Nueva capa de navegación y estados visuales.
- Aviso premium de copia local para evitar pérdida de configuración.
- `Ctrl/Cmd + K` lleva el foco al buscador global cuando existe.

## Corrección del fallo de publicación
El error final del workflow no viene de las páginas públicas, sino de un HTML dentro de `tools/cache/repos/osm-validador-ine-tmp/`.

v1.5 corrige esto de tres formas:
1. `validar_sitio.py` ejecuta su auditoría con `tools/cache` temporalmente fuera de la raíz del repositorio.
2. `generar_accesibilidad.py` hace lo mismo.
3. `sincronizar_repositorios.py` elimina siempre carpetas `*-tmp` al terminar.

## MITECO
Los enlaces públicos de `DescargaFichero?f=...zip` son páginas HTML de descarga/confirmación, no necesariamente un ZIP crudo. Se incluye una capa de compatibilidad que:
- usa cabeceras de navegador;
- mantiene cookies;
- detecta formulario de descarga;
- intenta enviarlo y devolver el ZIP al importador original.

## INE
La fuente oficial 31241 ofrece CSV separado por `;`, CSV tabulado, XLSX y JSON. El paquete documenta la conveniencia de usar el CSV completo como fallback del API si el importador obtiene un conjunto incompleto.
