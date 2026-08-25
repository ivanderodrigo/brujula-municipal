# Fuentes revisadas en v1.5

## MITECO
La página oficial de datos demográficos publica los Shapefile de población, variación, densidad, edad media y mayores de 65 años. Los enlaces llevan a `gis.miteco.gob.es/descargas/app/DescargaFichero?f=...`, que presenta una página de descarga en HTML antes de entregar el fichero.

Por eso un importador no debe asumir que esa URL responde directamente con bytes ZIP.

## INE
Tabla 31241 · Indicadores de renta media y mediana.

Fallback oficial recomendado:
- `https://www.ine.es/jaxiT3/files/t/csv_bdsc/31241.csv`

También existen:
- CSV tabulado;
- XLSX;
- JSON WSTempus.

Si el JSON devuelve un subconjunto insuficiente, el pipeline debe conservar el último snapshot válido o probar el CSV completo antes de declarar la fuente degradada.
