"""
Widgets reutilizables de la Fase 4:

- ScrollableFrame: área con scroll vertical.
- TarjetaJuego: tarjeta de juego con botón de compra (RF-4 / RF-5 / RF-6).
- generar_logo: monograma "BB" dorado sobre el fondo del sidebar (RF-r1).
"""

import tkinter as tk

from styles import (
    COLOR_BORDE,
    COLOR_DORADO,
    COLOR_FONDO,
    COLOR_PANEL,
    COLOR_ROJO,
    COLOR_TEXTO,
    COLOR_TEXTO_SECUNDARIO,
    FUENTE_BOTON,
    FUENTE_CUERPO,
    FUENTE_PEQUEÑA,
)


class ScrollableFrame(tk.Frame):
    """Contenedor con scroll vertical. Usar .contenido como área interior."""

    def __init__(self, master, bg=COLOR_FONDO):
        super().__init__(master, bg=bg)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0)
        self.barra = tk.Scrollbar(
            self,
            orient="vertical",
            command=self.canvas.yview,
            bg=COLOR_PANEL,
            activebackground=COLOR_DORADO,
            troughcolor=bg,
            bd=0,
            relief="flat",
        )
        self.contenido = tk.Frame(self.canvas, bg=bg)
        self._id_contenido = self.canvas.create_window(
            (0, 0), window=self.contenido, anchor="nw"
        )

        self.canvas.configure(yscrollcommand=self.barra.set)
        self.barra.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.contenido.bind(
            "<Configure>",
            lambda _e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )
        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfigure(self._id_contenido, width=e.width),
        )

        self.canvas.bind("<Enter>", lambda _e: self.canvas.bind_all("<MouseWheel>", self._on_scroll))
        self.canvas.bind("<Leave>", lambda _e: self.canvas.unbind_all("<MouseWheel>"))

    def _on_scroll(self, evento):
        self.canvas.yview_scroll(int(-evento.delta / 120), "units")


class TarjetaJuego(tk.Frame):
    """Tarjeta de un juego: título, categoría, precio, descripción y compra."""

    def __init__(self, master, juego, al_comprar=None, comprado=False):
        super().__init__(
            master,
            bg=COLOR_PANEL,
            highlightbackground=COLOR_BORDE,
            highlightthickness=1,
            bd=0,
        )
        self.juego = juego

        tk.Label(
            self,
            text=juego.titulo,
            font=("Segoe UI", 12, "bold"),
            bg=COLOR_PANEL,
            fg=COLOR_TEXTO,
            anchor="w",
            wraplength=200,
            justify="left",
        ).pack(fill="x", padx=14, pady=(12, 0))

        tk.Label(
            self,
            text=juego.categoria.upper(),
            font=(FUENTE_PEQUEÑA[0], FUENTE_PEQUEÑA[1]),
            bg=COLOR_PANEL,
            fg=COLOR_TEXTO_SECUNDARIO,
            anchor="w",
        ).pack(fill="x", padx=14)

        tk.Label(
            self,
            text=f"US$ {juego.precio:.2f}",
            font=("Segoe UI", 14, "bold"),
            bg=COLOR_PANEL,
            fg=COLOR_DORADO,
            anchor="w",
        ).pack(fill="x", padx=14, pady=(8, 0))

        tk.Label(
            self,
            text=juego.descripcion,
            font=FUENTE_PEQUEÑA,
            bg=COLOR_PANEL,
            fg=COLOR_TEXTO_SECUNDARIO,
            anchor="w",
            justify="left",
            wraplength=200,
        ).pack(fill="x", padx=14, pady=(8, 0))

        if comprado:
            tk.Button(
                self,
                text="EN TU BIBLIOTECA",
                font=FUENTE_BOTON,
                bg=COLOR_BORDE,
                fg=COLOR_DORADO,
                bd=0,
                state="disabled",
                disabledforeground=COLOR_DORADO,
                cursor="arrow",
            ).pack(fill="x", padx=14, pady=(14, 12), ipady=6)
        else:
            tk.Button(
                self,
                text="COMPRAR",
                font=FUENTE_BOTON,
                bg=COLOR_DORADO,
                fg=COLOR_FONDO,
                activebackground="#a8861e",
                activeforeground=COLOR_FONDO,
                bd=0,
                cursor="hand2",
                command=lambda: al_comprar(self.juego),
            ).pack(fill="x", padx=14, pady=(14, 12), ipady=6)


# --- Logo "BB" generado por código (RF-r1: imagen en la pantalla principal) ---

_BITMAP_B = [
    "#####",
    "#...#",
    "#...#",
    "####.",
    "#...#",
    "#...#",
    "#####",
]


def generar_logo(escala=9, color=COLOR_DORADO):
    """Monograma 'BB' dorado sobre fondo transparente para el sidebar."""
    h = len(_BITMAP_B)
    w = len(_BITMAP_B[0])
    ancho = w * escala * 2 + 2 * escala
    alto = h * escala
    img = tk.PhotoImage(width=ancho, height=alto)
    for f in range(h):
        for c in range(w):
            if _BITMAP_B[f][c] == "#":
                x0 = c * escala
                y0 = f * escala
                for dy in range(escala):
                    for dx in range(escala):
                        img.put(color, to=(x0 + dx, y0 + dy))
                        img.put(color, to=(x0 + dx + w * escala + 2 * escala, y0 + dy))
    return img
