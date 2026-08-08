"""
Smoke test de la Fase 4: pantallas funcionales (tienda, biblioteca,
comunidad, ajustes) y navegación por el menú sin recrear la ventana.
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
from views.menu_view import MenuView


def _flush(root):
    root.update_idletasks()
    root.update()


def _vista_actual(mv):
    return mv.cuerpo.winfo_children()[0]


def test_flujo_fase4():
    db.resetear_db()
    root = tk.Tk()
    app = App(root)

    # Login como demo (tiene 2 juegos en biblioteca por el seed)
    lv = app._vista_actual
    lv.entrada_usuario.insert(0, "demo")
    lv.entrada_clave.insert(0, "demo123")
    lv._on_ingresar()
    _flush(root)
    assert app._vista_actual.__class__.__name__ == "MenuView"
    print("[OK] Login demo -> MenuView")

    mv = app._vista_actual
    assert hasattr(mv, "_logo_img"), "el menú debe mostrar un logo (RF-r1)"
    print("[OK] Logo 'BB' presente en la pantalla principal (RF-r1)")

    # --- Tienda (RF-4) ---
    mv._ir_a("Tienda")
    _flush(root)
    tv = _vista_actual(mv)
    assert tv.__class__.__name__ == "TiendaView"
    juegos = juego_model.listar()
    assert len(juegos) == 10, len(juegos)
    print(f"[OK] Tienda muestra {len(juegos)} juegos desde la DB")

    # Búsqueda por nombre
    tv._var_busqueda.set("Neo")
    tv._refrescar()
    _flush(root)
    tarjetas = tv.scroll.contenido.winfo_children()
    assert len(tarjetas) == 1, f"esperaba 1 tarjeta, hay {len(tarjetas)}"
    print("[OK] Búsqueda 'Neo' filtra a 1 resultado")

    # Filtro por categoría
    tv._var_busqueda.set("")
    tv._var_categoria.set("RPG")
    tv._refrescar()
    _flush(root)
    tarjetas = tv.scroll.contenido.winfo_children()
    assert len(tarjetas) >= 1 and all(hasattr(t, "juego") for t in tarjetas)
    assert all(t.juego.categoria == "RPG" for t in tarjetas), "todas deben ser RPG"
    print("[OK] Filtro por categoría 'RPG' aplicado")
    tv._var_categoria.set("Todas")
    tv._refrescar()

    # Comprar un juego no comprado por demo
    usuario = session.usuario_actual()
    candidato = next(j for j in juegos if not biblioteca_model.tiene_juego(usuario.id, j.id))
    tv._comprar(candidato)
    _flush(root)
    assert biblioteca_model.tiene_juego(usuario.id, candidato.id)
    print(f"[OK] Compra de '{candidato.titulo}' inserta en biblioteca (RF-4)")

    # La tarjeta refleja el estado comprado
    botones = [b for b in tv.scroll.contenido.winfo_children() if b.juego.id == candidato.id]
    assert len(botones) == 1
    textos = [w.cget("text") for w in botones[0].winfo_children() if w.winfo_class() == "Button"]
    assert "EN TU BIBLIOTECA" in textos, textos
    print("[OK] La tarjeta pasa a 'EN TU BIBLIOTECA' tras comprar")

    # --- Biblioteca (RF-5) ---
    mv._ir_a("Biblioteca")
    _flush(root)
    bv = _vista_actual(mv)
    assert bv.__class__.__name__ == "BibliotecaView"
    tarjetas = bv.scroll.contenido.winfo_children()
    ids_mostrados = {t.juego.id for t in tarjetas}
    assert candidato.id in ids_mostrados, "el juego comprado debe aparecer"
    assert "Sombras del Toro" not in {t.juego.titulo for t in tarjetas}, "solo juegos del usuario"
    print(f"[OK] Biblioteca muestra {len(ids_mostrados)} juegos propios, sin juegos ajenos")

    # Estado vacío para un usuario sin compras
    auth_controller.registrar("fase4", "fase4@bb.com", "clave123", "clave123")
    session.cerrar_sesion()
    app.mostrar_login()
    _flush(root)
    lv2 = app._vista_actual
    lv2.entrada_usuario.insert(0, "fase4")
    lv2.entrada_clave.insert(0, "clave123")
    lv2._on_ingresar()
    _flush(root)
    mv2 = app._vista_actual
    mv2._ir_a("Biblioteca")
    _flush(root)
    bv2 = _vista_actual(mv2)
    textos = [w.cget("text") for w in bv2.scroll.contenido.winfo_children()[0].winfo_children()]
    assert any("Aún no tenés juegos" in t for t in textos), textos
    print("[OK] Biblioteca vacía muestra estado 'Aún no tenés juegos' (RF-5)")

    # --- Comunidad (RF-7) ---
    mv2._ir_a("Comunidad")
    _flush(root)
    cv = _vista_actual(mv2)
    assert cv.__class__.__name__ == "ComunidadView"
    cv.texto.insert("1.0", "Probando la comunidad de Black Bulls.")
    cv._publicar()
    _flush(root)
    resenas = cv.scroll.contenido.winfo_children()
    assert len(resenas) >= 1, "la reseña debe persistir y mostrarse"
    texto_publicado = [
        w.cget("text") for w in resenas[0].winfo_children()
        if w.winfo_class() == "Label" and w.cget("text") == "Probando la comunidad de Black Bulls."
    ]
    assert texto_publicado, "el comentario publicado debe verse en la lista"
    print("[OK] Reseña publicada y persistida (RF-7)")

    # --- Ajustes (RF-8) ---
    mv2._ir_a("Ajustes")
    _flush(root)
    av = _vista_actual(mv2)
    assert av.__class__.__name__ == "AjustesView"
    assert "fase4" in av.label_usuario.cget("text")
    assert "fase4@bb.com" in av.label_correo.cget("text")
    av.entrada_actual.insert(0, "clave123")
    av.entrada_nueva.insert(0, "nueva456")
    av.entrada_confirmar.insert(0, "nueva456")
    av._cambiar_clave()
    _flush(root)
    assert av.ok_clave.cget("text") == "Contraseña actualizada."
    print("[OK] Cambio de contraseña con validación de la actual (RF-8)")

    # Verificar que el login con la nueva contraseña funciona
    av._cerrar_sesion()
    _flush(root)
    assert app._vista_actual.__class__.__name__ == "LoginView"
    lv3 = app._vista_actual
    lv3.entrada_usuario.insert(0, "fase4")
    lv3.entrada_clave.insert(0, "nueva456")
    lv3._on_ingresar()
    _flush(root)
    assert app._vista_actual.__class__.__name__ == "MenuView"
    print("[OK] Reingreso con la nueva contraseña funciona")

    root.destroy()
    print("\nTODA LA FASE 4 FUNCIONA")


if __name__ == "__main__":
    test_flujo_fase4()
