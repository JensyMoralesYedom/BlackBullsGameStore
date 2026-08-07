"""
Sesión en memoria: guarda el Usuario autenticado mientras la app está abierta.

Es deliberadamente simple: no hay JWT ni cookies. La vista de menú y las
vistas de la Fase 4 (tienda, biblioteca, ajustes) leen self.usuario_actual
desde la raíz para saber a quién mostrar.
"""

from models import usuario as usuario_model


_usuario_actual = None


def iniciar_sesion(usuario):
    """usuario: instancia de models.usuario.Usuario."""
    global _usuario_actual
    _usuario_actual = usuario


def cerrar_sesion():
    global _usuario_actual
    _usuario_actual = None


def usuario_actual():
    return _usuario_actual


def refrescar_usuario_actual():
    """Si la fila en DB cambió (ej. cambió la contraseña), recarga desde DB."""
    global _usuario_actual
    if _usuario_actual is None:
        return None
    actualizado, _ = usuario_model.buscar_por_nombre(_usuario_actual.nombre_usuario)
    _usuario_actual = actualizado
    return _usuario_actual
