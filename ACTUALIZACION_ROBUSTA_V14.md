# Actualización robusta v1.4

## Secuencia
1. comprobar fuentes;
2. abortar si falla una crítica;
3. conservar snapshot si falla una auxiliar;
4. sincronizar repositorios o fallbacks;
5. descargar o procesar datasets válidos;
6. sanear salida y UI;
7. regenerar SEO;
8. validar;
9. publicar.

## Problemas abordados
- MITECO con URLs duras → descubrimiento previo;
- INE renta incompleta → validación por umbral;
- PAe con bucles 302 → fuente vigilada;
- fallback OSM con sparse innecesario → descarga directa;
- BOE con ruido técnico → saneado en origen.
