import threading
import customtkinter as ctk
from collections import deque
from sesion import Sesion
from base_de_datos.queries import listar_productos, crear_orden, listar_ordenes_usuario
from visualizaciones._widgets import mostrar_detalle_orden

# ── PALETA ────────────────────────────────────────────────────────────────────
C_BG      = "#0b0f1a"
C_SURFACE = "#111827"
C_CARD    = "#1a2236"
C_BORDER  = "#1e2d45"
C_ACCENT  = "#3b82f6"
C_GREEN   = "#10b981"
C_RED     = "#ef4444"
C_ORANGE  = "#f59e0b"
C_TEXT    = "#f1f5f9"
C_MUTED   = "#64748b"
C_ROW_ALT = "#141e30"

FONT_TITLE  = ("Trebuchet MS", 20, "bold")
FONT_HEAD   = ("Trebuchet MS", 14, "bold")
FONT_BODY   = ("Trebuchet MS", 12)
FONT_SMALL  = ("Trebuchet MS", 11)

CATEGORIAS = ["Todos", "Tecnología", "Electrónica"]

CAT_COLORS = {
    "Tecnología":  ("#1e3a5f", "#60a5fa"),
    "Electrónica": ("#2d1f00", "#f59e0b"),
}


class VentanaUsuario(ctk.CTk):

    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        self.sesion = Sesion.obtener()
        self.title(f"AURATEC  —  {self.sesion.nombre}")
        self.geometry("1160x700")
        self.minsize(900, 600)
        self.configure(fg_color=C_BG)
        self.carrito: dict = {}
        self._construir_interfaz()
        self._cargar_catalogo()

    # ── INTERFAZ ──────────────────────────────────────────────────────────────

    def _construir_interfaz(self):
        # Header
        header = ctk.CTkFrame(self, fg_color=C_SURFACE, corner_radius=0, height=62)
        header.pack(fill="x")
        header.pack_propagate(False)

        logo_frame = ctk.CTkFrame(header, fg_color=C_ACCENT, corner_radius=8, width=36, height=36)
        logo_frame.pack(side="left", padx=(18, 10), pady=13)
        logo_frame.pack_propagate(False)
        ctk.CTkLabel(logo_frame, text="A", font=("Trebuchet MS", 18, "bold"), text_color="white").place(relx=.5, rely=.5, anchor="center")

        ctk.CTkLabel(header, text="AURATEC", font=FONT_TITLE, text_color=C_TEXT).pack(side="left")
        ctk.CTkLabel(header, text=" / Tienda", font=FONT_BODY, text_color=C_MUTED).pack(side="left", pady=4)
        ctk.CTkLabel(header, text=f"👤 {self.sesion.nombre}", font=FONT_SMALL,
                     text_color=C_MUTED).pack(side="left", padx=14)

        ctk.CTkButton(header, text="⏻  Salir", width=90, height=34,
                      fg_color=C_RED, hover_color="#b91c1c", font=FONT_SMALL,
                      corner_radius=8, command=self._cerrar_sesion).pack(side="right", padx=18, pady=14)
        ctk.CTkButton(header, text="📋  Mis compras", width=130, height=34,
                      fg_color=C_SURFACE, hover_color=C_CARD, font=FONT_SMALL,
                      border_width=1, border_color=C_BORDER,
                      corner_radius=8, command=self._ver_historial).pack(side="right", padx=4, pady=14)

        # Cuerpo
        cuerpo = ctk.CTkFrame(self, fg_color="transparent")
        cuerpo.pack(fill="both", expand=True, padx=16, pady=12)
        cuerpo.grid_columnconfigure(0, weight=3)
        cuerpo.grid_columnconfigure(1, weight=1)
        cuerpo.grid_rowconfigure(0, weight=1)

        # Panel catálogo
        panel_cat = ctk.CTkFrame(cuerpo, fg_color=C_CARD, corner_radius=14,
                                 border_width=1, border_color=C_BORDER)
        panel_cat.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        ctk.CTkLabel(panel_cat, text="📦  Catálogo de Productos",
                     font=FONT_HEAD, text_color=C_TEXT).pack(pady=(14, 8), padx=16, anchor="w")

        # Barra búsqueda
        barra = ctk.CTkFrame(panel_cat, fg_color="transparent")
        barra.pack(fill="x", padx=14, pady=(0, 6))
        self.entry_buscar = ctk.CTkEntry(barra, placeholder_text="🔍  Buscar producto...",
                                         height=34, corner_radius=8,
                                         fg_color=C_SURFACE, border_color=C_BORDER, font=FONT_SMALL)
        self.entry_buscar.pack(side="left", fill="x", expand=True, padx=(0, 6))
        ctk.CTkButton(barra, text="Buscar", width=90, height=34, corner_radius=8,
                      fg_color=C_ACCENT, hover_color="#2563eb", font=FONT_SMALL,
                      command=self._buscar).pack(side="left", padx=(0, 4))
        ctk.CTkButton(barra, text="Ver todo", width=90, height=34, corner_radius=8,
                      fg_color=C_SURFACE, hover_color=C_BORDER, font=FONT_SMALL,
                      command=self._cargar_catalogo).pack(side="left")

        # Filtros categoría
        cat_bar = ctk.CTkFrame(panel_cat, fg_color="transparent")
        cat_bar.pack(fill="x", padx=14, pady=(0, 8))
        self.cat_btns = {}
        for cat in CATEGORIAS:
            b = ctk.CTkButton(cat_bar, text=cat, width=100, height=28, corner_radius=14,
                              font=FONT_SMALL,
                              fg_color=C_ACCENT if cat == "Todos" else C_SURFACE,
                              hover_color=C_BORDER,
                              text_color="white" if cat == "Todos" else C_MUTED,
                              command=lambda c=cat: self._filtrar_cat(c))
            b.pack(side="left", padx=3)
            self.cat_btns[cat] = b

        self.lbl_cargando = ctk.CTkLabel(panel_cat, text="", text_color=C_MUTED, font=FONT_SMALL)
        self.lbl_cargando.pack(anchor="w", padx=14)

        self.frame_catalogo = ctk.CTkScrollableFrame(panel_cat, fg_color="transparent")
        self.frame_catalogo.pack(fill="both", expand=True, padx=8, pady=(0, 10))

        self.cols_cat = {"ID": 45, "Nombre": 230, "Categoría": 130, "Precio": 90, "Stock": 65, "": 95}
        for col_i, (enc, ancho) in enumerate(self.cols_cat.items()):
            ctk.CTkLabel(self.frame_catalogo, text=enc, font=FONT_SMALL,
                         width=ancho, anchor="w", text_color=C_MUTED).grid(
                row=0, column=col_i, padx=5, pady=7)

        # Panel carrito
        panel_carrito = ctk.CTkFrame(cuerpo, fg_color=C_CARD, corner_radius=14,
                                     border_width=1, border_color=C_BORDER)
        panel_carrito.grid(row=0, column=1, sticky="nsew")

        ctk.CTkLabel(panel_carrito, text="🛒  Mi Carrito",
                     font=FONT_HEAD, text_color=C_TEXT).pack(pady=(14, 6), padx=14, anchor="w")

        self.lbl_cart_count = ctk.CTkLabel(panel_carrito, text="0 productos",
                                           font=FONT_SMALL, text_color=C_MUTED)
        self.lbl_cart_count.pack(anchor="w", padx=14)

        self.frame_carrito = ctk.CTkScrollableFrame(panel_carrito, height=300, fg_color="transparent")
        self.frame_carrito.pack(fill="x", padx=10, pady=6)

        divider = ctk.CTkFrame(panel_carrito, fg_color=C_BORDER, height=1)
        divider.pack(fill="x", padx=14, pady=4)

        total_frame = ctk.CTkFrame(panel_carrito, fg_color="transparent")
        total_frame.pack(fill="x", padx=14, pady=4)
        ctk.CTkLabel(total_frame, text="Total:", font=FONT_BODY, text_color=C_MUTED).pack(side="left")
        self.lbl_total = ctk.CTkLabel(total_frame, text="$0.00",
                                      font=("Trebuchet MS", 18, "bold"), text_color=C_GREEN)
        self.lbl_total.pack(side="right")

        ctk.CTkButton(panel_carrito, text="✅  Confirmar Compra", height=42,
                      fg_color=C_GREEN, hover_color="#059669",
                      font=("Trebuchet MS", 13, "bold"), corner_radius=10,
                      command=self._confirmar_compra).pack(fill="x", padx=14, pady=(6, 4))
        ctk.CTkButton(panel_carrito, text="🗑  Vaciar carrito", height=34,
                      fg_color=C_SURFACE, hover_color=C_BORDER, font=FONT_SMALL,
                      border_width=1, border_color=C_BORDER, corner_radius=8,
                      command=self._vaciar_carrito).pack(fill="x", padx=14, pady=(0, 8))

        self.lbl_msg = ctk.CTkLabel(panel_carrito, text="", font=FONT_SMALL,
                                    wraplength=200, text_color=C_GREEN)
        self.lbl_msg.pack(pady=4, padx=14)

    # ── CATÁLOGO ──────────────────────────────────────────────────────────────

    def _filtrar_cat(self, cat: str):
        for c, b in self.cat_btns.items():
            b.configure(fg_color=C_ACCENT if c == cat else C_SURFACE,
                        text_color="white" if c == cat else C_MUTED)
        self._cargar_catalogo(None if cat == "Todos" else cat)

    def _cargar_catalogo(self, filtro=None):
        self.lbl_cargando.configure(text="⏳ Cargando...")
        for w in self.frame_catalogo.winfo_children():
            if int(w.grid_info().get("row", 0)) > 0:
                w.destroy()
        threading.Thread(target=self._cargar_catalogo_bg, args=(filtro,), daemon=True).start()

    def _cargar_catalogo_bg(self, filtro):
        cola = listar_productos(filtro)
        self.after(0, lambda: self._renderizar_catalogo(cola))

    def _renderizar_catalogo(self, cola):
        self.lbl_cargando.configure(text="")
        if not cola:
            ctk.CTkLabel(self.frame_catalogo, text="Sin resultados.",
                         text_color=C_MUTED).grid(row=1, column=0, columnspan=6, pady=20)
            return
        anchos_cola = deque(self.cols_cat.values())
        fila = 1
        while cola:
            p = cola.popleft()
            color = C_ROW_ALT if fila % 2 == 0 else "transparent"
            col_anchos = deque(anchos_cola)
            for col_i, clave in enumerate(("id", "nombre", "categoria", "precio", "stock")):
                ancho = col_anchos.popleft()
                val = p[clave]
                if clave == "precio":
                    texto = f"${val:.2f}"
                    tc = C_TEXT
                elif clave == "categoria":
                    texto = val
                    bg_c, txt_c = CAT_COLORS.get(val, (C_SURFACE, C_MUTED))
                    ctk.CTkLabel(self.frame_catalogo, text=texto, width=ancho,
                                 anchor="w", fg_color=bg_c, text_color=txt_c,
                                 corner_radius=6, font=FONT_SMALL).grid(
                        row=fila, column=col_i, padx=5, pady=3)
                    continue
                elif clave == "stock":
                    texto = str(val)
                    tc = C_RED if val == 0 else (C_ORANGE if val <= 3 else C_GREEN)
                else:
                    texto = str(val)
                    tc = C_MUTED if clave == "id" else C_TEXT
                ctk.CTkLabel(self.frame_catalogo, text=texto, width=ancho,
                             anchor="w", fg_color=color, text_color=tc,
                             font=FONT_SMALL).grid(row=fila, column=col_i, padx=5, pady=3)

            ancho_btn = col_anchos.popleft()
            pid = p["id"]
            stock = p["stock"]
            sin_stock = stock <= 0
            ctk.CTkButton(
                self.frame_catalogo,
                text="Sin stock" if sin_stock else "+ Agregar",
                width=ancho_btn, height=28,
                fg_color="#333" if sin_stock else C_ACCENT,
                hover_color="#333" if sin_stock else "#2563eb",
                state="disabled" if sin_stock else "normal",
                font=FONT_SMALL, corner_radius=8,
                command=lambda pid=pid, nombre=p["nombre"], precio=p["precio"], stock=stock:
                    self._agregar_al_carrito(pid, nombre, precio, stock)
            ).grid(row=fila, column=5, padx=5, pady=3)
            fila += 1

    def _buscar(self):
        filtro = self.entry_buscar.get().strip()
        self._cargar_catalogo(filtro if filtro else None)

    # ── CARRITO ───────────────────────────────────────────────────────────────

    def _agregar_al_carrito(self, pid, nombre, precio, stock):
        cant = self.carrito.get(pid, {}).get("cantidad", 0)
        if cant + 1 > stock:
            self.lbl_msg.configure(text=f"Stock máximo: {stock}", text_color=C_RED)
            return
        if pid in self.carrito:
            self.carrito[pid]["cantidad"] += 1
        else:
            self.carrito[pid] = {"nombre": nombre, "precio": precio, "cantidad": 1}
        self._refrescar_carrito()
        self.lbl_msg.configure(text=f'✓ "{nombre}" agregado', text_color=C_GREEN)

    def _refrescar_carrito(self):
        for w in self.frame_carrito.winfo_children():
            w.destroy()
        total = 0.0
        for pid, item in self.carrito.items():
            subtotal = item["precio"] * item["cantidad"]
            total += subtotal
            fila_f = ctk.CTkFrame(self.frame_carrito, fg_color=C_SURFACE,
                                  corner_radius=8, border_width=1, border_color=C_BORDER)
            fila_f.pack(fill="x", pady=3, padx=2)
            ctk.CTkLabel(fila_f, text=item["nombre"], font=FONT_SMALL,
                         anchor="w", wraplength=120, text_color=C_TEXT).grid(
                row=0, column=0, padx=8, pady=6, sticky="w")
            ctk.CTkLabel(fila_f, text=f"${subtotal:.2f}",
                         font=("Trebuchet MS", 11, "bold"), text_color=C_GREEN).grid(
                row=0, column=1, padx=6)
            ctrl = ctk.CTkFrame(fila_f, fg_color="transparent")
            ctrl.grid(row=0, column=2, padx=6)
            ctk.CTkButton(ctrl, text="−", width=26, height=26, corner_radius=6,
                          fg_color=C_SURFACE, hover_color=C_BORDER,
                          command=lambda p=pid: self._cambiar_cant(p, -1)).pack(side="left", padx=2)
            ctk.CTkLabel(ctrl, text=f"x{item['cantidad']}", font=FONT_SMALL,
                         text_color=C_MUTED, width=28).pack(side="left")
            ctk.CTkButton(ctrl, text="+", width=26, height=26, corner_radius=6,
                          fg_color=C_ACCENT, hover_color="#2563eb",
                          command=lambda p=pid: self._cambiar_cant(p, 1)).pack(side="left", padx=2)

        n = sum(i["cantidad"] for i in self.carrito.values())
        self.lbl_cart_count.configure(text=f"{n} producto{'s' if n != 1 else ''}")
        self.lbl_total.configure(text=f"${total:.2f}")

    def _cambiar_cant(self, pid, delta):
        if pid in self.carrito:
            self.carrito[pid]["cantidad"] += delta
            if self.carrito[pid]["cantidad"] <= 0:
                del self.carrito[pid]
        self._refrescar_carrito()

    def _vaciar_carrito(self):
        self.carrito.clear()
        self._refrescar_carrito()
        self.lbl_msg.configure(text="Carrito vaciado.", text_color=C_MUTED)

    def _confirmar_compra(self):
        if not self.carrito:
            self.lbl_msg.configure(text="El carrito está vacío.", text_color=C_RED)
            return
        self.lbl_msg.configure(text="⏳ Procesando...", text_color=C_MUTED)
        threading.Thread(target=self._confirmar_compra_bg, daemon=True).start()

    def _confirmar_compra_bg(self):
        try:
            resultado = crear_orden(self.sesion.usuario_id, self.carrito)
            self.after(0, lambda: self._compra_exitosa(resultado))
        except (ValueError, ConnectionError) as e:
            self.after(0, lambda: self.lbl_msg.configure(text=f"⚠ {e}", text_color=C_RED))
        except Exception as e:
            self.after(0, lambda: self.lbl_msg.configure(text=f"Error: {e}", text_color=C_RED))

    def _compra_exitosa(self, resultado):
        n = len(resultado["items_ok"])
        total = resultado["total"]
        self.carrito.clear()
        self._refrescar_carrito()
        self._cargar_catalogo()
        self.lbl_msg.configure(
            text=f"✅ Compra OK: {n} producto(s) — ${total:,.2f}", text_color=C_GREEN)

    # ── HISTORIAL ─────────────────────────────────────────────────────────────

    def _ver_historial(self):
        v = ctk.CTkToplevel(self)
        v.title("Mis Compras — Historial")
        v.geometry("720x520")
        v.configure(fg_color=C_SURFACE)
        v.grab_set()

        ctk.CTkLabel(v, text="📋  Historial de Compras",
                     font=FONT_HEAD, text_color=C_TEXT).pack(pady=(18, 8))

        filtros = ctk.CTkFrame(v, fg_color=C_CARD, corner_radius=10,
                               border_width=1, border_color=C_BORDER)
        filtros.pack(fill="x", padx=16, pady=(0, 8), ipady=4)

        ctk.CTkLabel(filtros, text="Producto:", font=FONT_SMALL, text_color=C_MUTED).grid(row=0, column=0, padx=(12,4), pady=10)
        entry_prod = ctk.CTkEntry(filtros, placeholder_text="Nombre...", width=150, height=30,
                                   corner_radius=8, fg_color=C_SURFACE, border_color=C_BORDER, font=FONT_SMALL)
        entry_prod.grid(row=0, column=1, padx=(0, 8))
        ctk.CTkLabel(filtros, text="Desde:", font=FONT_SMALL, text_color=C_MUTED).grid(row=0, column=2, padx=(0,4))
        entry_desde = ctk.CTkEntry(filtros, placeholder_text="dd/mm/aaaa", width=110, height=30,
                                    corner_radius=8, fg_color=C_SURFACE, border_color=C_BORDER, font=FONT_SMALL)
        entry_desde.grid(row=0, column=3, padx=(0, 8))
        ctk.CTkLabel(filtros, text="Hasta:", font=FONT_SMALL, text_color=C_MUTED).grid(row=0, column=4, padx=(0,4))
        entry_hasta = ctk.CTkEntry(filtros, placeholder_text="dd/mm/aaaa", width=110, height=30,
                                    corner_radius=8, fg_color=C_SURFACE, border_color=C_BORDER, font=FONT_SMALL)
        entry_hasta.grid(row=0, column=5, padx=(0, 8))
        ctk.CTkButton(filtros, text="Filtrar", width=80, height=30, corner_radius=8,
                      fg_color=C_ACCENT, hover_color="#2563eb", font=FONT_SMALL,
                      command=lambda: _cargar(entry_prod.get().strip() or None,
                                              entry_desde.get().strip() or None,
                                              entry_hasta.get().strip() or None)
                      ).grid(row=0, column=6, padx=4)
        ctk.CTkButton(filtros, text="Ver todo", width=80, height=30, corner_radius=8,
                      fg_color=C_SURFACE, hover_color=C_BORDER, font=FONT_SMALL,
                      command=lambda: _cargar()).grid(row=0, column=7, padx=(0, 12))

        lbl_carg = ctk.CTkLabel(v, text="", text_color=C_MUTED, font=FONT_SMALL)
        lbl_carg.pack(anchor="w", padx=16)

        frame_scroll = ctk.CTkScrollableFrame(v, height=340, fg_color=C_CARD, corner_radius=12)
        frame_scroll.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        cols_hist = {"#Orden": 65, "Total": 90, "Estado": 90, "Ítems": 55, "Fecha": 170, "": 80}

        def _enc():
            for w in frame_scroll.winfo_children():
                w.destroy()
            for col_i, (enc, ancho) in enumerate(cols_hist.items()):
                ctk.CTkLabel(frame_scroll, text=enc, font=FONT_SMALL,
                             width=ancho, anchor="w", text_color=C_MUTED).grid(
                    row=0, column=col_i, padx=5, pady=7)

        def _render(ordenes):
            lbl_carg.configure(text="")
            _enc()
            if not ordenes:
                ctk.CTkLabel(frame_scroll, text="Sin compras registradas.",
                             text_color=C_MUTED).grid(row=1, column=0, columnspan=6, pady=20)
                return
            col_anchos = deque(cols_hist.values())
            for fila, h in enumerate(ordenes, start=1):
                color = C_ROW_ALT if fila % 2 == 0 else "transparent"
                aw = deque(col_anchos)
                for col_i, (clave, fmt) in enumerate({
                    "id": "{}", "total": "${:.2f}", "estado": "{}", "items": "{}", "fecha": "{}"
                }.items()):
                    ancho = aw.popleft()
                    ctk.CTkLabel(frame_scroll, text=fmt.format(h[clave]), width=ancho,
                                 anchor="w", fg_color=color, font=FONT_SMALL,
                                 text_color=C_TEXT).grid(row=fila, column=col_i, padx=5, pady=3)
                oid = h["id"]
                ctk.CTkButton(frame_scroll, text="Ver", width=aw.popleft(), height=26,
                              fg_color=C_ACCENT, hover_color="#2563eb", corner_radius=6,
                              font=FONT_SMALL,
                              command=lambda o=oid: mostrar_detalle_orden(v, o)
                              ).grid(row=fila, column=5, padx=5, pady=3)

        def _cargar(filtro_prod=None, desde=None, hasta=None):
            lbl_carg.configure(text="⏳ Cargando...")
            _enc()
            def _bg():
                ordenes = listar_ordenes_usuario(self.sesion.usuario_id,
                                                 filtro_producto=filtro_prod,
                                                 fecha_desde=desde, fecha_hasta=hasta)
                v.after(0, lambda: _render(ordenes))
            threading.Thread(target=_bg, daemon=True).start()

        _cargar()

    # ── SESIÓN ────────────────────────────────────────────────────────────────

    def _cerrar_sesion(self):
        Sesion.cerrar()
        self.destroy()
        from login import LoginApp
        LoginApp().mainloop()


if __name__ == '__main__':
    VentanaUsuario().mainloop()
