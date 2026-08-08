"""
Descarga portadas reales de juegos (Fase 6, 2ª iteración).

Baja la imagen 'header.jpg' de cada juego desde el CDN de Steam, la recorta
a 320x180 y la guarda como PNG en assets/juegos/ con el nombre que el seed
usa en `portada_path`. Solo requiere Pillow para la conversión; la app lee
los PNG con tk.PhotoImage (stdlib).

Uso (desde la raíz del paquete):
    python assets/descargar_portadas.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import urllib.request

from PIL import Image, ImageOps

from database import db

ANCHO, ALTO = 320, 180
SALIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "juegos")

# appid de Steam para cada título (header.jpg del CDN de Steam)
JUEGOS_REALES = [
    ("Cyberpunk 2077", 1091500),
    ("Elden Ring", 1245620),
    ("God of War", 1593500),
    ("Forza Horizon 5", 1551360),
    ("Halo: The Master Chief Collection", 976730),
    ("Age of Empires IV", 1466860),
    ("Stardew Valley", 413150),
    ("Hades", 1145360),
    ("The Witcher 3: Wild Hunt", 292030),
    ("Rocket League", 252950),
]

_CDN = "https://cdn.cloudflare.steamstatic.com/steam/apps/{}/header.jpg"


def descargar(titulo, appid):
    url = _CDN.format(appid)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        datos = r.read()
    if len(datos) < 1000:
        raise ValueError("imagen vacía o inesperada")

    img = Image.open(__import__("io").BytesIO(datos))
    img = ImageOps.fit(img, (ANCHO, ALTO), Image.LANCZOS)
    ruta = os.path.join(SALIDA, os.path.basename(db.portada_relativa(titulo)))
    img.save(ruta, "PNG")
    return ruta


def main():
    os.makedirs(SALIDA, exist_ok=True)
    ok, fallidos = 0, []
    for titulo, appid in JUEGOS_REALES:
        try:
            ruta = descargar(titulo, appid)
            print(f"  {titulo:35} -> {os.path.basename(ruta)}")
            ok += 1
        except Exception as e:
            print(f"  {titulo:35} ERROR: {e}")
            fallidos.append(titulo)
    print(f"\n{ok} portadas descargadas en {SALIDA}")
    if fallidos:
        print("Fallaron:", ", ".join(fallidos))
    return fallidos


if __name__ == "__main__":
    main()
