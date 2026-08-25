# Automatización de producción

## Qué ocurre cada día

A las 03:17 UTC GitHub lanza `.github/workflows/actualizar-datos.yml`.

El workflow ejecuta:

```text
actualizar_todo.py --mode daily
  ├─ localidades, si han pasado 30 días
  ├─ BDNS, si ha pasado 1 día
  ├─ BOE, si ha pasado 1 día
  └─ validar_sitio.py --require-national
```

Solo si todo termina correctamente realiza `git commit` y `git push`.

## Si una fuente falla

El job termina con error antes del commit. La versión publicada permanece intacta.

## Si una fuente devuelve datos incompletos

La validación rechaza, por ejemplo, un catálogo de localidades con menos de 30.000 entidades. El resultado no se publica.

## Última comprobación

`data/system/last-check.json` se regenera en cada ejecución satisfactoria. La web lo utiliza para indicar cuándo se comprobaron por última vez los datos.

## Cadencias

Las cadencias se controlan mediante `data/system/update-state.json`. No dependen del servidor web.

Para forzar todo manualmente desde GitHub, ejecutar el workflow con `mode=full`.
