import hashlib
import os
import secrets
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "black_bulls.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_usuario TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    correo TEXT NOT NULL UNIQUE,
    fecha_registro TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS juegos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    descripcion TEXT NOT NULL,
    precio REAL NOT NULL,
    categoria TEXT NOT NULL,
    portada_path TEXT
);

CREATE TABLE IF NOT EXISTS biblioteca (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    juego_id INTEGER NOT NULL,
    fecha_compra TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE (usuario_id, juego_id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (juego_id) REFERENCES juegos(id)
);

CREATE TABLE IF NOT EXISTS carrito (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    juego_id INTEGER NOT NULL,
    UNIQUE (usuario_id, juego_id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (juego_id) REFERENCES juegos(id)
);

CREATE TABLE IF NOT EXISTS resenas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    juego_id INTEGER,
    comentario TEXT NOT NULL,
    fecha TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (juego_id) REFERENCES juegos(id)
);
"""

USUARIOS_SEED = [
    ("demo", "demo@blackbulls.com", "demo123"),
    ("blackbull", "blackbull@blackbulls.com", "torobulls"),
]

JUEGOS_SEED = [
    ("Cyberpunk Adventures", "Mundo abierto lleno de neon, misiones y graficos de ultima generacion.", 59.99, "Aventura"),
    ("Toro Real Deluxe", "Simulador de arena y toros con modo carrera.", 39.99, "Deportes"),
    ("Sombras del Toro", "RPG oscuro de accion en un reino asediado.", 49.99, "RPG"),
    ("Neo Drift", "Carreras arcade con derrapes imposibles.", 29.99, "Carreras"),
    ("Bastion Zero", "Shooter tactico por escuadrones.", 44.99, "Shooter"),
    ("Granja en Llamas", "Estrategia y supervivencia cooperativa.", 24.99, "Estrategia"),
    ("Pixel Bulls", "Plataformas retro con saltos precisos.", 9.99, "Indie"),
    ("Arena de Campeones", "Combate en arenas con modo local.", 34.99, "Accion"),
    ("Ruta 66 Racing", "Viaje por carretera en carreras arcade.", 19.99, "Carreras"),
    ("El Ultimo Rebano", "Aventura narrativa sobre sobrevivir al apocalipsis.", 29.99, "Indie"),
]


def conectar():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def hash_password(clave):
    salt = secrets.token_hex(16)
    digest = hashlib.sha256((salt + clave).encode("utf-8")).hexdigest()
    return f"{salt}${digest}"


def verificar_password(clave, password_hash):
    salt, digest = password_hash.split("$")
    return hashlib.sha256((salt + clave).encode("utf-8")).hexdigest() == digest


def crear_tablas():
    conn = conectar()
    try:
        with conn:
            conn.executescript(SCHEMA)
    finally:
        conn.close()


def seed():
    conn = conectar()
    try:
        with conn:
            if conn.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0] == 0:
                for nombre, correo, clave in USUARIOS_SEED:
                    conn.execute(
                        "INSERT INTO usuarios (nombre_usuario, password_hash, correo) VALUES (?, ?, ?)",
                        (nombre, hash_password(clave), correo),
                    )

            if conn.execute("SELECT COUNT(*) FROM juegos").fetchone()[0] == 0:
                conn.executemany(
                    "INSERT INTO juegos (titulo, descripcion, precio, categoria) VALUES (?, ?, ?, ?)",
                    JUEGOS_SEED,
                )

            if conn.execute("SELECT COUNT(*) FROM biblioteca").fetchone()[0] == 0:
                demo = conn.execute(
                    "SELECT id FROM usuarios WHERE nombre_usuario = ?", ("demo",)
                ).fetchone()
                if demo:
                    filas = conn.execute(
                        "SELECT id FROM juegos WHERE titulo IN (?, ?)",
                        ("Cyberpunk Adventures", "Neo Drift"),
                    ).fetchall()
                    for juego in filas:
                        conn.execute(
                            "INSERT OR IGNORE INTO biblioteca (usuario_id, juego_id) VALUES (?, ?)",
                            (demo["id"], juego["id"]),
                        )
    finally:
        conn.close()


def resetear_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    crear_tablas()
    seed()


if __name__ == "__main__":
    crear_tablas()
    seed()

    conn = conectar()
    try:
        usuarios = conn.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]
        juegos = conn.execute("SELECT COUNT(*) FROM juegos").fetchone()[0]
        biblioteca = conn.execute("SELECT COUNT(*) FROM biblioteca").fetchone()[0]
        tablas = [r["name"] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
    finally:
        conn.close()

    print(f"Base de datos lista en: {DB_PATH}")
    print(f"Tablas: {', '.join(sorted(tablas))}")
    print(f"Usuarios: {usuarios} | Juegos: {juegos} | Compras seed: {biblioteca}")
