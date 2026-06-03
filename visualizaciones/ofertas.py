"""
ofertas.py — Módulo de lógica y asignación de ofertas
(estructura preparada para implementación futura)
"""
from collections import deque
from base_de_datos.connection import obtener_conexion


def listar_ofertas() -> deque:
    """Retorna deque de dicts con las ofertas activas."""
    conn = obtener_conexion()
    cursor = conn.cursor()
    # tabla ofertas se puede agregar en connection.py cuando se implemente
    try:
        cursor.execute("""
            SELECT o.id, p.nombre, o.descuento, o.fecha_inicio, o.fecha_fin
            FROM ofertas o
            JOIN productos p ON o.producto_id = p.id
            WHERE date('now') BETWEEN o.fecha_inicio AND o.fecha_fin
            ORDER BY o.descuento DESC
        """)
        cola = deque(
            {"id": r["id"], "producto": r["nombre"],
             "descuento": r["descuento"], "inicio": r["fecha_inicio"], "fin": r["fecha_fin"]}
            for r in cursor.fetchall()
        )
    except Exception:
        cola = deque()
    conn.close()
    return cola


def crear_oferta(producto_id: int, descuento: float, fecha_inicio: str, fecha_fin: str):
    """Registra una nueva oferta para el producto indicado."""
    conn = obtener_conexion()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS ofertas (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            producto_id  INTEGER NOT NULL,
            descuento    REAL    NOT NULL,
            fecha_inicio TEXT    NOT NULL,
            fecha_fin    TEXT    NOT NULL,
            FOREIGN KEY (producto_id) REFERENCES productos(id)
        )
    """)
    conn.execute(
        "INSERT INTO ofertas (producto_id, descuento, fecha_inicio, fecha_fin) VALUES (?,?,?,?)",
        (producto_id, descuento, fecha_inicio, fecha_fin)
    )
    conn.commit()
    conn.close()
