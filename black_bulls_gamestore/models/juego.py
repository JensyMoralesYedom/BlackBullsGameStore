"""
Entidad Juego y funciones de acceso a la base de datos.

Cubre RF-4 (tienda con filtro/búsqueda) y RF-6 (descubrir destacados).
"""

from dataclasses import dataclass

from database import db


@dataclass
class Juego:
    id: int
    titulo: str
    descripcion: str
    precio: float
    categoria: str
    portada_path: str | None = None

    @classmethod
    def desde_fila(cls, fila):
        return cls(
            id=fila["id"],
            titulo=fila["titulo"],
            descripcion=fila["descripcion"],
            precio=fila["precio"],
            categoria=fila["categoria"],
            portada_path=fila["portada_path"],
        )


def _ejecutar(sql, params=()):
    conn = db.conectar()
    try:
        filas = conn.execute(sql, params).fetchall()
    finally:
        conn.close()
    return [Juego.desde_fila(f) for f in filas]


def listar(categoria=None, busqueda=None):
    """Juegos opcionalmente filtrados por categoría y/o búsqueda por título."""
    sql = "SELECT * FROM juegos WHERE 1 = 1"
    params = []
    if categoria:
        sql += " AND categoria = ?"
        params.append(categoria)
    if busqueda:
        sql += " AND titulo LIKE ?"
        params.append(f"%{busqueda}%")
    sql += " ORDER BY titulo"
    return _ejecutar(sql, params)


def categorias():
    conn = db.conectar()
    try:
        filas = conn.execute(
            "SELECT DISTINCT categoria FROM juegos ORDER BY categoria"
        ).fetchall()
    finally:
        conn.close()
    return [f["categoria"] for f in filas]


def destacados(limite=4):
    return _ejecutar("SELECT * FROM juegos ORDER BY RANDOM() LIMIT ?", (limite,))


def por_id(juego_id):
    conn = db.conectar()
    try:
        fila = conn.execute("SELECT * FROM juegos WHERE id = ?", (juego_id,)).fetchone()
    finally:
        conn.close()
    return Juego.desde_fila(fila) if fila else None
