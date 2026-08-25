#!/usr/bin/env python3
"""Aplica Brújula Municipal v1.5 sobre un repositorio completo existente.
Preserva datos y módulos; añade capa visual global y corrige el bloqueo de validación causado por tools/cache.
"""
from __future__ import annotations
from pathlib import Path
import shutil, re, sys
ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT/'tools'

def is_public_html(p: Path) -> bool:
    bad={'.git','.github','node_modules','tools','cache','vendor'}
    rel=p.relative_to(ROOT)
    return not any(part in bad or part.startswith('.') for part in rel.parts[:-1])

def inject_assets():
    changed=0
    for p in ROOT.rglob('*.html'):
        if not is_public_html(p):
            continue
        text=p.read_text(encoding='utf-8',errors='ignore')
        rel=p.parent.relative_to(ROOT)
        depth=len(rel.parts)
        prefix='../'*depth if depth else './'
        css=f'{prefix}assets/css/agency-ultra-v15.css'
        js=f'{prefix}assets/js/agency-ultra-v15.js'
        if 'agency-ultra-v15.css' not in text:
            text=text.replace('</head>',f'<link rel="stylesheet" href="{css}"></head>')
        if 'agency-ultra-v15.js' not in text:
            text=text.replace('</body>',f'<script src="{js}"></script></body>')
        p.write_text(text,encoding='utf-8'); changed+=1
    print(f'OK · capa visual inyectada en {changed} HTML públicos')

def wrap_hide_cache(filename:str):
    p=TOOLS/filename
    if not p.exists():
        print(f'AVISO · no existe {filename}; no se parchea')
        return
    original=TOOLS/(p.stem+'_pre_v15.py')
    if original.exists():
        print(f'OK · {filename} ya estaba parcheado')
        return
    p.rename(original)
    wrapper=f'''#!/usr/bin/env python3\nfrom pathlib import Path\nimport runpy, shutil, tempfile, sys\nROOT=Path(__file__).resolve().parents[1]\nCACHE=ROOT/'tools'/'cache'\nTMP=Path(tempfile.mkdtemp(prefix='brujula-validation-'))/'cache'\nMOVED=False\ntry:\n    if CACHE.exists():\n        shutil.move(str(CACHE),str(TMP)); MOVED=True\n    runpy.run_path(str(Path(__file__).with_name('{original.name}')),run_name='__main__')\nfinally:\n    if MOVED and TMP.exists():\n        CACHE.parent.mkdir(parents=True,exist_ok=True)\n        if CACHE.exists(): shutil.rmtree(CACHE,ignore_errors=True)\n        shutil.move(str(TMP),str(CACHE))\n'''
    p.write_text(wrapper,encoding='utf-8')
    print(f'OK · {filename}: tools/cache queda fuera de la auditoría pública')

def wrap_repo_sync():
    p=TOOLS/'sincronizar_repositorios.py'
    if not p.exists(): return
    original=TOOLS/'sincronizar_repositorios_pre_v15.py'
    if original.exists(): return
    p.rename(original)
    wrapper='''#!/usr/bin/env python3\nfrom pathlib import Path\nimport runpy, shutil\nROOT=Path(__file__).resolve().parents[1]\ntry:\n    runpy.run_path(str(Path(__file__).with_name("sincronizar_repositorios_pre_v15.py")),run_name="__main__")\nfinally:\n    repo_cache=ROOT/'tools'/'cache'/'repos'\n    if repo_cache.exists():\n        for p in repo_cache.glob('*-tmp'):\n            shutil.rmtree(p,ignore_errors=True)\n'''
    p.write_text(wrapper,encoding='utf-8')
    print('OK · sincronizar_repositorios.py: temporales *-tmp se eliminan siempre')

def wrap_miteco_updaters():
    candidates=[]
    for p in TOOLS.glob('*.py'):
        if p.name in {'aplicar_parche_v15.py','miteco_compat_v15.py'} or p.name.endswith('_pre_v15.py'):
            continue
        try: src=p.read_text(encoding='utf-8',errors='ignore')
        except Exception: continue
        if 'DescargaFichero?f=' in src or ('MITECO' in src and 'territorial' in src.lower()):
            candidates.append(p)
    for p in candidates:
        original=TOOLS/(p.stem+'_pre_v15.py')
        if original.exists(): continue
        p.rename(original)
        wrapper=f
def patch_gitignore():
    p=ROOT/'.gitignore'; text=p.read_text(encoding='utf-8') if p.exists() else ''
    rules=['tools/cache/','tools/*_pre_v15.py']
    for r in rules:
        if r not in text: text+='\n'+r
    p.write_text(text.strip()+'\n',encoding='utf-8')

def main():
    inject_assets()
    wrap_hide_cache('generar_accesibilidad.py')
    wrap_hide_cache('validar_sitio.py')
    wrap_repo_sync()
    wrap_miteco_updaters()
    patch_gitignore()
    print('PARCHE v1.5 APLICADO · conserva datos, módulos y workflow existente.')
if __name__=='__main__': main()
