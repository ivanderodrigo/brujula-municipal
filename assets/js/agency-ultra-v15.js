(function(){
  'use strict';
  const q=(s,r=document)=>r.querySelector(s), qa=(s,r=document)=>[...r.querySelectorAll(s)];
  const base=()=>document.documentElement.dataset.base||'./';
  const getProfile=()=>{
    try{
      if(window.BM && typeof BM.getProfile==='function') return BM.getProfile();
      const raw=localStorage.getItem('brujula:profile')||localStorage.getItem('brujula_municipal_state');
      if(raw){const x=JSON.parse(raw); return x.profile||x}
    }catch(e){}
    return null;
  };
  function brand(){
    qa('.brand').forEach(el=>{
      if(el.dataset.agencyV15) return;
      el.dataset.agencyV15='1';
      const img=el.querySelector('img');
      if(!img){
        const logo=document.createElement('img');
        logo.src=base()+'assets/img/logo-brujula.svg'; logo.alt='';
        el.prepend(logo);
      }
    });
  }
  function mapMarkup(profile){
    const name=profile?.name||profile?.nombre||'Localidad seleccionada';
    const province=profile?.province||profile?.provincia||'';
    const region=profile?.autonomous_region||profile?.comunidad_autonoma||profile?.region||'';
    const lat=Number(profile?.lat ?? profile?.latitude ?? profile?.y);
    const lon=Number(profile?.lon ?? profile?.lng ?? profile?.longitude ?? profile?.x);
    let px=300, py=198, precise=false;
    if(Number.isFinite(lat)&&Number.isFinite(lon) && lat>=35.5 && lat<=44.5 && lon>=-10.5 && lon<=4.5){
      px=65+(lon+9.7)/13.3*430; py=55+(43.9-lat)/8.2*270; precise=true;
    }
    return `<article class="map-card agency-spain-map-card"><div class="kicker">Territorio en contexto</div><div class="agency-map-head"><div><h3>${name}</h3><p class="small muted">${[province,region].filter(Boolean).join(' · ')||'Contexto territorial'}</p></div><span class="badge ${precise?'ok':'warn'}">${precise?'posición del catálogo':'ubicación aproximada'}</span></div><svg viewBox="0 0 620 390" role="img" aria-label="Mapa de España con ${name} destacado"><defs><linearGradient id="v15sea" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#e8f5f8"/><stop offset="1" stop-color="#d9edf3"/></linearGradient><linearGradient id="v15land" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#ffffff"/><stop offset="1" stop-color="#eff6f8"/></linearGradient></defs><rect width="620" height="390" rx="28" fill="url(#v15sea)"/><g transform="translate(56 36)"><path d="M59 133 83 86l80-45 74-3 68 18 50-18 55 6 38 41 41 8 16 33-33 49 15 51-25 23-40 14-46 42-60 5-48 21-73-3-38-35-48 6-38-21-46-2-40-38 18-45-16-51 11-42 37-24 48-6Z" fill="url(#v15land)" stroke="#bcd2dd" stroke-width="3"/><circle cx="${px}" cy="${py}" r="8" fill="#20a18f"/><circle cx="${px}" cy="${py}" r="19" fill="#20a18f" opacity=".16"/><circle cx="${px}" cy="${py}" r="30" fill="none" stroke="#20a18f" stroke-width="1.2" opacity=".25"/></g></svg><div class="agency-map-footer"><span><i class="agency-map-dot"></i>${name}</span><span>${precise?'Coordenadas del perfil':'Se mostrará la posición exacta si el catálogo aporta coordenadas'}</span></div></article>`;
  }
  function dashboardMarkup(){
    return `<section class="agency-command-surface"><div class="agency-command-grid"><div class="agency-panel"><div class="agency-panel-head"><div><div class="kicker">Decision intelligence</div><h3>Qué merece atención ahora</h3></div><span class="badge ok">explicable</span></div><div class="agency-priority"><span class="agency-rank">01</span><div><strong>Seguridad y continuidad</strong><div class="small muted">obligación + impacto alto + capacidad asumible</div></div><span class="agency-score">Alta</span></div><div class="agency-priority"><span class="agency-rank">02</span><div><strong>Agua y eficiencia operativa</strong><div class="small muted">señal territorial + proyectos maduros + financiación</div></div><span class="agency-score">Alta</span></div><div class="agency-priority"><span class="agency-rank">03</span><div><strong>Energía y alumbrado</strong><div class="small muted">ahorro medible + precedentes replicables</div></div><span class="agency-score">Media</span></div><div class="agency-mini-chart" aria-hidden="true"><i style="height:38%"></i><i style="height:52%"></i><i style="height:45%"></i><i style="height:61%"></i><i style="height:68%"></i><i style="height:76%"></i><i style="height:72%"></i><i style="height:88%"></i><i style="height:94%"></i></div></div><div class="agency-panel dark"><div class="kicker" style="color:#a8eadd">Relaciones</div><h3>Del dato a la acción</h3><p class="small" style="color:#cbe0e7">Brújula muestra dependencias, no solo fichas.</p><div class="agency-network"><span class="agency-node primary" style="left:37%;top:42%">Municipio</span><span class="agency-node" style="left:7%;top:15%">Norma</span><span class="agency-node" style="right:7%;top:15%">Ayuda</span><span class="agency-node" style="left:6%;bottom:18%">Proyecto</span><span class="agency-node" style="right:8%;bottom:17%">Caso real</span><span class="agency-node" style="left:39%;top:7%">Servicio</span><span class="agency-node" style="left:39%;bottom:7%">Plan 90 días</span></div></div></div></section>`;
  }
  function injectVisuals(){
    const path=location.pathname.toLowerCase();
    const hero=q('.hero,.hero-v12,.detail-hero,.cockpit-top');
    if(hero && !q('.agency-spain-map-card')){
      const target=q('.hero-grid,.hero-v12-grid',hero)||q('.shell',hero);
      if(target && (path==='/'||path.endsWith('/index.html')||path.includes('/municipio')||path.includes('/inteligencia')||path.includes('/cockpit')||path.includes('/ejecutivo'))){
        const wrap=document.createElement('div'); wrap.className='agency-map-injection'; wrap.innerHTML=mapMarkup(getProfile());
        if(target.children.length>1) target.appendChild(wrap); else hero.insertAdjacentElement('afterend',wrap);
      }
    }
    const main=q('main');
    if(main && !q('.agency-command-surface') && (path==='/'||path.endsWith('/index.html')||path.includes('/cockpit')||path.includes('/ejecutivo'))){
      const firstSection=q('section',main); if(firstSection) firstSection.insertAdjacentHTML('afterend',`<section class="section agency-command-section"><div class="shell"><div class="section-head"><div><div class="kicker">Command Center</div><h2>Decisiones, no documentos.</h2><p class="muted">Una capa visual para priorizar, entender dependencias y detectar el siguiente movimiento.</p></div></div>${dashboardMarkup()}</div></section>`);
    }
  }
  function backupBanner(){
    if(q('.agency-backup-banner')) return;
    let has=false;
    try{has=!!localStorage.length}catch(e){}
    if(!has) return;
    const banner=document.createElement('aside'); banner.className='agency-backup-banner'; banner.innerHTML=`<div><strong>Tu trabajo se guarda solo en este navegador</strong><span>Descarga una copia si has configurado municipio, prioridades o elementos guardados.</span></div><a class="btn" href="${base()}espacio/">Revisar copia local</a><button class="agency-backup-close" aria-label="Cerrar aviso">×</button>`;
    document.body.appendChild(banner); q('.agency-backup-close',banner).onclick=()=>banner.remove();
  }
  function keyboardSearch(){
    window.addEventListener('keydown',e=>{
      if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='k'){
        const input=q('[data-global-search] input, .searchbox input'); if(input){e.preventDefault(); input.focus(); input.select();}
      }
    });
  }
  function init(){brand();injectVisuals();backupBanner();keyboardSearch();}
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',init); else init();
  window.addEventListener('bm-ready',()=>{brand();injectVisuals();});
})();
