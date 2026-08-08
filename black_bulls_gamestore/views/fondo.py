"""
Widgets de fondo (Fase 7):

- FondoLabel: fondo de collage borroso que llena un contenedor y se regenera
  al redimensionar. Ideal para pantallas con zonas libres (login/registro).
- FondoCanvas: Canvas que dibuja el collage y, encima, tintes RGBA
  semitransparentes (paneles de vidrio esmerilado). Los widgets interactivos
  se incrustan con create_window y quedan encima del tinte.
"""

import tkinter as tk

from utils import fondo as fondo_mod


class FondoLabel(tk.Label):
    """Imagen de fondo que cubre el contenedor y sigue el redimensionado."""

    def __init__(self, master):
        super().__init__(master, bg="#0a0a0a")
        self._img = None
        self.place(relx=0, rely=0, relwidth=1.0, relheight=1.0)
        master.bind("<Configure>", self._al_redimensionar, add="+")
        self._al_redimensionar()

    def _al_redimensionar(self, _e=None):
        ancho = self.master.winfo_width()
        alto = self.master.winfo_height()
        if ancho < 10 or alto < 10:
            return
        self._img = fondo_mod.fondo_tk(ancho, alto)
        self.configure(image=self._img)

    def bajar(self):
        self.lower()


class FondoCanvas(tk.Canvas):
    """Canvas con collage + tintes esmerilados redimensionables."""

    def __init__(self, master, *args, **kwargs):
        kwargs.setdefault("bg", "#0a0a0a")
        kwargs.setdefault("highlightthickness", 0)
        kwargs.setdefault("bd", 0)
        super().__init__(master, *args, **kwargs)
        self._img_base = None
        self._id_base = None
        self._zonas = []   # (rx, ry, rw, rh, rgba) en fracciones 0..1
        self._tintes = []  # (id_item, imagen_ref)
        self.bind("<Configure>", self._redibujar)

    def _redibujar(self, _e=None):
        ancho = self.winfo_width()
        alto = self.winfo_height()
        if ancho < 10 or alto < 10:
            return
        self._img_base = fondo_mod.fondo_tk(ancho, alto)
        if self._id_base is None:
            self._id_base = self.create_image(0, 0, anchor="nw", image=self._img_base)
        else:
            self.itemconfigure(self._id_base, image=self._img_base)
        self.tag_lower(self._id_base)
        self._redibujar_tintes()

    def _redibujar_tintes(self):
        for id_, _ in self._tintes:
            self.delete(id_)
        self._tintes = []
        ancho = max(self.winfo_width(), 1)
        alto = max(self.winfo_height(), 1)
        for rx, ry, rw, rh, rgba in self._zonas:
            x = int(ancho * rx)
            y = int(alto * ry)
            w = max(int(ancho * rw), 1)
            h = max(int(alto * rh), 1)
            img = fondo_mod.tint_tk(w, h, rgba)
            self._tintes.append((self.create_image(x, y, anchor="nw", image=img), img))

    def tintar(self, rx, ry, rw, rh, rgba=(22, 22, 22, 195)):
        """Agrega un panel de vidrio esmerilado en la zona dada (fracciones 0..1)."""
        self._zonas.append((rx, ry, rw, rh, rgba))
        self._redibujar_tintes()
