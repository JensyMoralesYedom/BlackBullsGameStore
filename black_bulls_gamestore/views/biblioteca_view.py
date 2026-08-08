"""
Vista Biblioteca (RF-5): juegos que el usuario actual ya compró
(JOIN entre `biblioteca` y `juegos` filtrando por `usuario_id`).
Estado vacío con mensaje en vez de pantalla en blanco.
"""

import tkinter as tk

from models import biblioteca as biblioteca_model
from utils import session
from styles import (
    COLOR_BORDE,
    COLOR_DORADO,
    COLOR_FONDO,
    COLOR_TEXTO_SECUNDARIO,
    FUENTE_CUERPO,
    FUENTE_PEQUEÑA,
    FUENTE_SUBTITULO,
)
from views.widgets import ScrollableFrame, TarjetaJuego


class BibliotecaView(tk.Frame):
    def __init__(self, master, app=None):
        super().__init__(master, bg=COLOR_FONDO)
        self.app = app
        self._construir()

    def _construir(self):
        tk.Label(
            self,
            text="BIBLIOTECA",
            font=FUENTE_SUBTITULO,
            bg=COLOR_FONDO,
            fg=COLOR_DORADO,
        ).pack(anchor="w", padx=24, pady=(20, 4))

        tk.Label(
            self,
            text="Los juegos que ya son tuyos.",
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
        if usuario is None:
            return

        juegos = biblioteca_model.listar_por_usuario(usuario.id)
        if not juegos:
            self._estado_vacio()
            return

        columnas = 3
        for i, juego in enumerate(juegos):
            fila, col = divmod(i, columnas)
            tarjeta = TarjetaJuego(
                self.scroll.contenido,
                juego,
                comprado=True,
            )
            tarjeta.grid(row=fila, column=col, sticky="nsew", padx=6, pady=6)
        for col in range(columnas):
            self.scroll.contenido.grid_columnconfigure(col, weight=1, uniform="tarjetas")

    def _estado_vacio(self):
        marco = tk.Frame(self.scroll.contenido, bg=COLOR_FONDO)
        marco.pack(expand=True, pady=56)

        tk.Label(
            marco,
            text="Aún no tenés juegos",
            font=FUENTE_SUBTITULO,
            bg=COLOR_FONDO,
            fg=COLOR_TEXTO_SECUNDARIO,
        ).pack()

        tk.Label(
            marco,
            text="Andá a la Tienda y comprá tu primer título.",
            font=FUENTE_CUERPO,
            bg=COLOR_FONDO,
            fg=COLOR_TEXTO_SECUNDARIO,
        ).pack(pady=(6, 0))

        tk.Button(
            marco,
            text="IR A LA TIENDA",
            font=FUENTE_CUERPO,
            bg=COLOR_DORADO,
            fg=COLOR_FONDO,
            activebackground="#a8861e",
            activeforeground=COLOR_FONDO,
            bd=0,
            cursor="hand2",
            command=self._ir_a_tienda,
        ).pack(pady=(16, 0), ipadx=16, ipady=6)

    def _ir_a_tienda(self):
        if self.app is not None and hasattr(self.app._vista_actual, "_ir_a"):
            self.app._vista_actual._ir_a("Tienda")
