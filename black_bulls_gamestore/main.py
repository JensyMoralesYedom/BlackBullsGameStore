"""
Arranque de la app Black Bulls Gamestore.

Fase 2: la raíz muestra Login, Registro o Menu. Cambiamos de Frame sin
destruir la ventana para mantener la misma sesión y geometría.
"""

import tkinter as tk

from database import db
from views.login_view import LoginView
from views.menu_view import MenuView
from views.registro_view import RegistroView
from styles import COLOR_FONDO


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Black Bulls Gamestore")
        self.root.geometry("1000x640")
        self.root.minsize(900, 660)
        self.root.configure(bg=COLOR_FONDO)
        self.root.resizable(True, True)

        self._vista_actual = None

        db.crear_tablas()
        db.seed()

        self.mostrar_login()

    def _cambiar_vista(self, vista_cls):
        if self._vista_actual is not None:
            self._vista_actual.destroy()
        self._vista_actual = vista_cls(self.root, self)
        self._vista_actual.pack(fill="both", expand=True)
        if hasattr(self._vista_actual, "reset"):
            self._vista_actual.reset()

    def mostrar_login(self):
        self._cambiar_vista(LoginView)

    def mostrar_registro(self):
        self._cambiar_vista(RegistroView)

    def mostrar_menu(self):
        self._cambiar_vista(MenuView)


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
