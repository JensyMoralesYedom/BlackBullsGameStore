"""
Fondo de la app (Fase 7): collage de portadas difuminado.

Construye una imagen de fondo a partir de las portadas reales de
assets/juegos/, la difumina fuertemente y la mezcla con el negro del tema
(~28%) para que se vea como un fondo "semi-transparente". También genera
tintes RGBA para los paneles de vidrio esmerilado.

Requiere Pillow EN RUNTIME (decisión del proyecto). Los PNG finales se
vuelcan a la UI vía ImageTk.PhotoImage; el Tk compone el canal alfa de los
tintes sobre el collage cuando ambos viven en el mismo Canvas.
"""

import glob
import os

from PIL import Image, ImageFilter, ImageOps, ImageTk

_BASE_TAM = (1280, 800)
_MEZCLA_IMAGEN = 0.28  # qué tanto del collage se ve sobre el negro
_NEGRO = (10, 10, 10)  # #0a0a0a

_COVERS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "juegos"
)

_COLAGE_CACHE = None


def _construir_colage():
    base = Image.new("RGB", _BASE_TAM, _NEGRO)
    covers = sorted(glob.glob(os.path.join(_COVERS_DIR, "*.png")))
    if covers:
        ancho_celda = _BASE_TAM[0] // 5
        alto_celda = _BASE_TAM[1] // 2
        for i, ruta in enumerate(covers[:10]):
            img = Image.open(ruta).convert("RGB")
            img = ImageOps.fit(img, (ancho_celda, alto_celda), Image.LANCZOS)
            fila, col = divmod(i, 5)
            base.paste(img, (col * ancho_celda, fila * alto_celda))
    borroso = base.filter(ImageFilter.GaussianBlur(42))
    fondo = Image.new("RGB", _BASE_TAM, _NEGRO)
    return Image.blend(fondo, borroso, _MEZCLA_IMAGEN)


def colage():
    """Collage borroso base, cacheado para reusarlo en el redimensionado."""
    global _COLAGE_CACHE
    if _COLAGE_CACHE is None:
        _COLAGE_CACHE = _construir_colage()
    return _COLAGE_CACHE


def fondo_tk(ancho, alto):
    """PhotoImage del collage a tamaño exacto (sin bordes al redimensionar)."""
    ancho = max(int(ancho), 1)
    alto = max(int(alto), 1)
    img = colage().resize((ancho, alto), Image.BILINEAR)
    return ImageTk.PhotoImage(img)


def tint_tk(ancho, alto, rgba=(22, 22, 22, 195)):
    """Tinte RGBA plano para los paneles de vidrio esmerilado."""
    ancho = max(int(ancho), 1)
    alto = max(int(alto), 1)
    return ImageTk.PhotoImage(Image.new("RGBA", (ancho, alto), rgba))
