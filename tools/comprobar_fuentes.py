#!/usr/bin/env python3
"""Preflight de fuentes de Brújula Municipal.

Comprueba disponibilidad, redirecciones, tipo de contenido y una muestra pequeña antes
de ejecutar los importadores. No descarga datasets completos.
"""
from __future__ import annotations
from pathlib import Path
import argparse, datetime as dt, json, ssl, sys, time, urllib.request, urllib.error

ROOT=Path(__file__).resolve().parents[1]
CFG=ROOT/'data'/'config'/'fuentes_actualizacion.json'
OUT=ROOT/'data'/'generated'/'salud_fuentes.json'
UA='BrujulaMunicipal/1.2 source-preflight (+https://brujulamunicipal.eu.org/)'

def now(): return dt.datetime.now(dt.timezone.utc)
def load(path,default):
    try:return json.loads(path.read_text(encoding='utf-8'))
    except Exception:return default

def looks_ok(expect, sample:bytes, content_type:str):
    s=sample.lstrip().lower(); c=(content_type or '').lower()
    if expect=='json': return ('json' in c) or s.startswith((b'{',b'['))
    if expect=='xml': return ('xml' in c) or s.startswith(b'<?xml') or b'<rss' in s[:500] or b'<feed' in s[:500]
    if expect=='json_or_xml': return looks_ok('json',sample,c) or looks_ok('xml',sample,c)
    if expect=='xml_or_html': return looks_ok('xml',sample,c) or looks_ok('html',sample,c)
    if expect=='html': return ('html' in c) or b'<html' in s[:1000] or b'<!doctype html' in s[:1000]
    if expect=='csv':
        text=sample.decode('utf-8','ignore')
        return ('csv' in c) or (';' in text or ',' in text) and ('\n' in text)
    return bool(sample)

def probe(src, timeout=20, retries=2):
    started=time.monotonic(); err=None
    for attempt in range(retries+1):
        try:
            req=urllib.request.Request(src['url'],headers={
                'User-Agent':UA,
                'Accept':'application/json, application/xml, text/xml, text/csv, text/html;q=0.9, */*;q=0.5',
                'Cache-Control':'no-cache'
            })
            ctx=ssl.create_default_context()
            with urllib.request.urlopen(req,timeout=timeout,context=ctx) as r:
                limit=int(src.get('max_probe_bytes',4096))
                sample=r.read(limit)
                ctype=r.headers.get('Content-Type','')
                final=r.geturl(); code=getattr(r,'status',200)
                ok=(200 <= code < 400) and looks_ok(src.get('expect','any'),sample,ctype)
                return {
                    'id':src['id'],'name':src['name'],'organization':src.get('organization'),
                    'url':src['url'],'final_url':final,'http_status':code,'content_type':ctype,
                    'available':bool(ok),'critical':bool(src.get('critical')),
                    'used_by':src.get('used_by',[]),'checked_at':now().isoformat(timespec='seconds'),
                    'latency_ms':round((time.monotonic()-started)*1000),
                    'sample_bytes':len(sample),'expect':src.get('expect')
                }
        except Exception as e:
            err=str(e)
            if attempt<retries: time.sleep(1.2*(attempt+1))
    return {
        'id':src['id'],'name':src['name'],'organization':src.get('organization'),
        'url':src['url'],'available':False,'critical':bool(src.get('critical')),
        'used_by':src.get('used_by',[]),'checked_at':now().isoformat(timespec='seconds'),
        'latency_ms':round((time.monotonic()-started)*1000),'error':err,'expect':src.get('expect')
    }

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--ids',default='',help='IDs separados por coma'); ap.add_argument('--fail-critical',action='store_true'); ap.add_argument('--timeout',type=int,default=20); a=ap.parse_args()
    cfg=load(CFG,{}); selected=set(x.strip() for x in a.ids.split(',') if x.strip())
    sources=[s for s in cfg.get('sources',[]) if not selected or s.get('id') in selected]
    results=[probe(s,a.timeout) for s in sources]
    summary={
        'generated_at':now().isoformat(timespec='seconds'),
        'policy':cfg.get('policy'),'total':len(results),
        'available':sum(1 for x in results if x['available']),
        'unavailable':sum(1 for x in results if not x['available']),
        'critical_unavailable':[x['id'] for x in results if x.get('critical') and not x['available']],
        'sources':results
    }
    OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    for x in results:
        flag='OK' if x['available'] else 'NO'
        extra=f" · {x.get('http_status','')} · {x.get('latency_ms')} ms" if x['available'] else f" · {x.get('error','sin respuesta')}"
        print(f"{flag:>2}  {x['id']}: {x['name']}{extra}")
    if a.fail_critical and summary['critical_unavailable']:
        print('BLOQUEO: fuentes críticas no disponibles:',', '.join(summary['critical_unavailable']))
        return 2
    return 0

if __name__=='__main__': sys.exit(main())
