from collections import deque
from datetime import datetime
from base_de_datos.connection import obtener_conexion


def _parse_fecha(texto: str):
    """Acepta 'dd/mm/aaaa' y devuelve 'aaaa-mm-dd' para SQL, o None si está vacío/inválido."""
    if not texto:
        return None
    try:
        return datetime.strptime(texto.strip(), "%d/%m/%Y").strftime("%Y-%m-%d")
    except ValueError:
        return None


def _fmt_fecha(f) -> str:
    """Formatea un datetime de MySQL a string legible."""
    if f is None:
        return ""
    if hasattr(f, "strftime"):
        return f.strftime("%d/%m/%Y %H:%M")
    return str(f)


# ── USUARIOS ──────────────────────────────────────────────────────────────────

def autenticar_usuario(usuario: str, password_hash: str):
    """Retorna dict con id/nombre/rol o None si no coincide."""
    conn = obtener_conexion()
    if not conn:
        return None
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, nombre, rol FROM usuarios WHERE usuario=%s AND password_hash=%s",
        (usuario, password_hash)
    )
    fila = cursor.fetchone()
    cursor.close()
    conn.close()
    if fila:
        return {"id": fila[0], "nombre": fila[1], "rol": fila[2]}
    return None


def listar_usuarios() -> deque:
    """Retorna deque de dicts con todos los usuarios."""
    conn = obtener_conexion()
    if not conn:
        return deque()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, usuario, rol FROM usuarios")
    cola = deque(
        {"id": r[0], "nombre": r[1], "usuario": r[2], "rol": r[3]}
        for r in cursor.fetchall()
    )
    cursor.close()
    conn.close()
    return cola


def crear_usuario(nombre: str, usuario: str, contrasena: str, rol: str = "user"):
    """Crea un nuevo usuario con contraseña hasheada. Lanza ValueError si el username ya existe."""
    import hashlib
    if not nombre.strip() or not usuario.strip() or not contrasena:
        raise ValueError("Todos los campos son obligatorios.")
    conn = obtener_conexion()
    if not conn:
        raise ConnectionError("Sin conexión a la base de datos.")
    hash_pass = hashlib.sha256(contrasena.encode("utf-8")).hexdigest()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO usuarios (nombre, usuario, password_hash, rol) VALUES (%s, %s, %s, %s)",
            (nombre.strip(), usuario.strip(), hash_pass, rol)
        )
        conn.commit()
    except Exception as e:
        raise ValueError(f"No se pudo crear el usuario: {e}")
    finally:
        cursor.close()
        conn.close()


def editar_usuario(usuario_id: int, nombre: str, usuario: str, rol: str, contrasena: str = None):
    """Actualiza datos de un usuario. Si contrasena no es None, también la cambia."""
    import hashlib
    if not nombre.strip() or not usuario.strip():
        raise ValueError("Nombre y usuario son obligatorios.")
    conn = obtener_conexion()
    if not conn:
        raise ConnectionError("Sin conexión a la base de datos.")
    try:
        cursor = conn.cursor()
        if contrasena:
            hash_pass = hashlib.sha256(contrasena.encode("utf-8")).hexdigest()
            cursor.execute(
                "UPDATE usuarios SET nombre=%s, usuario=%s, rol=%s, password_hash=%s WHERE id=%s",
                (nombre.strip(), usuario.strip(), rol, hash_pass, usuario_id)
            )
        else:
            cursor.execute(
                "UPDATE usuarios SET nombre=%s, usuario=%s, rol=%s WHERE id=%s",
                (nombre.strip(), usuario.strip(), rol, usuario_id)
            )
        if cursor.rowcount == 0:
            raise ValueError(f"No se encontró usuario con ID {usuario_id}.")
        conn.commit()
    except Exception as e:
        raise ValueError(f"Error al editar usuario: {e}")
    finally:
        cursor.close()
        conn.close()


def eliminar_usuario(usuario_id: int):
    """Elimina un usuario por ID. Lanza ValueError si no existe."""
    conn = obtener_conexion()
    if not conn:
        raise ConnectionError("Sin conexión a la base de datos.")
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM usuarios WHERE id = %s", (usuario_id,))
        if cursor.rowcount == 0:
            raise ValueError(f"No se encontró un usuario con ID {usuario_id}.")
        conn.commit()
    finally:
        cursor.close()
        conn.close()


