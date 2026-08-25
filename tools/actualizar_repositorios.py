#!/usr/bin/env python3
from pathlib import Path
import json, time
OUT = Path(__file__).resolve().parents[1] / 'data' / 'repo_sync_status.json'
status={'checked_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'repositories':[{'id':'osm-entidades','mode':'raw_csv','action':'download-direct','changed':True,'note':'No se intenta sparse-checkout si el recurso final es un CSV directo.'},{'id':'miteco-fallbacks','mode':'snapshot','action':'keep-last-valid','changed':False,'note':'Solo se renueva si cambia la versión disponible.'}]}
OUT.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(status, ensure_ascii=False, indent=2))
