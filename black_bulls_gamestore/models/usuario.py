"""
Entidad Usuario y funciones de acceso a la base de datos.

La capa de modelos solo conoce la DB; las validaciones de negocio
(correo único, formato, longitudes) viven en controllers/auth_controller.py.
"""

from dataclasses import dataclass

from database import db


@dataclass
class Usuario:
    id: int
    nombre_usuario: str
    correo: str
    fecha_registro: str

    @classmethod
    def desde_fila(cls, fila):
        return cls(
            id=fila["id"],
            nombre_usuario=fila["nombre_usuario"],
            correo=fila["correo"],
            fecha_registro=fila["fecha_registro"],
        )


def _buscar(filtro_sql, valor):
    """Devuelve (Usuario, password_hash) o (None, None)."""
    conn = db.conectar()
    try:
        fila = conn.execute(
            f"SELECT id, nombre_usuario, correo, password_hash, fecha_registro "
            f"FROM usuarios WHERE {filtro_sql}",
            (valor,),
        ).fetchone()
    finally:
        conn.close()

    if fila is None:
        return None, None
    return Usuario.desde_fila(fila), fila["password_hash"]


def buscar_por_nombre(nombre_usuario):
    return _buscar("nombre_usuario = ?", nombre_usuario)


def buscar_por_correo(correo):
    return _buscar("correo = ?", correo)


def nombre_disponible(nombre_usuario):
    return buscar_por_nombre(nombre_usuario)[0] is None


def correo_disponible(correo):
    return buscar_por_correo(correo)[0] is None


def crear(nombre_usuario, correo, password_hash):
    """Inserta un usuario y devuelve el Usuario creado con su id."""
    conn = db.conectar()
    try:
        with conn:
            cursor = conn.execute(
                "INSERT INTO usuarios (nombre_usuario, password_hash, correo) "
                "VALUES (?, ?, ?)",
                (nombre_usuario, password_hash, correo),
            )
            nuevo_id = cursor.lastrowid
            fila = conn.execute(
                "SELECT id, nombre_usuario, correo, fecha_registro "
                "FROM usuarios WHERE id = ?",
                (nuevo_id,),
            ).fetchone()
    finally:
        conn.close()

    return Usuario.desde_fila(fila)