# ── PRODUCTOS ─────────────────────────────────────────────────────────────────

def listar_productos(filtro: str = None) -> deque:
    """Retorna deque de dicts. Si hay filtro, busca por nombre o categoría."""
    conn = obtener_conexion()
    if not conn:
        return deque()
    cursor = conn.cursor()
    if filtro:
        cursor.execute(
            "SELECT id, nombre, categoria, precio, stock FROM productos "
            "WHERE nombre LIKE %s OR categoria LIKE %s ORDER BY categoria, nombre",
            (f"%{filtro}%", f"%{filtro}%")
        )
    else:
        cursor.execute(
            "SELECT id, nombre, categoria, precio, stock FROM productos ORDER BY categoria, nombre"
        )
    cola = deque(
        {"id": r[0], "nombre": r[1], "categoria": r[2], "precio": float(r[3]), "stock": r[4]}
        for r in cursor.fetchall()
    )
    cursor.close()
    conn.close()
    return cola


def insertar_producto(datos: dict):
    if not datos.get("nombre", "").strip():
        raise ValueError("El nombre del producto es obligatorio.")
    if not datos.get("categoria", "").strip():
        raise ValueError("La categoría es obligatoria.")
    if datos.get("precio", -1) < 0:
        raise ValueError("El precio debe ser mayor o igual a 0.")
    if datos.get("stock", -1) < 0:
        raise ValueError("El stock debe ser mayor o igual a 0.")
    conn = obtener_conexion()
    if not conn:
        raise ConnectionError("Sin conexión a la base de datos.")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO productos (nombre, categoria, precio, stock) VALUES (%s,%s,%s,%s)",
        (datos["nombre"].strip(), datos["categoria"].strip(), datos["precio"], datos["stock"])
    )
    conn.commit()
    cursor.close()
    conn.close()


def actualizar_precio(producto_id: int, nuevo_precio: float):
    if nuevo_precio < 0:
        raise ValueError("El precio no puede ser negativo.")
    conn = obtener_conexion()
    if not conn:
        raise ConnectionError("Sin conexión a la base de datos.")
    cursor = conn.cursor()
    cursor.execute("UPDATE productos SET precio=%s WHERE id=%s", (nuevo_precio, producto_id))
    if cursor.rowcount == 0:
        raise ValueError(f"No se encontró producto con ID {producto_id}.")
    conn.commit()
    cursor.close()
    conn.close()


def actualizar_stock(producto_id: int, nuevo_stock: int):
    if nuevo_stock < 0:
        raise ValueError("El stock no puede ser negativo.")
    conn = obtener_conexion()
    if not conn:
        raise ConnectionError("Sin conexión a la base de datos.")
    cursor = conn.cursor()
    cursor.execute("UPDATE productos SET stock=%s WHERE id=%s", (nuevo_stock, producto_id))
    if cursor.rowcount == 0:
        raise ValueError(f"No se encontró producto con ID {producto_id}.")
    conn.commit()
    cursor.close()
    conn.close()


def eliminar_producto(producto_id: int):
    conn = obtener_conexion()
    if not conn:
        raise ConnectionError("Sin conexión a la base de datos.")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM productos WHERE id=%s", (producto_id,))
    if cursor.rowcount == 0:
        raise ValueError(f"No se encontró producto con ID {producto_id}.")
    conn.commit()
    cursor.close()
    conn.close()


# ── ÓRDENES ───────────────────────────────────────────────────────────────────

