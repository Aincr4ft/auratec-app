import os
import hashlib
import mysql.connector
from mysql.connector.pooling import MySQLConnectionPool
from dotenv import load_dotenv

load_dotenv()

_pool = None


def obtener_pool() -> MySQLConnectionPool:
    """Crea el pool de conexiones una sola vez y lo reutiliza."""
    global _pool
    if _pool is None:
        _pool = MySQLConnectionPool(
            pool_name="auratec_pool",
            pool_size=5,
            pool_reset_session=True,
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", 3306)),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            connection_timeout=10,
        )
    return _pool


def obtener_conexion() -> mysql.connector.MySQLConnection:
    """Devuelve una conexión del pool. Mucho más rápido que abrir una nueva."""
    try:
        return obtener_pool().get_connection()
    except mysql.connector.Error as e:
        print(f"Error al obtener conexión del pool: {e}")
        return None


def inicializar_bd():
    """Crea las tablas si no existen e inserta datos iniciales."""
    conn = obtener_conexion()
    if not conn:
        print("No se pudo inicializar la base de datos: sin conexión.")
        return

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id            INT AUTO_INCREMENT PRIMARY KEY,
            nombre        VARCHAR(255) NOT NULL,
            usuario       VARCHAR(255) NOT NULL UNIQUE,
            password_hash VARCHAR(64)  NOT NULL,
            rol           VARCHAR(50)  NOT NULL DEFAULT 'user'
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id        INT AUTO_INCREMENT PRIMARY KEY,
            nombre    VARCHAR(255) NOT NULL,
            categoria VARCHAR(255) NOT NULL,
            precio    DECIMAL(10,2) NOT NULL,
            stock     INT          NOT NULL DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            id          INT AUTO_INCREMENT PRIMARY KEY,
            producto_id INT           NOT NULL,
            cantidad    INT           NOT NULL,
            total       DECIMAL(10,2) NOT NULL,
            fecha       DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
            usuario_id  INT           NOT NULL,
            FOREIGN KEY (producto_id) REFERENCES productos(id),
            FOREIGN KEY (usuario_id)  REFERENCES usuarios(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ordenes (
            id         INT AUTO_INCREMENT PRIMARY KEY,
            usuario_id INT           NOT NULL,
            total      DECIMAL(10,2) NOT NULL,
            estado     VARCHAR(20)   NOT NULL DEFAULT 'completada',
            fecha      DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
            INDEX idx_ordenes_usuario_fecha (usuario_id, fecha),
            INDEX idx_ordenes_fecha        (fecha)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS detalle_orden (
            id              INT AUTO_INCREMENT PRIMARY KEY,
            orden_id        INT           NOT NULL,
            producto_id     INT           NOT NULL,
            producto_nombre VARCHAR(255)  NOT NULL,
            precio_unitario DECIMAL(10,2) NOT NULL,
            cantidad        INT           NOT NULL,
            subtotal        DECIMAL(10,2) NOT NULL,
            FOREIGN KEY (orden_id)    REFERENCES ordenes(id)    ON DELETE CASCADE,
            FOREIGN KEY (producto_id) REFERENCES productos(id),
            INDEX idx_detalle_orden (orden_id)
        )
    """)

    hash_admin = hashlib.sha256("admin123".encode()).hexdigest()
    cursor.execute("""
        INSERT IGNORE INTO usuarios (nombre, usuario, password_hash, rol)
        VALUES ('Administrador', 'admin', %s, 'admin')
    """, (hash_admin,))

    hash_user = hashlib.sha256("user123".encode()).hexdigest()
    cursor.execute("""
        INSERT IGNORE INTO usuarios (nombre, usuario, password_hash, rol)
        VALUES ('Usuario Demo', 'usuario', %s, 'user')
    """, (hash_user,))

    cursor.execute("SELECT COUNT(*) FROM productos")
    count = cursor.fetchone()[0]
    if count == 0:
        productos_demo = [
            ("Laptop HP 15",        "Computadoras",   1200.00, 10),
            ("Mouse Inalámbrico",   "Periféricos",      25.00, 50),
            ("Teclado Mecánico",    "Periféricos",      85.00, 30),
            ("Monitor 24\"",        "Monitores",       320.00, 15),
            ("Audífonos Bluetooth", "Audio",            60.00, 25),
            ("Webcam Full HD",      "Periféricos",      45.00, 20),
            ("SSD 1TB",             "Almacenamiento",  110.00, 40),
            ("RAM 16GB DDR4",       "Componentes",      70.00, 35),
        ]
        cursor.executemany(
            "INSERT INTO productos (nombre, categoria, precio, stock) VALUES (%s,%s,%s,%s)",
            productos_demo
        )

    conn.commit()
    cursor.close()
    conn.close()
