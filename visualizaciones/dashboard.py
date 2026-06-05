import threading
import customtkinter as ctk
from collections import deque
from sesion import Sesion
from base_de_datos.queries import (
    listar_productos, listar_usuarios, insertar_producto,
    actualizar_precio, actualizar_stock, eliminar_producto, resumen_ventas,
    listar_todas_ordenes, obtener_detalle_orden,
    crear_usuario, editar_usuario, eliminar_usuario,
    cancelar_orden,
    estadisticas_ventas_7_dias, estadisticas_por_categoria, productos_mas_vendidos
)
from visualizaciones._widgets import mostrar_detalle_orden
from visualizaciones.graficos import crear_grafico_ventas, crear_grafico_categorias

REFRESH_MS = 120_000

# ── PALETA ────────────────────────────────────────────────────────────────────
C_BG       = "#0b0f1a"
C_SURFACE  = "#111827"
C_CARD     = "#1a2236"
C_BORDER   = "#1e2d45"
C_ACCENT   = "#3b82f6"
C_ACCENT2  = "#6366f1"
C_GREEN    = "#10b981"
C_RED      = "#ef4444"
C_ORANGE   = "#f59e0b"
C_PURPLE   = "#8b5cf6"
C_TEXT     = "#f1f5f9"
C_MUTED    = "#64748b"
C_ROW_ALT  = "#141e30"

FONT_TITLE  = ("Trebuchet MS", 22, "bold")
FONT_HEAD   = ("Trebuchet MS", 14, "bold")
FONT_BODY   = ("Trebuchet MS", 12)
FONT_SMALL  = ("Trebuchet MS", 11)
FONT_METRIC = ("Trebuchet MS", 24, "bold")

CATEGORIAS = ["Todos", "Tecnología", "Electrónica"]


class VentanaAdmin(ctk.CTk):

    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        sesion = Sesion.obtener()
        self.title(f"AURATEC  ·  Panel Admin  —  {sesion.nombre}")
        self.geometry("1200x760")
        self.configure(fg_color=C_BG)
        self._filtro_cat = "Todos"
        self._construir_interfaz()
        self._actualizar_metricas()
        self._cargar_productos()
        self._programar_refresh()

    # ── HEADER ────────────────────────────────────────────────────────────────

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
        ctk.CTkLabel(header, text=" / Admin", font=FONT_BODY, text_color=C_MUTED).pack(side="left", pady=4)

        sesion = Sesion.obtener()
        ctk.CTkButton(header, text="⏻  Cerrar sesión", width=140, height=34,
                      fg_color=C_RED, hover_color="#b91c1c",
                      font=FONT_SMALL, corner_radius=8,
                      command=self._cerrar_sesion).pack(side="right", padx=18, pady=14)
        ctk.CTkLabel(header, text=f"👤 {sesion.nombre}", font=FONT_SMALL,
                     text_color=C_MUTED).pack(side="right", padx=10)

        # Indicador conexión
        dot_frame = ctk.CTkFrame(header, fg_color="transparent")
        dot_frame.pack(side="right", padx=4)
        ctk.CTkLabel(dot_frame, text="⬤", font=("Trebuchet MS", 9), text_color=C_GREEN).pack(side="left")
        ctk.CTkLabel(dot_frame, text=" Railway", font=FONT_SMALL, text_color=C_MUTED).pack(side="left")

        # Métricas
        self.frame_metricas = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_metricas.pack(fill="x", padx=20, pady=(16, 8))
        self.metricas_labels = {}
        cards = [
            ("💰", "Ingresos",   C_GREEN,  "este mes"),
            ("🛒", "Ventas",     C_ACCENT, "órdenes"),
            ("📦", "Productos",  C_PURPLE, "en catálogo"),
            ("👥", "Usuarios",   C_ORANGE, "registrados"),
        ]
        for col, (ico, titulo, color, sub) in enumerate(cards):
            self.frame_metricas.grid_columnconfigure(col, weight=1)
            card = ctk.CTkFrame(self.frame_metricas, fg_color=C_CARD,
                                corner_radius=14, border_width=1, border_color=C_BORDER)
            card.grid(row=0, column=col, padx=6, sticky="ew", ipady=6)

            accent_bar = ctk.CTkFrame(card, fg_color=color, height=3, corner_radius=2)
            accent_bar.pack(fill="x", padx=0, pady=(0, 8))

            ctk.CTkLabel(card, text=f"{ico}  {titulo}", font=FONT_SMALL,
                         text_color=C_MUTED).pack(padx=14, anchor="w")
            lbl = ctk.CTkLabel(card, text="—", font=FONT_METRIC, text_color=C_TEXT)
            lbl.pack(padx=14, anchor="w")
            ctk.CTkLabel(card, text=sub, font=("Trebuchet MS", 10),
                         text_color=C_MUTED).pack(padx=14, anchor="w", pady=(0, 10))
            self.metricas_labels[titulo] = lbl

        # Tabs
        tab_bar = ctk.CTkFrame(self, fg_color=C_SURFACE, corner_radius=0, height=46)
        tab_bar.pack(fill="x")
        tab_bar.pack_propagate(False)
        self.btn_tabs = {}
