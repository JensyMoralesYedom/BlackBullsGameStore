"""
Widgets reutilizables de la Fase 4:

- ScrollableFrame: área con scroll vertical.
- TarjetaJuego: tarjeta de juego con botón de compra (RF-4 / RF-5 / RF-6).
- generar_logo: monograma "BB" dorado sobre el fondo del sidebar (RF-r1).
"""

import os
import tkinter as tk

from styles import (
    COLOR_BORDE,
    COLOR_DORADO,
    COLOR_FONDO,
    COLOR_PANEL,
    COLOR_TEXTO,
    COLOR_TEXTO_SECUNDARIO,
    FUENTE_BOTON,
    FUENTE_PEQUEÑA,
)

_PAQUETE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def vincular_hover(boton, normal, hover):
    """Feedback visual de hover sobre un botón (Fase 5, punto 5.2)."""
    boton.bind("<Enter>", lambda _e: boton.configure(bg=hover))
    boton.bind("<Leave>", lambda _e: boton.configure(bg=normal))
    return boton


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

        self._cargar_portada()

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
            boton = tk.Button(
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
            )
            boton.pack(fill="x", padx=14, pady=(14, 12), ipady=6)
            vincular_hover(boton, COLOR_DORADO, "#a8861e")

    def _cargar_portada(self):
        """Muestra la portada del juego (tk.PhotoImage, sin dependencias) o un
        placeholder con la inicial si el archivo no existe (Fase 6)."""
        self._cover_img = None
        ruta = self._ruta_absoluta_portada()
        if ruta is not None:
            try:
                img = tk.PhotoImage(file=ruta)
                factor = 1
                while img.width() // factor > 260:
                    factor += 1
                if factor > 1:
                    img = img.subsample(factor)
                self._cover_img = img
                tk.Label(self, image=img, bg=COLOR_PANEL).pack(fill="x", pady=(12, 0))
                return
            except tk.TclError:
                self._cover_img = None
        self._placeholder_portada()

    def _ruta_absoluta_portada(self):
        """Resuelve portada_path (relativo a la raíz del paquete) a ruta absoluta."""
        if not self.juego.portada_path:
            return None
        return os.path.join(_PAQUETE_DIR, self.juego.portada_path)

    def _placeholder_portada(self):
        marco = tk.Frame(
            self,
            bg=COLOR_BORDE,
            highlightbackground=COLOR_BORDE,
            highlightthickness=1,
            height=90,
        )
        marco.pack(fill="x", padx=14, pady=(12, 0))
        marco.pack_propagate(False)
        tk.Label(
            marco,
            text=self.juego.titulo[0].upper(),
            font=("Segoe UI", 40, "bold"),
            bg=COLOR_BORDE,
            fg=COLOR_DORADO,
        ).pack(expand=True)


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
