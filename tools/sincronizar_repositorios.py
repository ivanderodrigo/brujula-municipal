#!/usr/bin/env python3
"""Sincroniza repositorios externos frecuentes en caché y registra su commit.

El caché se puede conservar con actions/cache. Solo se publican metadatos ligeros;
los repositorios completos no inflan el Git de Brújula.
"""
from __future__ import annotations
from pathlib import Path
import argparse, datetime as dt, json, shutil, subprocess, sys

ROOT=Path(__file__).resolve().parents[1]
CFG=ROOT/'data'/'config'/'repositorios_fuentes.json'
CACHE=ROOT/'tools'/'cache'/'repos'
OUT=ROOT/'data'/'generated'/'repositorios.json'
STATE=ROOT/'data'/'system'/'repo-state.json'

def now(): return dt.datetime.now(dt.timezone.utc)
def load(p,d):
    try:return json.loads(p.read_text(encoding='utf-8'))
    except Exception:return d

def iso(v):
    try:return dt.datetime.fromisoformat(v.replace('Z','+00:00'))
    except Exception:return None

def due(old, days, force):
    if force:return True
    last=iso(old.get('checked_at',''))
    return not last or (now()-last).total_seconds() >= days*86400

def cmd(args,cwd=None,check=True):
    return subprocess.run(args,cwd=cwd,text=True,capture_output=True,check=check)

def remote_sha(url,branch):
    p=cmd(['git','ls-remote',url,f'refs/heads/{branch}'])
    line=(p.stdout or '').strip().splitlines()
    return line[0].split()[0] if line else None

def sync_repo(repo,old,force=False):
    rid=repo['id']; target=CACHE/rid; branch=repo.get('branch','main')
    sha=remote_sha(repo['git_url'],branch)
    if not sha: raise RuntimeError('No se pudo resolver commit remoto')
    changed=sha!=old.get('commit')
    should=force or changed or not target.exists()
    if should:
        tmp=CACHE/(rid+'-tmp'); shutil.rmtree(tmp,ignore_errors=True); CACHE.mkdir(parents=True,exist_ok=True)
        cmd(['git','clone','--depth','1','--branch',branch,'--filter=blob:none','--sparse',repo['git_url'],str(tmp)])
        files=repo.get('files') or []
        if files: cmd(['git','sparse-checkout','set',*files],cwd=tmp)
        shutil.rmtree(target,ignore_errors=True); tmp.rename(target)
    files_meta=[]
    for rel in repo.get('files',[]):
        p=target/rel; files_meta.append({'path':rel,'available':p.exists(),'bytes':p.stat().st_size if p.exists() else None})
    return {'id':rid,'name':repo['name'],'git_url':repo['git_url'],'branch':branch,'commit':sha,'changed':changed,'downloaded':should,'checked_at':now().isoformat(timespec='seconds'),'purpose':repo.get('purpose'),'files':files_meta,'cache_path':str(target.relative_to(ROOT))}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--force',action='store_true'); a=ap.parse_args()
    cfg=load(CFG,{}); state=load(STATE,{'repositories':{}}); results=[]; errors=[]
    for repo in cfg.get('repositories',[]):
        old=state.setdefault('repositories',{}).get(repo['id'],{})
        if not due(old,int(repo.get('cadence_days',7)),a.force):
            results.append({**old,'id':repo['id'],'name':repo['name'],'skipped_due_to_cadence':True}); continue
        try:
            r=sync_repo(repo,old,a.force); results.append(r); state['repositories'][repo['id']]=r
            print(f"OK · {repo['name']} · {r['commit'][:12]} · {'descargado' if r['downloaded'] else 'sin cambios'}")
        except Exception as e:
            err={'id':repo['id'],'name':repo['name'],'error':str(e),'checked_at':now().isoformat(timespec='seconds'),'critical':bool(repo.get('critical'))}; errors.append(err); print('AVISO ·',repo['name'],e)
            if repo.get('critical'): raise
    STATE.parent.mkdir(parents=True,exist_ok=True); STATE.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf-8')
    OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps({'generated_at':now().isoformat(timespec='seconds'),'policy':cfg.get('policy'),'repositories':results,'errors':errors},ensure_ascii=False,indent=2),encoding='utf-8')
    return 0
if __name__=='__main__': sys.exit(main())
