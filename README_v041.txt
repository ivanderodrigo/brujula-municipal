BRÚJULA MUNICIPAL v0.4.1 — CORRECCIÓN DEL CATÁLOGO NACIONAL
============================================================

QUÉ SE HA CORREGIDO
-------------------
La v0.4 incluía 16 localidades de demostración y dependía de una descarga automática
concreta del Centro de Descargas del CNIG. Si esa URL no respondía, el índice nacional
no se generaba y la web seguía mostrando únicamente el catálogo demo.

La v0.4.1 corrige ese comportamiento:

1. ACTUALIZAR_LOCALIDADES.bat intenta primero el ZIP oficial NGMEP del IGN/CNIG.
2. Si la descarga directa falla, intenta automáticamente ENTIDADES.2025.csv del
   repositorio público OSM-es/validador-ine, que conserva una copia del fichero
   ENTIDADES procedente del NGMEP.
3. Si ninguno funciona, NO sustituye el catálogo por datos incompletos.
4. El selector muestra claramente si está en:
      - CATÁLOGO DE DEMOSTRACIÓN
      - CATÁLOGO NACIONAL ACTIVO
   y muestra el número de localidades indexadas.
5. La búsqueda sigue siendo 100 % estática: el visitante solo descarga pequeños JSON
   conforme escribe. No hay API, backend, tarjeta ni coste por consulta.

PRIMER USO
----------
1. Descomprime la carpeta.
2. Doble clic en ACTUALIZAR_LOCALIDADES.bat.
3. Debes ver al final: "CATÁLOGO NACIONAL GENERADO CORRECTAMENTE" y un total muy
   superior a 8.000 localidades.
4. Doble clic en INICIAR_BRUJULA.bat.
5. Abre el selector. Arriba debe decir "Catálogo nacional activo".

Si sigue diciendo "Catálogo de demostración", la actualización NO se completó. En ese
caso copia el texto completo de la ventana de ACTUALIZAR_LOCALIDADES.bat y revísalo.

FUENTES
-------
Fuente primaria:
Nomenclátor Geográfico de Municipios y Entidades de Población (IGN/CNIG)
https://centrodedescargas.cnig.es/CentroDescargas/nomenclator-geografico-municipios-entidades-poblacion

Fallback de disponibilidad:
OSM-es/validador-ine · ENTIDADES.2025.csv, fichero derivado del NGMEP
https://github.com/OSM-es/validador-ine/blob/main/ENTIDADES.2025.csv

NOTA SOBRE EATIM
----------------
Cuando se usa el ZIP oficial, el proceso incorpora la tabla EATIMS nacional.
Cuando solo está disponible el fallback ENTIDADES.2025.csv, se cargan todos los
municipios y núcleos de población, pero la personalidad jurídica EATIM completa no
puede reconstruirse solo con ese CSV. El Hoyo se conserva explícitamente como EATIM;
el resto de núcleos se tratan conservadoramente a través de su municipio matriz hasta
que se cargue la tabla EATIM oficial.
