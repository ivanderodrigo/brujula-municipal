const BM={
  state:{
    places:[
      {id:'el-hoyo-cr',name:'El Hoyo',province:'Ciudad Real',autonomous_region:'Castilla-La Mancha',parent_municipality:'Mestanza',population:191,type:'Entidad de población'},
      {id:'soto-del-real',name:'Soto del Real',province:'Madrid',autonomous_region:'Comunidad de Madrid',population:9800,type:'Municipio'},
      {id:'alcaracejos',name:'Alcaracejos',province:'Córdoba',autonomous_region:'Andalucía',population:1410,type:'Municipio'},
      {id:'ayna',name:'Ayna',province:'Albacete',autonomous_region:'Castilla-La Mancha',population:650,type:'Municipio'},
      {id:'morella',name:'Morella',province:'Castellón',autonomous_region:'Comunitat Valenciana',population:2400,type:'Municipio'}
    ],
    sourceStatus:[
      {source:'AEBOE API',state:'ok',latency:'418 ms',note:'Legislación consolidada y cambios normativos.'},
      {source:'BDNS / SNPSAP',state:'ok',latency:'2312 ms',note:'Convocatorias y fichas de detalle.'},
      {source:'MITECO territorial',state:'ok',latency:'986 ms',note:'Descubrimiento dinámico de URL del dataset antes de descargar.'},
      {source:'INE renta',state:'warn',latency:'—',note:'Valida umbral de registros; conserva el snapshot anterior si es insuficiente.'},
      {source:'PAe',state:'warn',latency:'302 loop',note:'Fuente vigilada, no bloquea la publicación si buclea.'},
      {source:'CNIG / NGMEP',state:'ok',latency:'909 ms',note:'Catálogo nacional de localidades.'}
    ],
    searchIndex:[
      {title:'Telelectura de agua',type:'Proyecto',desc:'Lectura remota, sectorización y control de fugas.'},
      {title:'ENS para ayuntamientos pequeños',type:'Obligación',desc:'Política de seguridad, copias, inventario y continuidad.'},
      {title:'Alumbrado inteligente',type:'Proyecto',desc:'Eficiencia energética, telegestión y cuadros.'},
      {title:'Ayudas para conectividad rural',type:'Financiación',desc:'Cobertura, smart villages y servicios esenciales.'},
      {title:'Plan de 90 días',type:'Herramienta',desc:'Ruta práctica de implantación con responsables.'},
      {title:'RedCIT',type:'Caso',desc:'Aprendizajes replicables para municipios pequeños.'}
    ],
    priorities:[
      {title:'ENS básico y continuidad',score:92,why:['obligación clara','complejidad asumible','riesgo operativo alto']},
      {title:'Telelectura de agua',score:88,why:['señal territorial agua','ahorro y control','vías de financiación relacionadas']},
      {title:'Alumbrado inteligente',score:84,why:['eficiencia energética','madurez alta','casos replicables']},
      {title:'Conectividad y Wi‑Fi público',score:79,why:['atracción de población','uso ciudadano','smart villages']}
    ]
  },
  storageKey:'brujula_municipal_state',
  load(){try{return JSON.parse(localStorage.getItem(this.storageKey)||'{}')}catch(e){return {}}},
  save(data){localStorage.setItem(this.storageKey,JSON.stringify(data))},
  ensure(){const d=this.load(); const p=this.state.places[0]; this.local={profile:d.profile||p, priorities:d.priorities||['agua','ciberseguridad'], capacity:d.capacity||'media', workspace:{saved:(d.workspace&&d.workspace.saved)||3, dirty:(d.workspace&&typeof d.workspace.dirty==='boolean')?d.workspace.dirty:true, lastBackup:(d.workspace&&d.workspace.lastBackup)||null}}; this.save(this.local)},
  setTownLabels(){const p=this.local.profile; document.querySelectorAll('[data-selected-town]').forEach(x=>x.textContent=p.name); document.querySelectorAll('[data-selected-place]').forEach(x=>x.textContent=`${p.name} · ${p.province} · ${p.autonomous_region}`); document.querySelectorAll('[data-municipality-label]').forEach(x=>x.textContent=`${p.name}, ${p.province}`); document.querySelectorAll('[data-town-context]').forEach(x=>x.textContent=`${p.name} · ${p.type}${p.parent_municipality?' · municipio de '+p.parent_municipality:''} · ${p.province} · ${p.autonomous_region} · población aprox. ${p.population}`)},
  openSelector(){const ov=document.getElementById('municipality-overlay'); if(ov){ov.classList.add('open'); ov.setAttribute('aria-hidden','false'); const input=ov.querySelector('.field'); if(input)input.focus()}},
  closeSelector(){const ov=document.getElementById('municipality-overlay'); if(ov){ov.classList.remove('open'); ov.setAttribute('aria-hidden','true')}},
  initSelector(){document.querySelectorAll('[data-open-municipality]').forEach(b=>b.addEventListener('click',()=>this.openSelector())); document.querySelectorAll('[data-close-municipality]').forEach(b=>b.addEventListener('click',()=>this.closeSelector())); const ov=document.getElementById('municipality-overlay'); if(ov){ov.addEventListener('click',e=>{if(e.target===ov)this.closeSelector()})} window.addEventListener('keydown',e=>{if(e.key==='Escape')this.closeSelector()}); const input=document.querySelector('.selector .field'); const out=document.querySelector('.municipality-results'); if(!input||!out)return; const render=(q='')=>{q=q.trim().toLowerCase(); const items=this.state.places.filter(p=>!q||[p.name,p.province,p.autonomous_region,p.parent_municipality||''].join(' ').toLowerCase().includes(q)); out.innerHTML=items.map(p=>`<button class="municipality-option" data-id="${p.id}"><strong>${p.name}</strong><div class="muted">${p.type} · ${p.province} · ${p.autonomous_region}${p.parent_municipality?' · municipio de '+p.parent_municipality:''}</div></button>`).join(''); out.querySelectorAll('[data-id]').forEach(btn=>btn.addEventListener('click',()=>{const pick=this.state.places.find(x=>x.id===btn.dataset.id); this.local.profile=pick; this.local.workspace.dirty=true; this.save(this.local); this.setTownLabels(); this.renderBackupState(); this.renderExecutive(); this.renderPriorities(); this.closeSelector()}))}; input.addEventListener('input',()=>render(input.value)); render();},
  initSearch(){const form=document.querySelector('[data-global-search]'); if(!form)return; const input=form.querySelector('input'); const out=document.querySelector('[data-search-results]'); const render=(q='')=>{q=q.trim().toLowerCase(); if(!q){out.innerHTML='';return} const hits=this.state.searchIndex.filter(x=>[x.title,x.type,x.desc].join(' ').toLowerCase().includes(q)).slice(0,5); out.innerHTML=hits.length?hits.map(x=>`<article class="search-hit"><strong>${x.title}</strong><div class="small"><span class="badge">${x.type}</span></div><p class="muted" style="margin:8px 0 0">${x.desc}</p></article>`).join(''):'<div class="search-hit">Sin resultados de demostración. La versión completa consultaría el índice nacional.</div>'}; form.addEventListener('submit',e=>{e.preventDefault(); render(input.value)}); input.addEventListener('input',()=>render(input.value));},
  renderSourceTable(){document.querySelectorAll('[data-source-table]').forEach(tb=>tb.innerHTML=this.state.sourceStatus.map(s=>`<tr><td><strong>${s.source}</strong></td><td><span class="badge ${s.state==='ok'?'ok':s.state==='warn'?'warn':'danger'}">${s.state==='ok'?'Disponible':s.state==='warn'?'Degradada / vigilada':'Caída'}</span></td><td>${s.latency}</td><td>${s.note}</td></tr>`).join(''))},
  renderBackupState(){const w=this.local.workspace; document.querySelectorAll('[data-backup-state]').forEach(el=>el.innerHTML=`<div class="notice-card"><div><strong>${w.dirty?'Conviene descargar una copia local':'Tus datos locales están respaldados'}</strong><p class="muted" style="margin:6px 0 0">Tus datos de localidad, prioridades, capacidad y elementos guardados viven solo en este navegador. ${w.lastBackup?`Última copia: ${new Date(w.lastBackup).toLocaleString('es-ES')}. `:''}${w.dirty?'Si cambias de equipo, usas incógnito o borras datos, podrías perderlos.' : 'Aun así, puedes descargar una copia nueva cuando quieras.'}</p></div></div>`); document.querySelectorAll('[data-workspace-count]').forEach(x=>x.textContent=String(w.saved||0))},
  downloadBackup(){this.local.workspace.lastBackup=new Date().toISOString(); this.local.workspace.dirty=false; this.save(this.local); this.renderBackupState(); const blob=new Blob([JSON.stringify(this.local,null,2)],{type:'application/json'}); const a=document.createElement('a'); a.href=URL.createObjectURL(blob); a.download='brujula-municipal-backup.json'; a.click(); setTimeout(()=>URL.revokeObjectURL(a.href),500)},
  initBackup(){document.querySelectorAll('[data-download-backup]').forEach(b=>b.addEventListener('click',()=>this.downloadBackup())); document.querySelectorAll('[data-restore-backup]').forEach(inp=>inp.addEventListener('change',async()=>{const f=inp.files[0]; if(!f)return; const text=await f.text(); try{const parsed=JSON.parse(text); this.local=parsed; this.save(this.local); this.setTownLabels(); this.renderBackupState(); this.renderExecutive(); this.renderPriorities(); alert('Copia restaurada correctamente.')}catch(e){alert('No se pudo leer la copia JSON.')}}))},
  renderExecutive(){const root=document.querySelector('[data-executive]'); if(!root)return; const p=this.local.profile; root.innerHTML=`<div class="metric"><strong>${p.population}</strong><span>Población aprox.</span></div><div class="metric"><strong>6</strong><span>oportunidades prioritarias</span></div><div class="metric"><strong>4</strong><span>obligaciones activas</span></div><div class="metric"><strong>3</strong><span>casos comparables</span></div>`},
  renderPriorities(){const root=document.querySelector('[data-priority-list]'); if(!root)return; root.innerHTML=this.state.priorities.map(x=>`<article class="card"><div class="kicker">Score interno ${x.score}/100</div><h3>${x.title}</h3><p class="muted">${x.why.join(' · ')}</p></article>`).join('')},
  init(){this.ensure(); this.setTownLabels(); this.initSelector(); this.initSearch(); this.renderSourceTable(); this.renderBackupState(); this.initBackup(); this.renderExecutive(); this.renderPriorities(); window.dispatchEvent(new Event('bm-ready'))}
};
window.addEventListener('DOMContentLoaded',()=>BM.init());
