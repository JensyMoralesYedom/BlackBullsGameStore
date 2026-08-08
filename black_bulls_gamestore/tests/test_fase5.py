"""
Test de la Fase 5 (Pulido):

- 5.1 Estados vacíos en tienda, biblioteca y comunidad.
- 5.3 Las vistas no se rompen al redimensionar la ventana.
- 5.4 Aislamiento multi-usuario: cada cuenta ve solo su biblioteca.
- 5.5 La DB se crea desde cero (resetear_db) y queda operativa.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from controllers import auth_controller
from database import db
from main import App
from models import biblioteca as biblioteca_model
from models import juego as juego_model
from utils import session


def _flush(root):
    root.update_idletasks()
    root.update()


def _vista(mv):
    return mv.cuerpo.winfo_children()[0]


def _loguear(app, nombre, clave):
    lv = app._vista_actual
    lv.entrada_usuario.insert(0, nombre)
    lv.entrada_clave.insert(0, clave)
    lv._on_ingresar()


def test_db_desde_cero():
    """5.5: crear la DB desde cero y verificarla."""
    db.resetear_db()
    conn = db.conectar()
    try:
        usuarios = conn.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]
        juegos = conn.execute("SELECT COUNT(*) FROM juegos").fetchone()[0]
    finally:
        conn.close()
    assert usuarios == 2, usuarios
    assert juegos == 10, juegos
    print(f"[OK] DB desde cero: {usuarios} usuarios, {juegos} juegos (5.5)")


def test_multiusuario():
    """5.4: cada usuario ve solo su biblioteca."""
    # Usuario A compra 'Elden Ring'; usuario B compra 'Halo'
    auth_controller.registrar("usu_a", "a@bb.com", "clavea1", "clavea1")
    auth_controller.registrar("usu_b", "b@bb.com", "claveb2", "claveb2")

    conn = db.conectar()
    try:
        a_id = conn.execute("SELECT id FROM usuarios WHERE nombre_usuario='usu_a'").fetchone()["id"]
        b_id = conn.execute("SELECT id FROM usuarios WHERE nombre_usuario='usu_b'").fetchone()["id"]
    finally:
        conn.close()

    elden = next(j for j in juego_model.listar() if j.titulo == "Elden Ring")
    halo = next(j for j in juego_model.listar() if j.titulo == "Halo: The Master Chief Collection")
    biblioteca_model.agregar(a_id, elden.id)
    biblioteca_model.agregar(b_id, halo.id)

    titulos_a = {j.titulo for j in biblioteca_model.listar_por_usuario(a_id)}
    titulos_b = {j.titulo for j in biblioteca_model.listar_por_usuario(b_id)}
    assert titulos_a == {"Elden Ring"}, titulos_a
    assert titulos_b == {"Halo: The Master Chief Collection"}, titulos_b
    assert titulos_a.isdisjoint(titulos_b)
    print(f"[OK] Aislamiento multi-usuario: A={titulos_a} B={titulos_b} (5.4)")

    return a_id


def test_estados_vacios(root, app):
    """5.1: estados vacíos en tienda, biblioteca y comunidad."""
    # Usuario sin compras
    auth_controller.registrar("vacio", "vacio@bb.com", "clavev1", "clavev1")
    session.cerrar_sesion()
    app.mostrar_login()
    _flush(root)
    _loguear(app, "vacio", "clavev1")
    _flush(root)
    mv = app._vista_actual

    # Biblioteca vacía
    mv._ir_a("Biblioteca")
    _flush(root)
    textos = _textos_de(_vista(mv))
    assert any("Aún no tenés juegos" in t for t in textos), textos
    print("[OK] Biblioteca vacía con estado 'Aún no tenés juegos' (5.1)")

    # Tienda sin resultados de búsqueda
    mv._ir_a("Tienda")
    _flush(root)
    tv = _vista(mv)
    tv._var_busqueda.set("zzzznadaxxx")
    tv._refrescar()
    _flush(root)
    textos = [w.cget("text") for w in tv.scroll.contenido.winfo_children() if w.winfo_class() == "Label"]
    assert any("No hay juegos" in t for t in textos), textos
    print("[OK] Tienda sin resultados muestra mensaje (5.1)")
    tv._var_busqueda.set("")
    tv._refrescar()

    # Comunidad sin reseñas
    mv._ir_a("Comunidad")
    _flush(root)
    cv = _vista(mv)
    textos = [w.cget("text") for w in cv.scroll.contenido.winfo_children() if w.winfo_class() == "Label"]
    assert any("Todavía no hay comentarios" in t for t in textos), textos
    print("[OK] Comunidad vacía con mensaje (5.1)")


def _textos_de(vista):
    """Recolecta los textos de todas las Labels dentro de la vista (recursivo)."""
    textos = []
    def _recolectar(w):
        try:
            if w.winfo_class() == "Label":
                textos.append(w.cget("text"))
        except tk.TclError:
            pass
        for hijo in w.winfo_children():
            _recolectar(hijo)
    _recolectar(vista)
    return textos


def test_resize(root, app):
    """5.3: las vistas no se rompen al redimensionar."""
    session.cerrar_sesion()
    app.mostrar_login()
    _flush(root)
    _loguear(app, "demo", "demo123")
    _flush(root)
    mv = app._vista_actual

    for ancho, alto in ((900, 660), (1200, 760), (1500, 920)):
        root.geometry(f"{ancho}x{alto}")
        _flush(root)
        for seccion in ("Descubrir", "Tienda", "Biblioteca", "Comunidad", "Ajustes"):
            mv._ir_a(seccion)
            _flush(root)
            assert _vista(mv).winfo_class() == "Frame"
    print("[OK] Las 5 secciones toleran redimensionado 900x660 -> 1500x920 (5.3)")


def test_fase5():
    test_db_desde_cero()
    test_multiusuario()

    root = tk.Tk()
    app = App(root)
    test_estados_vacios(root, app)
    test_resize(root, app)
    root.destroy()
    print("\nTODA LA FASE 5 FUNCIONA")


if __name__ == "__main__":
    test_fase5()
