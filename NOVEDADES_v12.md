# Brújula Municipal v1.2 · Premium, robusta y accesible

## 1. Rediseño visual profundo
- Nueva portada editorial con **brújula de decisión**: necesidad → proyecto → financiación → obligaciones → ejecución.
- Jerarquía visual más limpia, espacios más generosos, navegación simplificada, mega-menú secundario y menú móvil accesible.
- Nuevo sistema de tarjetas/bento, superficies premium, contraste refinado y diseño coherente en todas las pantallas.
- Mantiene carga ligera: no depende de vídeos, fuentes web ni librerías visuales pesadas.

## 2. Organización transversal del conocimiento
Nueva sección `/explorar/`.

La información se organiza simultáneamente por:
- necesidad municipal;
- tipo de contenido.

8 macroáreas:
1. Gobierno digital.
2. Seguridad y cumplimiento.
3. Territorio y población.
4. Infraestructuras y servicios.
5. Energía y resiliencia.
6. Economía, turismo y patrimonio.
7. Vivienda y cuidados.
8. Datos e innovación.

Y cruza proyectos, financiación, obligaciones, servicios existentes, playbooks y casos reales.

## 3. Preflight obligatorio de fuentes
Nuevo `tools/comprobar_fuentes.py`.

Antes de ejecutar importadores:
1. comprueba DNS/HTTPS y respuesta;
2. sigue redirecciones;
3. comprueba código HTTP;
4. lee solo una muestra pequeña;
5. valida formato mínimo (JSON/XML/HTML/CSV);
6. registra latencia y estado en `data/generated/salud_fuentes.json`.

BOE y BDNS son **fuentes críticas**: si fallan, el pipeline aborta antes de modificar datasets.
Las fuentes de enriquecimiento pueden fallar sin eliminar la última copia válida.

## 4. Repositorios externos sincronizados con caché
Nuevo `tools/sincronizar_repositorios.py` y `data/config/repositorios_fuentes.json`.

- Consulta el commit remoto.
- Solo descarga cuando cambia o vence la cadencia.
- Usa `git clone --depth 1` y sparse checkout.
- Los repositorios se guardan en `tools/cache`, no en el Git público.
- GitHub Actions conserva el caché por semanas.
- Se publica únicamente un manifiesto ligero con commit, fecha, ficheros y finalidad.

El primer repositorio integrado es `OSM-es/validador-ine`, que Brújula utiliza como fallback del fichero `ENTIDADES.2025.csv` del NGMEP.

## 5. Protección del trabajo local
Brújula recuerda ahora que la configuración se guarda únicamente en el navegador.

El aviso explica que los datos pueden perderse al:
- borrar los datos del navegador;
- usar navegación privada;
- cambiar de navegador;
- cambiar de dispositivo.

`Mi espacio` incorpora:
- copia completa a JSON;
- restauración de copia;
- estado de la última copia;
- aviso cuando existen cambios posteriores a la copia.

La copia incluye localidad, prioridades, capacidad y elementos guardados.

## 6. Accesibilidad
- Enlace “Saltar al contenido principal”.
- Navegación móvil controlable por teclado y Escape.
- Foco `:focus-visible` de alto contraste.
- `aria-live` en resultados dinámicos.
- Regiones de tablas desplazables accesibles con teclado.
- `prefers-reduced-motion`.
- `prefers-contrast: more`.
- Tamaños táctiles mayores y tipografía más legible.
- Inyección/auditoría automática mediante `tools/generar_accesibilidad.py` para todas las páginas, incluidas las fichas SEO generadas.

## 7. Transparencia operativa
`/actualizacion/` muestra ahora:
- resultado del preflight;
- número de fuentes disponibles/no disponibles;
- fuentes críticas caídas;
- latencia de cada fuente;
- snapshots de repositorios y commit utilizado;
- novedades oficiales detectadas;
- páginas vigiladas y errores.

## 8. Pipeline v1.2

Fuente → preflight → caché/repositorios → descarga → extracción → clasificación → generación SEO → accesibilidad → validación → commit.

Nada se publica si la validación final falla.
