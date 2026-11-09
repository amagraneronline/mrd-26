#!/usr/bin/env python3
"""Descarga las fotografías seleccionadas de Wikimedia Commons para uso local.

Solo usa la biblioteca estándar de Python (3.9+). Las imágenes son reales,
no generadas; autores, enlaces y licencias en imagenes_infografia/fuentes_imagenes.json.
"""
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from urllib.parse import quote
import json, time, sys, hashlib

ROOT = Path(__file__).resolve().parent
DEST = ROOT / 'imagenes_infografia'
ITEMS = json.loads((DEST/'fuentes_imagenes.json').read_text(encoding='utf-8'))


def foto_valida(path):
    try:
        with open(path, 'rb') as f:
            sig = f.read(3)
        return path.stat().st_size > 4000 and sig[:2] == b'\xff\xd8'
    except OSError:
        return False


def descargar(f):
    path = DEST / f['file']
    if foto_valida(path):
        print('YA EXISTE:', f['file'])
        return True
    filename = quote(f['commons_filename'].replace(' ', '_'), safe='()_-.,')
    urls = [
        f['remote_url'],
        'https://commons.wikimedia.org/wiki/Special:FilePath/'+filename+'?width=960',
        'https://commons.wikimedia.org/wiki/Special:Redirect/file/'+filename+'?width=960',
        'https://commons.wikimedia.org/wiki/Special:FilePath/'+filename,
    ]
    for attempt, url in enumerate(urls, 1):
        try:
            req = Request(url, headers={'User-Agent':'InfografiaEducativaESO/1.0 (material docente; download de Wikimedia Commons)', 'Accept':'image/jpeg,image/*;q=0.9,*/*;q=0.1'})
            with urlopen(req, timeout=35) as resp:
                content = resp.read(12_000_000)
                if len(content) >= 12_000_000:
                    raise ValueError('Imagen demasiado grande')
            if not content.startswith(b'\xff\xd8'):
                raise ValueError('No se recibió un archivo JPEG; ¿hay un bloqueo de conexión?')
            tmp=path.with_suffix('.tmp')
            tmp.write_bytes(content)
            tmp.replace(path)
            print('OK:',f['file'],f'({len(content)//1024} KB)')
            return True
        except (HTTPError,URLError,TimeoutError,OSError,ValueError) as exc:
            print(f'  Intento {attempt} fallido: {str(exc)[:110]}')
            time.sleep(1)
    print('PENDIENTE:',f['file'],'\n  Fuente:',f['source_url'])
    return False


def main():
    DEST.mkdir(exist_ok=True)
    print('Descargando fotografías verificadas de Wikimedia Commons...\n')
    successes=sum(descargar(f) for f in ITEMS)
    print(f'\nResultado: {successes} de {len(ITEMS)} fotografías disponibles en {DEST.name}/')
    if successes != len(ITEMS):
        print('Revisa la conexión a Internet y vuelve a ejecutar este archivo. No se modificó la infografía.')
    else:
        print('La infografía ya funciona SIN CONEXIÓN con las fotografías locales.')
    return int(successes!=len(ITEMS))

if __name__=='__main__':
    sys.exit(main())
