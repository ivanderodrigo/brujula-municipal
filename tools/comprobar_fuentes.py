#!/usr/bin/env python3
from __future__ import annotations
import json, time, urllib.request, urllib.error
from pathlib import Path
CONFIG = Path(__file__).resolve().parents[1] / 'data' / 'config' / 'fuentes_actualizacion.json'
OUT = Path(__file__).resolve().parents[1] / 'data' / 'preflight_status.json'
def check(url:str)->dict:
    started=time.time(); req=urllib.request.Request(url, headers={'User-Agent':'Brújula Municipal Preflight/1.4'})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return {'ok':True,'status':getattr(r,'status',200),'final_url':r.geturl(),'ms':int((time.time()-started)*1000)}
    except urllib.error.HTTPError as e:
        return {'ok':False,'status':e.code,'error':str(e),'ms':int((time.time()-started)*1000)}
    except Exception as e:
        return {'ok':False,'status':None,'error':str(e),'ms':int((time.time()-started)*1000)}

def main():
    conf=json.loads(CONFIG.read_text(encoding='utf-8')); results=[]; abort=False
    for src in conf['sources']:
        res=check(src['check_url']); row={**src, **res}; results.append(row)
        if src.get('critical') and not res.get('ok'): abort=True
    payload={'checked_at':time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'abort_publication':abort, 'sources':results}
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if abort: raise SystemExit('Abortando publicación: ha fallado al menos una fuente crítica.')
if __name__=='__main__': main()