def crear_orden(usuario_id: int, items_carrito: dict) -> dict:
    """
    Crea una orden con sus ítems y descuenta stock atómicamente.
    items_carrito: {producto_id: {"nombre", "precio", "cantidad"}, ...}
    Retorna {"orden_id", "total", "items_ok": [nombres...]}.
    Levanta ValueError o ConnectionError.
    """
    if not items_carrito:
        raise ValueError("El carrito está vacío.")

    conn = obtener_conexion()
    if not conn:
        raise ConnectionError("Sin conexión a la base de datos.")

    try:
        cursor = conn.cursor()
        try:
            conn.start_transaction()

            total = 0.0
            items_ok = []
            detalles = []

            for pid, item in items_carrito.items():
                cantidad = int(item["cantidad"])
                if cantidad <= 0:
                    raise ValueError("La cantidad debe ser mayor a cero.")

                cursor.execute(
                    "UPDATE productos SET stock = stock - %s "
                    "WHERE id = %s AND stock >= %s",
                    (cantidad, pid, cantidad),
                )
                if cursor.rowcount == 0:
                    cursor.execute(
                        "SELECT nombre, stock FROM productos WHERE id = %s", (pid,)
                    )
                    fila = cursor.fetchone()
                    if not fila:
                        raise ValueError(f"Producto con id {pid} no encontrado.")
                    raise ValueError(
                        f'Stock insuficiente para "{fila[0]}". Disponible: {fila[1]}.'
                    )

                cursor.execute(
                    "SELECT nombre, precio FROM productos WHERE id = %s", (pid,)
                )
                nombre_bd, precio_bd = cursor.fetchone()
                precio_unit = round(float(precio_bd), 2)
                subtotal = round(precio_unit * cantidad, 2)
                total += subtotal

                detalles.append((pid, nombre_bd, precio_unit, cantidad, subtotal))
                items_ok.append(nombre_bd)

            total = round(total, 2)

            cursor.execute(
                "INSERT INTO ordenes (usuario_id, total, estado) VALUES (%s, %s, 'completada')",
                (usuario_id, total),
            )
            orden_id = cursor.lastrowid

            cursor.executemany(
                "INSERT INTO detalle_orden "
                "(orden_id, producto_id, producto_nombre, precio_unitario, cantidad, subtotal) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                [(orden_id, pid, nom, pu, cant, sub) for pid, nom, pu, cant, sub in detalles],
            )

            conn.commit()
            return {"orden_id": orden_id, "total": total, "items_ok": items_ok}
        except Exception:
            try:
                conn.rollback()
            except Exception:
                pass
            raise
        finally:
            cursor.close()
    finally:
        conn.close()


def cancelar_orden(orden_id: int) -> None:
    """Cancela una orden y devuelve el stock de cada ítem."""
    conn = obtener_conexion()
    if not conn:
        raise ConnectionError("Sin conexión a la base de datos.")
    try:
        cursor = conn.cursor()
        conn.start_transaction()

        cursor.execute("SELECT estado FROM ordenes WHERE id=%s", (orden_id,))
        fila = cursor.fetchone()
        if not fila:
            raise ValueError(f"Orden #{orden_id} no encontrada.")
        if fila[0] == "cancelada":
            raise ValueError(f"La orden #{orden_id} ya está cancelada.")

        # Devolver stock
        cursor.execute(
            "SELECT producto_id, cantidad FROM detalle_orden WHERE orden_id=%s", (orden_id,)
        )
        for pid, cant in cursor.fetchall():
            cursor.execute(
                "UPDATE productos SET stock = stock + %s WHERE id = %s", (cant, pid)
            )

        cursor.execute(
            "UPDATE ordenes SET estado='cancelada' WHERE id=%s", (orden_id,)
        )
        conn.commit()
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
        raise
    finally:
        cursor.close()
        conn.close()


def listar_ordenes_usuario(
    usuario_id: int,
    filtro_producto: str = None,
    fecha_desde: str = None,
    fecha_hasta: str = None,
) -> list:
    conn = obtener_conexion()
    if not conn:
        return []

    f_prod = f"%{filtro_producto.strip()}%" if filtro_producto and filtro_producto.strip() else None
    f_desde = _parse_fecha(fecha_desde)
    f_hasta = _parse_fecha(fecha_hasta)

    sql = """
        SELECT o.id, o.total, o.estado,
               o.fecha,
               COUNT(d.id) AS items
        FROM ordenes o
        LEFT JOIN detalle_orden d ON d.orden_id = o.id
        WHERE o.usuario_id = %s
    """
    params = [usuario_id]

    if f_prod:
        sql += " AND o.id IN (SELECT DISTINCT orden_id FROM detalle_orden WHERE producto_nombre LIKE %s)"
        params.append(f_prod)
    if f_desde:
        sql += " AND DATE(o.fecha) >= %s"
        params.append(f_desde)
    if f_hasta:
        sql += " AND DATE(o.fecha) <= %s"
        params.append(f_hasta)

    sql += " GROUP BY o.id ORDER BY o.fecha DESC"

    try:
        cursor = conn.cursor()
        cursor.execute(sql, tuple(params))
        return [
            {"id": r[0], "total": float(r[1]), "estado": r[2],
             "fecha": _fmt_fecha(r[3]), "items": r[4]}
            for r in cursor.fetchall()
        ]
    finally:
        cursor.close()
        conn.close()


