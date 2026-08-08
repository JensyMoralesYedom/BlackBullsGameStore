"""
Vista Comunidad (RF-7): comentarios/reseñas persistidos en la tabla
`reseñas`. Sin chat en tiempo real: se guarda el texto y se vuelve a mostrar.
"""

import tkinter as tk

from models import juego as juego_model
from models import resena as resena_model
from utils import session
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
    FUENTE_SUBTITULO,
)
from views.widgets import ScrollableFrame, vincular_hover


class ComunidadView(tk.Frame):
    def __init__(self, master, app=None):
        super().__init__(master, bg=COLOR_FONDO)
        self._juegos = juego_model.listar()
        self._var_juego = tk.StringVar(value="General")
        self._construir()
        self._refrescar_resenas()

    def _construir(self):
        tk.Label(
            self,
            text="COMUNIDAD",
            font=FUENTE_SUBTITULO,
            bg=COLOR_FONDO,
            fg=COLOR_DORADO,
        ).pack(anchor="w", padx=24, pady=(20, 4))

        tk.Label(
            self,
            text="Comentá sobre los juegos y contá tu experiencia.",
            font=FUENTE_PEQUEÑA,
            bg=COLOR_FONDO,
            fg=COLOR_TEXTO_SECUNDARIO,
        ).pack(anchor="w", padx=24)

        # --- Formulario de reseña ---
        panel = tk.Frame(self, bg=COLOR_PANEL, highlightbackground=COLOR_BORDE, highlightthickness=1, bd=0)
        panel.pack(fill="x", padx=24, pady=(16, 8))

        fila_juego = tk.Frame(panel, bg=COLOR_PANEL)
        fila_juego.pack(fill="x", padx=14, pady=(12, 6))

        tk.Label(
            fila_juego,
            text="Juego:  ",
            font=FUENTE_PEQUEÑA,
            bg=COLOR_PANEL,
            fg=COLOR_TEXTO_SECUNDARIO,
        ).pack(side="left")

        opciones = ["General"] + [j.titulo for j in self._juegos]
        menu = tk.OptionMenu(fila_juego, self._var_juego, *opciones)
        menu.configure(
            font=FUENTE_PEQUEÑA,
            bg=COLOR_PANEL,
            fg=COLOR_TEXTO,
            activebackground=COLOR_BORDE,
            activeforeground=COLOR_DORADO,
            bd=0,
            highlightthickness=0,
        )
        menu["menu"].configure(
            bg=COLOR_PANEL, fg=COLOR_TEXTO, activebackground=COLOR_BORDE, activeforeground=COLOR_DORADO, bd=0
        )
        menu.pack(side="left")

        self.texto = tk.Text(
            panel,
            font=FUENTE_CUERPO,
            bg=COLOR_FONDO,
            fg=COLOR_TEXTO,
            insertbackground=COLOR_TEXTO,
            bd=0,
            highlightbackground=COLOR_BORDE,
            highlightthickness=1,
            height=3,
            wrap="word",
        )
        self.texto.pack(fill="x", padx=14, pady=(6, 8))
        self.texto.bind("<Control-Return>", lambda _e: self._publicar())

        self.label_error = tk.Label(
            panel,
            text="",
            font=FUENTE_PEQUEÑA,
            bg=COLOR_PANEL,
            fg=COLOR_ROJO,
        )
        self.label_error.pack(anchor="w", padx=14)

        btn_publicar = tk.Button(
            panel,
            text="PUBLICAR",
            font=FUENTE_BOTON,
            bg=COLOR_DORADO,
            fg=COLOR_FONDO,
            activebackground="#a8861e",
            activeforeground=COLOR_FONDO,
            bd=0,
            cursor="hand2",
            command=self._publicar,
        )
        btn_publicar.pack(anchor="w", padx=14, pady=(4, 12), ipadx=14, ipady=4)
        vincular_hover(btn_publicar, COLOR_DORADO, "#a8861e")

        # --- Lista de reseñas ---
        self.scroll = ScrollableFrame(self, bg=COLOR_FONDO)
        self.scroll.pack(fill="both", expand=True, padx=24, pady=(8, 24))

    def _publicar(self):
        self.label_error.configure(text="")
        comentario = self.texto.get("1.0", "end").strip()
        if not comentario:
            self.label_error.configure(text="Escribí un comentario antes de publicar.")
            return

        usuario = session.usuario_actual()
        if usuario is None:
            return

        juego_id = None
        for j in self._juegos:
            if j.titulo == self._var_juego.get():
                juego_id = j.id
                break

        resena_model.agregar(usuario.id, juego_id, comentario)
        self.texto.delete("1.0", "end")
        self._refrescar_resenas()

    def _refrescar_resenas(self):
        for widget in self.scroll.contenido.winfo_children():
            widget.destroy()

        resenas = resena_model.listar()
        if not resenas:
            tk.Label(
                self.scroll.contenido,
                text="Todavía no hay comentarios. ¡Sé el primero!",
                font=FUENTE_CUERPO,
                bg=COLOR_FONDO,
                fg=COLOR_TEXTO_SECUNDARIO,
            ).pack(pady=32)
            return

        for resena in resenas:
            tarjeta = tk.Frame(
                self.scroll.contenido,
                bg=COLOR_PANEL,
                highlightbackground=COLOR_BORDE,
                highlightthickness=1,
                bd=0,
            )
            tarjeta.pack(fill="x", pady=4)

            cabecera = tk.Frame(tarjeta, bg=COLOR_PANEL)
            cabecera.pack(fill="x", padx=12, pady=(8, 0))
            tk.Label(
                cabecera,
                text=resena.usuario,
                font=("Segoe UI", 10, "bold"),
                bg=COLOR_PANEL,
                fg=COLOR_DORADO,
            ).pack(side="left")
            tk.Label(
                cabecera,
                text=f"  ·  {resena.juego}",
                font=FUENTE_PEQUEÑA,
                bg=COLOR_PANEL,
                fg=COLOR_TEXTO_SECUNDARIO,
            ).pack(side="left")
            tk.Label(
                cabecera,
                text=resena.fecha,
                font=(FUENTE_PEQUEÑA[0], FUENTE_PEQUEÑA[1]),
                bg=COLOR_PANEL,
                fg=COLOR_TEXTO_SECUNDARIO,
            ).pack(side="right")

            tk.Label(
                tarjeta,
                text=resena.comentario,
                font=FUENTE_CUERPO,
                bg=COLOR_PANEL,
                fg=COLOR_TEXTO,
                anchor="w",
                justify="left",
                wraplength=700,
            ).pack(fill="x", padx=12, pady=(4, 10))
