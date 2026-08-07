"""
Lógica de autenticación: registro y login contra la base de datos.

Ambas funciones devuelven un Resultado(ok, mensaje, usuario) para que las
vistas puedan pintar el error en pantalla en vez de un messagebox.
"""

import re

from database import db
from models import usuario as usuario_model


_NOMBRE_RE = re.compile(r"^[A-Za-z0-9_.-]{3,20}$")
_CORREO_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class Resultado:
    """Pequeño struct para devolver (ok, usuario, mensaje) desde el controlador."""

    __slots__ = ("ok", "mensaje", "usuario")

    def __init__(self, ok, mensaje="", usuario=None):
        self.ok = ok
        self.mensaje = mensaje
        self.usuario = usuario

    def __bool__(self):
        return self.ok


def _validar_campos_registro(nombre, correo, clave, confirmar):
    if not nombre or not correo or not clave or not confirmar:
        return "Todos los campos son obligatorios."
    if not _NOMBRE_RE.match(nombre):
        return "El nombre de usuario debe tener 3-20 caracteres (letras, números, . _ -)."
    if not _CORREO_RE.match(correo):
        return "El correo no tiene un formato válido."
    if len(clave) < 6:
        return "La contraseña debe tener al menos 6 caracteres."
    if clave != confirmar:
        return "Las contraseñas no coinciden."
    return None


def registrar(nombre, correo, clave, confirmar):
    """Crea un usuario nuevo. Devuelve Resultado con ok=False si algo falla."""
    error = _validar_campos_registro(nombre, correo, clave, confirmar)
    if error:
        return Resultado(False, error)

    if not usuario_model.nombre_disponible(nombre):
        return Resultado(False, "Ese nombre de usuario ya está en uso.")
    if not usuario_model.correo_disponible(correo):
        return Resultado(False, "Ya existe una cuenta con ese correo.")

    nuevo = usuario_model.crear(nombre, correo, db.hash_password(clave))
    return Resultado(True, "Cuenta creada. Bienvenido a Black Bulls.", nuevo)


def login(nombre, clave):
    """Valida credenciales. Devuelve Resultado con ok=False si fallan."""
    if not nombre or not clave:
        return Resultado(False, "Ingresa usuario y contraseña.")

    usuario, password_hash = usuario_model.buscar_por_nombre(nombre)
    if usuario is None or not db.verificar_password(clave, password_hash):
        return Resultado(False, "Usuario o contraseña incorrectos.")

    return Resultado(True, "Sesión iniciada.", usuario)


def cambiar_password(usuario_id, clave_actual, nueva_clave, confirmar):
    """Para la Fase 4. Lo dejamos listo para que ajustes_view.py lo consuma."""
    if not clave_actual or not nueva_clave or not confirmar:
        return Resultado(False, "Completa los tres campos de contraseña.")
    if nueva_clave != confirmar:
        return Resultado(False, "La nueva contraseña no coincide.")
    if len(nueva_clave) < 6:
        return Resultado(False, "La nueva contraseña debe tener al menos 6 caracteres.")

    conn = db.conectar()
    try:
        fila = conn.execute(
            "SELECT password_hash FROM usuarios WHERE id = ?", (usuario_id,)
        ).fetchone()
        if fila is None or not db.verificar_password(clave_actual, fila["password_hash"]):
            return Resultado(False, "La contraseña actual es incorrecta.")
        with conn:
            conn.execute(
                "UPDATE usuarios SET password_hash = ? WHERE id = ?",
                (db.hash_password(nueva_clave), usuario_id),
            )
    finally:
        conn.close()

    return Resultado(True, "Contraseña actualizada.")