def listar_todas_ordenes(
    filtro_usuario: str = None,
    filtro_producto: str = None,
    fecha_desde: str = None,
    fecha_hasta: str = None,
) -> list:
    conn = obtener_conexion()
    if not conn:
        return []

    f_usuario = f"%{filtro_usuario.strip()}%" if filtro_usuario and filtro_usuario.strip() else None
    f_prod = f"%{filtro_producto.strip()}%" if filtro_producto and filtro_producto.strip() else None
    f_desde = _parse_fecha(fecha_desde)
    f_hasta = _parse_fecha(fecha_hasta)

    sql = """
        SELECT o.id, o.total, o.estado,
               o.fecha,
               COUNT(d.id) AS items,
               u.nombre, u.usuario
        FROM ordenes o
        JOIN usuarios u ON u.id = o.usuario_id
        LEFT JOIN detalle_orden d ON d.orden_id = o.id
        WHERE 1=1
    """
    params = []

    if f_usuario:
        sql += " AND (u.nombre LIKE %s OR u.usuario LIKE %s)"
        params += [f_usuario, f_usuario]
    if f_prod:
        sql += " AND o.id IN (SELECT DISTINCT orden_id FROM detalle_orden WHERE producto_nombre LIKE %s)"
        params.append(f_prod)
    if f_desde:
        sql += " AND DATE(o.fecha) >= %s"
        params.append(f_desde)
    if f_hasta:
        sql += " AND DATE(o.fecha) <= %s"
        params.append(f_hasta)

    sql += " GROUP BY o.id ORDER BY o.fecha DESC"

    try:
        cursor = conn.cursor()
        cursor.execute(sql, tuple(params))
        return [
            {"id": r[0], "total": float(r[1]), "estado": r[2],
             "fecha": _fmt_fecha(r[3]), "items": r[4],
             "usuario_nombre": r[5], "usuario_login": r[6]}
            for r in cursor.fetchall()
        ]
    finally:
        cursor.close()
        conn.close()


def obtener_detalle_orden(orden_id: int) -> dict:
    conn = obtener_conexion()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT o.id, o.usuario_id, u.nombre, u.usuario, o.total, o.estado, o.fecha
            FROM ordenes o
            JOIN usuarios u ON u.id = o.usuario_id
            WHERE o.id = %s
            """,
            (orden_id,),
        )
        cab = cursor.fetchone()
        if not cab:
            return None

        cursor.execute(
            """
            SELECT producto_id, producto_nombre, precio_unitario, cantidad, subtotal
            FROM detalle_orden
            WHERE orden_id = %s
            ORDER BY id
            """,
            (orden_id,),
        )
        items = [
            {"producto_id": r[0], "producto_nombre": r[1],
             "precio_unitario": float(r[2]), "cantidad": r[3], "subtotal": float(r[4])}
            for r in cursor.fetchall()
        ]
        return {
            "id": cab[0], "usuario_id": cab[1],
            "usuario_nombre": cab[2], "usuario_login": cab[3],
            "total": float(cab[4]), "estado": cab[5], "fecha": _fmt_fecha(cab[6]),
            "items": items,
        }
    finally:
        cursor.close()
        conn.close()


def resumen_ventas() -> dict:
    """Métricas para el dashboard del admin."""
    conn = obtener_conexion()
    if not conn:
        return {"total_ventas": 0, "ingresos": 0.0, "productos": 0, "usuarios": 0}
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*), COALESCE(SUM(total), 0) FROM ordenes WHERE estado='completada'")
    fila = cursor.fetchone()
    cursor.execute("SELECT COUNT(*) FROM productos")
    productos = cursor.fetchone()
    cursor.execute("SELECT COUNT(*) FROM usuarios WHERE rol='user'")
    usuarios = cursor.fetchone()
    cursor.close()
    conn.close()
    return {
        "total_ventas": fila[0] or 0,
        "ingresos":     round(float(fila[1] or 0), 2),
        "productos":    productos[0],
        "usuarios":     usuarios[0],
    }
