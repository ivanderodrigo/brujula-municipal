#!/usr/bin/env python3
"""Orquestador de actualización automática de Brújula Municipal.

Daily: BDNS + BOE + validación. Localidades solo cuando vencen su cadencia.
Full: fuerza todas las fuentes.
El repositorio/hosting solo recibe el resultado si este proceso acaba con código 0.
"""
from __future__ import annotations
from pathlib import Path
import argparse, datetime as dt, json, os, subprocess, sys, traceback

ROOT=Path(__file__).resolve().parents[1]
STATE=ROOT/'data'/'system'/'update-state.json'
HEARTBEAT=ROOT/'data'/'system'/'last-check.json'
LOG=ROOT/'logs'/'ultima-actualizacion.txt'

DEFAULT_CADENCE={'localities':30,'bdns':1,'boe':1,'news':1,'territorial':180,'income':180,'repositories':7}

def now_utc(): return dt.datetime.now(dt.timezone.utc)
def load_json(path,default):
    try:return json.loads(path.read_text(encoding='utf-8'))
    except Exception:return default

def parse_iso(v):
    try:return dt.datetime.fromisoformat(str(v).replace('Z','+00:00'))
    except Exception:return None

def due(state,key,days,force=False):
    if force:return True
    src=state.get('sources',{}).get(key,{})
    last=parse_iso(src.get('last_success') or src.get('last_attempt'))
    if not last:return True
    return (now_utc()-last).total_seconds() >= days*86400

def run(label,args):
    print(f'\n=== {label} ===')
    p=subprocess.run([sys.executable,*map(str,args)],cwd=ROOT)
    if p.returncode: raise RuntimeError(f'{label} falló con código {p.returncode}')

def run_optional(label,args):
    print(f'\n=== {label} (fuente de enriquecimiento) ===')
    p=subprocess.run([sys.executable,*map(str,args)],cwd=ROOT)
    if p.returncode:
        print(f'AVISO: {label} no se actualizó (código {p.returncode}); se conserva la última copia válida.')
        return False
    return True

def source_health():
    return load_json(ROOT/'data'/'generated'/'salud_fuentes.json',{'sources':[]})

def sources_available(task):
    rows=[x for x in source_health().get('sources',[]) if task in (x.get('used_by') or [])]
    if not rows:return True
    return any(bool(x.get('available')) for x in rows)

def require_preflight():
    # Se ejecuta antes de tocar cualquier dataset. BOE/BDNS son críticas y bloquean
    # el pipeline si no responden con un formato mínimo válido.
    run('Preflight de fuentes', [ROOT/'tools'/'comprobar_fuentes.py','--fail-critical'])

def mark(state,key,ok=True,error=None):
    src=state.setdefault('sources',{}).setdefault(key,{})
    src['last_attempt']=now_utc().isoformat(timespec='seconds')
    if ok:
        src['last_success']=src['last_attempt']; src.pop('last_error',None)
    else: src['last_error']=str(error)

