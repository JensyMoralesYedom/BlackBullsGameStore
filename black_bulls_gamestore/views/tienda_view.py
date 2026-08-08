"""
Vista Tienda (RF-4): catálogo de juegos desde la DB con búsqueda y filtro
por categoría. Comprar inserta en `biblioteca` y la tarjeta pasa a
"EN TU BIBLIOTECA" sin recrear la ventana.
"""

import tkinter as tk

from models import biblioteca as biblioteca_model
from models import juego as juego_model
from utils import session
from styles import (
    COLOR_BORDE,
    COLOR_DORADO,
    COLOR_FONDO,
    COLOR_PANEL,
    COLOR_TEXTO,
    COLOR_TEXTO_SECUNDARIO,
    FUENTE_CUERPO,
    FUENTE_PEQUEÑA,
    FUENTE_SUBTITULO,
)
from views.widgets import ScrollableFrame, TarjetaJuego


class TiendaView(tk.Frame):
    def __init__(self, master, app=None):
        super().__init__(master, bg=COLOR_FONDO)
        self._categoria = None
        self._busqueda = ""
        self._var_categoria = tk.StringVar(value="Todas")
        self._var_busqueda = tk.StringVar()
        self._construir()
        self._refrescar()

    def _construir(self):
        tk.Label(
            self,
            text="TIENDA",
            font=FUENTE_SUBTITULO,
            bg=COLOR_FONDO,
            fg=COLOR_DORADO,
        ).pack(anchor="w", padx=24, pady=(20, 4))

        tk.Label(
            self,
            text="Todos los juegos disponibles en Black Bulls.",
            font=FUENTE_PEQUEÑA,
            bg=COLOR_FONDO,
            fg=COLOR_TEXTO_SECUNDARIO,
        ).pack(anchor="w", padx=24)

        # --- Barra de herramientas: búsqueda + categoría ---
        barra = tk.Frame(self, bg=COLOR_FONDO)
        barra.pack(fill="x", padx=24, pady=(16, 8))

        caja = tk.Frame(barra, bg=COLOR_PANEL, highlightbackground=COLOR_BORDE, highlightthickness=1, bd=0)
        caja.pack(side="left")

        tk.Label(
            caja,
            text="Buscar:  ",
            font=FUENTE_PEQUEÑA,
            bg=COLOR_PANEL,
            fg=COLOR_TEXTO_SECUNDARIO,
        ).pack(side="left", padx=(10, 0), pady=4)

        self.entrada_busqueda = tk.Entry(
            caja,
            textvariable=self._var_busqueda,
            font=FUENTE_CUERPO,
            bg=COLOR_PANEL,
            fg=COLOR_TEXTO,
            insertbackground=COLOR_TEXTO,
            bd=0,
            width=28,
        )
        self.entrada_busqueda.pack(side="left", pady=4, padx=(0, 10))
        self.entrada_busqueda.bind(
            "<KeyRelease>", lambda _e: self._refrescar()
        )

        cat = tk.Frame(barra, bg=COLOR_PANEL, highlightbackground=COLOR_BORDE, highlightthickness=1, bd=0)
        cat.pack(side="left", padx=(12, 0))

        tk.Label(
            cat,
            text="Categoría:  ",
            font=FUENTE_PEQUEÑA,
            bg=COLOR_PANEL,
            fg=COLOR_TEXTO_SECUNDARIO,
        ).pack(side="left", padx=(10, 0), pady=4)

        self.menu_categorias = tk.OptionMenu(
            cat, self._var_categoria, "Todas", *juego_model.categorias()
        )
        self.menu_categorias.configure(
            font=FUENTE_PEQUEÑA,
            bg=COLOR_PANEL,
            fg=COLOR_TEXTO,
            activebackground=COLOR_BORDE,
            activeforeground=COLOR_DORADO,
            bd=0,
            highlightthickness=0,
        )
        self.menu_categorias["menu"].configure(
            bg=COLOR_PANEL, fg=COLOR_TEXTO, activebackground=COLOR_BORDE, activeforeground=COLOR_DORADO, bd=0
        )
        self.menu_categorias.pack(side="left", pady=2)
        self._var_categoria.trace_add("write", lambda *_a: self._refrescar())

        self.label_conteo = tk.Label(
            barra,
            text="",
            font=FUENTE_PEQUEÑA,
            bg=COLOR_FONDO,
            fg=COLOR_TEXTO_SECUNDARIO,
        )
        self.label_conteo.pack(side="right")

        # --- Grid con scroll ---
        self.scroll = ScrollableFrame(self, bg=COLOR_FONDO)
        self.scroll.pack(fill="both", expand=True, padx=24, pady=(8, 24))

    def _refrescar(self):
        self._busqueda = self._var_busqueda.get().strip()
        valor = self._var_categoria.get()
        self._categoria = None if valor in ("Todas", "") else valor

        juegos = juego_model.listar(self._categoria, self._busqueda)
        self.label_conteo.configure(text=f"{len(juegos)} juego(s)")
        self._dibujar(juegos)

    def _dibujar(self, juegos):
        for widget in self.scroll.contenido.winfo_children():
            widget.destroy()

        if not juegos:
            tk.Label(
                self.scroll.contenido,
                text="No hay juegos que coincidan con la búsqueda.",
                font=FUENTE_CUERPO,
                bg=COLOR_FONDO,
                fg=COLOR_TEXTO_SECUNDARIO,
            ).pack(pady=48)
            return

        usuario = session.usuario_actual()
        usuario_id = usuario.id if usuario else None

        columnas = 3
        for i, juego in enumerate(juegos):
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
