# Automatización de producción

## Idea general
La actualización diaria debe ejecutarse desde GitHub Actions o un sistema equivalente gratuito.

## Cadencia sugerida
- diaria para BOE, BDNS y fuentes oficiales de novedades;
- semanal para ciertos repositorios o datasets grandes si no cambian a diario;
- publicación solo tras validación completa.

## Pasos
1. checkout del repositorio;
2. ejecutar `tools/comprobar_fuentes.py`;
3. ejecutar sincronización de repositorios/fallbacks;
4. refrescar datos si procede;
5. regenerar páginas y SEO;
6. validar;
7. commit y despliegue.
