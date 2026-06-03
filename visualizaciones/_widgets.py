"""
_widgets.py — Helpers de UI compartidos entre las vistas.
Por ahora solo expone mostrar_detalle_orden, que abre un modal con la
cabecera de la orden y la lista de ítems (producto, precio unitario,
cantidad, subtotal). Reutilizado por el usuario (historial) y el admin
(grilla global de ventas).
"""
import customtkinter as ctk
from base_de_datos.queries import obtener_detalle_orden


def mostrar_detalle_orden(parent, orden_id: int) -> None:
    """Abre un CTkToplevel con el detalle de la orden. Si la orden no existe, muestra error."""
    detalle = obtener_detalle_orden(orden_id)
    if not detalle:
        v = ctk.CTkToplevel(parent)
        v.title("Error")
        v.geometry("320x120")
        v.grab_set()
        ctk.CTkLabel(v, text=f"No se encontró la orden #{orden_id}.",
                     text_color="#e74c3c", font=("Arial", 12)).pack(expand=True, padx=20, pady=20)
        return

    v = ctk.CTkToplevel(parent)
    v.title(f"Detalle Orden #{detalle['id']}")
    v.geometry("620x440")
    v.grab_set()

    # Cabecera
    header = ctk.CTkFrame(v, fg_color="#0f3460", corner_radius=0)
    header.pack(fill="x")
    ctk.CTkLabel(
        header,
        text=f"🧾  Orden #{detalle['id']}  —  {detalle['usuario_nombre']} (@{detalle['usuario_login']})",
        font=("Arial", 14, "bold"), text_color="white",
    ).pack(side="left", padx=15, pady=10)
    ctk.CTkLabel(
        header,
        text=f"{detalle['fecha']}  •  {detalle['estado']}",
        font=("Arial", 11), text_color="#a0c4ff",
    ).pack(side="right", padx=15)

    # Tabla de ítems
    frame = ctk.CTkScrollableFrame(v, fg_color="transparent")
    frame.pack(fill="both", expand=True, padx=15, pady=12)

    cols = {"Producto": 260, "Precio unit.": 110, "Cant.": 60, "Subtotal": 110}
    for col_i, (enc, ancho) in enumerate(cols.items()):
        ctk.CTkLabel(
            frame, text=enc, font=("Arial", 12, "bold"),
            width=ancho, anchor="w", text_color="#a0c4ff",
        ).grid(row=0, column=col_i, padx=5, pady=6)

    if not detalle["items"]:
        ctk.CTkLabel(frame, text="Esta orden no tiene ítems.",
                     text_color="gray").grid(row=1, column=0, columnspan=4, pady=20)
    else:
        for i, item in enumerate(detalle["items"], start=1):
            color = "#16213e" if i % 2 == 0 else "transparent"
            ctk.CTkLabel(
                frame, text=item["producto_nombre"], width=cols["Producto"],
                anchor="w", fg_color=color, wraplength=250,
            ).grid(row=i, column=0, padx=5, pady=3)
            ctk.CTkLabel(
                frame, text=f"${item['precio_unitario']:.2f}",
                width=cols["Precio unit."], anchor="w", fg_color=color,
            ).grid(row=i, column=1, padx=5, pady=3)
            ctk.CTkLabel(
                frame, text=str(item["cantidad"]),
                width=cols["Cant."], anchor="w", fg_color=color,
            ).grid(row=i, column=2, padx=5, pady=3)
            ctk.CTkLabel(
                frame, text=f"${item['subtotal']:.2f}",
                width=cols["Subtotal"], anchor="w", fg_color=color,
            ).grid(row=i, column=3, padx=5, pady=3)

    # Pie con total
    pie = ctk.CTkFrame(v, fg_color="transparent")
    pie.pack(fill="x", padx=15, pady=(0, 12))
    ctk.CTkLabel(
        pie, text=f"Total: ${detalle['total']:,.2f}",
        font=("Arial", 15, "bold"), text_color="#2ecc71",
    ).pack(side="right")

    ctk.CTkButton(v, text="Cerrar", width=100, command=v.destroy).pack(pady=(0, 12))
