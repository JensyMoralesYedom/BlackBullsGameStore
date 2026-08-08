"""
Acceso a la tabla `biblioteca`: compras del usuario.

Cubre RF-4 (comprar) y RF-5 (biblioteca por usuario).
"""

from database import db
from models.juego import Juego


def agregar(usuario_id, juego_id):
    conn = db.conectar()
    try:
        with conn:
            conn.execute(
                "INSERT OR IGNORE INTO biblioteca (usuario_id, juego_id) VALUES (?, ?)",
                (usuario_id, juego_id),
            )
    finally:
        conn.close()


def tiene_juego(usuario_id, juego_id):
    conn = db.conectar()
    try:
        fila = conn.execute(
            "SELECT 1 FROM biblioteca WHERE usuario_id = ? AND juego_id = ?",
            (usuario_id, juego_id),
        ).fetchone()
    finally:
        conn.close()
    return fila is not None


def listar_por_usuario(usuario_id):
    sql = (
        "SELECT j.*, b.fecha_compra "
        "FROM biblioteca b "
        "JOIN juegos j ON j.id = b.juego_id "
        "WHERE b.usuario_id = ? "
        "ORDER BY b.fecha_compra DESC, j.titulo"
    )
    conn = db.conectar()
    try:
        filas = conn.execute(sql, (usuario_id,)).fetchall()
    finally:
        conn.close()
    return [Juego.desde_fila(f) for f in filas]
