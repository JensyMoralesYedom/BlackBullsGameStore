"""
Generador de portadas de respaldo (Fase 6).

Genera un PNG por juego en assets/juegos/ (gradiente oscuro, borde dorado,
inicial grande y título) SOLO para los juegos que aún no tienen portada
descargada. Las portadas reales se bajan con assets/descargar_portadas.py.

Uso (desde la raíz del paquete):
    python assets/generar_portadas.py

Solo requiere Pillow para GENERAR; la app en ejecución las lee con
tk.PhotoImage (stdlib), sin dependencias extra.
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image, ImageDraw, ImageFont

from database import db

ANCHO, ALTO = 320, 180

ROJO_INI, VERDE_INI, AZUL_INI = 22, 22, 22     # #161616
ROJO_FIN, VERDE_FIN, AZUL_FIN = 10, 10, 10     # #0a0a0a
DORADO = (201, 162, 39)                        # #c9a227
TEXTO = (245, 245, 240)                        # #f5f5f0
SECUNDARIO = (154, 154, 154)                   # #9a9a9a

SALIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "juegos")


def _slug(titulo):
    return re.sub(r"[^a-z0-9]+", "_", titulo.lower()).strip("_")


def _fuente(tamano, bold=True):
    nombres = (["segoeuib.ttf", "arialbd.ttf"] if bold else ["segoeui.ttf", "arial.ttf"])
    for nombre in nombres:
        ruta = os.path.join(os.environ.get("WINDIR", "C:/Windows"), "Fonts", nombre)
        try:
            return ImageFont.truetype(ruta, tamano)
        except Exception:
            continue
    try:
        return ImageFont.load_default(tamano)
    except TypeError:
        return ImageFont.load_default()


def _fondo(dib):
    for y in range(ALTO):
        t = y / (ALTO - 1)
        r = int(ROJO_INI + (ROJO_FIN - ROJO_INI) * t)
        g = int(VERDE_INI + (VERDE_FIN - VERDE_INI) * t)
        b = int(AZUL_INI + (AZUL_FIN - AZUL_INI) * t)
        dib.line([(0, y), (ANCHO, y)], fill=(r, g, b))


def _texto_centrado(dib, x0, x1, y, texto, fuente, color):
    bbox = dib.textbbox((0, 0), texto, font=fuente)
    ancho = bbox[2] - bbox[0]
    dib.text(((x0 + x1 - ancho) / 2, y), texto, font=fuente, fill=color)


def generar_portada(titulo):
    img = Image.new("RGB", (ANCHO, ALTO))
    dib = ImageDraw.Draw(img)
    _fondo(dib)

    # Borde dorado fino
    dib.rectangle([1, 1, ANCHO - 2, ALTO - 2], outline=DORADO, width=2)

    # Inicial grande en dorado
    inicial = titulo[0].upper()
    fuente_inicial = _fuente(130)
    dib.text((36, 18), inicial, font=fuente_inicial, fill=DORADO)

    # Línea separadora
    dib.line([(30, 128), (ANCHO - 30, 128)], fill=(58, 58, 58), width=1)

    # Título al pie
    fuente_titulo = _fuente(22)
    _texto_centrado(dib, 16, ANCHO - 16, 138, titulo, fuente_titulo, TEXTO)

    # Marca
    fuente_marca = _fuente(11, bold=False)
    _texto_centrado(dib, 16, ANCHO - 16, 166, "BLACK BULLS GAMESTORE", fuente_marca, SECUNDARIO)

    ruta = os.path.join(SALIDA, f"{_slug(titulo)}.png")
    img.save(ruta, "PNG")
    return ruta


def main():
    os.makedirs(SALIDA, exist_ok=True)
    conn = db.conectar()
    filas = conn.execute("SELECT id, titulo FROM juegos").fetchall()
    creadas, omitidas = 0, 0
    for fila in filas:
        destino = os.path.join(SALIDA, f"{_slug(fila['titulo'])}.png")
        if os.path.exists(destino):
            omitidas += 1
            continue
        ruta = generar_portada(fila["titulo"])
        portada = f"assets/juegos/{os.path.basename(ruta)}"
        with conn:
            conn.execute(
                "UPDATE juegos SET portada_path = ? WHERE id = ?",
                (portada, fila["id"]),
            )
        print(f"  {fila['titulo']:25} -> {portada}")
        creadas += 1
    conn.close()
    print(f"\n{creadas} portadas generadas, {omitidas} omitidas (ya existían) en {SALIDA}")


if __name__ == "__main__":
    main()
