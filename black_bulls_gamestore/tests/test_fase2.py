"""
Smoke test de la GUI: levanta la App sin mainloop y simula los clics del
flujo de Fase 2 (registrar -> login -> menu -> logout).
"""

import sys
import os

# Asegurarnos de que el paquete se importa como black_bulls_gamestore.*
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from database import db
from main import App


def _flush(root):
    root.update_idletasks()
    root.update()


def test_flujo_fase2():
    db.resetear_db()
    root = tk.Tk()
    app = App(root)

    # Estado inicial: LoginView
    assert app._vista_actual.__class__.__name__ == "LoginView", app._vista_actual.__class__.__name__
    print("[OK] Arranque muestra LoginView")

    # Ir a Registro
    app.mostrar_registro()
    _flush(root)
    assert app._vista_actual.__class__.__name__ == "RegistroView"
    print("[OK] Link 'Crear cuenta' lleva a RegistroView")

    # Llenar el formulario de registro y disparar
    rv = app._vista_actual
    rv.entrada_usuario.insert(0, "tester")
    rv.entrada_correo.insert(0, "tester@blackbulls.com")
    rv.entrada_clave.insert(0, "prueba123")
    rv.entrada_confirmar.insert(0, "prueba123")
    rv._on_registrar()
    _flush(root)

    assert app._vista_actual.__class__.__name__ == "MenuView"
    from utils import session
    assert session.usuario_actual().nombre_usuario == "tester"
    print("[OK] Registro exitoso auto-loguea y abre MenuView")

    # El header del menú debe saludar al usuario
    header_text = app._vista_actual.header.winfo_children()[0].cget("text")
    assert "tester" in header_text, header_text
    print(f"[OK] Saludo en menu: {header_text!r}")

    # Logout desde el menú
    app._vista_actual._cerrar_sesion()
    _flush(root)
    assert app._vista_actual.__class__.__name__ == "LoginView"
    assert session.usuario_actual() is None
    print("[OK] Cerrar sesión vuelve a LoginView y limpia la sesión")

    # Probar login con credenciales incorrectas
    lv = app._vista_actual
    lv.entrada_usuario.insert(0, "tester")
    lv.entrada_clave.insert(0, "equivocada")
    lv._on_ingresar()
    _flush(root)
    assert app._vista_actual.__class__.__name__ == "LoginView"
    assert lv.error_general.cget("text"), "debería haber un mensaje de error"
    print(f"[OK] Login con clave incorrecta muestra error: {lv.error_general.cget('text')!r}")

    # Login válido
    lv.entrada_clave.delete(0, tk.END)
    lv.entrada_clave.insert(0, "prueba123")
    lv._on_ingresar()
    _flush(root)
    assert app._vista_actual.__class__.__name__ == "MenuView"
    assert session.usuario_actual().nombre_usuario == "tester"
    print("[OK] Login válido con la cuenta recién creada")

    # Navegación por la sidebar
    mv = app._vista_actual
    for seccion in ("Tienda", "Biblioteca", "Comunidad", "Ajustes", "Descubrir"):
        mv._ir_a(seccion)
        _flush(root)
        assert mv._seccion_actual == seccion
        # El botón activo está en dorado
        btn_activo = mv._botones_seccion[seccion]
        assert btn_activo.cget("fg") == "#c9a227", f"sección {seccion} no resaltada"
    print("[OK] Las cinco secciones del sidebar resaltan correctamente")

    root.destroy()
    print("\nTODO EL FLUJO DE FASE 2 FUNCIONA")


if __name__ == "__main__":
    test_flujo_fase2()
