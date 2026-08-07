"""
Vista de login.

El error se pinta en un label rojo bajo el campo correspondiente, no en un
messagebox. Al iniciar sesión correctamente llama a App.mostrar_menu().
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
    FUENTE_TITULO,
)


class LoginView(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg=COLOR_FONDO)
        self.app = app
        self._construir()

    def _construir(self):
        tarjeta = tk.Frame(self, bg=COLOR_PANEL, bd=1, relief="solid")
        tarjeta.place(relx=0.5, rely=0.5, anchor="center", width=400, height=540)

        # Evitar que las claves internas del panel se vean en el log
        tarjeta.configure(highlightbackground=COLOR_BORDE, highlightthickness=1, bd=0)

        tk.Label(
            tarjeta,
            text="BLACK BULLS",
            font=("Segoe UI Black", 22),
            bg=COLOR_PANEL,
            fg=COLOR_DORADO,
        ).pack(pady=(36, 4))

        tk.Label(
            tarjeta,
            text="GAMESTORE",
            font=("Segoe UI", 10, "bold"),
            bg=COLOR_PANEL,
            fg=COLOR_TEXTO_SECUNDARIO,
        ).pack(pady=(0, 28))

        # --- Campo usuario ---
        self.entrada_usuario, self.error_usuario = self._crear_campo(
            tarjeta, "NOMBRE DE USUARIO"
        )

        # --- Campo contraseña ---
        self.entrada_clave, self.error_clave = self._crear_campo(
            tarjeta, "CONTRASEÑA", es_clave=True
        )

        # --- Error general (debajo del botón) ---
        self.error_general = tk.Label(
            tarjeta,
            text="",
            font=FUENTE_PEQUEÑA,
            bg=COLOR_PANEL,
            fg=COLOR_ROJO,
            wraplength=320,
            justify="center",
        )
        self.error_general.pack(pady=(8, 0))

        # --- Botón ingresar ---
        btn_ingresar = tk.Button(
            tarjeta,
            text="INICIAR SESIÓN",
            font=FUENTE_BOTON,
            bg=COLOR_DORADO,
            fg=COLOR_FONDO,
            activebackground="#a8861e",
            activeforeground=COLOR_FONDO,
            bd=0,
            cursor="hand2",
            command=self._on_ingresar,
        )
        btn_ingresar.pack(fill="x", padx=40, pady=(20, 8), ipady=8)

        # --- Link a registro ---
        frame_link = tk.Frame(tarjeta, bg=COLOR_PANEL)
        frame_link.pack(pady=(8, 0))

        tk.Label(
            frame_link,
            text="¿No tenés cuenta?",
            font=FUENTE_PEQUEÑA,
            bg=COLOR_PANEL,
            fg=COLOR_TEXTO_SECUNDARIO,
        ).pack(side="left")

        btn_registro = tk.Button(
            frame_link,
            text="Crear cuenta",
            font=(FUENTE_PEQUEÑA[0], FUENTE_PEQUEÑA[1], "underline"),
            bg=COLOR_PANEL,
            fg=COLOR_DORADO,
            activebackground=COLOR_PANEL,
            activeforeground=COLOR_DORADO,
            bd=0,
            cursor="hand2",
            command=self.app.mostrar_registro,
        )
        btn_registro.pack(side="left")

        # Atajos: Enter desde cualquier entrada dispara login
        self.entrada_usuario.bind("<Return>", lambda _e: self._on_ingresar())
        self.entrada_clave.bind("<Return>", lambda _e: self._on_ingresar())

    # --- helpers ---

    def _crear_campo(self, master, texto_label, es_clave=False):
        wrapper = tk.Frame(master, bg=COLOR_PANEL)
        wrapper.pack(fill="x", padx=40, pady=(8, 0))

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
        self.error_usuario.configure(text="")
        self.error_clave.configure(text="")
        self.error_general.configure(text="")

    def _on_ingresar(self):
        self._limpiar_errores()

        nombre = self.entrada_usuario.get().strip()
        clave = self.entrada_clave.get()

        resultado = auth_controller.login(nombre, clave)

        if not resultado.ok:
            # Si el error apunta a credenciales, lo pintamos en la línea general
            # (no tiene sentido distinguir entre "usuario no existe" y "clave mal"
            # — sería una pista para atacantes).
            self.error_general.configure(text=resultado.mensaje)
            self.entrada_clave.delete(0, tk.END)
            return

        session.iniciar_sesion(resultado.usuario)
        self.app.mostrar_menu()

    def reset(self):
        """Limpia el formulario cuando se vuelve a entrar al login."""
        self._limpiar_errores()
        self.entrada_usuario.delete(0, tk.END)
        self.entrada_clave.delete(0, tk.END)
        self.entrada_usuario.focus_set()
