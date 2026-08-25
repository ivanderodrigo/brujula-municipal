# Brújula Municipal · v0.5

Plataforma estática para inteligencia práctica municipal: localidades, oportunidades, proyectos, obligaciones, apoyo supramunicipal, casos y herramientas.

## Principio técnico

La web pública no necesita backend, base de datos cloud, funciones serverless, cuentas ni APIs de pago. Los visitantes solo descargan HTML/CSS/JS/JSON estáticos.

La actualización de datos se realiza **fuera de la web** mediante scripts Python. En producción puede ejecutarse diariamente con GitHub Actions y publicar los JSON validados mediante un único commit. Si una actualización falla, no se hace commit y el hosting conserva la última versión válida.

## Automatización v0.5

Archivo principal:

- `.github/workflows/actualizar-datos.yml`

Cadencia por defecto:

- BDNS: diaria.
- BOE: diaria.
- Localidades NGMEP: cada 30 días.

Todos los días se actualiza `data/system/last-check.json`, lo que permite mostrar al usuario la última comprobación y mantiene actividad periódica del repositorio.

El workflow también puede ejecutarse manualmente desde GitHub con tres modos:

- `daily`: respeta cadencias.
- `full`: fuerza todas las fuentes.
- `validate-only`: solo valida la versión existente.

## Publicación atómica

El orden es:

1. checkout temporal del repositorio;
2. actualización de fuentes;
3. generación de JSON e índices;
4. validación completa;
5. si TODO es correcto: commit + push;
6. si algo falla: no se publica nada.

Por ello el proveedor estático siempre recibe una versión completa y validada.

## Validaciones incluidas

`tools/validar_sitio.py` comprueba, entre otras cosas:

- todos los JSON parsean correctamente;
- mínimo 100 proyectos;
- mínimo 20 obligaciones;
- mínimo 5 oportunidades editoriales;
- catálogo nacional >= 30.000 localidades cuando se ejecuta en producción;
- cero enlaces internos rotos;
- oportunidades y obligaciones sensibles conservan fuente;
- candidatos automáticos BDNS/BOE permanecen `pending`;
- no aparecen dependencias dinámicas/backend en los assets públicos.

## Fuentes automáticas actuales

### Localidades

Prioridad:

1. ZIP oficial NGMEP del IGN/CNIG si existe una URL directa descubierta o se ha colocado en `tools/cache/`.
2. Fallback público `ENTIDADES.2025.csv` mantenido por OSM España a partir del Nomenclátor del IGN.

En el fallback la interfaz mantiene explícita la procedencia y no presenta como EATIM una entidad cuya personalidad jurídica no pueda comprobarse.

### BDNS

`tools/actualizar_bdns.py`

Genera candidatos de posible interés municipal. Ningún candidato automático se presenta como elegible ni como convocatoria abierta sin revisión.

### BOE

`tools/actualizar_boe.py`

Detecta normas consolidadas actualizadas con posible impacto municipal. Los cambios se publican únicamente como **candidatos pendientes de revisión**, nunca como nueva obligación jurídica automática.

## Respaldo local en Windows

La automatización de producción no depende del PC del mantenedor. Aun así se conservan los BAT como plan B:

- `ACTUALIZAR_TODO.bat`: fuerza todas las fuentes y valida.
- `VALIDAR_ANTES_DE_PUBLICAR.bat`: valida sin actualizar.
- `INICIAR_BRUJULA.bat`: servidor local de pruebas.

Los BAT llaman a los mismos scripts Python que GitHub Actions.

## Publicar gratis

La arquitectura es compatible con cualquier hosting que sirva archivos estáticos.

### GitHub Pages como opción inicial

1. Crear un repositorio **público**.
2. Subir esta carpeta a la rama principal.
3. En `Settings → Pages`, seleccionar publicación desde la rama principal y carpeta raíz.
4. En `Settings → Actions`, permitir que el `GITHUB_TOKEN` pueda escribir en el repositorio si la política de la cuenta lo restringe.
5. Ejecutar una vez `Actions → Actualizar datos de Brújula Municipal → Run workflow → full`.

A partir de ahí, los datos se revisan cada día y Pages publica automáticamente cada commit validado.

También puede usarse otro proveedor gratuito: basta con conectarlo al repositorio y servir el directorio raíz. No necesita Node, Python ni base de datos en producción.

## Sin secretos

El pipeline usa únicamente fuentes públicas. No necesita claves API ni variables secretas para su funcionamiento actual.

## Estructura relevante

```text
.github/workflows/actualizar-datos.yml
assets/
data/
  catalog/
  generated/
  localidades/
  system/
tools/
  actualizar_todo.py
  actualizar_localidades_cnig.py
  actualizar_bdns.py
  actualizar_boe.py
  validar_sitio.py
```

## Estado v0.5

- 112 proyectos municipales.
- 27 obligaciones prácticas base.
- Radar BDNS automático pendiente de revisión editorial.
- Radar BOE automático pendiente de revisión editorial.
- Apoyo supramunicipal con cobertura progresiva.
- Buscador nacional de localidades fragmentado bajo demanda.
- Matching local `PASS / FAIL / UNKNOWN`.
- Actualización diaria autónoma y publicación protegida por validación.
- Infraestructura pública static-first, sin coste por visitante.
