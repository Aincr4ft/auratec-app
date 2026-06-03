import customtkinter as ctk
from collections import deque
from sesion import Sesion
from base_de_datos.queries import listar_productos, crear_orden, listar_ordenes_usuario
from visualizaciones._widgets import mostrar_detalle_orden


class VentanaUsuario(ctk.CTk):
    """
    Interfaz de ventas para el usuario estándar.
    Diseño tipo tienda: catálogo con tarjetas, carrito lateral y resumen de compra.
    """

    def __init__(self):
        super().__init__()
        self.sesion = Sesion.obtener()
        self.title(f"AURATEC  —  {self.sesion.nombre}")
        self.geometry("1100x680")
        self.minsize(900, 600)
        ctk.set_appearance_mode("dark")

        # DICCIONARIO: producto_id -> {nombre, precio, cantidad} — carrito de compras
        self.carrito: dict = {}

        self._construir_interfaz()
        self._cargar_catalogo()

    # MENU PRINCIPAL
    def _construir_interfaz(self):
        # encabezado
        header = ctk.CTkFrame(self, fg_color="#0f3460", corner_radius=0, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(header, text="🛒  AURATEC  — Tienda",
                     font=("Arial", 20, "bold"), text_color="white").pack(side="left", padx=20)
        ctk.CTkLabel(header, text=f"👤  {self.sesion.nombre}",
                     font=("Arial", 13), text_color="#a0c4ff").pack(side="left", padx=10)
        ctk.CTkButton(header, text="Historial 📋", width=110, fg_color="#16213e",
                      hover_color="#1a1a2e", command=self._ver_historial).pack(side="right", padx=8, pady=10)
        ctk.CTkButton(header, text="Salir", width=80, fg_color="#e74c3c",
                      hover_color="#c0392b", command=self._cerrar_sesion).pack(side="right", padx=4, pady=10)

        # cuerpo dividido en dos columnas
        cuerpo = ctk.CTkFrame(self, fg_color="transparent")
        cuerpo.pack(fill="both", expand=True, padx=15, pady=10)
        cuerpo.grid_columnconfigure(0, weight=3)
        cuerpo.grid_columnconfigure(1, weight=1)
        cuerpo.grid_rowconfigure(0, weight=1)

        # panel izquierdo: catálogo
        panel_cat = ctk.CTkFrame(cuerpo, fg_color="#1a1a2e", corner_radius=12)
        panel_cat.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        ctk.CTkLabel(panel_cat, text="📦  Catálogo de Productos",
                     font=("Arial", 16, "bold")).pack(pady=(12, 6), padx=15, anchor="w")

        # barra de búsqueda
        barra = ctk.CTkFrame(panel_cat, fg_color="transparent")
        barra.pack(fill="x", padx=15, pady=(0, 8))
        self.entry_buscar = ctk.CTkEntry(barra, placeholder_text="Buscar producto o categoría...", height=34)
        self.entry_buscar.pack(side="left", fill="x", expand=True, padx=(0, 6))
        ctk.CTkButton(barra, text="Buscar", width=90, height=34,
                      command=self._buscar).pack(side="left", padx=(0, 4))
        ctk.CTkButton(barra, text="Ver todo", width=90, height=34, fg_color="#555",
                      hover_color="#333", command=self._cargar_catalogo).pack(side="left")

        # tabla de productos con scroll
        self.frame_catalogo = ctk.CTkScrollableFrame(panel_cat, fg_color="transparent")
        self.frame_catalogo.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # DICCIONARIO: columnas del catálogo
        self.cols_cat = {"ID": 45, "Nombre": 220, "Categoría": 130, "Precio": 90, "Stock": 65, "": 90}
        for col_i, (enc, ancho) in enumerate(self.cols_cat.items()):
            ctk.CTkLabel(self.frame_catalogo, text=enc, font=("Arial", 11, "bold"),
                         width=ancho, anchor="w", text_color="#a0c4ff").grid(
                row=0, column=col_i, padx=4, pady=6)

        # panel derecho: carrito
        panel_carrito = ctk.CTkFrame(cuerpo, fg_color="#1a1a2e", corner_radius=12)
        panel_carrito.grid(row=0, column=1, sticky="nsew")

        ctk.CTkLabel(panel_carrito, text="🛒  Mi Carrito",
                     font=("Arial", 15, "bold")).pack(pady=(12, 6), padx=12, anchor="w")

        self.frame_carrito = ctk.CTkScrollableFrame(panel_carrito, height=320, fg_color="transparent")
        self.frame_carrito.pack(fill="x", padx=10)

        self.lbl_total = ctk.CTkLabel(panel_carrito, text="Total: $0.00",
                                      font=("Arial", 16, "bold"), text_color="#2ecc71")
        self.lbl_total.pack(pady=(10, 4))

        ctk.CTkButton(panel_carrito, text="✅  Confirmar Compra", height=40,
                      fg_color="#27ae60", hover_color="#1e8449",
                      font=("Arial", 13, "bold"), command=self._confirmar_compra).pack(
            fill="x", padx=12, pady=4)
        ctk.CTkButton(panel_carrito, text="🗑  Vaciar Carrito", height=36,
                      fg_color="#555", hover_color="#333",
                      command=self._vaciar_carrito).pack(fill="x", padx=12, pady=(0, 8))

        self.lbl_msg = ctk.CTkLabel(panel_carrito, text="", font=("Arial", 11),
                                    wraplength=200)
        self.lbl_msg.pack(pady=4, padx=12)

    # CATALOGO
    def _cargar_catalogo(self, filtro=None):
        for w in self.frame_catalogo.winfo_children():
            if int(w.grid_info().get("row", 0)) > 0:
                w.destroy()

        # COLA: productos de la BD
        cola = listar_productos(filtro)
        anchos_cola = deque(self.cols_cat.values())

        if not cola:
            ctk.CTkLabel(self.frame_catalogo, text="Sin resultados.",
                         text_color="gray").grid(row=1, column=0, columnspan=6, pady=20)
            return

        fila = 1
        while cola:
            p = cola.popleft()
            color = "#16213e" if fila % 2 == 0 else "transparent"
            col_anchos = deque(anchos_cola)

            for col_i, clave in enumerate(("id", "nombre", "categoria", "precio", "stock")):
                ancho = col_anchos.popleft()
                val = p[clave]
                texto = f"${val:.2f}" if clave == "precio" else str(val)
                text_color = "#e74c3c" if clave == "stock" and val == 0 else "white"
                ctk.CTkLabel(self.frame_catalogo, text=texto, width=ancho,
                             anchor="w", fg_color=color,
                             text_color=text_color).grid(row=fila, column=col_i, padx=4, pady=3)

            # botón agregar al carrito
            ancho_btn = col_anchos.popleft()
            pid = p["id"]
            stock = p["stock"]
            ctk.CTkButton(
                self.frame_catalogo, text="+ Agregar", width=ancho_btn, height=26,
                fg_color="#2980b9", hover_color="#1a5276",
                font=("Arial", 11),
                command=lambda pid=pid, nombre=p["nombre"], precio=p["precio"], stock=stock: \
                    self._agregar_al_carrito(pid, nombre, precio, stock)
            ).grid(row=fila, column=5, padx=4, pady=3)

            fila += 1

    def _buscar(self):
        filtro = self.entry_buscar.get().strip()
        self._cargar_catalogo(filtro if filtro else None)

    # CARRITO
    def _agregar_al_carrito(self, pid: int, nombre: str, precio: float, stock: int):
        if stock <= 0:
            self.lbl_msg.configure(
                text=f'"{nombre}" sin stock disponible.', text_color="#e74c3c"
            )
            return

        cantidad_actual = self.carrito.get(pid, {}).get("cantidad", 0)
        if cantidad_actual + 1 > stock:
            self.lbl_msg.configure(
                text=f'Stock máximo alcanzado para "{nombre}" (disponible: {stock}).',
                text_color="#e74c3c",
            )
            return

        if pid in self.carrito:
            self.carrito[pid]["cantidad"] += 1
        else:
            self.carrito[pid] = {"nombre": nombre, "precio": precio, "cantidad": 1}
        self._refrescar_carrito()
        self.lbl_msg.configure(text=f'"{nombre}" agregado ✓', text_color="#2ecc71")

    def _refrescar_carrito(self):
        for w in self.frame_carrito.winfo_children():
            w.destroy()

        total = 0.0
        cola_items = deque(self.carrito.items())

        while cola_items:
            pid, item = cola_items.popleft()
            subtotal = item["precio"] * item["cantidad"]
            total += subtotal

            fila_frame = ctk.CTkFrame(self.frame_carrito, fg_color="#16213e", corner_radius=8)
            fila_frame.pack(fill="x", pady=3)

            ctk.CTkLabel(fila_frame, text=item["nombre"], font=("Arial", 11),
                         anchor="w", wraplength=140).grid(row=0, column=0, padx=8, pady=4, sticky="w")
            ctk.CTkLabel(fila_frame, text=f"x{item['cantidad']}  ${subtotal:.2f}",
                         font=("Arial", 11), text_color="#a0c4ff").grid(row=0, column=1, padx=6)

            ctrl = ctk.CTkFrame(fila_frame, fg_color="transparent")
            ctrl.grid(row=0, column=2, padx=6)
            ctk.CTkButton(ctrl, text="+", width=26, height=26, fg_color="#2980b9",
                          command=lambda p=pid: self._cambiar_cant(p, 1)).pack(side="left", padx=2)
            ctk.CTkButton(ctrl, text="−", width=26, height=26, fg_color="#555",
                          command=lambda p=pid: self._cambiar_cant(p, -1)).pack(side="left", padx=2)

        self.lbl_total.configure(text=f"Total: ${total:.2f}")

    def _cambiar_cant(self, pid: int, delta: int):
        if pid in self.carrito:
            self.carrito[pid]["cantidad"] += delta
            if self.carrito[pid]["cantidad"] <= 0:
                del self.carrito[pid]
        self._refrescar_carrito()

    def _vaciar_carrito(self):
        self.carrito.clear()
        self._refrescar_carrito()
        self.lbl_msg.configure(text="Carrito vaciado.", text_color="gray")

    def _confirmar_compra(self):
        if not self.carrito:
            self.lbl_msg.configure(text="El carrito está vacío.", text_color="#e74c3c")
            return

        try:
            resultado = crear_orden(self.sesion.usuario_id, self.carrito)
            n = len(resultado["items_ok"])
            total = resultado["total"]
            self.carrito.clear()
            self._refrescar_carrito()
            self._cargar_catalogo()
            self.lbl_msg.configure(
                text=f"✅ Compra OK: {n} producto(s) — Total ${total:,.2f}",
                text_color="#2ecc71",
            )
        except (ValueError, ConnectionError) as e:
            self.lbl_msg.configure(text=f"⚠ {e}", text_color="#e74c3c")
        except Exception as e:
            self.lbl_msg.configure(text=f"Error inesperado: {e}", text_color="#e74c3c")

    # HISTORIAL
    def _ver_historial(self):
        v = ctk.CTkToplevel(self)
        v.title("Mis Compras")
        v.geometry("700x500")
        v.grab_set()

        ctk.CTkLabel(v, text="📋  Historial de Compras",
                     font=("Arial", 16, "bold")).pack(pady=(15, 6))

        # Filtros
        filtros = ctk.CTkFrame(v, fg_color="transparent")
        filtros.pack(fill="x", padx=15, pady=(0, 8))

        ctk.CTkLabel(filtros, text="Producto:", font=("Arial", 11)).grid(row=0, column=0, padx=(0, 4))
        entry_prod = ctk.CTkEntry(filtros, placeholder_text="Nombre...", width=160, height=30)
        entry_prod.grid(row=0, column=1, padx=(0, 10))

        ctk.CTkLabel(filtros, text="Desde:", font=("Arial", 11)).grid(row=0, column=2, padx=(0, 4))
        entry_desde = ctk.CTkEntry(filtros, placeholder_text="dd/mm/aaaa", width=110, height=30)
        entry_desde.grid(row=0, column=3, padx=(0, 10))

        ctk.CTkLabel(filtros, text="Hasta:", font=("Arial", 11)).grid(row=0, column=4, padx=(0, 4))
        entry_hasta = ctk.CTkEntry(filtros, placeholder_text="dd/mm/aaaa", width=110, height=30)
        entry_hasta.grid(row=0, column=5, padx=(0, 10))

        frame_scroll = ctk.CTkScrollableFrame(v, height=340)
        frame_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        cols_hist = {"#Orden": 65, "Total": 90, "Estado": 90, "Ítems": 55, "Fecha": 160, "": 80}

        def _encabezados():
            for w in frame_scroll.winfo_children():
                w.destroy()
            for col_i, (enc, ancho) in enumerate(cols_hist.items()):
                ctk.CTkLabel(frame_scroll, text=enc, font=("Arial", 11, "bold"),
                             width=ancho, anchor="w", text_color="#a0c4ff").grid(
                    row=0, column=col_i, padx=4, pady=5)

        def _cargar(filtro_prod=None, desde=None, hasta=None):
            _encabezados()
            ordenes = listar_ordenes_usuario(
                self.sesion.usuario_id,
                filtro_producto=filtro_prod,
                fecha_desde=desde,
                fecha_hasta=hasta,
            )
            if not ordenes:
                ctk.CTkLabel(frame_scroll, text="Sin compras registradas.", text_color="gray").grid(
                    row=1, column=0, columnspan=6, pady=20)
                return
            col_anchos = deque(cols_hist.values())
            for fila, h in enumerate(ordenes, start=1):
                color = "#16213e" if fila % 2 == 0 else "transparent"
                aw = deque(col_anchos)
                for col_i, (clave, fmt) in enumerate({
                    "id": "{}", "total": "${:.2f}", "estado": "{}",
                    "items": "{}", "fecha": "{}"
                }.items()):
                    ancho = aw.popleft()
                    texto = fmt.format(h[clave])
                    ctk.CTkLabel(frame_scroll, text=texto, width=ancho,
                                 anchor="w", fg_color=color).grid(row=fila, column=col_i, padx=4, pady=3)
                # botón ver detalle
                oid = h["id"]
                ctk.CTkButton(frame_scroll, text="Ver", width=aw.popleft(), height=26,
                              fg_color="#2980b9", hover_color="#1a5276",
                              command=lambda o=oid: mostrar_detalle_orden(v, o)
                              ).grid(row=fila, column=5, padx=4, pady=3)

        def _buscar_historial():
            _cargar(
                filtro_prod=entry_prod.get().strip() or None,
                desde=entry_desde.get().strip() or None,
                hasta=entry_hasta.get().strip() or None,
            )

        ctk.CTkButton(filtros, text="Filtrar", width=80, height=30,
                      command=_buscar_historial).grid(row=0, column=6, padx=4)
        ctk.CTkButton(filtros, text="Ver todo", width=80, height=30, fg_color="#555",
                      hover_color="#333",
                      command=lambda: _cargar()).grid(row=0, column=7, padx=4)

        _cargar()

    # SESION
    def _cerrar_sesion(self):
        Sesion.cerrar()
        self.destroy()
        from login import LoginApp
        LoginApp().mainloop()
