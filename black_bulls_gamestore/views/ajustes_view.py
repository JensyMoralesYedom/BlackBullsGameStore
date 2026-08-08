"""
Vista Ajustes (RF-8): datos del usuario actual, cambio de contraseña
con validación de la actual y botón "Cerrar sesión".
"""

import tkinter as tk

from controllers import auth_controller
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
from views.widgets import vincular_hover


class AjustesView(tk.Frame):
    def __init__(self, master, app=None):
        super().__init__(master, bg=COLOR_FONDO)
        self.app = app
        self._construir()

    def _construir(self):
        tk.Label(
            self,
            text="AJUSTES",
            font=FUENTE_SUBTITULO,
            bg=COLOR_FONDO,
            fg=COLOR_DORADO,
        ).pack(anchor="w", padx=24, pady=(20, 12))

        # --- Datos del usuario ---
        self._panel_datos = tk.Frame(
            self, bg=COLOR_PANEL, highlightbackground=COLOR_BORDE, highlightthickness=1, bd=0
        )
        self._panel_datos.pack(fill="x", padx=24, pady=(0, 12))

        tk.Label(
            self._panel_datos,
            text="MI CUENTA",
            font=(FUENTE_PEQUEÑA[0], FUENTE_PEQUEÑA[1], "bold"),
            bg=COLOR_PANEL,
            fg=COLOR_DORADO,
        ).pack(anchor="w", padx=14, pady=(12, 4))

        self.label_usuario = tk.Label(
            self._panel_datos,
            text="",
            font=FUENTE_CUERPO,
            bg=COLOR_PANEL,
            fg=COLOR_TEXTO,
            anchor="w",
        )
        self.label_usuario.pack(fill="x", padx=14)

        self.label_correo = tk.Label(
            self._panel_datos,
            text="",
            font=FUENTE_CUERPO,
            bg=COLOR_PANEL,
            fg=COLOR_TEXTO_SECUNDARIO,
            anchor="w",
        )
        self.label_correo.pack(fill="x", padx=14, pady=(2, 12))

        # --- Cambiar contraseña ---
        self._panel_clave = tk.Frame(
            self, bg=COLOR_PANEL, highlightbackground=COLOR_BORDE, highlightthickness=1, bd=0
        )
        self._panel_clave.pack(fill="x", padx=24, pady=(0, 12))

        tk.Label(
            self._panel_clave,
            text="CAMBIAR CONTRASEÑA",
            font=(FUENTE_PEQUEÑA[0], FUENTE_PEQUEÑA[1], "bold"),
            bg=COLOR_PANEL,
            fg=COLOR_DORADO,
        ).pack(anchor="w", padx=14, pady=(12, 4))

        self.entrada_actual, self.entrada_nueva, self.entrada_confirmar = self._crear_campos_clave()

        self.error_clave = tk.Label(
            self._panel_clave,
            text="",
            font=FUENTE_PEQUEÑA,
            bg=COLOR_PANEL,
            fg=COLOR_ROJO,
            wraplength=460,
            justify="left",
        )
        self.error_clave.pack(anchor="w", padx=14)

        self.ok_clave = tk.Label(
            self._panel_clave,
            text="",
            font=FUENTE_PEQUEÑA,
            bg=COLOR_PANEL,
            fg=COLOR_DORADO,
        )
        self.ok_clave.pack(anchor="w", padx=14)

        btn_guardar = tk.Button(
            self._panel_clave,
            text="GUARDAR NUEVA CONTRASEÑA",
            font=FUENTE_BOTON,
            bg=COLOR_DORADO,
            fg=COLOR_FONDO,
            activebackground="#a8861e",
            activeforeground=COLOR_FONDO,
            bd=0,
            cursor="hand2",
            command=self._cambiar_clave,
        )
        btn_guardar.pack(anchor="w", padx=14, pady=(4, 12), ipadx=14, ipady=5)
        vincular_hover(btn_guardar, COLOR_DORADO, "#a8861e")

        # --- Cerrar sesión ---
        tk.Button(
            self,
            text="CERRAR SESIÓN",
            font=FUENTE_BOTON,
            bg=COLOR_PANEL,
            fg=COLOR_ROJO,
            activebackground=COLOR_ROJO,
            activeforeground=COLOR_TEXTO,
            bd=0,
            highlightbackground=COLOR_BORDE,
            highlightthickness=1,
            cursor="hand2",
            command=self._cerrar_sesion,
        ).pack(anchor="w", padx=24, ipadx=16, ipady=6)

        self._cargar_usuario()

    def _crear_campos_clave(self):
        def campo(texto):
            wrapper = tk.Frame(self._panel_clave, bg=COLOR_PANEL)
            wrapper.pack(fill="x", padx=14, pady=(4, 0))
            tk.Label(
                wrapper,
                text=texto,
                font=FUENTE_PEQUEÑA,
                bg=COLOR_PANEL,
                fg=COLOR_TEXTO_SECUNDARIO,
                anchor="w",
            ).pack(fill="x")
            entrada = tk.Entry(
                wrapper,
                font=FUENTE_CUERPO,
                bg=COLOR_PANEL,
                fg=COLOR_TEXTO,
                insertbackground=COLOR_TEXTO,
                bd=0,
                show="*",
            )
            entrada.pack(fill="x", pady=(2, 2))
            linea = tk.Frame(wrapper, bg=COLOR_BORDE, height=1)
            linea.pack(fill="x")
            entrada.bind("<FocusIn>", lambda _e: linea.configure(bg=COLOR_DORADO))
            entrada.bind("<FocusOut>", lambda _e: linea.configure(bg=COLOR_BORDE))
            return entrada

        return campo("CONTRASEÑA ACTUAL"), campo("NUEVA CONTRASEÑA"), campo("CONFIRMAR NUEVA")

    def _cargar_usuario(self):
        usuario = session.usuario_actual()
        if usuario is None:
            return
        self.label_usuario.configure(text=f"Usuario:  {usuario.nombre_usuario}")
        self.label_correo.configure(text=f"Correo:  {usuario.correo}")

    def _cambiar_clave(self):
        self.error_clave.configure(text="")
        self.ok_clave.configure(text="")

        usuario = session.usuario_actual()
        if usuario is None:
            return

        resultado = auth_controller.cambiar_password(
            usuario.id,
            self.entrada_actual.get(),
            self.entrada_nueva.get(),
            self.entrada_confirmar.get(),
        )
        if not resultado.ok:
            self.error_clave.configure(text=resultado.mensaje)
            return

        session.refrescar_usuario_actual()
        for entrada in (self.entrada_actual, self.entrada_nueva, self.entrada_confirmar):
            entrada.delete(0, tk.END)
        self.ok_clave.configure(text=resultado.mensaje)

    def _cerrar_sesion(self):
        session.cerrar_sesion()
        if self.app is not None:
            self.app.mostrar_login()
