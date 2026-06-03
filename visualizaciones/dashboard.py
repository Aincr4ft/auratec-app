import customtkinter as ctk
from collections import deque
from sesion import Sesion
from base_de_datos.queries import (
    listar_productos, listar_usuarios, insertar_producto,
    actualizar_precio, eliminar_producto, resumen_ventas,
    listar_todas_ordenes, obtener_detalle_orden,
    crear_usuario, eliminar_usuario,
)
from visualizaciones._widgets import mostrar_detalle_orden


class VentanaAdmin(ctk.CTk):

    def __init__(self):
        super().__init__()
        sesion = Sesion.obtener()
        self.title(f"Panel Admin  —  {sesion.nombre}")
        self.geometry("1050x700")
        self._construir_interfaz()
        self._actualizar_metricas()
        self._cargar_productos()

    # ── INTERFAZ PRINCIPAL ────────────────────────────────────────────────────

    def _construir_interfaz(self):
        # encabezado
        header = ctk.CTkFrame(self, fg_color="#1a1a2e", corner_radius=0)
        header.pack(fill="x")
        ctk.CTkLabel(header, text="⚙  Panel de Administración AURATEC",
                     font=("Arial", 22, "bold"), text_color="white").pack(side="left", padx=20, pady=12)
        ctk.CTkButton(header, text="Cerrar Sesión", width=130, fg_color="#e74c3c",
                      hover_color="#c0392b", command=self._cerrar_sesion).pack(side="right", padx=20, pady=12)

        # tarjetas de métricas
        self.frame_metricas = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_metricas.pack(fill="x", padx=20, pady=(15, 5))

        self.metricas_labels = {}
        colores = {"💰 Ingresos": "#16a085", "🛒 Ventas": "#2980b9",
                   "📦 Productos": "#8e44ad", "👥 Usuarios": "#d35400"}
        col = 0
        for titulo, color in colores.items():
            card = ctk.CTkFrame(self.frame_metricas, fg_color=color, corner_radius=12)
            card.grid(row=0, column=col, padx=8, sticky="ew")
            self.frame_metricas.grid_columnconfigure(col, weight=1)
            ctk.CTkLabel(card, text=titulo, font=("Arial", 12), text_color="white").pack(pady=(10, 2))
            lbl_val = ctk.CTkLabel(card, text="—", font=("Arial", 20, "bold"), text_color="white")
            lbl_val.pack(pady=(0, 10))
            self.metricas_labels[titulo] = lbl_val
            col += 1

        # barra de tabs
        tab_bar = ctk.CTkFrame(self, fg_color="transparent")
        tab_bar.pack(fill="x", padx=20, pady=(8, 0))
        self.btn_tab_prod = ctk.CTkButton(tab_bar, text="📦 Productos", width=150,
                                          command=self._mostrar_tab_productos)
        self.btn_tab_prod.pack(side="left", padx=(0, 4))
        self.btn_tab_ord = ctk.CTkButton(tab_bar, text="🧾 Órdenes", width=150,
                                         fg_color="#555", hover_color="#333",
                                         command=self._mostrar_tab_ordenes)
        self.btn_tab_ord.pack(side="left", padx=4)
        self.btn_tab_usr = ctk.CTkButton(tab_bar, text="👥 Usuarios", width=150,
                                         fg_color="#555", hover_color="#333",
                                         command=self._mostrar_tab_usuarios)
        self.btn_tab_usr.pack(side="left", padx=4)

        # contenedor de tabs
        self.frame_tab = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_tab.pack(fill="both", expand=True, padx=20, pady=10)

        self._construir_tab_productos()
        self._construir_tab_ordenes()
        self._construir_tab_usuarios()
        self._mostrar_tab_productos()

    # ── TAB PRODUCTOS ─────────────────────────────────────────────────────────

    def _construir_tab_productos(self):
        self.tab_productos = ctk.CTkFrame(self.frame_tab, fg_color="transparent")

        acc = ctk.CTkFrame(self.tab_productos, fg_color="transparent")
        acc.pack(fill="x", pady=(0, 8))
        ctk.CTkButton(acc, text="➕ Añadir Producto", width=160,
                      command=self._agregar_producto).pack(side="left", padx=4)
        ctk.CTkButton(acc, text="✏️ Modificar Precio", width=160,
                      command=self._modificar_precio).pack(side="left", padx=4)
        ctk.CTkButton(acc, text="🗑 Eliminar", width=130, fg_color="#e74c3c",
                      hover_color="#c0392b", command=self._eliminar_producto).pack(side="left", padx=4)

        self.frame_tabla = ctk.CTkScrollableFrame(self.tab_productos, height=420)
        self.frame_tabla.pack(fill="both", expand=True)

        self.columnas = {"ID": 50, "Nombre": 260, "Categoría": 160, "Precio": 100, "Stock": 80}
        for col_i, (enc, ancho) in enumerate(self.columnas.items()):
            ctk.CTkLabel(self.frame_tabla, text=enc, font=("Arial", 12, "bold"),
                         width=ancho, anchor="w").grid(row=0, column=col_i, padx=5, pady=6)

    def _mostrar_tab_productos(self):
        self.tab_ordenes.pack_forget()
        self.tab_usuarios.pack_forget()
        self.tab_productos.pack(fill="both", expand=True)
        self.btn_tab_prod.configure(fg_color=["#3a7ebf", "#1f538d"])
        self.btn_tab_ord.configure(fg_color="#555")
        self.btn_tab_usr.configure(fg_color="#555")

    # ── TAB ÓRDENES ───────────────────────────────────────────────────────────

    def _construir_tab_ordenes(self):
        self.tab_ordenes = ctk.CTkFrame(self.frame_tab, fg_color="transparent")

        # filtros
        filtros = ctk.CTkFrame(self.tab_ordenes, fg_color="transparent")
        filtros.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(filtros, text="Usuario:", font=("Arial", 11)).grid(row=0, column=0, padx=(0, 4))
        self.ord_entry_usr = ctk.CTkEntry(filtros, placeholder_text="Nombre o @login", width=150, height=30)
        self.ord_entry_usr.grid(row=0, column=1, padx=(0, 10))

        ctk.CTkLabel(filtros, text="Producto:", font=("Arial", 11)).grid(row=0, column=2, padx=(0, 4))
        self.ord_entry_prod = ctk.CTkEntry(filtros, placeholder_text="Nombre...", width=150, height=30)
        self.ord_entry_prod.grid(row=0, column=3, padx=(0, 10))

        ctk.CTkLabel(filtros, text="Desde:", font=("Arial", 11)).grid(row=0, column=4, padx=(0, 4))
        self.ord_entry_desde = ctk.CTkEntry(filtros, placeholder_text="dd/mm/aaaa", width=110, height=30)
        self.ord_entry_desde.grid(row=0, column=5, padx=(0, 6))

        ctk.CTkLabel(filtros, text="Hasta:", font=("Arial", 11)).grid(row=0, column=6, padx=(0, 4))
        self.ord_entry_hasta = ctk.CTkEntry(filtros, placeholder_text="dd/mm/aaaa", width=110, height=30)
        self.ord_entry_hasta.grid(row=0, column=7, padx=(0, 6))

        ctk.CTkButton(filtros, text="Filtrar", width=80, height=30,
                      command=self._buscar_ordenes).grid(row=0, column=8, padx=4)
        ctk.CTkButton(filtros, text="Ver todo", width=80, height=30, fg_color="#555",
                      hover_color="#333",
                      command=self._cargar_ordenes).grid(row=0, column=9, padx=4)

        self.frame_ordenes = ctk.CTkScrollableFrame(self.tab_ordenes, height=400)
        self.frame_ordenes.pack(fill="both", expand=True)

        self.cols_ord = {"#": 55, "Usuario": 160, "Login": 110, "Total": 90,
                         "Estado": 90, "Ítems": 55, "Fecha": 160, "": 75}
        for col_i, (enc, ancho) in enumerate(self.cols_ord.items()):
            ctk.CTkLabel(self.frame_ordenes, text=enc, font=("Arial", 11, "bold"),
                         width=ancho, anchor="w", text_color="#a0c4ff").grid(
                row=0, column=col_i, padx=4, pady=6)

    def _mostrar_tab_ordenes(self):
        self.tab_productos.pack_forget()
        self.tab_usuarios.pack_forget()
        self.tab_ordenes.pack(fill="both", expand=True)
        self.btn_tab_prod.configure(fg_color="#555")
        self.btn_tab_ord.configure(fg_color=["#3a7ebf", "#1f538d"])
        self.btn_tab_usr.configure(fg_color="#555")
        self._cargar_ordenes()

    def _cargar_ordenes(self, **kwargs):
        for w in self.frame_ordenes.winfo_children():
            if int(w.grid_info().get("row", 0)) > 0:
                w.destroy()

        ordenes = listar_todas_ordenes(**kwargs)
        if not ordenes:
            ctk.CTkLabel(self.frame_ordenes, text="Sin órdenes registradas.",
                         text_color="gray").grid(row=1, column=0, columnspan=8, pady=20)
            return

        col_anchos = deque(self.cols_ord.values())
        for fila, o in enumerate(ordenes, start=1):
            color = "#2b2b2b" if fila % 2 == 0 else "transparent"
            aw = deque(col_anchos)
            for col_i, (clave, fmt) in enumerate({
                "id": "{}", "usuario_nombre": "{}", "usuario_login": "@{}",
                "total": "${:.2f}", "estado": "{}", "items": "{}", "fecha": "{}"
            }.items()):
                ancho = aw.popleft()
                texto = fmt.format(o[clave])
                ctk.CTkLabel(self.frame_ordenes, text=texto, width=ancho,
                             anchor="w", fg_color=color).grid(row=fila, column=col_i, padx=4, pady=2)
            oid = o["id"]
            ctk.CTkButton(self.frame_ordenes, text="Detalle", width=aw.popleft(), height=26,
                          fg_color="#2980b9", hover_color="#1a5276",
                          command=lambda o=oid: mostrar_detalle_orden(self, o)
                          ).grid(row=fila, column=7, padx=4, pady=2)

    def _buscar_ordenes(self):
        self._cargar_ordenes(
            filtro_usuario=self.ord_entry_usr.get().strip() or None,
            filtro_producto=self.ord_entry_prod.get().strip() or None,
            fecha_desde=self.ord_entry_desde.get().strip() or None,
            fecha_hasta=self.ord_entry_hasta.get().strip() or None,
        )

    # ── TAB USUARIOS ──────────────────────────────────────────────────────────

    def _construir_tab_usuarios(self):
        self.tab_usuarios = ctk.CTkFrame(self.frame_tab, fg_color="transparent")

        acc_u = ctk.CTkFrame(self.tab_usuarios, fg_color="transparent")
        acc_u.pack(fill="x", pady=(0, 8))
        ctk.CTkButton(acc_u, text="➕ Nuevo Usuario", width=160,
                      command=self._nuevo_usuario).pack(side="left", padx=4)
        ctk.CTkButton(acc_u, text="🗑 Eliminar Usuario", width=160, fg_color="#e74c3c",
                      hover_color="#c0392b", command=self._eliminar_usuario_ui).pack(side="left", padx=4)

        self.frame_usuarios = ctk.CTkScrollableFrame(self.tab_usuarios, height=420)
        self.frame_usuarios.pack(fill="both", expand=True)

        self.cols_usr = {"ID": 50, "Nombre": 200, "Usuario": 160, "Rol": 80}
        for col_i, (enc, ancho) in enumerate(self.cols_usr.items()):
            ctk.CTkLabel(self.frame_usuarios, text=enc, font=("Arial", 12, "bold"),
                         width=ancho, anchor="w").grid(row=0, column=col_i, padx=5, pady=6)

    def _mostrar_tab_usuarios(self):
        self.tab_productos.pack_forget()
        self.tab_ordenes.pack_forget()
        self.tab_usuarios.pack(fill="both", expand=True)
        self.btn_tab_prod.configure(fg_color="#555")
        self.btn_tab_ord.configure(fg_color="#555")
        self.btn_tab_usr.configure(fg_color=["#3a7ebf", "#1f538d"])
        self._cargar_usuarios_tabla()

    def _cargar_usuarios_tabla(self):
        for w in self.frame_usuarios.winfo_children():
            if int(w.grid_info().get("row", 0)) > 0:
                w.destroy()
        cola_u = listar_usuarios()
        fila = 1
        while cola_u:
            u = cola_u.popleft()
            color = "#2b2b2b" if fila % 2 == 0 else "transparent"
            col_anchos = deque(self.cols_usr.values())
            for col_i, clave in enumerate(("id", "nombre", "usuario", "rol")):
                ancho = col_anchos.popleft()
                ctk.CTkLabel(self.frame_usuarios, text=str(u[clave]), width=ancho,
                             anchor="w", fg_color=color).grid(row=fila, column=col_i, padx=5, pady=3)
            fila += 1

    # ── DATOS ─────────────────────────────────────────────────────────────────

    def _actualizar_metricas(self):
        datos = resumen_ventas()
        mapeo = {
            "💰 Ingresos":  f"${datos['ingresos']:,.2f}",
            "🛒 Ventas":    str(datos["total_ventas"]),
            "📦 Productos": str(datos["productos"]),
            "👥 Usuarios":  str(datos["usuarios"]),
        }
        for titulo, valor in mapeo.items():
            self.metricas_labels[titulo].configure(text=valor)

    def _cargar_productos(self, filtro=None):
        for w in self.frame_tabla.winfo_children():
            if int(w.grid_info().get("row", 0)) > 0:
                w.destroy()

        cola = listar_productos(filtro)
        anchos_cola = deque(self.columnas.values())

        fila = 1
        while cola:
            p = cola.popleft()
            color = "#2b2b2b" if fila % 2 == 0 else "transparent"
            vals = deque([p["id"], p["nombre"], p["categoria"], p["precio"], p["stock"]])
            col_anchos = deque(anchos_cola)
            col_i = 0
            while vals:
                val   = vals.popleft()
                ancho = col_anchos.popleft()
                texto = f"${val:.2f}" if col_i == 3 else str(val)
                ctk.CTkLabel(self.frame_tabla, text=texto, width=ancho,
                             anchor="w", fg_color=color).grid(row=fila, column=col_i, padx=5, pady=2)
                col_i += 1
            fila += 1

        if fila == 1:
            ctk.CTkLabel(self.frame_tabla, text="Sin productos registrados.",
                         text_color="gray").grid(row=1, column=0, columnspan=5, pady=20)

    # ── FORMULARIOS PRODUCTOS ─────────────────────────────────────────────────

    def _agregar_producto(self):
        v = ctk.CTkToplevel(self)
        v.title("Agregar Producto")
        v.geometry("400x380")
        v.grab_set()

        entries = {}
        for campo in ("Nombre", "Categoría", "Precio", "Stock"):
            ctk.CTkLabel(v, text=campo + ":").pack(pady=(10, 0))
            e = ctk.CTkEntry(v, width=300)
            e.pack()
            entries[campo] = e

        lbl = ctk.CTkLabel(v, text="", text_color="red")
        lbl.pack(pady=5)

        def guardar():
            try:
                insertar_producto({
                    "nombre":    entries["Nombre"].get().strip(),
                    "categoria": entries["Categoría"].get().strip(),
                    "precio":    float(entries["Precio"].get()),
                    "stock":     int(entries["Stock"].get()),
                })
                v.destroy()
                self._cargar_productos()
                self._actualizar_metricas()
            except Exception as e:
                lbl.configure(text=f"Error: {e}")

        ctk.CTkButton(v, text="Guardar", command=guardar).pack(pady=15)

    def _modificar_precio(self):
        v = ctk.CTkToplevel(self)
        v.title("Modificar Precio")
        v.geometry("350x220")
        v.grab_set()

        ctk.CTkLabel(v, text="ID del producto:").pack(pady=(20, 0))
        e_id = ctk.CTkEntry(v, width=280)
        e_id.pack()
        ctk.CTkLabel(v, text="Nuevo precio:").pack(pady=(10, 0))
        e_precio = ctk.CTkEntry(v, width=280)
        e_precio.pack()
        lbl = ctk.CTkLabel(v, text="", text_color="red")
        lbl.pack(pady=5)

        def guardar():
            try:
                actualizar_precio(int(e_id.get()), float(e_precio.get()))
                v.destroy()
                self._cargar_productos()
            except Exception as e:
                lbl.configure(text=f"Error: {e}")

        ctk.CTkButton(v, text="Actualizar", command=guardar).pack(pady=10)

    def _eliminar_producto(self):
        v = ctk.CTkToplevel(self)
        v.title("Eliminar Producto")
        v.geometry("350x180")
        v.grab_set()

        ctk.CTkLabel(v, text="ID del producto a eliminar:").pack(pady=(20, 0))
        e_id = ctk.CTkEntry(v, width=280)
        e_id.pack()
        lbl = ctk.CTkLabel(v, text="", text_color="red")
        lbl.pack(pady=5)

        def eliminar():
            try:
                eliminar_producto(int(e_id.get()))
                v.destroy()
                self._cargar_productos()
                self._actualizar_metricas()
            except Exception as e:
                lbl.configure(text=f"Error: {e}")

        ctk.CTkButton(v, text="Eliminar", fg_color="#e74c3c",
                      hover_color="#c0392b", command=eliminar).pack(pady=10)

    # ── FORMULARIOS USUARIOS ──────────────────────────────────────────────────

    def _nuevo_usuario(self):
        v = ctk.CTkToplevel(self)
        v.title("Nuevo Usuario")
        v.geometry("400x400")
        v.grab_set()

        entries = {}
        for campo in ("Nombre completo", "Nombre de usuario", "Contraseña"):
            ctk.CTkLabel(v, text=campo + ":").pack(pady=(12, 0))
            e = ctk.CTkEntry(v, width=300, show="*" if campo == "Contraseña" else "")
            e.pack()
            entries[campo] = e

        ctk.CTkLabel(v, text="Rol:").pack(pady=(12, 0))
        rol_var = ctk.StringVar(value="user")
        frame_rol = ctk.CTkFrame(v, fg_color="transparent")
        frame_rol.pack()
        ctk.CTkRadioButton(frame_rol, text="Usuario", variable=rol_var, value="user").pack(side="left", padx=10)
        ctk.CTkRadioButton(frame_rol, text="Admin", variable=rol_var, value="admin").pack(side="left", padx=10)

        lbl = ctk.CTkLabel(v, text="", text_color="red")
        lbl.pack(pady=5)

        def guardar():
            nombre = entries["Nombre completo"].get().strip()
            usuario = entries["Nombre de usuario"].get().strip()
            contrasena = entries["Contraseña"].get()
            if not nombre or not usuario or not contrasena:
                lbl.configure(text="Completa todos los campos.")
                return
            try:
                crear_usuario(nombre, usuario, contrasena, rol_var.get())
                v.destroy()
                self._cargar_usuarios_tabla()
                self._actualizar_metricas()
            except Exception as e:
                lbl.configure(text=f"Error: {e}")

        ctk.CTkButton(v, text="Crear Usuario", command=guardar).pack(pady=15)

    def _eliminar_usuario_ui(self):
        v = ctk.CTkToplevel(self)
        v.title("Eliminar Usuario")
        v.geometry("360x200")
        v.grab_set()

        ctk.CTkLabel(v, text="ID del usuario a eliminar:").pack(pady=(20, 0))
        e_id = ctk.CTkEntry(v, width=280)
        e_id.pack()
        lbl = ctk.CTkLabel(v, text="No puedes eliminar tu propia cuenta.",
                           font=("Arial", 10), text_color="gray")
        lbl.pack(pady=4)
        lbl_err = ctk.CTkLabel(v, text="", text_color="red")
        lbl_err.pack()

        def eliminar():
            try:
                uid = int(e_id.get())
                sesion = Sesion.obtener()
                if uid == sesion.usuario_id:
                    lbl_err.configure(text="No puedes eliminar tu propia cuenta.")
                    return
                eliminar_usuario(uid)
                v.destroy()
                self._cargar_usuarios_tabla()
                self._actualizar_metricas()
            except Exception as e:
                lbl_err.configure(text=f"Error: {e}")

        ctk.CTkButton(v, text="Eliminar", fg_color="#e74c3c",
                      hover_color="#c0392b", command=eliminar).pack(pady=10)

    # ── SESIÓN ────────────────────────────────────────────────────────────────

    def _cerrar_sesion(self):
        Sesion.cerrar()
        self.destroy()
        from login import LoginApp
        LoginApp().mainloop()
