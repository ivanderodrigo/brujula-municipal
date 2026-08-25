#!/usr/bin/env python3
"""Refuerza accesibilidad estructural de todas las páginas HTML generadas."""
from __future__ import annotations
from pathlib import Path
import re, sys
ROOT=Path(__file__).resolve().parents[1]
def patch(text:str):
    # Conserva ids funcionales existentes (p.ej. modo presentación) y hace que el enlace de salto apunte al main real.
    m=re.search(r'<main[^>]*\bid=["\']([^"\']+)["\']',text,re.I)
    target=m.group(1) if m else 'main-content'
    if not m:
        text=re.sub(r'<main(?![^>]*\bid=)([^>]*)>', r'<main id="main-content"\1>', text, count=1)
    if 'class="skip-link"' not in text:
        skip=f'<a class="skip-link" href="#{target}">Saltar al contenido principal</a>'
        text=re.sub(r'<body([^>]*)>', lambda mm:mm.group(0)+skip, text, count=1, flags=re.I)
    text=text.replace('<nav class="navlinks">','<nav class="navlinks" aria-label="Navegación principal">')
    text=text.replace('<div class="search-results" data-search-results>','<div class="search-results" data-search-results aria-live="polite">')
    # Tablas con scroll deben poder recibir foco con teclado para usuarios de teclado/lector.
    text=text.replace('<div class="table-wrap">','<div class="table-wrap" tabindex="0" role="region" aria-label="Tabla desplazable">')
    return text

def main():
    count=0
    for p in ROOT.rglob('*.html'):
        if any(part in {'tools','cache'} for part in p.parts): continue
        old=p.read_text(encoding='utf-8',errors='ignore'); new=patch(old)
        if new!=old:
            p.write_text(new,encoding='utf-8'); count+=1
    print(f'OK · accesibilidad estructural aplicada a {count} páginas modificadas.')
    return 0
if __name__=='__main__': sys.exit(main())