<<<<<<< HEAD
        for texto, cmd in [("📊 Dashboard", self._mostrar_tab_stats),
                           ("📦 Productos", self._mostrar_tab_productos),
                           ("🧾 Órdenes",   self._mostrar_tab_ordenes),
                           ("👥 Usuarios",  self._mostrar_tab_usuarios)]:
            b = ctk.CTkButton(tab_bar, text=texto, width=150,
                              fg_color="#555", hover_color="#333", command=cmd)
            b.pack(side="left", padx=4)
=======
        for texto, cmd in [("📦  Productos", self._mostrar_tab_productos),
                           ("🧾  Órdenes",   self._mostrar_tab_ordenes),
                           ("👥  Usuarios",  self._mostrar_tab_usuarios)]:
            b = ctk.CTkButton(tab_bar, text=texto, width=160, height=36,
                              fg_color="transparent", hover_color=C_CARD,
                              text_color=C_MUTED, font=FONT_SMALL,
                              corner_radius=0, command=cmd)
            b.pack(side="left", padx=2)
>>>>>>> d871b64 (mejoras UI: panel admin y usuario)
            self.btn_tabs[texto] = b

        self.frame_tab = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_tab.pack(fill="both", expand=True, padx=20, pady=12)

        self._construir_tab_stats()
        self._construir_tab_productos()
        self._construir_tab_ordenes()
        self._construir_tab_usuarios()
        self._mostrar_tab_stats()

    def _activar_tab(self, nombre: str):
        for k, b in self.btn_tabs.items():
            if k == nombre:
                b.configure(fg_color=C_CARD, text_color=C_ACCENT,
                            border_width=0)
            else:
                b.configure(fg_color="transparent", text_color=C_MUTED)

    # ── TAB PRODUCTOS ─────────────────────────────────────────────────────────

    def _construir_tab_productos(self):
        self.tab_productos = ctk.CTkFrame(self.frame_tab, fg_color="transparent")

        # Barra de acciones
        acc = ctk.CTkFrame(self.tab_productos, fg_color=C_CARD,
                           corner_radius=10, border_width=1, border_color=C_BORDER)
        acc.pack(fill="x", pady=(0, 8), ipady=6)

        self.prod_entry_buscar = ctk.CTkEntry(acc, placeholder_text="🔍  Buscar producto...",
                                              width=220, height=32, corner_radius=8,
                                              fg_color=C_SURFACE, border_color=C_BORDER,
                                              font=FONT_SMALL)
        self.prod_entry_buscar.pack(side="left", padx=(12, 4), pady=8)

        ctk.CTkButton(acc, text="Buscar", width=80, height=32, corner_radius=8,
                      fg_color=C_ACCENT, hover_color="#2563eb", font=FONT_SMALL,
                      command=self._buscar_productos).pack(side="left", padx=4)
        ctk.CTkButton(acc, text="Ver todo", width=80, height=32, corner_radius=8,
                      fg_color=C_SURFACE, hover_color=C_BORDER, font=FONT_SMALL,
                      command=lambda: self._cargar_productos()).pack(side="left", padx=(0, 12))

        # Filtros categoría
        self.cat_btns_admin = {}
        for cat in CATEGORIAS:
            b = ctk.CTkButton(acc, text=cat, width=100, height=28, corner_radius=14,
                              font=FONT_SMALL,
                              fg_color=C_ACCENT if cat == "Todos" else C_SURFACE,
                              hover_color=C_BORDER,
                              text_color="white" if cat == "Todos" else C_MUTED,
                              command=lambda c=cat: self._filtrar_cat_admin(c))
            b.pack(side="left", padx=3)
            self.cat_btns_admin[cat] = b

        # Botones CRUD
        ctk.CTkButton(acc, text="➕ Añadir", width=100, height=32, corner_radius=8,
                      fg_color=C_GREEN, hover_color="#059669", font=FONT_SMALL,
                      command=self._agregar_producto).pack(side="right", padx=4)
        ctk.CTkButton(acc, text="✏️ Precio", width=100, height=32, corner_radius=8,
                      fg_color=C_ORANGE, hover_color="#d97706", font=FONT_SMALL,
                      command=self._modificar_precio).pack(side="right", padx=4)
        ctk.CTkButton(acc, text="📦 Stock", width=100, height=32, corner_radius=8,
                      fg_color=C_ACCENT2, hover_color="#4f46e5", font=FONT_SMALL,
                      command=self._modificar_stock).pack(side="right", padx=4)
        ctk.CTkButton(acc, text="🗑 Eliminar", width=100, height=32, corner_radius=8,
                      fg_color=C_RED, hover_color="#b91c1c", font=FONT_SMALL,
                      command=self._eliminar_producto).pack(side="right", padx=4)

        self.lbl_cargando_prod = ctk.CTkLabel(self.tab_productos, text="",
                                              text_color=C_MUTED, font=FONT_SMALL)
        self.lbl_cargando_prod.pack(anchor="w", padx=4)

        self.frame_tabla = ctk.CTkScrollableFrame(self.tab_productos, height=400,
                                                   fg_color=C_CARD, corner_radius=12)
        self.frame_tabla.pack(fill="both", expand=True)

        self.columnas = {"ID": 50, "Nombre": 260, "Categoría": 160, "Precio": 100, "Stock": 80}
        for col_i, (enc, ancho) in enumerate(self.columnas.items()):
            ctk.CTkLabel(self.frame_tabla, text=enc, font=FONT_SMALL,
                         width=ancho, anchor="w",
                         text_color=C_MUTED).grid(row=0, column=col_i, padx=8, pady=8)

    def _filtrar_cat_admin(self, cat: str):
        self._filtro_cat = cat
        for c, b in self.cat_btns_admin.items():
            b.configure(fg_color=C_ACCENT if c == cat else C_SURFACE,
                        text_color="white" if c == cat else C_MUTED)
        filtro = None if cat == "Todos" else cat
        self._cargar_productos(filtro)

    def _mostrar_tab_productos(self):
        self.tab_stats.pack_forget()
        self.tab_ordenes.pack_forget()
        self.tab_usuarios.pack_forget()
        self.tab_productos.pack(fill="both", expand=True)
        self._activar_tab("📦  Productos")

    def _mostrar_tab_stats(self):
        self.tab_productos.pack_forget()
        self.tab_ordenes.pack_forget()
        self.tab_usuarios.pack_forget()
        self.tab_stats.pack(fill="both", expand=True)
        self._activar_tab("📊 Dashboard")
        self._actualizar_graficos()

    def _construir_tab_stats(self):
        self.tab_stats = ctk.CTkFrame(self.frame_tab, fg_color="transparent")
        
        # Contenedor de gráficos
        self.frame_charts = ctk.CTkFrame(self.tab_stats, fg_color="transparent")
        self.frame_charts.pack(fill="both", expand=True)
        
        self.frame_charts.grid_columnconfigure(0, weight=1)
        self.frame_charts.grid_columnconfigure(1, weight=1)
        self.frame_charts.grid_rowconfigure(0, weight=1)
        
        self.chart_ventas_container = ctk.CTkFrame(self.frame_charts, fg_color="#2b2b2b", corner_radius=12)
        self.chart_ventas_container.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.chart_cat_container = ctk.CTkFrame(self.frame_charts, fg_color="#2b2b2b", corner_radius=12)
        self.chart_cat_container.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # Ranking de productos
        self.frame_ranking = ctk.CTkFrame(self.tab_stats, fg_color="#1a1a2e", corner_radius=12, height=150)
        self.frame_ranking.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(self.frame_ranking, text="🏆 Top 5 Productos más Vendidos", font=("Arial", 14, "bold")).pack(pady=10)
        self.ranking_container = ctk.CTkFrame(self.frame_ranking, fg_color="transparent")
        self.ranking_container.pack(fill="x", padx=20, pady=(0, 15))

    def _actualizar_graficos(self):
        # Limpiar contenedores
        for w in self.chart_ventas_container.winfo_children(): w.destroy()
        for w in self.chart_cat_container.winfo_children(): w.destroy()
        for w in self.ranking_container.winfo_children(): w.destroy()
        
        # Obtener datos
        datos_ventas = estadisticas_ventas_7_dias()
        datos_cat = estadisticas_por_categoria()
        top_productos = productos_mas_vendidos()
        
        if datos_ventas:
            crear_grafico_ventas(self.chart_ventas_container, datos_ventas).pack(fill="both", expand=True, padx=5, pady=5)
        else:
            ctk.CTkLabel(self.chart_ventas_container, text="No hay datos de ventas recientes").pack(expand=True)
            
        if datos_cat:
            crear_grafico_categorias(self.chart_cat_container, datos_cat).pack(fill="both", expand=True, padx=5, pady=5)
        else:
            ctk.CTkLabel(self.chart_cat_container, text="No hay datos por categoría").pack(expand=True)
            
        # Actualizar ranking
        for i, p in enumerate(top_productos):
            row = ctk.CTkFrame(self.ranking_container, fg_color="transparent")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=f"{i+1}. {p['nombre']}", font=("Arial", 12)).pack(side="left")
            ctk.CTkLabel(row, text=f"{p['cantidad']} unidades", font=("Arial", 12, "bold"), text_color="#16a085").pack(side="right")

    def _buscar_productos(self):
        filtro = self.prod_entry_buscar.get().strip()
        self._cargar_productos(filtro if filtro else None)

    # ── TAB ÓRDENES ───────────────────────────────────────────────────────────

    def _construir_tab_ordenes(self):
        self.tab_ordenes = ctk.CTkFrame(self.frame_tab, fg_color="transparent")

        filtros = ctk.CTkFrame(self.tab_ordenes, fg_color=C_CARD,
                               corner_radius=10, border_width=1, border_color=C_BORDER)
        filtros.pack(fill="x", pady=(0, 8), ipady=4)

        for col, (label, attr, ph) in enumerate([
            ("Usuario", "ord_entry_usr", "Nombre o @login"),
            ("Producto", "ord_entry_prod", "Nombre..."),
            ("Desde",   "ord_entry_desde", "dd/mm/aaaa"),
            ("Hasta",   "ord_entry_hasta", "dd/mm/aaaa"),
        ]):
            ctk.CTkLabel(filtros, text=label+":", font=FONT_SMALL,
                         text_color=C_MUTED).grid(row=0, column=col*2, padx=(12 if col==0 else 6, 4), pady=10)
            e = ctk.CTkEntry(filtros, placeholder_text=ph, width=130, height=30,
                             corner_radius=8, fg_color=C_SURFACE, border_color=C_BORDER, font=FONT_SMALL)
            e.grid(row=0, column=col*2+1, padx=(0, 4), pady=10)
            setattr(self, attr, e)

        ctk.CTkButton(filtros, text="Filtrar", width=80, height=30, corner_radius=8,
                      fg_color=C_ACCENT, hover_color="#2563eb", font=FONT_SMALL,
                      command=self._buscar_ordenes).grid(row=0, column=8, padx=6)
        ctk.CTkButton(filtros, text="Ver todo", width=80, height=30, corner_radius=8,
                      fg_color=C_SURFACE, hover_color=C_BORDER, font=FONT_SMALL,
                      command=self._cargar_ordenes).grid(row=0, column=9, padx=(0, 12))

        self.lbl_cargando_ord = ctk.CTkLabel(self.tab_ordenes, text="",
                                             text_color=C_MUTED, font=FONT_SMALL)
        self.lbl_cargando_ord.pack(anchor="w", padx=4)

        self.frame_ordenes = ctk.CTkScrollableFrame(self.tab_ordenes, height=400,
                                                     fg_color=C_CARD, corner_radius=12)
        self.frame_ordenes.pack(fill="both", expand=True)

        self.cols_ord = {"#": 55, "Usuario": 150, "Login": 100, "Total": 90,
                         "Estado": 90, "Ítems": 50, "Fecha": 150, "": 75, " ": 80}
        for col_i, (enc, ancho) in enumerate(self.cols_ord.items()):
            ctk.CTkLabel(self.frame_ordenes, text=enc, font=FONT_SMALL,
                         width=ancho, anchor="w", text_color=C_MUTED).grid(
                row=0, column=col_i, padx=5, pady=8)

    def _mostrar_tab_ordenes(self):
        self.tab_productos.pack_forget()
        self.tab_usuarios.pack_forget()
        self.tab_ordenes.pack(fill="both", expand=True)
        self._activar_tab("🧾  Órdenes")
        self._cargar_ordenes()

    def _cargar_ordenes(self, **kwargs):
        self.lbl_cargando_ord.configure(text="⏳ Cargando órdenes...")
        threading.Thread(target=self._cargar_ordenes_bg, kwargs=kwargs, daemon=True).start()

    def _cargar_ordenes_bg(self, **kwargs):
        ordenes = listar_todas_ordenes(**kwargs)
        self.after(0, lambda: self._renderizar_ordenes(ordenes))

    def _renderizar_ordenes(self, ordenes):
        self.lbl_cargando_ord.configure(text="")
        for w in self.frame_ordenes.winfo_children():
            if int(w.grid_info().get("row", 0)) > 0:
                w.destroy()
        if not ordenes:
            ctk.CTkLabel(self.frame_ordenes, text="Sin órdenes registradas.",
                         text_color=C_MUTED).grid(row=1, column=0, columnspan=9, pady=20)
            return
        col_anchos = deque(self.cols_ord.values())
        for fila, o in enumerate(ordenes, start=1):
            color = C_ROW_ALT if fila % 2 == 0 else "transparent"
            aw = deque(col_anchos)
            for col_i, (clave, fmt) in enumerate({
                "id": "{}", "usuario_nombre": "{}", "usuario_login": "@{}",
                "total": "${:.2f}", "estado": "{}", "items": "{}", "fecha": "{}"
            }.items()):
                ancho = aw.popleft()
                texto = fmt.format(o[clave])
                tc = C_RED if o["estado"] == "cancelada" else C_TEXT
                ctk.CTkLabel(self.frame_ordenes, text=texto, width=ancho,
                             anchor="w", fg_color=color, text_color=tc,
                             font=FONT_SMALL).grid(row=fila, column=col_i, padx=5, pady=3)
            oid = o["id"]
            ctk.CTkButton(self.frame_ordenes, text="Detalle", width=aw.popleft(), height=26,
                          fg_color=C_ACCENT, hover_color="#2563eb", font=FONT_SMALL, corner_radius=6,
                          command=lambda o=oid: mostrar_detalle_orden(self, o)
                          ).grid(row=fila, column=7, padx=4, pady=2)
            estado = o["estado"]
            ctk.CTkButton(self.frame_ordenes, text="Cancelar", width=aw.popleft(), height=26,
                          fg_color=C_RED if estado != "cancelada" else "#333",
                          hover_color="#b91c1c", font=FONT_SMALL, corner_radius=6,
                          state="normal" if estado != "cancelada" else "disabled",
                          command=lambda o=oid: self._cancelar_orden(o)
                          ).grid(row=fila, column=8, padx=4, pady=2)

    def _buscar_ordenes(self):
        self._cargar_ordenes(
            filtro_usuario=self.ord_entry_usr.get().strip() or None,
            filtro_producto=self.ord_entry_prod.get().strip() or None,
            fecha_desde=self.ord_entry_desde.get().strip() or None,
            fecha_hasta=self.ord_entry_hasta.get().strip() or None,
        )

    def _cancelar_orden(self, orden_id: int):
        v = ctk.CTkToplevel(self)
        v.title("Confirmar cancelación")
        v.geometry("380x170")
        v.configure(fg_color=C_SURFACE)
        v.grab_set()
        ctk.CTkLabel(v, text=f"¿Cancelar la orden #{orden_id}?\nSe devolverá el stock de los productos.",
                     font=FONT_BODY, wraplength=320, text_color=C_TEXT).pack(pady=(22, 8))
        lbl = ctk.CTkLabel(v, text="", text_color=C_RED, font=FONT_SMALL)
        lbl.pack()
        def confirmar():
            try:
                cancelar_orden(orden_id)
                v.destroy()
                self._cargar_ordenes()
                self._actualizar_metricas()
                self._cargar_productos()
            except Exception as e:
                lbl.configure(text=str(e))
        btns = ctk.CTkFrame(v, fg_color="transparent")
        btns.pack(pady=10)
        ctk.CTkButton(btns, text="Sí, cancelar", fg_color=C_RED, hover_color="#b91c1c",
                      corner_radius=8, command=confirmar).pack(side="left", padx=8)
        ctk.CTkButton(btns, text="No", fg_color=C_SURFACE, hover_color=C_BORDER,
                      border_width=1, border_color=C_BORDER,
                      corner_radius=8, command=v.destroy).pack(side="left", padx=8)

    # ── TAB USUARIOS ──────────────────────────────────────────────────────────

    def _construir_tab_usuarios(self):
        self.tab_usuarios = ctk.CTkFrame(self.frame_tab, fg_color="transparent")
        acc_u = ctk.CTkFrame(self.tab_usuarios, fg_color=C_CARD,
                             corner_radius=10, border_width=1, border_color=C_BORDER)
        acc_u.pack(fill="x", pady=(0, 8), ipady=4)
        ctk.CTkButton(acc_u, text="➕ Nuevo", width=130, height=32, corner_radius=8,
                      fg_color=C_GREEN, hover_color="#059669", font=FONT_SMALL,
                      command=self._nuevo_usuario).pack(side="left", padx=(12, 4), pady=8)
        ctk.CTkButton(acc_u, text="✏️ Editar", width=130, height=32, corner_radius=8,
                      fg_color=C_ACCENT, hover_color="#2563eb", font=FONT_SMALL,
                      command=self._editar_usuario_ui).pack(side="left", padx=4)
        ctk.CTkButton(acc_u, text="🗑 Eliminar", width=130, height=32, corner_radius=8,
                      fg_color=C_RED, hover_color="#b91c1c", font=FONT_SMALL,
                      command=self._eliminar_usuario_ui).pack(side="left", padx=4)

        self.lbl_cargando_usr = ctk.CTkLabel(self.tab_usuarios, text="",
                                             text_color=C_MUTED, font=FONT_SMALL)
        self.lbl_cargando_usr.pack(anchor="w", padx=4)

        self.frame_usuarios = ctk.CTkScrollableFrame(self.tab_usuarios, height=400,
                                                      fg_color=C_CARD, corner_radius=12)
        self.frame_usuarios.pack(fill="both", expand=True)

        self.cols_usr = {"ID": 50, "Nombre": 240, "Usuario": 200, "Rol": 80}
        for col_i, (enc, ancho) in enumerate(self.cols_usr.items()):
            ctk.CTkLabel(self.frame_usuarios, text=enc, font=FONT_SMALL,
                         width=ancho, anchor="w", text_color=C_MUTED).grid(
                row=0, column=col_i, padx=8, pady=8)

    def _mostrar_tab_usuarios(self):
        self.tab_productos.pack_forget()
        self.tab_ordenes.pack_forget()
        self.tab_usuarios.pack(fill="both", expand=True)
        self._activar_tab("👥  Usuarios")
        self._cargar_usuarios_tabla()

    def _cargar_usuarios_tabla(self):
        self.lbl_cargando_usr.configure(text="⏳ Cargando usuarios...")
        threading.Thread(target=self._cargar_usuarios_bg, daemon=True).start()

    def _cargar_usuarios_bg(self):
        cola_u = listar_usuarios()
        self.after(0, lambda: self._renderizar_usuarios(cola_u))

    def _renderizar_usuarios(self, cola_u):
        self.lbl_cargando_usr.configure(text="")
        for w in self.frame_usuarios.winfo_children():
            if int(w.grid_info().get("row", 0)) > 0:
                w.destroy()
        fila = 1
        while cola_u:
            u = cola_u.popleft()
            color = C_ROW_ALT if fila % 2 == 0 else "transparent"
            col_anchos = deque(self.cols_usr.values())
            for col_i, clave in enumerate(("id", "nombre", "usuario", "rol")):
                ancho = col_anchos.popleft()
                tc = C_ACCENT if clave == "rol" and u[clave] == "admin" else C_TEXT
                ctk.CTkLabel(self.frame_usuarios, text=str(u[clave]), width=ancho,
                             anchor="w", fg_color=color, text_color=tc,
                             font=FONT_SMALL).grid(row=fila, column=col_i, padx=8, pady=4)
            fila += 1

    # ── DATOS ─────────────────────────────────────────────────────────────────

    def _actualizar_metricas(self):
        threading.Thread(target=self._actualizar_metricas_bg, daemon=True).start()

    def _actualizar_metricas_bg(self):
        datos = resumen_ventas()
        self.after(0, lambda: self._renderizar_metricas(datos))

    def _renderizar_metricas(self, datos):
        mapeo = {
            "Ingresos":   f"${datos['ingresos']:,.2f}",
            "Ventas":     str(datos["total_ventas"]),
            "Productos":  str(datos["productos"]),
            "Usuarios":   str(datos["usuarios"]),
        }
        for titulo, valor in mapeo.items():
            self.metricas_labels[titulo].configure(text=valor)
        
        # Alertas de stock
        if datos.get("bajo_stock", 0) > 0:
            self.metricas_labels["📦 Productos"].configure(text_color="#e74c3c")
        else:
            self.metricas_labels["📦 Productos"].configure(text_color="white")

    def _programar_refresh(self):
        self._actualizar_metricas()
        self.after(REFRESH_MS, self._programar_refresh)

    def _cargar_productos(self, filtro=None):
        self.lbl_cargando_prod.configure(text="⏳ Cargando productos...")
        threading.Thread(target=self._cargar_productos_bg, args=(filtro,), daemon=True).start()

    def _cargar_productos_bg(self, filtro):
        cola = listar_productos(filtro)
        self.after(0, lambda: self._renderizar_productos(cola))

    def _renderizar_productos(self, cola):
        self.lbl_cargando_prod.configure(text="")
        for w in self.frame_tabla.winfo_children():
            if int(w.grid_info().get("row", 0)) > 0:
                w.destroy()
        anchos_cola = deque(self.columnas.values())
        fila = 1
        while cola:
            p = cola.popleft()
            color = C_ROW_ALT if fila % 2 == 0 else "transparent"
            vals = deque([p["id"], p["nombre"], p["categoria"], p["precio"], p["stock"]])
            col_anchos = deque(anchos_cola)
            col_i = 0
            while vals:
                val   = vals.popleft()
                ancho = col_anchos.popleft()
                texto = f"${val:.2f}" if col_i == 3 else str(val)
                tc = C_RED if col_i == 4 and val == 0 else C_TEXT
                ctk.CTkLabel(self.frame_tabla, text=texto, width=ancho,
                             anchor="w", fg_color=color, text_color=tc,
                             font=FONT_SMALL).grid(row=fila, column=col_i, padx=8, pady=3)
                col_i += 1
            fila += 1
        if fila == 1:
            ctk.CTkLabel(self.frame_tabla, text="Sin productos registrados.",
                         text_color=C_MUTED).grid(row=1, column=0, columnspan=5, pady=20)

    # ── FORMULARIOS PRODUCTOS ─────────────────────────────────────────────────

    def _popup(self, titulo: str, w: int = 420, h: int = 360) -> ctk.CTkToplevel:
        v = ctk.CTkToplevel(self)
        v.title(titulo)
        v.geometry(f"{w}x{h}")
        v.configure(fg_color=C_SURFACE)
        v.grab_set()
        ctk.CTkLabel(v, text=titulo, font=FONT_HEAD, text_color=C_TEXT).pack(pady=(20, 10))
        return v

    def _agregar_producto(self):
        v = self._popup("➕  Agregar Producto", 440, 440)
        entries = {}
        for campo in ("Nombre", "Precio", "Stock"):
            ctk.CTkLabel(v, text=campo+":", font=FONT_SMALL, text_color=C_MUTED).pack(anchor="w", padx=30)
            e = ctk.CTkEntry(v, width=370, height=34, corner_radius=8,
                             fg_color=C_CARD, border_color=C_BORDER, font=FONT_BODY)
            e.pack(pady=(0, 8))
            entries[campo] = e

        ctk.CTkLabel(v, text="Categoría:", font=FONT_SMALL, text_color=C_MUTED).pack(anchor="w", padx=30)
        cat_var = ctk.StringVar(value="Tecnología")
        ctk.CTkOptionMenu(v, values=["Tecnología", "Electrónica"],
                          variable=cat_var, width=370, height=34,
                          fg_color=C_CARD, button_color=C_ACCENT,
                          font=FONT_BODY).pack(pady=(0, 8))

        lbl = ctk.CTkLabel(v, text="", text_color=C_RED, font=FONT_SMALL)
        lbl.pack()

        def guardar():
            try:
                insertar_producto({
                    "nombre":    entries["Nombre"].get().strip(),
                    "categoria": cat_var.get(),
                    "precio":    float(entries["Precio"].get()),
                    "stock":     int(entries["Stock"].get()),
                })
                v.destroy()
                self._cargar_productos()
                self._actualizar_metricas()
            except Exception as e:
                lbl.configure(text=f"Error: {e}")

        ctk.CTkButton(v, text="Guardar", width=370, height=38, corner_radius=8,
                      fg_color=C_GREEN, hover_color="#059669", font=FONT_BODY,
                      command=guardar).pack(pady=12)

    def _modificar_precio(self):
        v = self._popup("✏️  Modificar Precio", 380, 240)
        ctk.CTkLabel(v, text="ID del producto:", font=FONT_SMALL, text_color=C_MUTED).pack(anchor="w", padx=30)
        e_id = ctk.CTkEntry(v, width=310, height=34, corner_radius=8,
                            fg_color=C_CARD, border_color=C_BORDER, font=FONT_BODY)
        e_id.pack(pady=(0, 8))
        ctk.CTkLabel(v, text="Nuevo precio ($):", font=FONT_SMALL, text_color=C_MUTED).pack(anchor="w", padx=30)
        e_precio = ctk.CTkEntry(v, width=310, height=34, corner_radius=8,
                                fg_color=C_CARD, border_color=C_BORDER, font=FONT_BODY)
        e_precio.pack(pady=(0, 8))
        lbl = ctk.CTkLabel(v, text="", text_color=C_RED, font=FONT_SMALL)
        lbl.pack()
        def guardar():
            try:
                actualizar_precio(int(e_id.get()), float(e_precio.get()))
                v.destroy(); self._cargar_productos()
            except Exception as e:
                lbl.configure(text=f"Error: {e}")
        ctk.CTkButton(v, text="Actualizar", width=310, height=36, corner_radius=8,
                      fg_color=C_ORANGE, hover_color="#d97706", font=FONT_BODY,
                      command=guardar).pack(pady=8)

    def _modificar_stock(self):
        v = self._popup("📦  Modificar Stock", 380, 240)
        ctk.CTkLabel(v, text="ID del producto:", font=FONT_SMALL, text_color=C_MUTED).pack(anchor="w", padx=30)
        e_id = ctk.CTkEntry(v, width=310, height=34, corner_radius=8,
                            fg_color=C_CARD, border_color=C_BORDER, font=FONT_BODY)
        e_id.pack(pady=(0, 8))
        ctk.CTkLabel(v, text="Nuevo stock:", font=FONT_SMALL, text_color=C_MUTED).pack(anchor="w", padx=30)
        e_stock = ctk.CTkEntry(v, width=310, height=34, corner_radius=8,
                               fg_color=C_CARD, border_color=C_BORDER, font=FONT_BODY)
        e_stock.pack(pady=(0, 8))
        lbl = ctk.CTkLabel(v, text="", text_color=C_RED, font=FONT_SMALL)
        lbl.pack()
        def guardar():
            try:
                actualizar_stock(int(e_id.get()), int(e_stock.get()))
                v.destroy(); self._cargar_productos()
            except Exception as e:
                lbl.configure(text=f"Error: {e}")
        ctk.CTkButton(v, text="Actualizar", width=310, height=36, corner_radius=8,
                      fg_color=C_ACCENT2, hover_color="#4f46e5", font=FONT_BODY,
                      command=guardar).pack(pady=8)

    def _eliminar_producto(self):
        v = self._popup("🗑  Eliminar Producto", 380, 200)
        ctk.CTkLabel(v, text="ID del producto a eliminar:", font=FONT_SMALL, text_color=C_MUTED).pack(anchor="w", padx=30)
        e_id = ctk.CTkEntry(v, width=310, height=34, corner_radius=8,
                            fg_color=C_CARD, border_color=C_BORDER, font=FONT_BODY)
        e_id.pack(pady=(0, 8))
        lbl = ctk.CTkLabel(v, text="", text_color=C_RED, font=FONT_SMALL)
        lbl.pack()
        def eliminar():
            try:
                eliminar_producto(int(e_id.get()))
                v.destroy(); self._cargar_productos(); self._actualizar_metricas()
            except Exception as e:
                lbl.configure(text=f"Error: {e}")
        ctk.CTkButton(v, text="Eliminar", width=310, height=36, corner_radius=8,
                      fg_color=C_RED, hover_color="#b91c1c", font=FONT_BODY,
                      command=eliminar).pack(pady=8)

    # ── FORMULARIOS USUARIOS ──────────────────────────────────────────────────

    def _form_usuario(self, titulo, defaults=None, on_guardar=None):
        v = ctk.CTkToplevel(self)
        v.title(titulo)
        v.geometry("440x460")
        v.configure(fg_color=C_SURFACE)
        v.grab_set()
        defaults = defaults or {}
        ctk.CTkLabel(v, text=titulo, font=FONT_HEAD, text_color=C_TEXT).pack(pady=(20, 10))
        entries = {}
        for campo, ph in [("Nombre completo", ""), ("Nombre de usuario", ""), ("Contraseña", "Dejar vacío para no cambiar")]:
            ctk.CTkLabel(v, text=campo+":", font=FONT_SMALL, text_color=C_MUTED).pack(anchor="w", padx=30)
            e = ctk.CTkEntry(v, width=370, height=34, corner_radius=8,
                             fg_color=C_CARD, border_color=C_BORDER, font=FONT_BODY,
                             show="*" if campo == "Contraseña" else "",
                             placeholder_text=ph)
            if campo in defaults:
                e.insert(0, defaults[campo])
            e.pack(pady=(0, 8))
            entries[campo] = e
        ctk.CTkLabel(v, text="Rol:", font=FONT_SMALL, text_color=C_MUTED).pack(anchor="w", padx=30)
        rol_var = ctk.StringVar(value=defaults.get("Rol", "user"))
        frame_rol = ctk.CTkFrame(v, fg_color="transparent")
        frame_rol.pack(anchor="w", padx=30, pady=(0, 8))
        ctk.CTkRadioButton(frame_rol, text="Usuario", variable=rol_var, value="user",
                           font=FONT_SMALL).pack(side="left", padx=(0, 16))
        ctk.CTkRadioButton(frame_rol, text="Admin", variable=rol_var, value="admin",
                           font=FONT_SMALL).pack(side="left")
        lbl = ctk.CTkLabel(v, text="", text_color=C_RED, font=FONT_SMALL)
        lbl.pack()
        def guardar():
            try:
                on_guardar(entries["Nombre completo"].get(),
                           entries["Nombre de usuario"].get(),
                           entries["Contraseña"].get(), rol_var.get())
                v.destroy(); self._cargar_usuarios_tabla(); self._actualizar_metricas()
            except Exception as e:
                lbl.configure(text=f"Error: {e}")
        ctk.CTkButton(v, text="Guardar", width=370, height=38, corner_radius=8,
                      fg_color=C_GREEN, hover_color="#059669", font=FONT_BODY,
                      command=guardar).pack(pady=12)

    def _nuevo_usuario(self):
        def on_guardar(nombre, usuario, pw, rol):
            if not pw: raise ValueError("La contraseña es obligatoria.")
            crear_usuario(nombre, usuario, pw, rol)
        self._form_usuario("➕  Nuevo Usuario", on_guardar=on_guardar)

    def _editar_usuario_ui(self):
        v = self._popup("✏️  Editar — Seleccionar ID", 360, 180)
        e_id = ctk.CTkEntry(v, width=290, height=34, corner_radius=8,
                            fg_color=C_CARD, border_color=C_BORDER, font=FONT_BODY)
        e_id.pack(pady=(0, 8))
        lbl = ctk.CTkLabel(v, text="", text_color=C_RED, font=FONT_SMALL)
        lbl.pack()
        def abrir():
            try:
                uid = int(e_id.get())
                from base_de_datos.queries import listar_usuarios
                usuarios = listar_usuarios()
                u = next((x for x in usuarios if x["id"] == uid), None)
                if not u: lbl.configure(text=f"No existe usuario con ID {uid}."); return
                v.destroy()
                def on_guardar(nombre, usuario, pw, rol):
                    editar_usuario(uid, nombre, usuario, rol, pw if pw.strip() else None)
                self._form_usuario(f"✏️  Editar Usuario #{uid}",
                    defaults={"Nombre completo": u["nombre"], "Nombre de usuario": u["usuario"], "Rol": u["rol"]},
                    on_guardar=on_guardar)
            except ValueError as e:
                lbl.configure(text=str(e))
        ctk.CTkButton(v, text="Continuar", width=290, height=36, corner_radius=8,
                      fg_color=C_ACCENT, hover_color="#2563eb", font=FONT_BODY,
                      command=abrir).pack(pady=8)

    def _eliminar_usuario_ui(self):
        v = self._popup("🗑  Eliminar Usuario", 380, 220)
        e_id = ctk.CTkEntry(v, width=310, height=34, corner_radius=8,
                            fg_color=C_CARD, border_color=C_BORDER, font=FONT_BODY)
        e_id.pack(pady=(0, 4))
        ctk.CTkLabel(v, text="No puedes eliminar tu propia cuenta.",
                     font=("Trebuchet MS", 10), text_color=C_MUTED).pack()
        lbl_err = ctk.CTkLabel(v, text="", text_color=C_RED, font=FONT_SMALL)
        lbl_err.pack(pady=4)
        def eliminar():
            try:
                uid = int(e_id.get())
                if uid == Sesion.obtener().usuario_id:
                    lbl_err.configure(text="No puedes eliminar tu propia cuenta."); return
                eliminar_usuario(uid)
                v.destroy(); self._cargar_usuarios_tabla(); self._actualizar_metricas()
            except Exception as e:
                lbl_err.configure(text=f"Error: {e}")
        ctk.CTkButton(v, text="Eliminar", width=310, height=36, corner_radius=8,
                      fg_color=C_RED, hover_color="#b91c1c", font=FONT_BODY,
                      command=eliminar).pack(pady=8)

    # ── SESIÓN ────────────────────────────────────────────────────────────────

    def _cerrar_sesion(self):
        Sesion.cerrar()
        self.destroy()
        from login import LoginApp
        LoginApp().mainloop()
