"""
Vista Descubrir (RF-6): juegos destacados leídos desde la tabla `juegos`,
no hardcodeados. Cada tarjeta permite comprar.
"""

import tkinter as tk

from models import biblioteca as biblioteca_model
from models import juego as juego_model
from utils import session
from styles import (
    COLOR_FONDO,
    COLOR_DORADO,
    COLOR_TEXTO_SECUNDARIO,
    FUENTE_CUERPO,
    FUENTE_PEQUEÑA,
    FUENTE_SUBTITULO,
)
from views.widgets import ScrollableFrame, TarjetaJuego


class DescubrirView(tk.Frame):
    def __init__(self, master, app=None):
        super().__init__(master, bg=COLOR_FONDO)
        self._construir()

    def _construir(self):
        tk.Label(
            self,
            text="DESCUBRIR",
            font=FUENTE_SUBTITULO,
            bg=COLOR_FONDO,
            fg=COLOR_DORADO,
        ).pack(anchor="w", padx=24, pady=(20, 4))

        tk.Label(
            self,
            text="Lo mejor de la manada, seleccionado para vos.",
            font=FUENTE_PEQUEÑA,
            bg=COLOR_FONDO,
            fg=COLOR_TEXTO_SECUNDARIO,
        ).pack(anchor="w", padx=24)

        self.scroll = ScrollableFrame(self, bg=COLOR_FONDO)
        self.scroll.pack(fill="both", expand=True, padx=24, pady=(16, 24))

        self._refrescar()

    def _refrescar(self):
        for widget in self.scroll.contenido.winfo_children():
            widget.destroy()

        usuario = session.usuario_actual()
        usuario_id = usuario.id if usuario else None

        destacados = juego_model.destacados(limite=6)
        if not destacados:
            tk.Label(
                self.scroll.contenido,
                text="Pronto habrá juegos destacados.",
                font=FUENTE_CUERPO,
                bg=COLOR_FONDO,
                fg=COLOR_TEXTO_SECUNDARIO,
            ).pack(pady=48)
            return

        columnas = 3
        for i, juego in enumerate(destacados):
            fila, col = divmod(i, columnas)
            tarjeta = TarjetaJuego(
                self.scroll.contenido,
                juego,
                al_comprar=self._comprar,
                comprado=bool(usuario_id and biblioteca_model.tiene_juego(usuario_id, juego.id)),
            )
            tarjeta.grid(row=fila, column=col, sticky="nsew", padx=6, pady=6)
        for col in range(columnas):
            self.scroll.contenido.grid_columnconfigure(col, weight=1, uniform="tarjetas")

    def _comprar(self, juego):
        usuario = session.usuario_actual()
        if usuario is None:
            return
        biblioteca_model.agregar(usuario.id, juego.id)
        self._refrescar()