def write_success(state,ran,mode):
    ts=now_utc().isoformat(timespec='seconds')
    state['last_successful_pipeline']=ts; state['mode']=mode; state['last_run_sources']=ran
    STATE.parent.mkdir(parents=True,exist_ok=True)
    STATE.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf-8')
    status=load_json(ROOT/'data'/'generated'/'status.json',{})
    health=source_health()
    repos=load_json(ROOT/'data'/'generated'/'repositorios.json',{})
    heartbeat={
      'ok':True,'checked_at':ts,'pipeline':'static-offline','mode':mode,'sources_run':ran,
      'data_status':status,
      'source_health':{'total':health.get('total',0),'available':health.get('available',0),'unavailable':health.get('unavailable',0),'critical_unavailable':health.get('critical_unavailable',[])},
      'repositories_checked':len(repos.get('repositories',[]) or []),
      'note':'Generado automáticamente. Los visitantes no ejecutan consultas a las fuentes oficiales.'
    }
    HEARTBEAT.write_text(json.dumps(heartbeat,ensure_ascii=False,indent=2),encoding='utf-8')
    LOG.parent.mkdir(parents=True,exist_ok=True)
    LOG.write_text(f'OK {ts}\nModo: {mode}\nFuentes: {", ".join(ran)}\n',encoding='utf-8')

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--mode',choices=('daily','full','validate-only'),default='daily')
    ap.add_argument('--localities-days',type=int,default=DEFAULT_CADENCE['localities'])
    ap.add_argument('--bdns-days',type=int,default=DEFAULT_CADENCE['bdns'])
    ap.add_argument('--boe-days',type=int,default=DEFAULT_CADENCE['boe'])
    ap.add_argument('--news-days',type=int,default=DEFAULT_CADENCE['news'])
    ap.add_argument('--territorial-days',type=int,default=DEFAULT_CADENCE['territorial'])
    ap.add_argument('--income-days',type=int,default=DEFAULT_CADENCE['income'])
    ap.add_argument('--repositories-days',type=int,default=DEFAULT_CADENCE['repositories'])
    ap.add_argument('--bdns-window',type=int,default=120)
    ap.add_argument('--boe-window',type=int,default=60)
    a=ap.parse_args()
    state=load_json(STATE,{'version':1,'sources':{}}); ran=[]; force=a.mode=='full'
    try:
        if a.mode!='validate-only':
            require_preflight(); ran.append('preflight')
            # Repositorios/datasets externos frecuentes: sincronización ligera y cacheada.
            # La propia utilidad decide por commit/cadencia si necesita descargar.
            if sources_available('repositories'):
                ok=run_optional('Sincronización de repositorios externos', [ROOT/'tools'/'sincronizar_repositorios.py']+(['--force'] if force else [])); mark(state,'repositories',ok=ok,error=None if ok else 'Repositorio no actualizado'); ran.append('repositories')
            else:
                print('AVISO: repositorios externos no disponibles en preflight; se conserva caché anterior.')
            if due(state,'localities',a.localities_days,force):
                if sources_available('localities') or (ROOT/'tools'/'cache'/'repos'/'osm-validador-ine'/'ENTIDADES.2025.csv').exists():
                    run('Localidades IGN/CNIG', [ROOT/'tools'/'actualizar_localidades_cnig.py']); mark(state,'localities'); ran.append('localities')
                else:
                    mark(state,'localities',ok=False,error='Fuentes de localidades no disponibles en preflight'); print('AVISO: localidades no actualizadas; se conserva la copia válida.')
            if due(state,'bdns',a.bdns_days,force):
                run('Radar BDNS', [ROOT/'tools'/'actualizar_bdns.py','--days',str(a.bdns_window),'--max-details','300']); mark(state,'bdns'); ran.append('bdns')
            if due(state,'boe',a.boe_days,force):
                run('Radar BOE', [ROOT/'tools'/'actualizar_boe.py','--days',str(a.boe_window),'--max-details','180']); mark(state,'boe'); ran.append('boe')
            if due(state,'news',a.news_days,force):
                if sources_available('news'):
                    ok=run_optional('Novedades oficiales MITECO/FEMP + páginas vigiladas', [ROOT/'tools'/'actualizar_novedades.py','--days','45','--max-items','120']); mark(state,'news',ok=ok,error=None if ok else 'No actualizado'); ran.append('news')
                else: mark(state,'news',ok=False,error='Fuentes de novedades no disponibles en preflight')
            if due(state,'territorial',a.territorial_days,force):
                if sources_available('territorial'):
                    ok=run_optional('Indicadores territoriales MITECO', [ROOT/'tools'/'actualizar_indicadores_territoriales.py']); mark(state,'territorial',ok=ok,error=None if ok else 'No actualizado; ver source_status'); ran.append('territorial')
                else: mark(state,'territorial',ok=False,error='MITECO territorial no disponible en preflight')
            if due(state,'income',a.income_days,force):
                if sources_available('income'):
                    ok=run_optional('Renta municipal INE', [ROOT/'tools'/'actualizar_renta_ine.py']); mark(state,'income',ok=ok,error=None if ok else 'No actualizado'); ran.append('income')
                else: mark(state,'income',ok=False,error='INE no disponible en preflight')
            if 'territorial' in ran or 'income' in ran or force:
                run('Benchmark territorial', [ROOT/'tools'/'generar_benchmark_territorial.py'])
        # SEO y accesibilidad se regeneran en cada ejecución para refrescar páginas estáticas.
        run('SEO técnico y sitemap', [ROOT/'tools'/'generar_seo.py']); ran.append('seo')
        run('Auditoría/inyección de accesibilidad', [ROOT/'tools'/'generar_accesibilidad.py']); ran.append('accessibility')
        # In production automation we require the national catalogue.
        require_national = os.environ.get('BRUJULA_REQUIRE_NATIONAL','0')=='1'
        cmd=[ROOT/'tools'/'validar_sitio.py']+(['--require-national'] if require_national else [])
        run('Validación de publicación',cmd)
        write_success(state,ran,a.mode)
        print('\nPIPELINE COMPLETADO. Es seguro publicar el árbol actual.')
        return 0
    except Exception as e:
        ts=now_utc().isoformat(timespec='seconds')
        state['last_failed_pipeline']=ts; state['last_pipeline_error']=str(e)
        STATE.parent.mkdir(parents=True,exist_ok=True); STATE.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf-8')
        LOG.parent.mkdir(parents=True,exist_ok=True); LOG.write_text(f'ERROR {ts}\n{e}\n{traceback.format_exc()}\n',encoding='utf-8')
        print('\nPIPELINE ABORTADO:',e)
        print('No debe publicarse ni hacerse commit de estos cambios.')
        return 1

if __name__=='__main__': sys.exit(main())
