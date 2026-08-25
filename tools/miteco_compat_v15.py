#!/usr/bin/env python3
"""Compatibilidad de descarga para el portal GIS de MITECO.
Los enlaces públicos DescargaFichero son páginas de confirmación HTML, no ZIP crudos.
Este módulo reintenta con cabeceras de navegador y, si recibe un formulario, intenta su envío.
"""
from __future__ import annotations
import io, urllib.request, urllib.parse, urllib.error, http.cookiejar
from html.parser import HTMLParser

_ORIG = urllib.request.urlopen

class _Form(HTMLParser):
    def __init__(self):
        super().__init__(); self.action=None; self.method='post'; self.inputs=[]; self._in_form=False
    def handle_starttag(self, tag, attrs):
        d=dict(attrs)
        if tag.lower()=='form' and not self._in_form:
            self._in_form=True; self.action=d.get('action'); self.method=d.get('method','post').lower()
        elif self._in_form and tag.lower()=='input':
            name=d.get('name'); value=d.get('value',''); typ=d.get('type','text').lower()
            if name and typ not in {'file'}: self.inputs.append((name,value,typ))
    def handle_endtag(self, tag):
        if tag.lower()=='form' and self._in_form: self._in_form=False

class MemoryResponse(io.BytesIO):
    def __init__(self,data,url,headers=None,status=200):
        super().__init__(data); self._url=url; self.headers=headers or {}; self.status=status
    def geturl(self): return self._url
    def getcode(self): return self.status
    def __enter__(self): return self
    def __exit__(self,*args): self.close()

def _download_miteco(url, timeout=60):
    cj=http.cookiejar.CookieJar(); opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    headers={'User-Agent':'Mozilla/5.0 (compatible; BrujulaMunicipal/1.5)','Accept':'text/html,application/zip,*/*','Referer':'https://www.miteco.gob.es/es/cartografia-y-sig/ide/descargas/reto-demografico/'}
    req=urllib.request.Request(url,headers=headers)
    with opener.open(req,timeout=timeout) as r:
        data=r.read(); final=r.geturl(); ctype=r.headers.get('content-type','')
    if data[:2]==b'PK': return MemoryResponse(data,final,{'Content-Type':'application/zip'})
    text=data.decode('utf-8','ignore'); parser=_Form(); parser.feed(text)
    if parser.action is not None or parser.inputs:
        action=urllib.parse.urljoin(final,parser.action or final)
        vals={name:value for name,value,typ in parser.inputs if typ in {'hidden','submit','text','button'}}
        filename=urllib.parse.parse_qs(urllib.parse.urlparse(url).query).get('f',[''])[0]
        if filename and 'f' not in vals: vals['f']=filename
        post=urllib.parse.urlencode(vals).encode('utf-8')
        req2=urllib.request.Request(action,data=post,headers={**headers,'Content-Type':'application/x-www-form-urlencoded'})
        with opener.open(req2,timeout=timeout) as r2:
            d2=r2.read(); f2=r2.geturl(); ct2=r2.headers.get('content-type','')
        if d2[:2]==b'PK' or 'zip' in ct2.lower(): return MemoryResponse(d2,f2,{'Content-Type':ct2 or 'application/zip'})
    return MemoryResponse(data,final,{'Content-Type':ctype})

def install():
    def smart(req,*args,**kwargs):
        url=req.full_url if hasattr(req,'full_url') else str(req)
        if 'gis.miteco.gob.es/descargas/app/DescargaFichero?f=' in url:
            try: return _download_miteco(url,kwargs.get('timeout',60) or 60)
            except Exception:
                pass
        return _ORIG(req,*args,**kwargs)
    urllib.request.urlopen=smart
