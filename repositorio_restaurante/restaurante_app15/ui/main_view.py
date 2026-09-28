import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable

from modelos.usuario import Usuario
from servicios.restaurante_servicio import RestauranteServicio
from ui.recursos import cargar_imagen

COLOR_OK: str = "#1b6e2d"
COLOR_ERROR: str = "#b00020"


class SeccionUsuarios(ttk.Frame):
    """Consulta de los usuarios registrados (solo lectura)."""

    def __init__(self, master: tk.Misc, servicio: RestauranteServicio) -> None:
        super().__init__(master, padding=12)
        self.servicio: RestauranteServicio = servicio

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        ttk.Label(self, text="Usuarios registrados", style="Seccion.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 10))

        marco = ttk.Frame(self)
        marco.grid(row=1, column=0, sticky="nsew")
        marco.columnconfigure(0, weight=1)
        marco.rowconfigure(0, weight=1)

        self.tabla: ttk.Treeview = ttk.Treeview(
            marco, columns=("identificacion", "nombre"), show="headings")
        self.tabla.heading("identificacion", text="Identificación")
        self.tabla.heading("nombre", text="Nombre")
        self.tabla.column("identificacion", width=160, anchor="w")
        self.tabla.column("nombre", width=320, anchor="w")
        self.tabla.grid(row=0, column=0, sticky="nsew")

        barra = ttk.Scrollbar(marco, orient="vertical", command=self.tabla.yview)
        barra.grid(row=0, column=1, sticky="ns")
        self.tabla.configure(yscrollcommand=barra.set)

    def actualizar(self) -> None:
        self.tabla.delete(*self.tabla.get_children())
        for usuario in self.servicio.listar_usuarios():
            self.tabla.insert("", "end", values=(usuario.identificacion, usuario.nombre))


class SeccionProductos(ttk.Frame):
    """Formulario + acciones + tabla para registrar, consultar, actualizar y eliminar productos."""

    CATEGORIAS: tuple[str, ...] = ("Plato", "Bebida", "Postre", "Otro")

    def __init__(self, master: tk.Misc, servicio: RestauranteServicio) -> None:
        super().__init__(master, padding=12)
        self.servicio: RestauranteServicio = servicio

        self.var_codigo: tk.StringVar = tk.StringVar()
        self.var_nombre: tk.StringVar = tk.StringVar()
        self.var_precio: tk.StringVar = tk.StringVar()
        self.var_categoria: tk.StringVar = tk.StringVar(value=self.CATEGORIAS[0])
        self.var_stock: tk.StringVar = tk.StringVar(value="0")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)

        ttk.Label(self, text="Gestión de productos", style="Seccion.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 10))
        self._crear_formulario()
        self._crear_estado()
        self._crear_tabla()

    # ------------------------------------------------------------------
    # Construcción de la interfaz
    # ------------------------------------------------------------------
    def _crear_formulario(self) -> None:
        marco = ttk.LabelFrame(self, text="Datos del producto", padding=12)
        marco.grid(row=1, column=0, sticky="ew")
        marco.columnconfigure(1, weight=1)
        marco.columnconfigure(3, weight=1)

        ttk.Label(marco, text="Código:").grid(row=0, column=0, sticky="e", padx=(0, 6), pady=5)
        ttk.Entry(marco, textvariable=self.var_codigo).grid(
            row=0, column=1, sticky="ew", padx=(0, 16), pady=5)

        ttk.Label(marco, text="Nombre:").grid(row=0, column=2, sticky="e", padx=(0, 6), pady=5)
        ttk.Entry(marco, textvariable=self.var_nombre).grid(row=0, column=3, sticky="ew", pady=5)

        ttk.Label(marco, text="Precio:").grid(row=1, column=0, sticky="e", padx=(0, 6), pady=5)
        ttk.Entry(marco, textvariable=self.var_precio).grid(
            row=1, column=1, sticky="ew", padx=(0, 16), pady=5)

        ttk.Label(marco, text="Categoría:").grid(row=1, column=2, sticky="e", padx=(0, 6), pady=5)
        ttk.Combobox(marco, textvariable=self.var_categoria, values=self.CATEGORIAS).grid(
            row=1, column=3, sticky="ew", pady=5)

        ttk.Label(marco, text="Stock:").grid(row=2, column=0, sticky="e", padx=(0, 6), pady=5)
        ttk.Spinbox(marco, textvariable=self.var_stock, from_=0, to=9999, width=8).grid(
            row=2, column=1, sticky="w", padx=(0, 16), pady=5)

        botones = ttk.Frame(marco)
        botones.grid(row=3, column=0, columnspan=4, pady=(10, 0))
        ttk.Button(botones, text="Registrar", command=self._registrar).grid(row=0, column=0, padx=4)
        ttk.Button(botones, text="Consultar", command=self._consultar).grid(row=0, column=1, padx=4)
        ttk.Button(botones, text="Actualizar", command=self._actualizar).grid(row=0, column=2, padx=4)
        ttk.Button(botones, text="Eliminar", command=self._eliminar).grid(row=0, column=3, padx=4)
        ttk.Button(botones, text="Limpiar", command=self._limpiar_formulario).grid(
            row=0, column=4, padx=4)

    def _crear_estado(self) -> None:
        self.lbl_estado: ttk.Label = ttk.Label(self, text="", foreground=COLOR_OK)
        self.lbl_estado.grid(row=2, column=0, sticky="w", pady=8)

    def _crear_tabla(self) -> None:
        marco = ttk.LabelFrame(self, text="Productos registrados", padding=8)
        marco.grid(row=3, column=0, sticky="nsew")
        marco.columnconfigure(0, weight=1)
        marco.rowconfigure(0, weight=1)

        columnas = ("codigo", "nombre", "precio", "categoria", "stock")
        self.tabla: ttk.Treeview = ttk.Treeview(marco, columns=columnas, show="headings")
        encabezados = {"codigo": "Código", "nombre": "Nombre", "precio": "Precio",
                       "categoria": "Categoría", "stock": "Stock"}
        anchos = {"codigo": 80, "nombre": 240, "precio": 80, "categoria": 110, "stock": 70}
        for columna in columnas:
            self.tabla.heading(columna, text=encabezados[columna])
            self.tabla.column(columna, width=anchos[columna], anchor="w")
        self.tabla.grid(row=0, column=0, sticky="nsew")

        barra = ttk.Scrollbar(marco, orient="vertical", command=self.tabla.yview)
        barra.grid(row=0, column=1, sticky="ns")
        self.tabla.configure(yscrollcommand=barra.set)

    # ------------------------------------------------------------------
    # Utilidades de la vista
    # ------------------------------------------------------------------
    def _mostrar_estado(self, mensaje: str, error: bool = False) -> None:
        self.lbl_estado.configure(text=mensaje, foreground=COLOR_ERROR if error else COLOR_OK)

    def _leer_precio_y_stock(self) -> tuple[float, int] | None:
        """Convierte los textos del formulario a números. Las reglas de negocio las valida el servicio."""
        try:
            precio = float(self.var_precio.get().strip().replace(",", "."))
        except ValueError:
            self._mostrar_estado("El precio debe ser un número.", error=True)
            return None
        try:
            stock = int(self.var_stock.get().strip())
        except ValueError:
            self._mostrar_estado("El stock debe ser un número entero.", error=True)
            return None
        return precio, stock

    def _limpiar_campos(self) -> None:
        self.var_codigo.set("")
        self.var_nombre.set("")
        self.var_precio.set("")
        self.var_categoria.set(self.CATEGORIAS[0])
        self.var_stock.set("0")

    def _limpiar_formulario(self) -> None:
        self._limpiar_campos()
        self._mostrar_estado("")

    def actualizar(self) -> None:
        """Vuelve a cargar la tabla con lo que informa el servicio."""
        self.tabla.delete(*self.tabla.get_children())
        for producto in self.servicio.listar_productos():
            self.tabla.insert("", "end", values=(
                producto.id_producto, producto.nombre, f"{producto.precio:.2f}",
                producto.categoria, producto.stock))

    # ------------------------------------------------------------------
    # Acciones (command=): coordinan la interfaz y delegan en el servicio
    # ------------------------------------------------------------------
    def _registrar(self) -> None:
        numeros = self._leer_precio_y_stock()
        if numeros is None:
            return
        precio, stock = numeros
        try:
            registrado = self.servicio.registrar_producto(
                self.var_codigo.get(), self.var_nombre.get(), precio,
                self.var_categoria.get(), stock)
        except ValueError as error:
            self._mostrar_estado(str(error), error=True)
            return

        if not registrado:
            self._mostrar_estado("Ya existe un producto con ese código.", error=True)
            return
        self.actualizar()
        self._limpiar_campos()
        self._mostrar_estado("Producto registrado correctamente.")

    def _consultar(self) -> None:
        codigo = self.var_codigo.get().strip()
        if not codigo:
            self._mostrar_estado("Ingrese el código del producto a consultar.", error=True)
            return
        producto = self.servicio.buscar_producto(codigo)
        if producto is None:
            self._mostrar_estado("No existe un producto con ese código.", error=True)
            return
        self.var_nombre.set(producto.nombre)
        self.var_precio.set(str(producto.precio))
        self.var_categoria.set(producto.categoria)
        self.var_stock.set(str(producto.stock))
        self._mostrar_estado("Producto cargado en el formulario.")

    def _actualizar(self) -> None:
        numeros = self._leer_precio_y_stock()
        if numeros is None:
            return
        precio, stock = numeros
        try:
            actualizado = self.servicio.actualizar_producto(
                self.var_codigo.get(), self.var_nombre.get(), precio,
                self.var_categoria.get(), stock)
        except ValueError as error:
            self._mostrar_estado(str(error), error=True)
            return

        if not actualizado:
            self._mostrar_estado("No existe un producto con ese código.", error=True)
            return
        self.actualizar()
        self._mostrar_estado("Producto actualizado correctamente.")

    def _eliminar(self) -> None:
        codigo = self.var_codigo.get().strip()
        if not codigo:
            self._mostrar_estado("Ingrese el código del producto a eliminar.", error=True)
            return
        producto = self.servicio.buscar_producto(codigo)
        if producto is None:
            self._mostrar_estado("No existe un producto con ese código.", error=True)
            return
        if not messagebox.askyesno("Confirmar eliminación",
                                   f"¿Eliminar el producto '{producto.nombre}'?"):
            self._mostrar_estado("Eliminación cancelada.")
            return

        self.servicio.eliminar_producto(codigo)
        self.actualizar()
        self._limpiar_campos()
        self._mostrar_estado("Producto eliminado correctamente.")


class SeccionVentas(ttk.Frame):
    """Registro de ventas: elegir usuario y producto, pulsar el botón y ver la tabla.

    Flujo de eventos:
        clic en "Registrar venta" -> command= -> _registrar_venta (callback)
        -> RestauranteServicio.registrar_venta -> ventas.json -> tabla y mensaje.
    """

    def __init__(self, master: tk.Misc, servicio: RestauranteServicio) -> None:
        super().__init__(master, padding=12)
        self.servicio: RestauranteServicio = servicio

        self.var_usuario: tk.StringVar = tk.StringVar()
        self.var_producto: tk.StringVar = tk.StringVar()
        self.var_cantidad: tk.StringVar = tk.StringVar(value="1")

        # Texto que ve la persona en el Combobox -> valor real (identificación / código).
        self._usuarios_por_texto: dict[str, str] = {}
        self._productos_por_texto: dict[str, str] = {}

        self.img_registrar: tk.PhotoImage | None = cargar_imagen("icono_registrar.png")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)

        ttk.Label(self, text="Registro de ventas", style="Seccion.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, 10))
        self._crear_formulario()
        self._crear_estado()
        self._crear_tabla()

    # ------------------------------------------------------------------
    # Construcción de la interfaz
    # ------------------------------------------------------------------
    def _crear_formulario(self) -> None:
        marco = ttk.LabelFrame(self, text="Nueva venta", padding=12)
        marco.grid(row=1, column=0, sticky="ew")
        marco.columnconfigure(1, weight=1)
        marco.columnconfigure(3, weight=1)

        ttk.Label(marco, text="Usuario:").grid(row=0, column=0, sticky="e", padx=(0, 6), pady=5)
        self.cmb_usuario: ttk.Combobox = ttk.Combobox(
            marco, textvariable=self.var_usuario, state="readonly")
        self.cmb_usuario.grid(row=0, column=1, sticky="ew", padx=(0, 16), pady=5)

        ttk.Label(marco, text="Producto:").grid(row=0, column=2, sticky="e", padx=(0, 6), pady=5)
        self.cmb_producto: ttk.Combobox = ttk.Combobox(
            marco, textvariable=self.var_producto, state="readonly")
        self.cmb_producto.grid(row=0, column=3, sticky="ew", pady=5)

        ttk.Label(marco, text="Cantidad:").grid(row=1, column=0, sticky="e", padx=(0, 6), pady=5)
        ttk.Spinbox(marco, textvariable=self.var_cantidad, from_=1, to=999, width=8).grid(
            row=1, column=1, sticky="w", padx=(0, 16), pady=5)

        # command= asocia el clic del botón con el callback _registrar_venta.
        kwargs_boton = {"image": self.img_registrar, "compound": "left"} \
            if self.img_registrar is not None else {}
        ttk.Button(marco, text="Registrar venta", command=self._registrar_venta,
                   style="Exito.TButton", **kwargs_boton).grid(
            row=2, column=0, columnspan=4, pady=(10, 0))

    def _crear_estado(self) -> None:
        self.lbl_estado: ttk.Label = ttk.Label(self, text="", foreground=COLOR_OK)
        self.lbl_estado.grid(row=2, column=0, sticky="w", pady=8)

    def _crear_tabla(self) -> None:
        marco = ttk.LabelFrame(self, text="Ventas registradas", padding=8)
        marco.grid(row=3, column=0, sticky="nsew")
        marco.columnconfigure(0, weight=1)
        marco.rowconfigure(0, weight=1)

        columnas = ("fecha", "usuario", "producto", "cantidad")
        self.tabla: ttk.Treeview = ttk.Treeview(marco, columns=columnas, show="headings")
        encabezados = {"fecha": "Fecha", "usuario": "Usuario",
                       "producto": "Producto", "cantidad": "Cantidad"}
        anchos = {"fecha": 150, "usuario": 200, "producto": 240, "cantidad": 80}
        for columna in columnas:
            self.tabla.heading(columna, text=encabezados[columna])
            self.tabla.column(columna, width=anchos[columna], anchor="w")
        self.tabla.grid(row=0, column=0, sticky="nsew")

        barra = ttk.Scrollbar(marco, orient="vertical", command=self.tabla.yview)
        barra.grid(row=0, column=1, sticky="ns")
        self.tabla.configure(yscrollcommand=barra.set)

    # ------------------------------------------------------------------
    # Utilidades de la vista
    # ------------------------------------------------------------------
    def _mostrar_estado(self, mensaje: str, error: bool = False) -> None:
        self.lbl_estado.configure(text=mensaje, foreground=COLOR_ERROR if error else COLOR_OK)

    def _cargar_selectores(self) -> None:
        """Llena los Combobox con los usuarios y productos que informa el servicio."""
        self._usuarios_por_texto = {
            f"{u.identificacion} - {u.nombre}": u.identificacion
            for u in self.servicio.listar_usuarios()}
        self._productos_por_texto = {
            f"{p.id_producto} - {p.nombre} (stock: {p.stock})": p.id_producto
            for p in self.servicio.listar_productos()}

        self.cmb_usuario.configure(values=list(self._usuarios_por_texto))
        self.cmb_producto.configure(values=list(self._productos_por_texto))

        # Si lo que estaba seleccionado ya no existe (o el stock cambió), se limpia.
        if self.var_usuario.get() not in self._usuarios_por_texto:
            self.var_usuario.set("")
        if self.var_producto.get() not in self._productos_por_texto:
            self.var_producto.set("")

    def _cargar_tabla(self) -> None:
        self.tabla.delete(*self.tabla.get_children())
        for venta in self.servicio.listar_ventas():
            usuario = self.servicio.buscar_usuario(venta.usuario_id)
            producto = self.servicio.buscar_producto(venta.producto_codigo)
            self.tabla.insert("", "end", values=(
                venta.fecha or "Sin fecha",
                usuario.nombre if usuario else f"{venta.usuario_id} (eliminado)",
                producto.nombre if producto else f"{venta.producto_codigo} (eliminado)",
                venta.cantidad))
        # Muestra la venta más reciente al final de la lista.
        hijos = self.tabla.get_children()
        if hijos:
            self.tabla.see(hijos[-1])

    def actualizar(self) -> None:
        """Vuelve a cargar selectores y tabla con lo que informa el servicio."""
        self._cargar_selectores()
        self._cargar_tabla()

    # ------------------------------------------------------------------
    # Callback (command=): coordina la interfaz y delega en el servicio
    # ------------------------------------------------------------------
    def _registrar_venta(self) -> None:
        identificacion = self._usuarios_por_texto.get(self.var_usuario.get())
        codigo = self._productos_por_texto.get(self.var_producto.get())
        if identificacion is None:
            self._mostrar_estado("Seleccione un usuario.", error=True)
            return
        if codigo is None:
            self._mostrar_estado("Seleccione un producto.", error=True)
            return
        try:
            cantidad = int(self.var_cantidad.get().strip())
        except ValueError:
            self._mostrar_estado("La cantidad debe ser un número entero.", error=True)
            return

        # Las reglas de la venta (existencia, cantidad, stock) las valida el servicio.
        try:
            venta = self.servicio.registrar_venta(identificacion, codigo, cantidad)
        except ValueError as error:
            self._mostrar_estado(str(error), error=True)
            return

        self.actualizar()
        self.var_cantidad.set("1")
        self._mostrar_estado(
            f"Venta registrada: {venta.cantidad} x {self._nombre_producto(codigo)} "
            f"para {self._nombre_usuario(identificacion)}.")

    def _nombre_producto(self, codigo: str) -> str:
        producto = self.servicio.buscar_producto(codigo)
        return producto.nombre if producto else codigo

    def _nombre_usuario(self, identificacion: str) -> str:
        usuario = self.servicio.buscar_usuario(identificacion)
        return usuario.nombre if usuario else identificacion


class MainView(ttk.Frame):
    """Panel principal: encabezado, menú de navegación y zona de contenido."""

    def __init__(self, master: tk.Misc, servicio: RestauranteServicio, usuario: Usuario,
                 al_cerrar_sesion: Callable[[], None]) -> None:
        super().__init__(master)
        self.servicio: RestauranteServicio = servicio
        self.usuario: Usuario = usuario
        self.al_cerrar_sesion: Callable[[], None] = al_cerrar_sesion

        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        # Imágenes de assets/ (se guardan como atributos para que no se liberen).
        self.img_logo: tk.PhotoImage | None = cargar_imagen("logo.png")
        self.iconos: dict[str, tk.PhotoImage | None] = {
            nombre: cargar_imagen(f"icono_{nombre}.png")
            for nombre in ("productos", "usuarios", "ventas", "salir")}

        self._crear_encabezado()
        self._crear_menu()
        self._crear_contenido()
        self.mostrar_seccion("productos")

    def _crear_encabezado(self) -> None:
        encabezado = ttk.Frame(self, style="Encabezado.TFrame", padding=(16, 10))
        encabezado.grid(row=0, column=0, columnspan=2, sticky="ew")
        encabezado.columnconfigure(1, weight=1)

        if self.img_logo is not None:
            ttk.Label(encabezado, image=self.img_logo, style="Encabezado.TLabel").grid(
                row=0, column=0, padx=(0, 12))
        ttk.Label(encabezado, text="Panel principal del restaurante",
                  style="EncabezadoTitulo.TLabel").grid(row=0, column=1, sticky="w")
        ttk.Label(encabezado, text=f"Sesión: {self.usuario.nombre}",
                  style="Encabezado.TLabel").grid(row=0, column=2, padx=16)
        ttk.Button(encabezado, text="Cerrar sesión", command=self.al_cerrar_sesion,
                   **self._opciones_icono("salir")).grid(row=0, column=3)

    def _opciones_icono(self, nombre: str) -> dict:
        """Opciones de ttk.Button para mostrar un ícono a la izquierda del texto."""
        icono = self.iconos.get(nombre)
        return {"image": icono, "compound": "left"} if icono is not None else {}

    def _crear_menu(self) -> None:
        menu = ttk.LabelFrame(self, text="Menú", padding=10)
        menu.grid(row=1, column=0, sticky="ns", padx=(12, 6), pady=12)

        opciones = (("Productos", "productos"),
                    ("Usuarios", "usuarios"),
                    ("Ventas", "ventas"))
        for fila, (texto, clave) in enumerate(opciones):
            ttk.Button(menu, text=texto, width=20, command=lambda c=clave: self.mostrar_seccion(c),
                       **self._opciones_icono(clave)).grid(row=fila, column=0, pady=4)

    def _crear_contenido(self) -> None:
        contenido = ttk.Frame(self)
        contenido.grid(row=1, column=1, sticky="nsew", padx=(6, 12), pady=12)
        contenido.columnconfigure(0, weight=1)
        contenido.rowconfigure(0, weight=1)

        self.secciones: dict[str, ttk.Frame] = {
            "productos": SeccionProductos(contenido, self.servicio),
            "usuarios": SeccionUsuarios(contenido, self.servicio),
            "ventas": SeccionVentas(contenido, self.servicio),
        }
        for seccion in self.secciones.values():
            seccion.grid(row=0, column=0, sticky="nsew")

    def mostrar_seccion(self, clave: str) -> None:
        seccion = self.secciones[clave]
        seccion.actualizar()
        seccion.tkraise()
