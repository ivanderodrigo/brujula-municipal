# Actualización robusta v1.2

## Principio
Nunca empezar una actualización importante a ciegas.

## Secuencia diaria
1. `comprobar_fuentes.py`: prueba todos los endpoints con una muestra pequeña.
2. Si BOE o BDNS fallan: abortar antes de tocar datos.
3. Sincronizar repositorios externos que hayan cambiado o estén vencidos.
4. Ejecutar importadores según cadencia.
5. Conservar última copia válida de fuentes opcionales que fallen.
6. Regenerar benchmark cuando corresponda.
7. Regenerar SEO y fichas estáticas.
8. Aplicar accesibilidad estructural.
9. Ejecutar `validar_sitio.py`.
10. Solo entonces GitHub hace commit.

## Cadencias
- BOE: diaria.
- BDNS: diaria.
- Novedades oficiales: diaria.
- Repositorios externos: semanal por defecto.
- Localidades: mensual.
- Indicadores territoriales: semestral, salvo `full`.
- Renta INE: semestral, salvo `full`.

## Caché
GitHub Actions conserva `tools/cache` mediante una clave semanal. Así se evitan descargas masivas repetitivas y el repositorio Git no crece con archivos externos que no forman parte del producto publicado.
