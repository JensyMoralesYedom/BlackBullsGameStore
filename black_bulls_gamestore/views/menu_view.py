"""
Vista de menú (pantalla principal): sidebar con las cinco secciones y logo,
y un área central que conmuta entre las vistas de la Fase 4 sin recrear la
ventana. Resalta la sección activa en dorado (RF-r2, RNF-4) y muestra el
logo "BB" generado por código (RF-r1).
"""

import tkinter as tk

from utils import session
from styles import (
    COLOR_BORDE,
    COLOR_DORADO,
    COLOR_FONDO,
    COLOR_PANEL,
    COLOR_TEXTO,
    COLOR_TEXTO_SECUNDARIO,
    FUENTE_BOTON,
    FUENTE_CUERPO,
    FUENTE_PEQUEÑA,
    FUENTE_SUBTITULO,
    FUENTE_TITULO_MENU,
)
from views.ajustes_view import AjustesView
from views.biblioteca_view import BibliotecaView
from views.comunidad_view import ComunidadView
from views.descubrir_view import DescubrirView
from views.tienda_view import TiendaView
from views.widgets import generar_logo


_SECCIONES = [
    ("Descubrir", "Descubrir"),
    ("Tienda", "Tienda"),
    ("Biblioteca", "Biblioteca"),
    ("Comunidad", "Comunidad"),
    ("Ajustes", "Ajustes"),
]

_VIEWS = {
    "Descubrir": DescubrirView,
    "Tienda": TiendaView,
    "Biblioteca": BibliotecaView,
    "Comunidad": ComunidadView,
    "Ajustes": AjustesView,
}


class MenuView(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg=COLOR_FONDO)
        self.app = app
        self._seccion_actual = None
        self._botones_seccion = {}
        self._construir()

    def _construir(self):
        # --- Sidebar ---
        sidebar = tk.Frame(self, bg=COLOR_PANEL, width=230, highlightbackground=COLOR_BORDE, highlightthickness=1, bd=0)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # Logo "BB" generado por código (RF-r1: imagen en la pantalla principal)
        self._logo_img = generar_logo()
        logo = tk.Label(sidebar, image=self._logo_img, bg=COLOR_PANEL)
        logo.image = self._logo_img
        logo.pack(pady=(24, 4))

        tk.Label(
            sidebar,
            text="BLACK BULLS",
            font=FUENTE_TITULO_MENU,
            bg=COLOR_PANEL,
            fg=COLOR_DORADO,
        ).pack(pady=(0, 2))

        tk.Label(
            sidebar,
            text="GAMESTORE",
            font=(FUENTE_PEQUEÑA[0], FUENTE_PEQUEÑA[1], "bold"),
            bg=COLOR_PANEL,
            fg=COLOR_TEXTO_SECUNDARIO,
        ).pack(pady=(0, 24))

        for clave, etiqueta in _SECCIONES:
            btn = tk.Button(
                sidebar,
                text=f"  {etiqueta}",
                font=FUENTE_CUERPO,
                bg=COLOR_PANEL,
                fg=COLOR_TEXTO,
                activebackground=COLOR_BORDE,
                activeforeground=COLOR_DORADO,
                bd=0,
                anchor="w",
                cursor="hand2",
                command=lambda c=clave: self._ir_a(c),
            )
            btn.pack(fill="x", padx=12, pady=2, ipady=8)
            self._botones_seccion[clave] = btn
            btn.bind("<Enter>", lambda _e, b=btn: self._hover(b, True))
            btn.bind("<Leave>", lambda _e, b=btn, c=clave: self._hover(b, self._seccion_actual == c))

        btn_cerrar = tk.Button(
            sidebar,
            text="Cerrar sesión",
            font=FUENTE_BOTON,
            bg=COLOR_BORDE,
            fg=COLOR_TEXTO,
            activebackground="#3a2a2a",
            activeforeground="#ff7a7a",
            bd=0,
            cursor="hand2",
            command=self._cerrar_sesion,
        )
        btn_cerrar.pack(side="bottom", fill="x", padx=16, pady=20, ipady=8)

        # --- Contenido ---
        self.contenido = tk.Frame(self, bg=COLOR_FONDO)
        self.contenido.pack(side="right", fill="both", expand=True)

        # Header con saludo
        self.header = tk.Frame(self.contenido, bg=COLOR_FONDO)
        self.header.pack(fill="x", padx=40, pady=(28, 8))

        usuario = session.usuario_actual()
        nombre = usuario.nombre_usuario if usuario else "invitado"
        tk.Label(
            self.header,
            text=f"Hola, {nombre}",
            font=FUENTE_SUBTITULO,
            bg=COLOR_FONDO,
            fg=COLOR_TEXTO,
        ).pack(side="left")

        # Cuerpo placeholder (cada sección lo reemplaza)
        self.cuerpo = tk.Frame(self.contenido, bg=COLOR_PANEL, highlightbackground=COLOR_BORDE, highlightthickness=1, bd=0)
        self.cuerpo.pack(fill="both", expand=True, padx=40, pady=(8, 32))

        self._ir_a("Descubrir")

    def _hover(self, boton, activo):
        if activo:
            boton.configure(bg=COLOR_BORDE, fg=COLOR_DORADO)
        else:
            boton.configure(bg=COLOR_PANEL, fg=COLOR_TEXTO)

    def _resaltar(self, clave):
        for k, btn in self._botones_seccion.items():
            if k == clave:
                btn.configure(bg=COLOR_BORDE, fg=COLOR_DORADO)
            else:
                btn.configure(bg=COLOR_PANEL, fg=COLOR_TEXTO)

    def _ir_a(self, clave):
        self._seccion_actual = clave
        self._resaltar(clave)

        for widget in self.cuerpo.winfo_children():
            widget.destroy()

        vista_cls = _VIEWS[clave]
        vista = vista_cls(self.cuerpo, app=self.app)
        vista.pack(fill="both", expand=True)

    def _cerrar_sesion(self):
        session.cerrar_sesion()
        self.app.mostrar_login()
