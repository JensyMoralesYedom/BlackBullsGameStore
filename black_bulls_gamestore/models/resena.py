"""
Acceso a la tabla `reseñas`: comentarios persistidos de la comunidad.

Cubre RF-7 (comunidad con texto persistido en SQLite).
"""

from dataclasses import dataclass

from database import db


@dataclass
class Resena:
    id: int
    usuario: str
    juego: str
    comentario: str
    fecha: str

    @classmethod
    def desde_fila(cls, fila):
        return cls(
            id=fila["id"],
            usuario=fila["nombre_usuario"],
            juego=fila["titulo"] or "General",
            comentario=fila["comentario"],
            fecha=fila["fecha"],
        )


def agregar(usuario_id, juego_id, comentario):
    conn = db.conectar()
    try:
        with conn:
            conn.execute(
                "INSERT INTO resenas (usuario_id, juego_id, comentario) VALUES (?, ?, ?)",
                (usuario_id, juego_id, comentario),
            )
    finally:
        conn.close()


def listar():
    sql = (
        "SELECT r.id, r.comentario, r.fecha, u.nombre_usuario, j.titulo "
        "FROM resenas r "
        "LEFT JOIN usuarios u ON u.id = r.usuario_id "
        "LEFT JOIN juegos j ON j.id = r.juego_id "
        "ORDER BY r.fecha DESC"
    )
    conn = db.conectar()
    try:
        filas = conn.execute(sql).fetchall()
    finally:
        conn.close()
    return [Resena.desde_fila(f) for f in filas]
