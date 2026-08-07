from database import db

if __name__ == "__main__":
    db.crear_tablas()
    db.seed()
    print("Black Bulls Gamestore - Fase 1 lista. La interfaz llega en la Fase 2.")
