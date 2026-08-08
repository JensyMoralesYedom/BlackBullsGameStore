import hashlib
import os
import re
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
    ("Cyberpunk 2077", "Mundo abierto en Night City: ciberimplantes, neon y misiones que definen tu historia.", 49.99, "RPG"),
    ("Elden Ring", "RPG de acción de mundo abierto firmado por FromSoftware.", 59.99, "RPG"),
    ("God of War", "Kratos y Atreus en los reinos nórdicos: acción brutal y narrativa épica.", 39.99, "Accion"),
    ("Forza Horizon 5", "Carreras arcade en el mundo abierto de México, lleno de eventos y personalización.", 59.99, "Carreras"),
    ("Halo: The Master Chief Collection", "Seis campañas clásicas de Halo reunidas en un solo paquete.", 39.99, "Shooter"),
    ("Age of Empires IV", "La saga de estrategia en tiempo real regresa con civilizaciones históricas.", 29.99, "Estrategia"),
    ("Stardew Valley", "Simulador de granja con cientos de actividades, pueblos y secretos.", 14.99, "Indie"),
    ("Hades", "Roguelike de acción con mitología griega y combate frenético.", 24.99, "Indie"),
    ("The Witcher 3: Wild Hunt", "Aventura de rol épica en un continente en guerra, llena de decisiones.", 39.99, "Aventura"),
    ("Rocket League", "Fútbol con coches: partidos rápidos, espectaculares y multijugador.", 19.99, "Deportes"),
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


def _slug(titulo):
    """Nombre de archivo para la portada de un juego (Fase 6)."""
    return re.sub(r"[^a-z0-9]+", "_", titulo.lower()).strip("_")


def portada_relativa(titulo):
    return f"assets/juegos/{_slug(titulo)}.png"


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
                    "INSERT INTO juegos (titulo, descripcion, precio, categoria, portada_path) "
                    "VALUES (?, ?, ?, ?, ?)",
                    [
                        (titulo, descripcion, precio, categoria, portada_relativa(titulo))
                        for titulo, descripcion, precio, categoria in JUEGOS_SEED
                    ],
                )

            if conn.execute("SELECT COUNT(*) FROM biblioteca").fetchone()[0] == 0:
                demo = conn.execute(
                    "SELECT id FROM usuarios WHERE nombre_usuario = ?", ("demo",)
                ).fetchone()
                if demo:
                    filas = conn.execute(
                        "SELECT id FROM juegos WHERE titulo IN (?, ?)",
                        ("Stardew Valley", "Hades"),
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
