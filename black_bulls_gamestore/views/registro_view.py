"""
Vista de registro.

Cuando la cuenta se crea con éxito, auto-loguea y manda al menú
(no tiene sentido devolver al usuario al login si ya está autenticado).
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
)
from views.fondo import FondoLabel


class RegistroView(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg=COLOR_FONDO)
        self.app = app
        self._construir()

    def _construir(self):
        # Fondo con collage de portadas difuminado (Fase 7)
        self._fondo = FondoLabel(self)

        tarjeta = tk.Frame(self, bg=COLOR_PANEL, highlightbackground=COLOR_BORDE, highlightthickness=1, bd=0)
        tarjeta.place(relx=0.5, rely=0.5, anchor="center", width=420, height=620)

        tk.Label(
            tarjeta,
            text="CREAR CUENTA",
            font=("Segoe UI Black", 20),
            bg=COLOR_PANEL,
            fg=COLOR_DORADO,
        ).pack(pady=(32, 4))

        tk.Label(
            tarjeta,
            text="Unite a la manada Black Bulls",
            font=FUENTE_PEQUEÑA,
            bg=COLOR_PANEL,
            fg=COLOR_TEXTO_SECUNDARIO,
        ).pack(pady=(0, 24))

        self.entrada_usuario, self.error_usuario = self._crear_campo(tarjeta, "NOMBRE DE USUARIO")
        self.entrada_correo, self.error_correo = self._crear_campo(tarjeta, "CORREO")
        self.entrada_clave, self.error_clave = self._crear_campo(tarjeta, "CONTRASEÑA", es_clave=True)
        self.entrada_confirmar, self.error_confirmar = self._crear_campo(tarjeta, "CONFIRMAR CONTRASEÑA", es_clave=True)

        self.error_general = tk.Label(
            tarjeta,
            text="",
            font=FUENTE_PEQUEÑA,
            bg=COLOR_PANEL,
            fg=COLOR_ROJO,
            wraplength=340,
            justify="center",
        )
        self.error_general.pack(pady=(6, 0))

        btn_crear = tk.Button(
            tarjeta,
            text="CREAR CUENTA",
            font=FUENTE_BOTON,
            bg=COLOR_DORADO,
            fg=COLOR_FONDO,
            activebackground="#a8861e",
            activeforeground=COLOR_FONDO,
            bd=0,
            cursor="hand2",
            command=self._on_registrar,
        )
        btn_crear.pack(fill="x", padx=40, pady=(18, 6), ipady=8)

        btn_volver = tk.Button(
            tarjeta,
            text="Ya tengo cuenta · Iniciar sesión",
            font=(FUENTE_PEQUEÑA[0], FUENTE_PEQUEÑA[1], "underline"),
            bg=COLOR_PANEL,
            fg=COLOR_TEXTO_SECUNDARIO,
            activebackground=COLOR_PANEL,
            activeforeground=COLOR_DORADO,
            bd=0,
            cursor="hand2",
            command=self.app.mostrar_login,
        )
        btn_volver.pack(pady=(4, 0))

        for entrada in (self.entrada_usuario, self.entrada_correo, self.entrada_clave, self.entrada_confirmar):
            entrada.bind("<Return>", lambda _e: self._on_registrar())

        # Asegurar que el fondo quede detrás de la tarjeta
        self._fondo.bajar()

    def _crear_campo(self, master, texto_label, es_clave=False):
        wrapper = tk.Frame(master, bg=COLOR_PANEL)
        wrapper.pack(fill="x", padx=40, pady=(6, 0))

        tk.Label(
            wrapper,
            text=texto_label,
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
            show="*" if es_clave else "",
        )
        entrada.pack(fill="x", pady=(4, 2))

        linea = tk.Frame(wrapper, bg=COLOR_BORDE, height=1)
        linea.pack(fill="x")

        entrada.bind("<FocusIn>", lambda _e: linea.configure(bg=COLOR_DORADO))
        entrada.bind("<FocusOut>", lambda _e: linea.configure(bg=COLOR_BORDE))

        error = tk.Label(
            wrapper,
            text="",
            font=(FUENTE_PEQUEÑA[0], FUENTE_PEQUEÑA[1]),
            bg=COLOR_PANEL,
            fg=COLOR_ROJO,
            anchor="w",
        )
        error.pack(fill="x", pady=(2, 0))

        return entrada, error

    def _limpiar_errores(self):
        for label in (self.error_usuario, self.error_correo, self.error_clave, self.error_confirmar):
            label.configure(text="")
        self.error_general.configure(text="")

    def _on_registrar(self):
        self._limpiar_errores()

        nombre = self.entrada_usuario.get().strip()
        correo = self.entrada_correo.get().strip()
        clave = self.entrada_clave.get()
        confirmar = self.entrada_confirmar.get()

        resultado = auth_controller.registrar(nombre, correo, clave, confirmar)

        if not resultado.ok:
            # Mapeo del mensaje a la fila más probable. No es perfecto,
            # pero evita cinco errores contiguos arriba.
            msg = resultado.mensaje
            if "usuario" in msg.lower():
                self.error_usuario.configure(text=msg)
            elif "correo" in msg.lower():
                self.error_correo.configure(text=msg)
            elif "contraseña" in msg.lower() or "clave" in msg.lower():
                # No podemos saber entre las dos filas; pintamos en general.
                self.error_general.configure(text=msg)
            else:
                self.error_general.configure(text=msg)
            return

        # Éxito: auto-login y al menú
        session.iniciar_sesion(resultado.usuario)
        self.app.mostrar_menu()

    def reset(self):
        self._limpiar_errores()
        for entrada in (self.entrada_usuario, self.entrada_correo, self.entrada_clave, self.entrada_confirmar):
            entrada.delete(0, tk.END)
        self.entrada_usuario.focus_set()
