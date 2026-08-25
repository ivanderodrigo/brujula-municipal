#!/usr/bin/env python3
"""Validación de publicación de Brújula Municipal.

No usa red ni dependencias externas. Si falla, la automatización NO debe hacer commit.
"""
from __future__ import annotations
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
import argparse, json, re, sys

ROOT = Path(__file__).resolve().parents[1]

class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.refs=[]
    def handle_starttag(self, tag, attrs):
        d=dict(attrs)
        for key in ('href','src'):
            if key in d: self.refs.append((tag,key,d[key]))

def load(path):
    return json.loads((ROOT/path).read_text(encoding='utf-8'))

def items_of(obj):
    if isinstance(obj,list): return obj
    if isinstance(obj,dict):
        v=obj.get('items')
        if isinstance(v,list): return v
    return []

def is_external(ref):
    if not ref or ref.startswith(('#','mailto:','tel:','javascript:','data:')): return True
    p=urlparse(ref)
    return bool(p.scheme or p.netloc)

def local_target(html_path:Path, ref:str):
    clean=ref.split('#',1)[0].split('?',1)[0]
    if not clean: return None
    base=html_path.parent
    if clean.startswith('/'):
        target=ROOT/clean.lstrip('/')
    else:
        target=(base/clean).resolve()
    # must stay inside root
    try: target.relative_to(ROOT.resolve())
    except ValueError: return None
    if target.is_dir(): target=target/'index.html'
    elif not target.suffix: target=target/'index.html'
    return target

def validate_json(errors):
    for p in ROOT.rglob('*.json'):
        if any(part in {'cache','raw_bdns','boe_raw'} for part in p.parts): continue
        try: json.loads(p.read_text(encoding='utf-8'))
        except Exception as e: errors.append(f'JSON inválido: {p.relative_to(ROOT)} · {e}')

def validate_counts(errors, warnings, require_national=False):
    projects=items_of(load('data/catalog/proyectos.json'))
    obligations=items_of(load('data/catalog/obligaciones.json'))
    opportunities=items_of(load('data/catalog/oportunidades.json'))
    support=items_of(load('data/catalog/apoyo.json'))
    if len(projects)<100: errors.append(f'Proyectos insuficientes: {len(projects)} < 100')
    if len(obligations)<20: errors.append(f'Obligaciones insuficientes: {len(obligations)} < 20')
    if len(opportunities)<5: errors.append(f'Oportunidades revisadas insuficientes: {len(opportunities)} < 5')
    if len(support)<5: warnings.append(f'Cobertura de apoyo todavía pequeña: {len(support)}')
    manifest=load('data/localidades/manifest.json')
    total=int(manifest.get('total_entities') or 0)
    if require_national and total<30000: errors.append(f'Catálogo nacional incompleto: {total} entidades < 30000')
    elif total<8000: warnings.append(f'Catálogo de localidades aún no nacional: {total} entidades')
    return {'projects':len(projects),'obligations':len(obligations),'opportunities':len(opportunities),'support':len(support),'localities':total}

def validate_sources(errors):
    # Curated/sensitive records must retain evidence links.
    for path in ('data/catalog/oportunidades.json','data/catalog/obligaciones.json'):
        for x in items_of(load(path)):
            src=x.get('source') or x.get('official_source') or x.get('source_url')
            if not src: errors.append(f'{path}: {x.get("id","sin-id")} sin fuente')
    # Automatic candidates must never silently become verified.
    for path in ('data/generated/oportunidades_bdns.json','data/generated/normativa_boe.json'):
        obj=load(path)
        for x in items_of(obj):
            if x.get('review_status')!='pending': errors.append(f'{path}: candidato {x.get("id")} no está pending')
            if x.get('status') not in (None,'pending_review'):
                errors.append(f'{path}: candidato {x.get("id")} tiene status no seguro: {x.get("status")}')

def validate_html(errors):
    for html in ROOT.rglob('*.html'):
        if any(part.startswith('.') for part in html.relative_to(ROOT).parts): continue
        parser=LinkParser()
        try: parser.feed(html.read_text(encoding='utf-8'))
        except Exception as e:
            errors.append(f'HTML no parseable: {html.relative_to(ROOT)} · {e}'); continue
        for tag,key,ref in parser.refs:
            if is_external(ref): continue
            # dynamic template refs are intentionally ignored
            if '${' in ref or '{{' in ref: continue
            target=local_target(html,ref)
            if target is not None and not target.exists():
                errors.append(f'Enlace interno roto: {html.relative_to(ROOT)} -> {ref}')

def validate_no_backend(errors):
    forbidden=[r'localhost:\d+',r'127\.0\.0\.1:\d+',r'api[_-]?key\s*[:=]',r'supabase\.co',r'cloudflare.*workers']
    for p in list(ROOT.rglob('*.html'))+list(ROOT.rglob('*.js')):
        txt=p.read_text(encoding='utf-8',errors='ignore')
        for pat in forbidden:
            if re.search(pat,txt,re.I):
                # INICIAR local server reference is not in html/js; any production asset match is suspicious.
                errors.append(f'Dependencia dinámica sospechosa en {p.relative_to(ROOT)}: {pat}')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--require-national',action='store_true'); a=ap.parse_args()
    errors=[]; warnings=[]
    validate_json(errors)
    counts=validate_counts(errors,warnings,a.require_national)
    validate_sources(errors)
    validate_html(errors)
    validate_no_backend(errors)
    print('VALIDACIÓN BRÚJULA MUNICIPAL')
    print(json.dumps(counts,ensure_ascii=False,indent=2))
    for w in warnings: print('AVISO:',w)
    if errors:
        for e in errors: print('ERROR:',e)
        print(f'\nRESULTADO: NO PUBLICABLE · {len(errors)} errores')
        return 1
    print('\nRESULTADO: PUBLICABLE')
    return 0

if __name__=='__main__': sys.exit(main())
