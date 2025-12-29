import sys
import os
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5.QtCore import QDate, QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QMessageBox
from PyQt5 import QtCore
from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtGui import QTextDocument
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
import pandas as pd
import subprocess
import platform
import tempfile
import time
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

def inicializar_bases_de_datos():
    ruta = "bases_de_datos"

    # Crear carpeta si no existe
    if not os.path.exists(ruta):
        os.makedirs(ruta)

    # ----- articulos.csv -----
    archivo_articulos = f"{ruta}/articulos.csv"
    if not os.path.exists(archivo_articulos):
        df = pd.DataFrame(columns=["id", "Nombre", "Familia", "Unidad"])
        df.to_csv(archivo_articulos, index=False, encoding="utf-8-sig")

    # ----- familias.csv -----
    archivo_familias = f"{ruta}/familias.csv"
    if not os.path.exists(archivo_familias):
        familias = [
            "Pavo y aves","Pollo","Pollo eco","Ternera","Maduradas","Conejo","Cordero",
            "Cerdo","Lechona","Carne Picada","Queso","Fiambre","Charcutería","Huevo",
            "Elaborado","Relleno","Conservas","Varios"
        ]
        df = pd.DataFrame({"Familia": familias})
        df.to_csv(archivo_familias, index=False, encoding="utf-8-sig")

    # ----- unidades.csv -----
    archivo_unidades = f"{ruta}/unidades.csv"
    if not os.path.exists(archivo_unidades):
        unidades = ["KG", "Unidades", "Gramos"]
        df = pd.DataFrame({"unidades": unidades})
        df.to_csv(archivo_unidades, index=False, encoding="utf-8-sig")

    # ----- pedidos.csv -----
    archivo_pedidos = f"{ruta}/pedidos.csv"
    if not os.path.exists(archivo_pedidos):

        columnas_base = [
            "Pedido","Nombre","Apellido","Telefono","Encargo","Entrega",
            "Observaciones","Elaborado","Entregado","Modificar","Recogida"
        ]

        # 20 bloques de producto
        columnas_productos = []
        for i in range(1, 21):
            columnas_productos += [
                f"Familia{i}", f"Producto{i}", f"ID{i}",
                f"Cantidad{i}", f"Unidad{i}", f"Obs{i}"
            ]

        columnas = columnas_base + columnas_productos

        df = pd.DataFrame(columns=columnas)
        df.to_csv(archivo_pedidos, index=False, encoding="utf-8-sig")

# Ejecutar al iniciar el programa
inicializar_bases_de_datos()
# ===========================================================

def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

#Clase para manejar fácilmente el cambio de ventanas 
class Navigator:
    def __init__(self, widget):
        self.widget = widget
        self.titles = {}
        
    def go(self, index):
        #cambia la pantalla y actualiza el título
        pantalla = self.widget.widget(index)
        
        if hasattr(pantalla, "actualizarPantalla"):
            pantalla.actualizarPantalla()
            
        self.widget.setCurrentIndex(index)
            
        title = self.titles.get(index, "Carnicería")
        self.widget.setWindowTitle(f"Carnicería - {title}")
        
    def set_title(self, index, title):
        #Registra el título de las pantallas
        self.titles[index] = title

#Inicializacion y abre la pantalla principal por medio del archivo UI
class mainWindow(QMainWindow):
    def __init__(self, stacked):
        super(mainWindow, self).__init__()
        loadUi(resource_path("interfaces/main_window.ui"), self)
        self.stacked = stacked
        self.nav = nav
        
        #Botones para pasar de una ventana a otra
        self.menuPantallaPrincipal.clicked.connect(lambda: self.nav.go(0))
        self.menuIntroduccionPedidos.clicked.connect(lambda: self.nav.go(1))
        self.menuElaboracionPedidos.clicked.connect(lambda: self.nav.go(2))
        self.menuEntregaPedidos.clicked.connect(lambda: self.nav.go(3))
        self.menuConsultaPedidos.clicked.connect(lambda: self.nav.go(4))
        self.menuConsultaCompras.clicked.connect(lambda: self.nav.go(5))
        self.menuConsultaArticulos.clicked.connect(lambda: self.nav.go(6))
        
        #Botones grandes exclusivos de la pantalla principal
        self.menuIntroduccionPedidos2.clicked.connect(lambda: self.nav.go(1))
        self.menuElaboracionPedidos2.clicked.connect(lambda: self.nav.go(2))
        self.menuEntregaPedidos2.clicked.connect(lambda: self.nav.go(3))
        self.menuConsultaPedidos2.clicked.connect(lambda: self.nav.go(4))
        self.menuConsultaCompras2.clicked.connect(lambda: self.nav.go(5))
        self.menuConsultaArticulos2.clicked.connect(lambda: self.nav.go(6))

#Una clase por ventana
class IntroduccionPedidos(QMainWindow):
    def __init__(self, stacked):
        super(IntroduccionPedidos, self).__init__()
        loadUi(resource_path("interfaces/introduccionPedidos.ui"), self)
        self.stacked = stacked
        self.nav = nav
        
        #Numero de pedido automático
        nombre_archivo = "bases_de_datos/pedidos.csv"
        if os.path.exists(nombre_archivo):
                df = pd.read_csv(nombre_archivo)
                #Si no hay filas, reiniciamos el contador
                if df.empty:
                    ultimo_num = 0
                else:
                    #extraemos el último número de pedido
                    ultimo_pedido = df['Pedido'].iloc[-1]
                    ultimo_num = int(ultimo_pedido[1:])
        else:
            #si no existe, empezamos de cero
            ultimo_num = 0
        nuevo_num = ultimo_num + 1
        self.txtNumPedido.setText(f"P{nuevo_num:04d}")
        
        #Botones para pasar de una ventana a otra
        self.menuPantallaPrincipal.clicked.connect(lambda: self.nav.go(0))
        self.menuIntroduccionPedidos.clicked.connect(lambda: self.nav.go(1))
        self.menuElaboracionPedidos.clicked.connect(lambda: self.nav.go(2))
        self.menuEntregaPedidos.clicked.connect(lambda: self.nav.go(3))
        self.menuConsultaPedidos.clicked.connect(lambda: self.nav.go(4))
        self.menuConsultaCompras.clicked.connect(lambda: self.nav.go(5))
        self.menuConsultaArticulos.clicked.connect(lambda: self.nav.go(6))
        
        #Fecha de hoy en la fecha de ingreso del pedido
        self.fechaIngresoPedido.setDate(QDate.currentDate())
        self.fechaEntregaPedido.setMinimumDate(QDate.currentDate())
    
        #Cargar base de datos de artículos
        archivo_articulos = "bases_de_datos/articulos.csv"
        if os.path.exists(archivo_articulos):
            self.df_articulos = pd.read_csv(archivo_articulos)
        else:
            QMessageBox.warning(self, "Error", "No se encontró la base de datos de artículos.")
            self.df_articulos = pd.DataFrame(columns=["id", "Nombre", "Familia", "Unidad"])

        # Familias únicas con una opción vacía al inicio
        familias = [""] + sorted(self.df_articulos["Familia"].dropna().unique().tolist())

        #Configurar comboboxes dinámicos (1 a 20)
        for i in range(1, 21):
            box_familia = getattr(self, f"boxFamilia{i}")
            box_producto = getattr(self, f"producto{i}")
            id_producto = getattr(self, f"idProducto{i}")
            unidad_producto = getattr(self, f"unidad{i}")

            # Cargar familias con opción vacía
            box_familia.addItems(familias)

            # Inicialmente, productos vacíos
            box_producto.addItem("")

            # Conectar eventos
            box_familia.currentTextChanged.connect(lambda fam, idx=i: self.actualizarProductos(idx, fam))
            box_producto.currentTextChanged.connect(lambda prod, idx=i: self.actualizarDatosProducto(idx, prod))

        #completar pedido
        self.CompletarPedido.clicked.connect(lambda: completarPedidoF())

        def completarPedidoF():
            nombre_archivo = "bases_de_datos/pedidos.csv"

            # Se obtienen los datos del cliente
            numeroPedido = self.txtNumPedido.text()
            nombreCliente = self.txtNombreCliente.text()
            apellidoCliente = self.txtApellidoCliente.text()
            telefonoCliente = self.txtTelefonoCliente.text()
            fechaIngresoPedido = self.fechaIngresoPedido.dateTime().toString("dd-MM-yyyy")
            fechaEntregaPedido = self.fechaEntregaPedido.dateTime().toString("dd-MM-yyyy")
            observacionesGenerales = self.txtObservaciones.toPlainText()
            
            # VALIDACIONES OBLIGATORIAS
            if not nombreCliente:
                QMessageBox.warning(self, "Campo obligatorio", "Por favor ingrese el nombre del cliente.")
                return
            if not apellidoCliente:
                QMessageBox.warning(self, "Campo obligatorio", "Por favor ingrese el apellido del cliente.")
                return
            if not telefonoCliente:
                QMessageBox.warning(self, "Campo obligatorio", "Por favor ingrese el teléfono del cliente.")
                return
            if not telefonoCliente.isdigit():
                QMessageBox.warning(self, "Campo obligatorio", "Por favor ingrese un número de teléfono válido.")
                return
            if not self.fechaEntregaPedido.date().isValid():
                QMessageBox.warning(self, "Campo obligatorio", "Por favor seleccione una fecha de entrega válida.")
                return

            #Diccionario base del pedido
            nuevoPedido = {
                'Pedido': numeroPedido, 
                'Nombre': nombreCliente, 
                'Apellido': apellidoCliente, 
                'Telefono': telefonoCliente, 
                "Encargo": fechaIngresoPedido, 
                "Entrega": fechaEntregaPedido, 
                "Observaciones": observacionesGenerales if observacionesGenerales else "",
                "Elaborado": False,
                "Entregado": False
            }

            #Datos de productos (hasta 20)
            productos_validos = 0 #contador de productos completos
            
            for i in range(1, 21):
                familia = getattr(self, f"boxFamilia{i}").currentText().strip()
                producto = getattr(self, f"producto{i}").currentText().strip()
                id_producto = getattr(self, f"idProducto{i}").text().strip()
                cantidad = getattr(self, f"cantidad{i}").text().strip()
                unidad = getattr(self, f"unidad{i}").text().strip()
                observacion = getattr(self, f"observaciones{i}").text().strip()

                # si todos están vacíos, simplemente agregar vacíos
                if not any([familia, producto, id_producto, cantidad, unidad, observacion]):
                    nuevoPedido[f"Familia{i}"] = ""
                    nuevoPedido[f"Producto{i}"] = ""
                    nuevoPedido[f"ID{i}"] = ""
                    nuevoPedido[f"Cantidad{i}"] = ""
                    nuevoPedido[f"Unidad{i}"] = ""
                    nuevoPedido[f"Obs{i}"] = ""
                    continue

                # si alguno está vacío, error
                if not all([familia, producto, id_producto, cantidad, unidad]):
                    QMessageBox.warning(self, "Error", f"Por favor complete todos los campos del producto {i}.")
                    return
                
                #Validar que la cantidad sí sea un número
                try:
                    valor_cantidad = float(cantidad)
                except ValueError:
                    QMessageBox.warning(self, "Error", f"La cantidad en el producto {i} debe ser un número entero o decimal.")
                    return
                
                productos_validos += 1

                # asignar datos
                nuevoPedido[f"Familia{i}"] = familia
                nuevoPedido[f"Producto{i}"] = producto
                nuevoPedido[f"ID{i}"] = id_producto
                nuevoPedido[f"Cantidad{i}"] = cantidad
                nuevoPedido[f"Unidad{i}"] = unidad
                nuevoPedido[f"Obs{i}"] = observacion
                

            if productos_validos == 0:
                QMessageBox.warning(self, "Error", "Debe agregar al menos un producto al pedido antes de guardarlo.")
                return
            
            #Guardar el pedido
            df_nuevo = pd.DataFrame([nuevoPedido])

            if os.path.exists(nombre_archivo):
                df = pd.read_csv(nombre_archivo)
                df = pd.concat([df, df_nuevo], ignore_index=True)
            else:
                df = df_nuevo

            try:
                df.to_csv(nombre_archivo, index=False, encoding='utf-8-sig')
            except PermissionError:
                QMessageBox.warning(self, "Archivo en uso",
                    "No se puede guardar el pedido porque 'pedidos.csv' está abierto.\n"
                    "Ciérrelo e intente de nuevo.")
                return

            #Mensaje de confirmación
            QMessageBox.information(self, "Carnicería - Pedido Agregado", f"Pedido {numeroPedido} agregado exitosamente.")
            
            #Salta a la pantalla principal
            self.nav.go(0)

            #Limpiar campos
            self.txtNombreCliente.clear()
            self.txtApellidoCliente.clear()
            self.txtTelefonoCliente.clear()
            self.txtObservaciones.clear()
            self.fechaIngresoPedido.setDate(QDate.currentDate())
            self.fechaEntregaPedido.setDate(QDate.currentDate())
            
            #limpiar productos para dejar todo listo para el siguiente pedido
            self.limpiarProductos()

            #Calcular nuevo número de pedido
            if os.path.exists(nombre_archivo):
                df = pd.read_csv(nombre_archivo)
                if not df.empty and "Pedido" in df.columns:
                    ultimo_pedido = df["Pedido"].iloc[-1]
                    if isinstance(ultimo_pedido, str) and ultimo_pedido.startswith("P"):
                        ultimo_num = int(ultimo_pedido[1:])
                    else:
                        ultimo_num = 0
                else:
                    ultimo_num = 0
            else:
                ultimo_num = 0

            nuevo_num = ultimo_num + 1
            self.txtNumPedido.setText(f"P{nuevo_num:04d}")

    def actualizarProductos(self, index, familia_seleccionada):
        #Llena el combobox de productos según la familia elegida
        box_producto = getattr(self, f"producto{index}")
        box_producto.clear()
        box_producto.addItem("")  # opción vacía

        if not familia_seleccionada:
            return

        productos = self.df_articulos[self.df_articulos["Familia"] == familia_seleccionada]["Nombre"].dropna().tolist()
        box_producto.addItems(sorted(productos))

    def actualizarDatosProducto(self, index, producto_seleccionado):
        #Llena los campos id y unidad según el producto elegido
        id_producto = getattr(self, f"idProducto{index}")
        unidad_producto = getattr(self, f"unidad{index}")

        if not producto_seleccionado:
            id_producto.clear()
            unidad_producto.clear()
            return

        fila = self.df_articulos[self.df_articulos["Nombre"] == producto_seleccionado]
        if not fila.empty:
            id_producto.setText(str(fila.iloc[0]["id"]))
            unidad_producto.setText(str(fila.iloc[0]["Unidad"]))
        else:
            id_producto.clear()
            unidad_producto.clear()

    def actualizarFamilias(self):
        #Recarga la lista de familias y productos desde el CSV
        archivo_articulos = "bases_de_datos/articulos.csv"
        if os.path.exists(archivo_articulos):
            self.df_articulos = pd.read_csv(archivo_articulos)
        else:
            QMessageBox.warning(self, "Error", "No se encontró la base de datos de artículos.")
            self.df_articulos = pd.DataFrame(columns=["id", "Nombre", "Familia", "Unidad"])

        # Familias únicas con una opción vacía al inicio
        familias = [""] + sorted(self.df_articulos["Familia"].dropna().unique().tolist())

        # --- Limpiar y recargar todos los combos y campos relacionados ---
        for i in range(1, 21):
            box_familia = getattr(self, f"boxFamilia{i}")
            box_producto = getattr(self, f"producto{i}")
            id_producto = getattr(self, f"idProducto{i}")
            unidad_producto = getattr(self, f"unidad{i}")

            # Limpiar combos y line edits
            box_familia.clear()
            box_producto.clear()
            id_producto.clear()
            unidad_producto.clear()

            # Volver a agregar las familias
            box_familia.addItems(familias)
            box_producto.addItem("")  # opción vacía

    def limpiarProductos(self):
        # Familias únicas con opción vacía
        familias = [""] + sorted(self.df_articulos["Familia"].dropna().unique().tolist())

        for i in range(1, 21):
            box_familia = getattr(self, f"boxFamilia{i}")
            box_producto = getattr(self, f"producto{i}")
            id_producto = getattr(self, f"idProducto{i}")
            cantidad = getattr(self, f"cantidad{i}")
            unidad = getattr(self, f"unidad{i}")
            observacion = getattr(self, f"observaciones{i}")

            # --- Resetear familia ---
            box_familia.blockSignals(True)
            box_familia.clear()
            box_familia.addItems(familias)
            box_familia.setCurrentIndex(0)
            box_familia.blockSignals(False)

            # --- Resetear productos ---
            box_producto.blockSignals(True)
            box_producto.clear()
            box_producto.addItem("")  # opción vacía
            box_producto.setCurrentIndex(0)
            box_producto.blockSignals(False)

            # --- Limpiar lineedits ---
            id_producto.clear()
            cantidad.clear()
            unidad.clear()
            observacion.clear()

    def actualizarPantalla(self):
        self.actualizarFamilias()

class ElaboracionPedidos(QMainWindow):
    def __init__(self, stacked):
        super(ElaboracionPedidos, self).__init__()
        loadUi(resource_path("interfaces/elaboracionPedidos.ui"), self)
        self.stacked = stacked
        self.nav = nav
        
        #Botones para pasar de una ventana a otra
        self.menuPantallaPrincipal.clicked.connect(lambda: self.nav.go(0))
        self.menuIntroduccionPedidos.clicked.connect(lambda: self.nav.go(1))
        self.menuElaboracionPedidos.clicked.connect(lambda: self.nav.go(2))
        self.menuEntregaPedidos.clicked.connect(lambda: self.nav.go(3))        
        self.menuConsultaPedidos.clicked.connect(lambda: self.nav.go(4))
        self.menuConsultaCompras.clicked.connect(lambda: self.nav.go(5))
        self.menuConsultaArticulos.clicked.connect(lambda: self.nav.go(6))
        
        #Establecer como fecha por defecto ahora hace un año
        self.fechaIngresoDesde.setDate(QDate.currentDate())
        self.fechaIngresoHasta.setDate(QDate.currentDate())
        self.fechaEntregaDesde.setDate(QDate.currentDate())
        self.fechaEntregaHasta.setDate(QDate.currentDate())
        
        #Variables para ordenamiento
        self._columna_orden_actual = None
        self._orden_ascendente_actual = True
        
        
        #cargar la tabla al iniciar
        self.cargarTablaPedidos()
        self.btnActualizar.clicked.connect(self.cargarTablaPedidos)
        
        # Conectar el clic del encabezado con la función personalizada de orden
        self.tablaPedidos.horizontalHeader().sectionClicked.connect(self.ordenarPorColumna)
        
        # Variable auxiliar para alternar ascendente/descendente
        self._orden_desc = False
        self.tablaPedidos.setSortingEnabled(False)

        #Se llaman los filtros
        self.txtNumPedido.textChanged.connect(self.filtrarTabla)
        self.txtNombreCliente.textChanged.connect(self.filtrarTabla)
        self.txtApellidoCliente.textChanged.connect(self.filtrarTabla)
        self.txtTelefonoCliente.textChanged.connect(self.filtrarTabla)

        self.fechaIngresoDesde.dateChanged.connect(self.filtrarTabla)
        self.fechaIngresoHasta.dateChanged.connect(self.filtrarTabla)
        self.fechaEntregaDesde.dateChanged.connect(self.filtrarTabla)
        self.fechaEntregaHasta.dateChanged.connect(self.filtrarTabla)

        self.boxElaborado.stateChanged.connect(self.filtrarTabla)
        self.boxEntregado.stateChanged.connect(self.filtrarTabla)

        #Mantener coherencia en fechas
        self.fechaIngresoDesde.dateChanged.connect(self.mantenerCoherenciaFechasIngreso)
        self.fechaEntregaDesde.dateChanged.connect(self.mantenerCoherenciaFechasEntrega)

        #boton de limpiar
        self.btnLimpiar.clicked.connect(self.limpiarFiltros)

        #boton de imprimir todos 
        self.btnImprimirTabla.clicked.connect(self.imprimirTodosLosPedidosElaborados)

    def filtrarTabla(self):
        # Desactivar ordenamiento temporalmente para evitar conflicto durante el filtrado
        self.tablaPedidos.setSortingEnabled(False)

        # Obtener valores de los widgets de filtro
        filtro_numero = self.txtNumPedido.text().strip().lower()
        filtro_nombre = self.txtNombreCliente.text().strip().lower()
        filtro_apellido = self.txtApellidoCliente.text().strip().lower()
        filtro_telefono = self.txtTelefonoCliente.text().strip().lower()

        fecha_ingreso_desde = self.fechaIngresoDesde.date().toPyDate() if self.fechaIngresoDesde.date().isValid() else None
        fecha_ingreso_hasta = self.fechaIngresoHasta.date().toPyDate() if self.fechaIngresoHasta.date().isValid() else None
        fecha_entrega_desde = self.fechaEntregaDesde.date().toPyDate() if self.fechaEntregaDesde.date().isValid() else None
        fecha_entrega_hasta = self.fechaEntregaHasta.date().toPyDate() if self.fechaEntregaHasta.date().isValid() else None

        elaborado_checked = self.boxElaborado.isChecked()
        entregado_checked = self.boxEntregado.isChecked()

        # Crear copia del DataFrame original
        df_filtrado = self.df_pedidos.copy()

        # Filtros de texto
        if filtro_numero:
            df_filtrado = df_filtrado[df_filtrado["Pedido"].astype(str).str.lower().str.contains(filtro_numero, regex=False)]
        if filtro_nombre:
            df_filtrado = df_filtrado[df_filtrado["Nombre"].astype(str).str.lower().str.contains(filtro_nombre, regex=False)]
        if filtro_apellido:
            df_filtrado = df_filtrado[df_filtrado["Apellido"].astype(str).str.lower().str.contains(filtro_apellido, regex=False)]
        if filtro_telefono:
            df_filtrado = df_filtrado[df_filtrado["Telefono"].astype(str).str.lower().str.contains(filtro_telefono, regex=False)]

        # Convertimos a datetime
        fechas_ingreso = pd.to_datetime(df_filtrado["Encargo"], format="%d-%m-%Y", errors="coerce")
        fechas_entrega = pd.to_datetime(df_filtrado["Entrega"], format="%d-%m-%Y", errors="coerce")
        
        # Eliminamos filas con fechas inválidas
        mask_fechas_validas = fechas_ingreso.notna() & fechas_entrega.notna()
        df_filtrado = df_filtrado[mask_fechas_validas]
        fechas_ingreso = fechas_ingreso[mask_fechas_validas]
        fechas_entrega = fechas_entrega[mask_fechas_validas]

        # Filas válidas
        mascara_validas = fechas_ingreso.notna() & fechas_entrega.notna()

        df_filtrado = df_filtrado[mascara_validas].reset_index(drop=True)
        fechas_ingreso = fechas_ingreso[mascara_validas].reset_index(drop=True)
        fechas_entrega = fechas_entrega[mascara_validas].reset_index(drop=True)
        
        # Eliminamos filas con fechas inválidas
        df_filtrado = df_filtrado[fechas_ingreso.notna() & fechas_entrega.notna()]
        fechas_ingreso = fechas_ingreso[fechas_ingreso.notna()]
        fechas_entrega = fechas_entrega[fechas_entrega.notna()]
        
        #Filtros por fechas
        mask = fechas_ingreso.notna() & fechas_entrega.notna()

        if fecha_ingreso_desde:
            mask &= fechas_ingreso >= pd.Timestamp(fecha_ingreso_desde)
        if fecha_ingreso_hasta:
            mask &= fechas_ingreso <= pd.Timestamp(fecha_ingreso_hasta)
            
        if fecha_entrega_desde:
            mask &= fechas_entrega >= pd.Timestamp(fecha_entrega_desde)
        if fecha_entrega_hasta:
            mask &= fechas_entrega <= pd.Timestamp(fecha_entrega_hasta)

        df_filtrado = df_filtrado[mask].reset_index(drop=True)
            
        # Filtros booleanos
        if elaborado_checked:
            df_filtrado = df_filtrado[df_filtrado["Elaborado"] == True]
        if entregado_checked:
            df_filtrado = df_filtrado[df_filtrado["Entregado"] == True]

        # Evitar filas vacías y resetear índices
        df_filtrado = df_filtrado.dropna(how="all").reset_index(drop=True)
        
        #Guardamos el resultado filtrado actual
        self.df_filtrado_actual = df_filtrado.copy()

        # Aplicar ordenamiento si existe
        if hasattr(self, '_columna_orden_actual') and self._columna_orden_actual:
            if self._columna_orden_actual in df_filtrado.columns:
                # Re-aplicar el ordenamiento al DataFrame filtrado
                df_filtrado = self.aplicarOrdenamiento(df_filtrado, self._columna_orden_actual, self._orden_ascendente_actual)

        # Mostrar el DataFrame filtrado
        self.mostrarTabla(df_filtrado)
    
    def cargarTablaPedidos(self):
        
        #carga los datos del CSV en el table widget
        nombre_archivo = "bases_de_datos/pedidos.csv"
        
        if not os.path.exists(nombre_archivo):
            #si no existe, muestra una tabla vacia
            self.tablaPedidos.setRowCount(0)
            self.tablaPedidos.setColumnCount(0)
            self.df_pedidos = pd.DataFrame()
            return
        
        #leer datos con pandas
        try:
            df = pd.read_csv(nombre_archivo, dtype=str, encoding="utf-8-sig")
        except Exception as e:
            print(f"Error al leer CSV: {e}")
            df = pd.DataFrame()
        
        # Limpiar posibles espacios
        df.columns = df.columns.str.strip()
        
        # Quitar filas completamente vacías
        df = df.dropna(how="all")

        # Quitar filas sin fechas (encargo o entrega)
        df = df[df["Encargo"].notna() & df["Entrega"].notna()]
        
        # Convertir columnas booleanas
        if "Elaborado" in df.columns:
            df["Elaborado"] = df["Elaborado"].astype(str).str.strip().str.lower().isin(["true", "1", "sí", "si"])
        if "Entregado" in df.columns:
            df["Entregado"] = df["Entregado"].astype(str).str.strip().str.lower().isin(["true", "1", "sí", "si"])

        self.df_pedidos = df
        
        #INICIALIZAR ENCABEZADOS SIN INDICADORES
        columnas_originales = list(df.columns)
        idx_modificacion = columnas_originales.index("Modificar")
        nueva_columna = columnas_originales.copy()
        nueva_columna.insert(idx_modificacion + 1, "Imprimir")
        
        self.tablaPedidos.setColumnCount(len(nueva_columna))
        for i, nombre in enumerate(nueva_columna):
            self.tablaPedidos.setHorizontalHeaderItem(i, QtWidgets.QTableWidgetItem(nombre))
        
        # Solo reiniciar si no hay columna ordenada actualmente
        self.filtrarTabla()
        
        self.tablaPedidos.resizeColumnsToContents()    

    def aplicarOrdenamiento(self, df, columna, ascendente):
        #Aplica el ordenamiento actual a un DataFrame
        df_ordenado = df.copy()
        
        # Detectar si la columna es fecha por su nombre
        columnas_fecha = ["Encargo", "Entrega"]

        if columna in columnas_fecha:
            try:
                # Convertir a datetime asegurando el formato día-mes-año
                df_ordenado["_fecha_tmp"] = pd.to_datetime(
                    df_ordenado[columna],
                    format="%d-%m-%Y",
                    errors="coerce"
                )
                
                # Eliminar filas con fechas inválidas
                df_ordenado = df_ordenado[df_ordenado["_fecha_tmp"].notna()]
                
                # Ordenar con datetime
                df_ordenado = df_ordenado.sort_values(
                    by="_fecha_tmp",
                    ascending=ascendente,
                    ignore_index=True
                )

                # Eliminar columna auxiliar
                df_ordenado.drop(columns=["_fecha_tmp"], inplace=True)
                
            except Exception as e:
                print(f"Error al ordenar fechas: {e}")
                # Fallback: ordenamiento normal
                df_ordenado = df_ordenado.sort_values(
                    by=columna,
                    ascending=ascendente,
                    ignore_index=True
                )

        else:
            # Orden normal para columnas no fecha
            df_ordenado = df_ordenado.sort_values(
                by=columna,
                ascending=ascendente,
                ignore_index=True
            )
        
        return df_ordenado

    def limpiarFiltros(self):
        #Limpia todos los QLineEdit y QDateEdit de los filtros
        self.txtNumPedido.clear()
        self.txtNombreCliente.clear()
        self.txtApellidoCliente.clear()
        self.txtTelefonoCliente.clear()
        self.boxElaborado.setCheckState(0)
        self.boxEntregado.setCheckState(0)

        #Establecer como fecha por defecto ahora hace y después de un año
        self.fechaIngresoDesde.setDate(QDate.currentDate())
        self.fechaIngresoHasta.setDate(QDate.currentDate())
        
        self.fechaEntregaDesde.setDate(QDate.currentDate())
        self.fechaEntregaHasta.setDate(QDate.currentDate())

        self.filtrarTabla()

    def mostrarTabla(self, df):    
        self.df_filtrado_actual = df.copy()
        # Desactivar ordenamiento mientras se actualiza la tabla
        self.tablaPedidos.setSortingEnabled(False)
        self.tablaPedidos.clearContents()
        
        # Desconectar todas las señales cellChanged existentes
        try:
            self.tablaPedidos.cellChanged.disconnect()
        except:
            pass  # Si no estaba conectada, no hay problema
        
        #Columnas a mostrar
        columnas_cliente = ["Pedido", "Nombre", "Apellido", "Telefono","Encargo", "Entrega", "Observaciones", "Elaborado", "Entregado", "Recogida"]
        # Filtrar solo las columnas que existen en el DataFrame
        columnas_cliente = [col for col in columnas_cliente if col in df.columns]
        df = df[columnas_cliente].copy()
        
        # Agregar "Imprimir" al FINAL de las columnas
        nueva_columna = columnas_cliente + ["Imprimir"]
        
        self.tablaPedidos.setColumnCount(len(nueva_columna))
        
        #ACTUALIZAR ENCABEZADOS MANTENIENDO INDICADORES DE ORDEN
        for i, nombre_columna in enumerate(nueva_columna):
            # Si esta columna es la que está ordenada, mantener el indicador
            nombre_columna_limpio = nombre_columna.replace(" ▲", "").replace(" ▼", "")  #Limpiar
            if self._columna_orden_actual == nombre_columna_limpio:  #Comparar con limpio
                if self._orden_ascendente_actual:
                    nombre_con_indicador = f"{nombre_columna} ▲"
                else:
                    nombre_con_indicador = f"{nombre_columna} ▼"
                self.tablaPedidos.setHorizontalHeaderItem(i, QtWidgets.QTableWidgetItem(nombre_con_indicador))
            else:
                # Si no tiene indicador, establecer nombre normal
                self.tablaPedidos.setHorizontalHeaderItem(i, QtWidgets.QTableWidgetItem(nombre_columna))
        
        self.tablaPedidos.setRowCount(len(df))
        
        # Obtener índices dinámicos basados en nombres de columnas
        col_elaborado = columnas_cliente.index("Elaborado")
        col_entregado = columnas_cliente.index("Entregado") 
        col_recogida = columnas_cliente.index("Recogida")
        col_imprimir = len(columnas_cliente)  # "Imprimir" está en la última posición

        #Iterar usando el índice del DataFrame ordenado
        for posicion_tabla in range(len(df)):
            fila = df.iloc[posicion_tabla]
            #Determinar si el pedido ya está elaborado o entregado
            elaborado = bool(fila["Elaborado"])
            entregado = bool(fila["Entregado"])
            fila_bloqueada = elaborado
            
            #color de texto en rojo si está bloqueada (entregado o elaborado)
            color_texto = QtGui.QColor("red") if fila_bloqueada else QtGui.QColor("black")
            
            # Recorre todas las columnas del df dinámicamente
            for j, col in enumerate(columnas_cliente):
                col_destino = j
                valor = "" if pd.isna(fila[col]) else str(fila[col])
                item = QtWidgets.QTableWidgetItem(valor)
                item.setForeground(QtGui.QBrush(color_texto))
                self.tablaPedidos.setItem(posicion_tabla, col_destino, item)  

            # Checkbox de "Elaborado"
            chk_elaborado = QtWidgets.QTableWidgetItem()
            # PERMITE MARCAR Y DESMARCAR EL ELABORADO
            if entregado:
                # Pedido entregado → NO se puede modificar
                chk_elaborado.setFlags(QtCore.Qt.ItemIsEnabled)
            else:
                # No entregado → se puede marcar y desmarcar
                chk_elaborado.setFlags(
                    QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled
                )

            chk_elaborado.setCheckState(
                QtCore.Qt.Checked if elaborado else QtCore.Qt.Unchecked
            )

            self.tablaPedidos.setItem(posicion_tabla, col_elaborado, chk_elaborado)

            # Checkbox de "Entregado"
            chk_entregado = QtWidgets.QTableWidgetItem()
            chk_entregado.setFlags(QtCore.Qt.ItemIsEnabled)
            chk_entregado.setCheckState(QtCore.Qt.Checked if fila["Entregado"] else QtCore.Qt.Unchecked)
            self.tablaPedidos.setItem(posicion_tabla, col_entregado, chk_entregado)

            if fila_bloqueada:
                #Boton imprimir
                btnImprimir = QtWidgets.QPushButton("Imprimir")
                btnImprimir.setStyleSheet("""
                    QPushButton {
                            background-color: rgb(0, 0, 0);
                            color: white;
                            border-radius: 10px;
                            padding: 3px 8px;
                        }

                        QPushButton:hover {
                            background-color: rgb(86, 86, 86);
                        }
                    """)
                pedido_actual = str(fila["Pedido"])
                self.tablaPedidos.setCellWidget(posicion_tabla, col_imprimir, btnImprimir)
                btnImprimir.clicked.connect(lambda _, pedido=pedido_actual: self.guardarPDFpedidoTemporal(pedido))
                
            else:
                # Agregar una celda vacía para mantener alineación visual
                self.tablaPedidos.setItem(posicion_tabla, col_imprimir, QtWidgets.QTableWidgetItem(""))
        
        # Conectar la señal cellChanged UNA SOLA VEZ después de crear toda la tabla
        self.tablaPedidos.cellChanged.connect(self.onCellChanged)

        QTimer.singleShot(0, self.tablaPedidos.resizeColumnsToContents)

    def ordenarPorColumna(self, indice):
        nombre_columna = self.tablaPedidos.horizontalHeaderItem(indice).text()
        
        #LIMPIAR EL NOMBRE DE LA COLUMNA (quitar ▲/▼)
        nombre_columna_limpio = nombre_columna.replace(" ▲", "").replace(" ▼", "")

        # Si la columna es de botones o columnas especiales
        if nombre_columna_limpio in ["Modificar", "Imprimir"]:
            return

        #DETERMINAR DIRECCIÓN DEL ORDEN
        # Si es la misma columna, alternar dirección
        if self._columna_orden_actual == nombre_columna_limpio:
            self._orden_ascendente_actual = not self._orden_ascendente_actual
        else:
            # Si es una columna diferente, orden ascendente por defecto
            self._orden_ascendente_actual = True
            self._columna_orden_actual = nombre_columna_limpio

        #ACTUALIZAR INDICADOR VISUAL
        self.actualizarIndicadorOrden(indice, self._orden_ascendente_actual)

        # Tomar el DF actual (filtrado o completo)
        if hasattr(self, "df_filtrado_actual"):
            df_a_ordenar = self.df_filtrado_actual.copy()
        else:
            df_a_ordenar = self.df_pedidos.copy()
        
        df_ordenado = df_a_ordenar.copy()

        # Detectar si la columna es fecha por su nombre
        columnas_fecha = ["Encargo", "Entrega"]

        if nombre_columna_limpio in columnas_fecha:
            try:
                # Convertir a datetime asegurando el formato día-mes-año
                df_ordenado["_fecha_tmp"] = pd.to_datetime(
                    df_ordenado[nombre_columna_limpio],
                    format="%d-%m-%Y",
                    errors="coerce"
                )
                
                # Eliminar filas con fechas inválidas
                df_ordenado = df_ordenado[df_ordenado["_fecha_tmp"].notna()]
                
                # Ordenar con datetime
                df_ordenado = df_ordenado.sort_values(
                    by="_fecha_tmp",
                    ascending=self._orden_ascendente_actual,
                    ignore_index=True
                )

                # Eliminar columna auxiliar
                df_ordenado.drop(columns=["_fecha_tmp"], inplace=True)
                
            except Exception as e:
                print(f"Error al ordenar fechas: {e}")
                # Fallback: ordenamiento normal
                df_ordenado = df_ordenado.sort_values(
                    by=nombre_columna_limpio,
                    ascending=self._orden_ascendente_actual,
                    ignore_index=True
                )

        else:
            # Orden normal para columnas no fecha
            df_ordenado = df_ordenado.sort_values(
                by=nombre_columna_limpio,
                ascending=self._orden_ascendente_actual,
                ignore_index=True
            )

        # Guardar nuevo DF ordenado
        self.df_filtrado_actual = df_ordenado.copy()

        # Mostrar tabla ordenada
        self.mostrarTabla(df_ordenado)

    def actualizarIndicadorOrden(self, indice_columna, ascendente):
        #Actualiza el indicador visual de orden en el encabezado
        header = self.tablaPedidos.horizontalHeader()
        
        #LIMPIAR INDICADORES ANTERIORES
        for i in range(self.tablaPedidos.columnCount()):
            item_actual = self.tablaPedidos.horizontalHeaderItem(i)
            if item_actual:
                nombre_actual = item_actual.text()
                # Remover flechas anteriores
                nombre_limpio = nombre_actual.replace(" ▲", "").replace(" ▼", "")
                if nombre_limpio != nombre_actual:  # Si tenía indicador
                    item_actual.setText(nombre_limpio)
        
        #AGREGAR NUEVO INDICADOR
        item_actual = self.tablaPedidos.horizontalHeaderItem(indice_columna)
        if item_actual:
            nombre_actual = item_actual.text()
            nombre_limpio = nombre_actual.replace(" ▲", "").replace(" ▼", "")  # Limpiar por si acaso
            
            if ascendente:
                nuevo_nombre = f"{nombre_limpio} ▲"
            else:
                nuevo_nombre = f"{nombre_limpio} ▼"
            
            item_actual.setText(nuevo_nombre)
    
    def onCellChanged(self, row, column):
        """Maneja cambios en cualquier celda de la tabla"""
        # Solo procesar si es la columna del checkbox de elaborado (columna 7)
        if column == 7:
            item = self.tablaPedidos.item(row, column)
            if item:
                pedido_item = self.tablaPedidos.item(row, 0)
                if not pedido_item:
                    return

                pedido = pedido_item.text()

                self.tablaPedidos.cellChanged.disconnect()
                try:
                    if item.checkState() == QtCore.Qt.Checked:
                        self.marcarComoElaborado(pedido)
                    else:
                        self.desmarcarComoElaborado(pedido)
                finally:
                    self.tablaPedidos.cellChanged.connect(self.onCellChanged)
       
    def marcarComoElaborado(self, pedido):
        
        # Buscar el índice en el DataFrame completo
        idx = self.df_pedidos[self.df_pedidos["Pedido"] == pedido].index
        if len(idx) == 0:
            QMessageBox.warning(self, "Error", f"No se encontró el pedido {pedido}.")
            return

        idx = idx[0]

        # Marcar como elaborado en el DataFrame principal
        self.df_pedidos.at[idx, "Elaborado"] = True

        # Generar el número de recogida 0 a 99 para cada día por separado
        # Obtener fecha de entrega del pedido actual (formato: dd-mm-YYYY)
        fecha_entrega = self.df_pedidos.at[idx, "Entrega"]
        
        try:
            fecha_dt = pd.to_datetime(fecha_entrega, format="%d-%m-%Y", dayfirst=True)
        except:
            QMessageBox.warning(self, "Error", f"La fecha de entrega del pedido {pedido} no es válida.")
            return
        
        # Filtrar todos los pedidos con la MISMA fecha de entrega
        df_mismo_dia = self.df_pedidos[
            self.df_pedidos["Entrega"] == fecha_entrega
        ]
        
        # Obtener recogidas existentes del mismo día
        recogidas_existentes = self.df_pedidos.loc[
            (self.df_pedidos["Entrega"] == fecha_entrega) &
            (self.df_pedidos["Elaborado"] == True) &
            (self.df_pedidos["Recogida"].notna()) &
            (self.df_pedidos["Recogida"] != ""),
            "Recogida"
        ]

        # Convertir a enteros
        recogidas_usadas = sorted(recogidas_existentes.astype(str).astype(int).tolist())

        # Buscar el primer hueco disponible
        numero_recogida = None
        for i in range(1, 100):
            if i not in recogidas_usadas:
                numero_recogida = i
                break

        if numero_recogida is None:
            QMessageBox.warning(
                self,
                "Límite alcanzado",
                "Ya existen 99 pedidos elaborados para este día."
            )
            return

        numero_formateado = f"{numero_recogida:02d}"

        # Guardarlo en el CSV
        self.df_pedidos.at[idx, "Recogida"] = numero_formateado
        
        # Guardar CSV
        nombre_archivo = "bases_de_datos/pedidos.csv"
        try:
            self.df_pedidos.to_csv(nombre_archivo, index=False, encoding="utf-8-sig")
        except PermissionError:
            QMessageBox.warning(self, "Archivo en uso",
                "No se puede marcar como elaborado porque 'pedidos.csv' está abierto.\n"
                "Ciérrelo e intente de nuevo.")
            return
        
        if hasattr(self, "df_filtrado_actual") and not self.df_filtrado_actual.empty:
            idx_filt = self.df_filtrado_actual[self.df_filtrado_actual["Pedido"] == pedido].index
            if len(idx_filt) > 0:
                self.df_filtrado_actual.at[idx_filt[0], "Elaborado"] = True
                self.df_filtrado_actual.at[idx_filt[0], "Recogida"] = numero_formateado
            
        # Buscar la fila visible en tabla
        for row in range(self.tablaPedidos.rowCount()):
            item_ped = self.tablaPedidos.item(row, 0)
            if item_ped and item_ped.text() == pedido:

                #Pintar la fila en rojo
                for col in range(self.tablaPedidos.columnCount()):
                    item = self.tablaPedidos.item(row, col)
                    if item:
                        item.setForeground(QtGui.QBrush(QtGui.QColor("red")))

                #Convertir checkbox en solo lectura
                col_elaborado = 7   # o donde corresponda
                chk = self.tablaPedidos.item(row, col_elaborado)
                if chk:
                    chk.setCheckState(QtCore.Qt.Checked)

                #Actualizar número de recogida en su celda
                col_recogida = 9  # o tu índice exacto
                item_rec = self.tablaPedidos.item(row, col_recogida)
                if item_rec:
                    item_rec.setText(numero_formateado)

                #Poner botón imprimir solo en esa fila
                col_imprimir = self.tablaPedidos.columnCount() - 1
                btn = QtWidgets.QPushButton("Imprimir")
                btn.setStyleSheet("""QPushButton {
                            background-color: rgb(0, 0, 0);
                            color: white;
                            border-radius: 10px;
                            padding: 3px 8px;
                        }

                        QPushButton:hover {
                            background-color: rgb(86, 86, 86);
                        }
                    """)
                pedido_actual = pedido

                btn.clicked.connect(lambda _, p=pedido_actual: self.guardarPDFpedidoTemporal(p))

                self.tablaPedidos.setCellWidget(row, col_imprimir, btn)
                break
            
        #EVITA DEJAR HUECOS O NUMEROS DE RECOGIDA DUPLICADOS
        fecha = self.df_pedidos.at[idx, "Entrega"]
        #self.renumerarRecogidasDelDia(fecha)
        #self.mostrarTabla(self.df_pedidos)

    def desmarcarComoElaborado(self, pedido):
        idx = self.df_pedidos[self.df_pedidos["Pedido"] == pedido].index
        if len(idx) == 0:
            return

        idx = idx[0]

        # Actualizar DataFrame
        self.df_pedidos.at[idx, "Elaborado"] = False
        self.df_pedidos.at[idx, "Recogida"] = ""

        # Guardar CSV
        try:
            self.df_pedidos.to_csv(
                "bases_de_datos/pedidos.csv",
                index=False,
                encoding="utf-8-sig"
            )
        except PermissionError:
            QMessageBox.warning(
                self,
                "Archivo en uso",
                "Cierre pedidos.csv antes de continuar."
            )
            return

        # Actualizar DF filtrado si existe
        if hasattr(self, "df_filtrado_actual"):
            idx_filt = self.df_filtrado_actual[
                self.df_filtrado_actual["Pedido"] == pedido
            ].index
            if len(idx_filt) > 0:
                self.df_filtrado_actual.at[idx_filt[0], "Elaborado"] = False
                self.df_filtrado_actual.at[idx_filt[0], "Recogida"] = ""

        # Actualizar la fila visual
        for row in range(self.tablaPedidos.rowCount()):
            item_ped = self.tablaPedidos.item(row, 0)
            if item_ped and item_ped.text() == pedido:

                # Color normal
                for col in range(self.tablaPedidos.columnCount()):
                    item = self.tablaPedidos.item(row, col)
                    if item:
                        item.setForeground(QtGui.QBrush(QtGui.QColor("black")))

                # Limpiar recogida
                col_recogida = 9
                item_rec = self.tablaPedidos.item(row, col_recogida)
                if item_rec:
                    item_rec.setText("")

                # Quitar botón imprimir
                col_imprimir = self.tablaPedidos.columnCount() - 1
                self.tablaPedidos.removeCellWidget(row, col_imprimir)
                self.tablaPedidos.setItem(row, col_imprimir, QtWidgets.QTableWidgetItem(""))
                break
            
        #EVITA DEJAR HUECOS O NUMEROS DE RECOGIDA DUPLICADOS
        #fecha = self.df_pedidos.at[idx, "Entrega"]
        #self.renumerarRecogidasDelDia(fecha)
        #self.mostrarTabla(self.df_pedidos)

    def renumerarRecogidasDelDia(self, fecha):
        # Filtrar pedidos elaborados del mismo día
        df_dia = self.df_pedidos[
            (self.df_pedidos["Entrega"] == fecha) &
            (self.df_pedidos["Elaborado"] == True)
        ]

        # Ordenar por momento de elaboración
        df_dia = df_dia.sort_index()

        # Asignar nuevos números
        for i, idx in enumerate(df_dia.index, start=1):
            self.df_pedidos.at[idx, "Recogida"] = str(i)

        # Guardar
        self.df_pedidos.to_csv(
            "bases_de_datos/pedidos.csv",
            index=False,
            encoding="utf-8-sig"
        )

    def imprimir_con_dialogo_sistema(self, pdf_filename):
        try:
            
            sistema = platform.system()
            
            if sistema == "Windows":
                # Método más confiable para Windows
                try:
                    # Abrir el PDF y sugerir al usuario que imprima manualmente
                    os.startfile(pdf_filename)
                    time.sleep(1)
                    return True, "PDF abierto. Por favor, imprima manualmente."
                except Exception as e:
                    return False, f"No se pudo abrir el PDF: {str(e)}"
                    
            elif sistema == "Darwin":  # macOS
                subprocess.run(["lpr", pdf_filename])
                return True, "PDF enviado a imprimir"
                
            elif sistema == "Linux":
                subprocess.run(["lp", pdf_filename])
                return True, "PDF enviado a imprimir"
                
            else:
                return False, "Sistema operativo no soportado"
                
        except Exception as e:
            return False, f"Error al imprimir: {str(e)}"

    def dibujarPDF(self, c, pedido, width, height):
        """Función común para dibujar un pedido en el PDF"""
        # ======== DATOS DEL PEDIDO ========
        num_recogida_val = pedido.get("Recogida", "")

        # Convertir siempre directamente a string, sin tocar ceros ni convertir a número
        if pd.isna(num_recogida_val) or num_recogida_val == "":
            num_recogida = ""
        else:
            num_recogida = str(num_recogida_val)
            
        apellido = str(pedido["Apellido"])
        nombre = str(pedido["Nombre"])
        telefono = str(pedido["Telefono"])
        num_pedido = str(pedido["Pedido"])
        fecha_ingreso = str(pedido["Encargo"])
        fecha_entrega = str(pedido["Entrega"])
        
        observaciones = pedido.get("Observaciones", "")
        if pd.isna(observaciones):
            observaciones = ""
        else:
            observaciones = str(observaciones)

        # ======== CONFIGURACIÓN ========
        margin_left = 1.5*cm
        margin_right = 1.5*cm
        line_x = 13*cm
        
        # ======== SECCIÓN SUPERIOR ========
        
        # Número grande izquierda (arriba)
        c.setFont("Helvetica-Bold", 90)
        c.drawString(margin_left, height - 3.5*cm, num_recogida)
        
        # Información del cliente (derecha del número)
        info_x = margin_left + 4*cm
        c.setFont("Helvetica-Bold", 16)
        c.drawString(info_x, height - 2.5*cm, f"{apellido}, {nombre}")
        
        c.setFont("Helvetica", 11)
        c.drawString(info_x, height - 3.3*cm, f"Fecha ingreso: {fecha_ingreso}")
        c.drawString(info_x, height - 4.1*cm, f"Fecha entrega: {fecha_entrega}")
        c.drawString(info_x, height - 4.9*cm, telefono)
        c.drawString(info_x, height - 5.7*cm, f"Nº pedido: {num_pedido}")
        
        # Productos con familia en COLUMNAS - TODOS LOS PRODUCTOS
        productos_y = height - 8*cm
        c.setFont("Helvetica", 10)
        
        # Obtener productos del DataFrame CON FAMILIA
        productos_data = []
        for i in range(1, 21):
            familia = pedido.get(f"Familia{i}", "")
            producto = pedido.get(f"Producto{i}", "")
            if producto and not pd.isna(producto) and str(producto).strip():
                cantidad = pedido.get(f"Cantidad{i}", "")
                unidad = pedido.get(f"Unidad{i}", "")
                productos_data.append({
                    'familia': str(familia) if familia and not pd.isna(familia) else "",
                    'producto': str(producto),
                    'cantidad': str(cantidad) if cantidad and not pd.isna(cantidad) else "",
                    'unidad': str(unidad) if unidad and not pd.isna(unidad) else ""
                })
        
        # Posiciones de columnas
        col_familia_x = margin_left
        col_producto_x = margin_left + 3.5*cm
        col_cantidad_x = margin_left + 7*cm
        col_unidad_x = margin_left + 9*cm
        
        # Dibujar TODOS los productos (no solo 12)
        for producto in productos_data:
            c.drawString(col_familia_x, productos_y, producto['familia'])
            c.drawString(col_producto_x, productos_y, producto['producto'])
            c.drawString(col_cantidad_x, productos_y, producto['cantidad'])
            c.drawString(col_unidad_x, productos_y, producto['unidad'])
            productos_y -= 0.6*cm
        
        # ======== AJUSTE DE LÍNEA HORIZONTAL ========
        line_y_horizontal = height - 20*cm
        
        # Línea vertical
        c.line(line_x, height - 2*cm, line_x, line_y_horizontal)
        
        # Observaciones superior derecha
        obs_x = line_x + 0.5*cm
        obs_y = height - 16*cm
            
        c.setFont("Helvetica-Bold", 11)
        c.drawString(obs_x, obs_y, "OBSERVACIONES:")
        
        # Manejo de texto largo para observaciones
        c.setFont("Helvetica", 10)
        
        # Función para dividir texto
        def split_text(text, max_width):
            lines = []
            words = text.split()
            current_line = []
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                if c.stringWidth(test_line, "Helvetica", 10) <= max_width:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                    current_line = [word]
            
            if current_line:
                lines.append(' '.join(current_line))
            
            return lines
        
        # Dividir observaciones
        max_obs_width_superior = width - line_x - 2.5*cm
        max_obs_width_inferior = 10*cm
        
        obs_lines_superior = []
        obs_lines_inferior = []
        
        for line in observaciones.split("\n"):
            obs_lines_superior.extend(split_text(line, max_obs_width_superior))
            obs_lines_inferior.extend(split_text(line, max_obs_width_inferior))
        
        # Dibujar observaciones superiores
        text_object = c.beginText(obs_x, obs_y - 0.7*cm)
        text_object.setLeading(12)
        for line in obs_lines_superior[:8]:
            text_object.textLine(line)
        c.drawText(text_object)
        
        # ======== LÍNEA HORIZONTAL DIVISORIA ========
        c.line(margin_left, line_y_horizontal, width - margin_right, line_y_horizontal)
        
        # ======== SECCIÓN INFERIOR ========
        
        # Número grande rotado (vertical) a la izquierda
        c.saveState()
        c.translate(2*cm, line_y_horizontal - 1*cm)
        c.rotate(-90)
        c.setFont("Helvetica-Bold", 90)
        c.drawString(0, 0, num_recogida)
        c.restoreState()
        
        # Información del cliente en el CENTRO
        center_x = width / 3
        
        # Posiciones ajustadas para línea más baja
        info_start_y = line_y_horizontal - 1*cm
        
        c.setFont("Helvetica-Bold", 16)
        c.drawString(center_x, info_start_y, f"{apellido}, {nombre}")
        
        c.setFont("Helvetica-Bold", 12)
        c.drawString(center_x, info_start_y - 0.8*cm, f"Fecha ingreso: {fecha_ingreso}")
        c.drawString(center_x, info_start_y - 1.6*cm, f"Fecha entrega: {fecha_entrega}")
        c.drawString(center_x, info_start_y - 2.4*cm, telefono)
        c.drawString(center_x, info_start_y - 3.2*cm, f"Nº pedido: {num_pedido}")
        
        # Observaciones inferior
        obs_y_inf = info_start_y - 4*cm
        c.setFont("Helvetica-Bold", 11)
        c.drawString(center_x, obs_y_inf, "OBSERVACIONES:")
        
        c.setFont("Helvetica", 10)
        text_object2 = c.beginText(center_x, obs_y_inf - 0.7*cm)
        text_object2.setLeading(11)
        
        for line in obs_lines_inferior[:15]:
            text_object2.textLine(line)
        
        c.drawText(text_object2)

    def guardarPDFpedidoTemporal(self, numero_pedido):
        """Versión simplificada para un solo pedido"""
        # Buscar el pedido por número
        fila = self.df_pedidos[self.df_pedidos["Pedido"] == numero_pedido]

        if fila.empty:
            QMessageBox.warning(self, "Error", f"No se encontró el pedido {numero_pedido}.")
            return

        pedido = fila.iloc[0]
        num_pedido = str(pedido["Pedido"])

        # Crear archivo temporal para el PDF
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False, prefix=f'Pedido_{num_pedido}_') as temp_file:
            temp_filename = temp_file.name

        # Crear PDF directamente en el archivo temporal
        c = canvas.Canvas(temp_filename, pagesize=letter)
        width, height = letter

        # Dibujar el pedido usando la función común
        self.dibujarPDF(c, pedido, width, height)
        
        # ======== GUARDAR Y PROCESAR ========
        c.save()
        
        # Imprimir usando el sistema
        success, message = self.imprimir_con_dialogo_sistema(temp_filename)
        
        # Esperar un poco y luego eliminar
        time.sleep(2)
        
        try:
            os.unlink(temp_filename)
        except:
            pass
        
        if success:
            QMessageBox.information(self, "Éxito", message)
        else:
            QMessageBox.warning(self, "Información", message)

    def imprimirTodosLosPedidosElaborados(self):        
        # Usar el DataFrame filtrado actual
        if hasattr(self, "df_filtrado_actual") and not self.df_filtrado_actual.empty:
            df_a_imprimir = self.df_filtrado_actual.copy()
        else:
            df_a_imprimir = self.df_pedidos.copy()
        
        # Solo los elaborados
        df_elaborados = df_a_imprimir[df_a_imprimir["Elaborado"] == True]
        
        if df_elaborados.empty:
            QMessageBox.information(self, "Sin datos", "No hay pedidos elaborados en la vista actual para imprimir.")
            return
        
        # Crear archivo temporal (MULTIPÁGINA)
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False, prefix='PedidosElaborados_') as temp_file:
            temp_filename = temp_file.name

        try:
            # Crear PDF multipágina
            c = canvas.Canvas(temp_filename, pagesize=letter)
            width, height = letter

            for idx, (_, pedido) in enumerate(df_elaborados.iterrows()):
                if idx > 0:
                    c.showPage()
                self.dibujarPDF(c, pedido, width, height)

            # Guardar PDF temporal
            c.save()

            # Abrir con app del sistema (NO guardar permanentemente)
            success, message = self.imprimir_con_dialogo_sistema(temp_filename)

            # Feedback al usuario
            if success:
                QMessageBox.information(self, "Éxito", message)
            else:
                QMessageBox.warning(self, "Información", message)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al generar el PDF: {str(e)}")

        finally:
            # Borrar temporal después de un momento
            time.sleep(2)
            try:
                os.unlink(temp_filename)
            except:
                pass

    def mantenerCoherenciaFechasIngreso(self):
        if self.fechaIngresoDesde.date().toPyDate() > self.fechaIngresoHasta.date().toPyDate():
            self.fechaIngresoHasta.setDate(self.fechaIngresoDesde.date().toPyDate())
        else:
            return

    def mantenerCoherenciaFechasEntrega(self):
        if self.fechaEntregaDesde.date().toPyDate() > self.fechaEntregaHasta.date().toPyDate():
            self.fechaEntregaHasta.setDate(self.fechaEntregaDesde.date().toPyDate())
        else:
            return

    def actualizarPantalla(self):
        self.cargarTablaPedidos()

class EntregaPedidos(QMainWindow):
    def __init__(self, stacked):
        super(EntregaPedidos, self).__init__()
        loadUi(resource_path("interfaces/entregaPedidos.ui"), self)
        self.stacked = stacked
        self.nav = nav
        
        #Botones para pasar de una ventana a otra
        self.menuPantallaPrincipal.clicked.connect(lambda: self.nav.go(0))
        self.menuIntroduccionPedidos.clicked.connect(lambda: self.nav.go(1))
        self.menuElaboracionPedidos.clicked.connect(lambda: self.nav.go(2))
        self.menuEntregaPedidos.clicked.connect(lambda: self.nav.go(3))        
        self.menuConsultaPedidos.clicked.connect(lambda: self.nav.go(4))
        self.menuConsultaCompras.clicked.connect(lambda: self.nav.go(5))
        self.menuConsultaArticulos.clicked.connect(lambda: self.nav.go(6))
        
        #Establecer como fecha por defecto ahora hace un año
        self.fechaIngresoDesde.setDate(QDate.currentDate())
        self.fechaIngresoHasta.setDate(QDate.currentDate())
        self.fechaEntregaDesde.setDate(QDate.currentDate())
        self.fechaEntregaHasta.setDate(QDate.currentDate())
        
        #Variables para ordenamiento
        self._columna_orden_actual = None
        self._orden_ascendente_actual = True
        
        #cargar la tabla al iniciar
        self.cargarTablaPedidos()
        self.btnActualizar.clicked.connect(self.cargarTablaPedidos)
        
        # Conectar el clic del encabezado con la función personalizada de orden
        self.tablaPedidos.horizontalHeader().sectionClicked.connect(self.ordenarPorColumna)
        
        # Variable auxiliar para alternar ascendente/descendente
        self._orden_desc = False
        self.tablaPedidos.setSortingEnabled(False)

        #Se llaman los filtros
        self.txtNumPedido.textChanged.connect(self.filtrarTabla)
        self.txtNombreCliente.textChanged.connect(self.filtrarTabla)
        self.txtApellidoCliente.textChanged.connect(self.filtrarTabla)
        self.txtTelefonoCliente.textChanged.connect(self.filtrarTabla)

        self.fechaIngresoDesde.dateChanged.connect(self.filtrarTabla)
        self.fechaIngresoHasta.dateChanged.connect(self.filtrarTabla)
        self.fechaEntregaDesde.dateChanged.connect(self.filtrarTabla)
        self.fechaEntregaHasta.dateChanged.connect(self.filtrarTabla)

        self.boxElaborado.stateChanged.connect(self.filtrarTabla)
        self.boxEntregado.stateChanged.connect(self.filtrarTabla)

        #Mantener coherencia en fechas
        self.fechaIngresoDesde.dateChanged.connect(self.mantenerCoherenciaFechasIngreso)
        self.fechaEntregaDesde.dateChanged.connect(self.mantenerCoherenciaFechasEntrega)

        #boton de limpiar
        self.btnLimpiar.clicked.connect(self.limpiarFiltros)

        self.tablaPedidos.cellChanged.connect(self.onCellChanged)

    def filtrarTabla(self):
        # Desactivar ordenamiento temporalmente para evitar conflicto durante el filtrado
        self.tablaPedidos.setSortingEnabled(False)

        # Obtener valores de los widgets de filtro
        filtro_numero = self.txtNumPedido.text().strip().lower()
        filtro_nombre = self.txtNombreCliente.text().strip().lower()
        filtro_apellido = self.txtApellidoCliente.text().strip().lower()
        filtro_telefono = self.txtTelefonoCliente.text().strip().lower()

        fecha_ingreso_desde = self.fechaIngresoDesde.date().toPyDate() if self.fechaIngresoDesde.date().isValid() else None
        fecha_ingreso_hasta = self.fechaIngresoHasta.date().toPyDate() if self.fechaIngresoHasta.date().isValid() else None
        fecha_entrega_desde = self.fechaEntregaDesde.date().toPyDate() if self.fechaEntregaDesde.date().isValid() else None
        fecha_entrega_hasta = self.fechaEntregaHasta.date().toPyDate() if self.fechaEntregaHasta.date().isValid() else None

        elaborado_checked = self.boxElaborado.isChecked()
        entregado_checked = self.boxEntregado.isChecked()

        # Crear copia del DataFrame original
        df_filtrado = self.df_pedidos.copy()

        # Filtros de texto
        if filtro_numero:
            df_filtrado = df_filtrado[df_filtrado["Pedido"].astype(str).str.lower().str.contains(filtro_numero, regex=False)]
        if filtro_nombre:
            df_filtrado = df_filtrado[df_filtrado["Nombre"].astype(str).str.lower().str.contains(filtro_nombre, regex=False)]
        if filtro_apellido:
            df_filtrado = df_filtrado[df_filtrado["Apellido"].astype(str).str.lower().str.contains(filtro_apellido, regex=False)]
        if filtro_telefono:
            df_filtrado = df_filtrado[df_filtrado["Telefono"].astype(str).str.lower().str.contains(filtro_telefono, regex=False)]

        # Convertimos a datetime
        fechas_ingreso = pd.to_datetime(df_filtrado["Encargo"], format="%d-%m-%Y", errors="coerce")
        fechas_entrega = pd.to_datetime(df_filtrado["Entrega"], format="%d-%m-%Y", errors="coerce")
        
        # Eliminamos filas con fechas inválidas
        mask_fechas_validas = fechas_ingreso.notna() & fechas_entrega.notna()
        df_filtrado = df_filtrado[mask_fechas_validas]
        fechas_ingreso = fechas_ingreso[mask_fechas_validas]
        fechas_entrega = fechas_entrega[mask_fechas_validas]

        # Filas válidas
        mascara_validas = fechas_ingreso.notna() & fechas_entrega.notna()

        df_filtrado = df_filtrado[mascara_validas].reset_index(drop=True)
        fechas_ingreso = fechas_ingreso[mascara_validas].reset_index(drop=True)
        fechas_entrega = fechas_entrega[mascara_validas].reset_index(drop=True)
        
        # Eliminamos filas con fechas inválidas
        df_filtrado = df_filtrado[fechas_ingreso.notna() & fechas_entrega.notna()]
        fechas_ingreso = fechas_ingreso[fechas_ingreso.notna()]
        fechas_entrega = fechas_entrega[fechas_entrega.notna()]
        
        #Filtros por fechas
        mask = fechas_ingreso.notna() & fechas_entrega.notna()

        if fecha_ingreso_desde:
            mask &= fechas_ingreso >= pd.Timestamp(fecha_ingreso_desde)
        if fecha_ingreso_hasta:
            mask &= fechas_ingreso <= pd.Timestamp(fecha_ingreso_hasta)
            
        if fecha_entrega_desde:
            mask &= fechas_entrega >= pd.Timestamp(fecha_entrega_desde)
        if fecha_entrega_hasta:
            mask &= fechas_entrega <= pd.Timestamp(fecha_entrega_hasta)

        df_filtrado = df_filtrado[mask].reset_index(drop=True)
            
        # Filtros booleanos
        if elaborado_checked:
            df_filtrado = df_filtrado[df_filtrado["Elaborado"] == True]
        if entregado_checked:
            df_filtrado = df_filtrado[df_filtrado["Entregado"] == True]

        # Evitar filas vacías y resetear índices
        df_filtrado = df_filtrado.dropna(how="all").reset_index(drop=True)
        
        #Guardamos el resultado filtrado actual
        self.df_filtrado_actual = df_filtrado.copy()

        # Mostrar el DataFrame filtrado
        self.mostrarTabla(df_filtrado)

        if hasattr(self, '_columna_orden_actual') and self._columna_orden_actual:
                if self._columna_orden_actual in df_filtrado.columns:
                    # Re-aplicar el ordenamiento al DataFrame filtrado
                    df_ordenado = self.aplicarOrdenamiento(df_filtrado, self._columna_orden_actual, self._orden_ascendente_actual)
                    self.mostrarTabla(df_ordenado)

    def cargarTablaPedidos(self):
        
        #carga los datos del CSV en el table widget
        nombre_archivo = "bases_de_datos/pedidos.csv"
        
        if not os.path.exists(nombre_archivo):
            #si no existe, muestra una tabla vacia
            self.tablaPedidos.setRowCount(0)
            self.tablaPedidos.setColumnCount(0)
            self.df_pedidos = pd.DataFrame()
            return
        
        #leer datos con pandas
        try:
            df = pd.read_csv(nombre_archivo, dtype=str, encoding="utf-8-sig")
        except Exception as e:
            print(f"Error al leer CSV: {e}")
            df = pd.DataFrame()
        
        # Limpiar posibles espacios
        df.columns = df.columns.str.strip()
        
        # Quitar filas completamente vacías
        df = df.dropna(how="all")

        # Quitar filas sin fechas (encargo o entrega)
        df = df[df["Encargo"].notna() & df["Entrega"].notna()]
        
        # Convertir columnas booleanas
        if "Elaborado" in df.columns:
            df["Elaborado"] = df["Elaborado"].astype(str).str.strip().str.lower().isin(["true", "1", "sí", "si"])
        if "Entregado" in df.columns:
            df["Entregado"] = df["Entregado"].astype(str).str.strip().str.lower().isin(["true", "1", "sí", "si"])

        self.df_pedidos = df
        
        #INICIALIZAR ENCABEZADOS SIN INDICADORES
        
        #Columnas a mostrar
        columnas_cliente = ["Pedido", "Nombre", "Apellido", "Telefono","Encargo", "Entrega", "Observaciones", "Elaborado", "Entregado", "Recogida"]
        # Filtrar solo las columnas que existen en el DataFrame
        columnas_cliente = [col for col in columnas_cliente if col in df.columns]
        df = df[columnas_cliente].copy()
        #columnas_originales = list(df.columns)
        #idx_modificacion = columnas_originales.index("Modificar")
        #nueva_columna = columnas_originales.copy()
        #nueva_columna.insert(idx_modificacion + 1, "Imprimir")
        
        self.tablaPedidos.setColumnCount(len(columnas_cliente))
        for i, nombre in enumerate(columnas_cliente):
            self.tablaPedidos.setHorizontalHeaderItem(i, QtWidgets.QTableWidgetItem(nombre))
        
        # Solo reiniciar si no hay columna ordenada actualmente
        if self._columna_orden_actual is None:
            self._columna_orden_actual = None
            self._orden_ascendente_actual = True

        self.filtrarTabla()
        
        self.tablaPedidos.resizeColumnsToContents()    

    def aplicarOrdenamiento(self, df, columna, ascendente):
        #Aplica el ordenamiento actual a un DataFrame
        df_ordenado = df.copy()
        
        # Detectar si la columna es fecha por su nombre
        columnas_fecha = ["Encargo", "Entrega"]

        if columna in columnas_fecha:
            try:
                # Convertir a datetime asegurando el formato día-mes-año
                df_ordenado["_fecha_tmp"] = pd.to_datetime(
                    df_ordenado[columna],
                    format="%d-%m-%Y",
                    errors="coerce"
                )
                
                # Eliminar filas con fechas inválidas
                df_ordenado = df_ordenado[df_ordenado["_fecha_tmp"].notna()]
                
                # Ordenar con datetime
                df_ordenado = df_ordenado.sort_values(
                    by="_fecha_tmp",
                    ascending=ascendente,
                    ignore_index=True
                )

                # Eliminar columna auxiliar
                df_ordenado.drop(columns=["_fecha_tmp"], inplace=True)
                
            except Exception as e:
                print(f"Error al ordenar fechas: {e}")
                # Fallback: ordenamiento normal
                df_ordenado = df_ordenado.sort_values(
                    by=columna,
                    ascending=ascendente,
                    ignore_index=True
                )

        else:
            # Orden normal para columnas no fecha
            df_ordenado = df_ordenado.sort_values(
                by=columna,
                ascending=ascendente,
                ignore_index=True
            )
        
        return df_ordenado

    def limpiarFiltros(self):
        #Limpia todos los QLineEdit y QDateEdit de los filtros
        self.txtNumPedido.clear()
        self.txtNombreCliente.clear()
        self.txtApellidoCliente.clear()
        self.txtTelefonoCliente.clear()
        self.boxElaborado.setCheckState(0)
        self.boxEntregado.setCheckState(0)

        #Establecer como fecha por defecto ahora hace y después de un año
        self.fechaIngresoDesde.setDate(QDate.currentDate())
        self.fechaIngresoHasta.setDate(QDate.currentDate())
        
        self.fechaEntregaDesde.setDate(QDate.currentDate())
        self.fechaEntregaHasta.setDate(QDate.currentDate())

        self.filtrarTabla()

    def mostrarTabla(self, df):    
        self.df_filtrado_actual = df.copy()
        # Desactivar ordenamiento mientras se actualiza la tabla
        self.tablaPedidos.setSortingEnabled(False)
        self.tablaPedidos.clearContents()
        
        # Desconectar todas las señales cellChanged existentes
        try:
            self.tablaPedidos.cellChanged.disconnect()
        except:
            pass  # Si no estaba conectada, no hay problema
        
        #Ahora agregamos una columna extra para los botones
        #columnas_originales = list(df.columns)
        
        #Columnas a mostrar
        columnas_cliente = ["Pedido", "Nombre", "Apellido", "Telefono","Encargo", "Entrega", "Observaciones", "Elaborado", "Entregado", "Recogida"]
        # Filtrar solo las columnas que existen en el DataFrame
        columnas_cliente = [col for col in columnas_cliente if col in df.columns]
        df = df[columnas_cliente].copy()
        
        #Creamos una columna adicional solo para esta tabla para el botón de imprimir:
        idx_modificacion = columnas_cliente.index("Entregado")
        nueva_columna = columnas_cliente.copy()
        
        #ACTUALIZAR ENCABEZADOS MANTENIENDO INDICADORES DE ORDEN
        for i, nombre_columna in enumerate(nueva_columna):
            # Si esta columna es la que está ordenada, mantener el indicador
            nombre_columna_limpio = nombre_columna.replace(" ▲", "").replace(" ▼", "")  #Limpiar
            if self._columna_orden_actual == nombre_columna_limpio:  #Comparar con limpio
                if self._orden_ascendente_actual:
                    nombre_con_indicador = f"{nombre_columna} ▲"
                else:
                    nombre_con_indicador = f"{nombre_columna} ▼"
                self.tablaPedidos.setHorizontalHeaderItem(i, QtWidgets.QTableWidgetItem(nombre_con_indicador))
            else:
                # Si no tiene indicador, establecer nombre normal
                self.tablaPedidos.setHorizontalHeaderItem(i, QtWidgets.QTableWidgetItem(nombre_columna))
        
        self.tablaPedidos.setRowCount(len(df))
        
        #Iterar usando el índice del DataFrame ordenado
        for posicion_tabla in range(len(df)):
            fila = df.iloc[posicion_tabla]
            #Determinar si el pedido ya está elaborado o entregado
            elaborado = bool(fila["Elaborado"])
            entregado = bool(fila["Entregado"])
            fila_bloqueada = elaborado or entregado
            fila_boton_entregar = elaborado==True and entregado==False
            
            #color de texto en rojo si está bloqueada (entregado o elaborado)
            color_texto = QtGui.QColor("red") if fila_bloqueada else QtGui.QColor("black")
            
            # Recorre todas las columnas del df dinámicamente
            for j, col in enumerate(columnas_cliente):
                col_destino = j
                valor = "" if pd.isna(fila[col]) else str(fila[col])
                item = QtWidgets.QTableWidgetItem(valor)
                item.setForeground(QtGui.QBrush(color_texto))
                self.tablaPedidos.setItem(posicion_tabla, col_destino, item)  

            # Checkbox de "Elaborado"
            chk_elaborado = QtWidgets.QTableWidgetItem()
            chk_elaborado.setFlags(QtCore.Qt.ItemIsEnabled)
            chk_elaborado.setCheckState(QtCore.Qt.Checked if fila["Elaborado"] else QtCore.Qt.Unchecked)
            self.tablaPedidos.setItem(posicion_tabla, 7, chk_elaborado)

            # Checkbox de "Entregado"
            chk_entregado = QtWidgets.QTableWidgetItem()

            if fila["Elaborado"]:
                # Solo si está elaborado se puede marcar/desmarcar
                chk_entregado.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
            else:
                # No elaborado = solo lectura
                chk_entregado.setFlags(QtCore.Qt.ItemIsEnabled)

            chk_entregado.setCheckState(QtCore.Qt.Checked if fila["Entregado"] else QtCore.Qt.Unchecked)

            self.tablaPedidos.setItem(posicion_tabla, 8, chk_entregado)
            
        
        # Conectar la señal cellChanged UNA SOLA VEZ después de crear toda la tabla
        self.tablaPedidos.cellChanged.connect(self.onCellChanged)
        QTimer.singleShot(0, self.tablaPedidos.resizeColumnsToContents)

    def ordenarPorColumna(self, indice):
        nombre_columna = self.tablaPedidos.horizontalHeaderItem(indice).text()
        
        #LIMPIAR EL NOMBRE DE LA COLUMNA (quitar ▲/▼)
        nombre_columna_limpio = nombre_columna.replace(" ▲", "").replace(" ▼", "")

        # Si la columna es de botones o columnas especiales
        if nombre_columna_limpio in ["Modificar", "Imprimir"]:
            return

        #DETERMINAR DIRECCIÓN DEL ORDEN
        # Si es la misma columna, alternar dirección
        if self._columna_orden_actual == nombre_columna_limpio:
            self._orden_ascendente_actual = not self._orden_ascendente_actual
        else:
            # Si es una columna diferente, orden ascendente por defecto
            self._orden_ascendente_actual = True
            self._columna_orden_actual = nombre_columna_limpio

        #ACTUALIZAR INDICADOR VISUAL
        self.actualizarIndicadorOrden(indice, self._orden_ascendente_actual)

        # Tomar el DF actual (filtrado o completo)
        if hasattr(self, "df_filtrado_actual"):
            df_a_ordenar = self.df_filtrado_actual.copy()
        else:
            df_a_ordenar = self.df_pedidos.copy()
        
        df_ordenado = df_a_ordenar.copy()

        # Detectar si la columna es fecha por su nombre
        columnas_fecha = ["Encargo", "Entrega"]

        if nombre_columna_limpio in columnas_fecha:
            try:
                # Convertir a datetime asegurando el formato día-mes-año
                df_ordenado["_fecha_tmp"] = pd.to_datetime(
                    df_ordenado[nombre_columna_limpio],
                    format="%d-%m-%Y",
                    errors="coerce"
                )
                
                # Eliminar filas con fechas inválidas
                df_ordenado = df_ordenado[df_ordenado["_fecha_tmp"].notna()]
                
                # Ordenar con datetime
                df_ordenado = df_ordenado.sort_values(
                    by="_fecha_tmp",
                    ascending=self._orden_ascendente_actual,
                    ignore_index=True
                )

                # Eliminar columna auxiliar
                df_ordenado.drop(columns=["_fecha_tmp"], inplace=True)
                
            except Exception as e:
                print(f"Error al ordenar fechas: {e}")
                # Fallback: ordenamiento normal
                df_ordenado = df_ordenado.sort_values(
                    by=nombre_columna_limpio,
                    ascending=self._orden_ascendente_actual,
                    ignore_index=True
                )

        else:
            # Orden normal para columnas no fecha
            df_ordenado = df_ordenado.sort_values(
                by=nombre_columna_limpio,
                ascending=self._orden_ascendente_actual,
                ignore_index=True
            )

        # Guardar nuevo DF ordenado
        self.df_filtrado_actual = df_ordenado.copy()

        # Mostrar tabla ordenada
        self.mostrarTabla(df_ordenado)

    def actualizarIndicadorOrden(self, indice_columna, ascendente):
        #Actualiza el indicador visual de orden en el encabezado
        header = self.tablaPedidos.horizontalHeader()
        
        #LIMPIAR INDICADORES ANTERIORES
        for i in range(self.tablaPedidos.columnCount()):
            item_actual = self.tablaPedidos.horizontalHeaderItem(i)
            if item_actual:
                nombre_actual = item_actual.text()
                # Remover flechas anteriores
                nombre_limpio = nombre_actual.replace(" ▲", "").replace(" ▼", "")
                if nombre_limpio != nombre_actual:  # Si tenía indicador
                    item_actual.setText(nombre_limpio)
        
        #AGREGAR NUEVO INDICADOR
        item_actual = self.tablaPedidos.horizontalHeaderItem(indice_columna)
        if item_actual:
            nombre_actual = item_actual.text()
            nombre_limpio = nombre_actual.replace(" ▲", "").replace(" ▼", "")  # Limpiar por si acaso
            
            if ascendente:
                nuevo_nombre = f"{nombre_limpio} ▲"
            else:
                nuevo_nombre = f"{nombre_limpio} ▼"
            
            item_actual.setText(nuevo_nombre)

    def marcarComoEntregado(self, pedido, row):
        # 1) Actualizar DataFrame principal
        idx = self.df_pedidos[self.df_pedidos["Pedido"] == pedido].index
        if len(idx) == 0:
            QMessageBox.warning(self, "Error", f"No se encontró el pedido {pedido}.")
            return

        self.df_pedidos.at[idx[0], "Entregado"] = True

        # 2) Guardar en CSV
        nombre_archivo = "bases_de_datos/pedidos.csv"
        try:
            self.df_pedidos.to_csv(nombre_archivo, index=False, encoding="utf-8-sig")
        except:
            QMessageBox.warning(self, "Error", "No se pudo guardar el archivo.")
            return

        # 3) Actualizar visualmente SOLO esa fila
        row_count = self.tablaPedidos.columnCount()

        # Pintar fila en rojo
        for col in range(row_count):
            item = self.tablaPedidos.item(row, col)
            if item:
                item.setForeground(QtGui.QBrush(QtGui.QColor("red")))

        # 4) Volver checkbox “Entregado” en solo lectura
        col_entregado = 8  # ajusta si cambia
        chk = self.tablaPedidos.item(row, col_entregado)
        if chk:
            chk.setFlags(QtCore.Qt.ItemIsEnabled)
            chk.setCheckState(QtCore.Qt.Checked)

        # 5) Actualizar df_filtrado_actual si hay filtros activos
        if hasattr(self, "df_filtrado_actual") and not self.df_filtrado_actual.empty:
            idx_fil = self.df_filtrado_actual[self.df_filtrado_actual["Pedido"] == pedido].index
            if len(idx_fil) > 0:
                self.df_filtrado_actual.at[idx_fil[0], "Entregado"] = True
    
    def onCellChanged(self, row, column):
        # Verificar que esté elaborado
        elaborado_item = self.tablaPedidos.item(row, 7)  # columna Elaborado
        if not elaborado_item or elaborado_item.checkState() != QtCore.Qt.Checked:
            return
        # Columna "Entregado" (ajusta si cambia el orden)
        col_entregado = 8  

        if column != col_entregado:
            return

        pedido_item = self.tablaPedidos.item(row, 0)
        if not pedido_item:
            return

        pedido = pedido_item.text()
        item = self.tablaPedidos.item(row, column)

        nuevo_estado = item.checkState() == QtCore.Qt.Checked

        # Evitar recursión
        self.tablaPedidos.blockSignals(True)
        try:
            self.actualizarEntregadoCSV(pedido, nuevo_estado)
        finally:
            self.tablaPedidos.blockSignals(False)

    def actualizarEntregadoCSV(self, pedido, estado):
        idx = self.df_pedidos[self.df_pedidos["Pedido"] == pedido].index
        if len(idx) == 0:
            return

        idx = idx[0]
        self.df_pedidos.at[idx, "Entregado"] = estado

        try:
            self.df_pedidos.to_csv(
                "bases_de_datos/pedidos.csv",
                index=False,
                encoding="utf-8-sig"
            )
        except PermissionError:
            QMessageBox.warning(
                self,
                "Archivo en uso",
                "Cierre pedidos.csv antes de continuar."
            )

    def mantenerCoherenciaFechasIngreso(self):
        if self.fechaIngresoDesde.date().toPyDate() > self.fechaIngresoHasta.date().toPyDate():
            self.fechaIngresoHasta.setDate(self.fechaIngresoDesde.date().toPyDate())
        else:
            return

    def mantenerCoherenciaFechasEntrega(self):
        if self.fechaEntregaDesde.date().toPyDate() > self.fechaEntregaHasta.date().toPyDate():
            self.fechaEntregaHasta.setDate(self.fechaEntregaDesde.date().toPyDate())
        else:
            return

    def actualizarPantalla(self):
        self.cargarTablaPedidos()

class ConsultaPedidos(QMainWindow):
    def __init__(self, stacked):
        super(ConsultaPedidos, self).__init__()
        loadUi(resource_path("interfaces/consultaPedidos.ui"), self)
        self.stacked = stacked
        self.nav = nav
        
        #Botones para pasar de una ventana a otra
        self.menuPantallaPrincipal.clicked.connect(lambda: self.nav.go(0))
        self.menuIntroduccionPedidos.clicked.connect(lambda: self.nav.go(1))
        self.menuElaboracionPedidos.clicked.connect(lambda: self.nav.go(2))
        self.menuEntregaPedidos.clicked.connect(lambda: self.nav.go(3))
        self.menuConsultaPedidos.clicked.connect(lambda: self.nav.go(4))
        self.menuConsultaCompras.clicked.connect(lambda: self.nav.go(5))
        self.menuConsultaArticulos.clicked.connect(lambda: self.nav.go(6))

        #Establecer como fecha por defecto ahora hace un año
        self.fechaIngresoDesde.setDate(QDate.currentDate())
        self.fechaIngresoHasta.setDate(QDate.currentDate())
        self.fechaEntregaDesde.setDate(QDate.currentDate())
        self.fechaEntregaHasta.setDate(QDate.currentDate())
        
        # Variable auxiliar para alternar ascendente/descendente
        self._orden_desc = False
        self._columna_orden_actual = None
        self._orden_ascendente_actual = True
        self.tablaPedidos.setSortingEnabled(False)
        
        #cargar la tabla al iniciar
        self.cargarTablaPedidos()
        self.btnActualizar.clicked.connect(self.cargarTablaPedidos)
        
        # Conectar el clic del encabezado con la función personalizada de orden
        self.tablaPedidos.horizontalHeader().sectionClicked.connect(self.ordenarPorColumna)

        #Se llaman los filtros
        self.txtNumPedido.textChanged.connect(self.filtrarTabla)
        self.txtNombreCliente.textChanged.connect(self.filtrarTabla)
        self.txtApellidoCliente.textChanged.connect(self.filtrarTabla)
        self.txtTelefonoCliente.textChanged.connect(self.filtrarTabla)

        self.fechaIngresoDesde.dateChanged.connect(self.filtrarTabla)
        self.fechaIngresoHasta.dateChanged.connect(self.filtrarTabla)
        self.fechaEntregaDesde.dateChanged.connect(self.filtrarTabla)
        self.fechaEntregaHasta.dateChanged.connect(self.filtrarTabla)

        self.boxElaborado.stateChanged.connect(self.filtrarTabla)
        self.boxEntregado.stateChanged.connect(self.filtrarTabla)
        
        #Mantener coherencia en fechas
        self.fechaIngresoDesde.dateChanged.connect(self.mantenerCoherenciaFechasIngreso)
        self.fechaEntregaDesde.dateChanged.connect(self.mantenerCoherenciaFechasEntrega)

        #boton de limpiar
        self.btnLimpiar.clicked.connect(self.limpiarFiltros)
        
        #Doble click sobre la tabla hará que se abra un dialogo aparte para modificar ese registro en específico
        self.tablaPedidos.cellClicked.connect(self.abrirEditor)

    def filtrarTabla(self):
        # Desactivar ordenamiento temporalmente para evitar conflicto durante el filtrado
        self.tablaPedidos.setSortingEnabled(False)

        # Obtener valores de los widgets de filtro
        filtro_numero = self.txtNumPedido.text().strip().lower()
        filtro_nombre = self.txtNombreCliente.text().strip().lower()
        filtro_apellido = self.txtApellidoCliente.text().strip().lower()
        filtro_telefono = self.txtTelefonoCliente.text().strip().lower()

        fecha_ingreso_desde = self.fechaIngresoDesde.date().toPyDate() if self.fechaIngresoDesde.date().isValid() else None
        fecha_ingreso_hasta = self.fechaIngresoHasta.date().toPyDate() if self.fechaIngresoHasta.date().isValid() else None
        fecha_entrega_desde = self.fechaEntregaDesde.date().toPyDate() if self.fechaEntregaDesde.date().isValid() else None
        fecha_entrega_hasta = self.fechaEntregaHasta.date().toPyDate() if self.fechaEntregaHasta.date().isValid() else None

        elaborado_checked = self.boxElaborado.isChecked()
        entregado_checked = self.boxEntregado.isChecked()

        # Crear copia del DataFrame original
        df_filtrado = self.df_pedidos.copy()

        # Filtros de texto
        if filtro_numero:
            df_filtrado = df_filtrado[df_filtrado["Pedido"].astype(str).str.lower().str.contains(filtro_numero, regex=False)]
        if filtro_nombre:
            df_filtrado = df_filtrado[df_filtrado["Nombre"].astype(str).str.lower().str.contains(filtro_nombre, regex=False)]
        if filtro_apellido:
            df_filtrado = df_filtrado[df_filtrado["Apellido"].astype(str).str.lower().str.contains(filtro_apellido, regex=False)]
        if filtro_telefono:
            df_filtrado = df_filtrado[df_filtrado["Telefono"].astype(str).str.lower().str.contains(filtro_telefono, regex=False)]

        # Filtros por fechas
        if fecha_ingreso_desde:
            df_filtrado = df_filtrado[pd.to_datetime(df_filtrado["Encargo"], format="%d-%m-%Y", dayfirst=True) >= pd.to_datetime(fecha_ingreso_desde)]
        if fecha_ingreso_hasta:
            df_filtrado = df_filtrado[pd.to_datetime(df_filtrado["Encargo"], format="%d-%m-%Y", dayfirst=True) <= pd.to_datetime(fecha_ingreso_hasta)]
        if fecha_entrega_desde:
            df_filtrado = df_filtrado[pd.to_datetime(df_filtrado["Entrega"], format="%d-%m-%Y", dayfirst=True) >= pd.to_datetime(fecha_entrega_desde)]
        if fecha_entrega_hasta:
            df_filtrado = df_filtrado[pd.to_datetime(df_filtrado["Entrega"], format="%d-%m-%Y", dayfirst=True) <= pd.to_datetime(fecha_entrega_hasta)]
            
        # Filtros booleanos
        if elaborado_checked:
            df_filtrado = df_filtrado[df_filtrado["Elaborado"] == True]
        if entregado_checked:
            df_filtrado = df_filtrado[df_filtrado["Entregado"] == True]

        # Evitar filas vacías y resetear índices
        df_filtrado = df_filtrado.dropna(how="all").reset_index(drop=True)
        
        #Guardamos el resultado filtrado actual
        self.df_filtrado_actual = df_filtrado.copy()

        # Mostrar el DataFrame filtrado
        self.mostrarTabla(df_filtrado)

        # Reactivar el ordenamiento después del filtrado
        #self.tablaPedidos.setSortingEnabled(True)
    
    def cargarTablaPedidos(self):
        
        #carga los datos del CSV en el table widget
        nombre_archivo = "bases_de_datos/pedidos.csv"
        
        if not os.path.exists(nombre_archivo):
            #si no existe, muestra una tabla vacia
            self.tablaPedidos.setRowCount(0)
            self.tablaPedidos.setColumnCount(0)
            self.df_pedidos = pd.DataFrame()
            return
        
        #leer datos con pandas
        try:
            df = pd.read_csv(nombre_archivo, dtype=str, encoding="utf-8-sig")
        except Exception as e:
            print(f"Error al leer CSV: {e}")
            df = pd.DataFrame()
        
        # Limpiar posibles espacios
        df.columns = df.columns.str.strip()
        
        #Quitar filas completamente vacías
        df = df.dropna(how="all")
        
        #Quitar filas sin fechas (encargo o entrega)
        df = df[df["Encargo"].notna() & df["Entrega"].notna()]
        
        # Convertir columnas booleanas
        if "Elaborado" in df.columns:
            df["Elaborado"] = df["Elaborado"].astype(str).str.strip().str.lower().isin(["true", "1", "sí", "si"])
        if "Entregado" in df.columns:
            df["Entregado"] = df["Entregado"].astype(str).str.strip().str.lower().isin(["true", "1", "sí", "si"])

        self.df_pedidos = df
        
        #INICIALIZAR ENCABEZADOS SIN INDICADORES
        #columnas_originales = list(df.columns)
        
        self.columnas_visibles = ["Pedido", "Nombre", "Apellido", "Telefono", "Encargo", "Entrega", "Observaciones", "Elaborado", "Entregado", "Modificar", "Eliminar", "Recogida"]
        columnas_originales = [c for c in self.columnas_visibles if c in df.columns]
        
        # Columnas visuales extra
        columnas_extra = ["Eliminar"]
        total_columnas = len(columnas_originales) + len(columnas_extra)

        self.tablaPedidos.setColumnCount(total_columnas)
        headers = columnas_originales + columnas_extra
        self.tablaPedidos.setHorizontalHeaderLabels(headers)

        # Solo reiniciar si no hay columna ordenada actualmente
        if self._columna_orden_actual is None:
            self._columna_orden_actual = None
            self._orden_ascendente_actual = True
        
        # Ajustar tamaño de columnas automáticamente
        self.tablaPedidos.setSortingEnabled(False)
        
        self.filtrarTabla()
        
        self.tablaPedidos.resizeColumnsToContents()     

    def aplicarOrdenamiento(self, df, columna, ascendente):
        #Aplica el ordenamiento actual a un DataFrame
        df_ordenado = df.copy()
        
        # Detectar si la columna es fecha por su nombre
        columnas_fecha = ["Encargo", "Entrega"]

        if columna in columnas_fecha:
            try:
                # Convertir a datetime asegurando el formato día-mes-año
                df_ordenado["_fecha_tmp"] = pd.to_datetime(
                    df_ordenado[columna],
                    format="%d-%m-%Y",
                    errors="coerce"
                )
                
                # Eliminar filas con fechas inválidas
                df_ordenado = df_ordenado[df_ordenado["_fecha_tmp"].notna()]
                
                # Ordenar con datetime
                df_ordenado = df_ordenado.sort_values(
                    by="_fecha_tmp",
                    ascending=ascendente,
                    ignore_index=True
                )

                # Eliminar columna auxiliar
                df_ordenado.drop(columns=["_fecha_tmp"], inplace=True)
                
            except Exception as e:
                print(f"Error al ordenar fechas: {e}")
                # Fallback: ordenamiento normal
                df_ordenado = df_ordenado.sort_values(
                    by=columna,
                    ascending=ascendente,
                    ignore_index=True
                )

        else:
            # Orden normal para columnas no fecha
            df_ordenado = df_ordenado.sort_values(
                by=columna,
                ascending=ascendente,
                ignore_index=True
            )
        
        return df_ordenado

    def limpiarFiltros(self):
        #Limpia todos los QLineEdit y QDateEdit de los filtros
        self.txtNumPedido.clear()
        self.txtNombreCliente.clear()
        self.txtApellidoCliente.clear()
        self.txtTelefonoCliente.clear()
        self.boxElaborado.setCheckState(0)
        self.boxEntregado.setCheckState(0)

        #Establecer como fecha por defecto ahora hace y después de un año
        self.fechaIngresoDesde.setDate(QDate.currentDate())
        self.fechaIngresoHasta.setDate(QDate.currentDate())
        
        self.fechaEntregaDesde.setDate(QDate.currentDate())
        self.fechaEntregaHasta.setDate(QDate.currentDate())

        self.filtrarTabla()

    def mostrarTabla(self, df):
        
        self.df_filtrado_actual = df.copy()
        # Desactivar ordenamiento mientras se actualiza la tabla
        self.tablaPedidos.setSortingEnabled(False)
        self.tablaPedidos.clearContents()
        
        #Ahora agregamos una columna extra para los botones
        #columnas_originales = list(df.columns)
        self.columnas_visibles = ["Pedido", "Nombre", "Apellido", "Telefono","Encargo", "Entrega", "Observaciones", "Elaborado", "Entregado", "Modificar", "Eliminar", "Recogida"]
        columnas_originales = [c for c in self.columnas_visibles if c in df.columns]
        columnas_extra = ["Eliminar"]
        total_columnas = len(columnas_originales) + len(columnas_extra)

        #ACTUALIZAR ENCABEZADOS MANTENIENDO INDICADORES DE ORDEN
        for i, nombre_columna in enumerate(columnas_originales):
            # Si esta columna es la que está ordenada, mantener el indicador
            nombre_columna_limpio = nombre_columna.replace(" ▲", "").replace(" ▼", "")
            if self._columna_orden_actual == nombre_columna_limpio:
                if self._orden_ascendente_actual:
                    nombre_con_indicador = f"{nombre_columna} ▲"
                else:
                    nombre_con_indicador = f"{nombre_columna} ▼"
                self.tablaPedidos.setHorizontalHeaderItem(i, QtWidgets.QTableWidgetItem(nombre_con_indicador))
            else:
                # Si no tiene indicador, establecer nombre normal
                self.tablaPedidos.setHorizontalHeaderItem(i, QtWidgets.QTableWidgetItem(nombre_columna))
                
        self.tablaPedidos.setColumnCount(total_columnas)
        self.tablaPedidos.setRowCount(len(df))

        for posicion_tabla in range(len(df)):
            fila = df.iloc[posicion_tabla]
            #Determinar si el pedido ya está elaborado o entregado
            elaborado = bool(fila["Elaborado"])
            entregado = bool(fila["Entregado"])
            fila_bloqueada = elaborado or entregado
            
            #color de texto en rojo si está bloqueada (entregado o elaborado)
            color_texto = QtGui.QColor("red") if fila_bloqueada else QtGui.QColor("black")
            
            # Recorre todas las columnas del df dinámicamente
            for j, col in enumerate(columnas_originales):
                valor = "" if pd.isna(fila[col]) else str(fila[col])
                item = QtWidgets.QTableWidgetItem(valor)
                item.setForeground(QtGui.QBrush(color_texto))
                self.tablaPedidos.setItem(posicion_tabla, j, item)

            # Checkbox de "Elaborado"
            chk_elaborado = QtWidgets.QTableWidgetItem()
            chk_elaborado.setFlags(QtCore.Qt.ItemIsEnabled)
            chk_elaborado.setCheckState(QtCore.Qt.Checked if fila["Elaborado"] else QtCore.Qt.Unchecked)
            self.tablaPedidos.setItem(posicion_tabla, 7, chk_elaborado)

            # Checkbox de "Entregado"
            chk_entregado = QtWidgets.QTableWidgetItem()
            chk_entregado.setFlags(QtCore.Qt.ItemIsEnabled)
            chk_entregado.setCheckState(QtCore.Qt.Checked if fila["Entregado"] else QtCore.Qt.Unchecked)
            self.tablaPedidos.setItem(posicion_tabla, 8, chk_entregado)
            
            
            # Solo agregar botón si el pedido NO está elaborado ni entregado
            if not fila_bloqueada:
                btn_editar = QtWidgets.QPushButton("Modificar")
                
                btn_editar.setStyleSheet("""
                    QPushButton {
                        background-color: rgb(0, 0, 0);
                        color: white;
                        border-radius: 10px;
                        padding: 3px 8px;
                    }

                    QPushButton:hover {
                        background-color: rgb(86, 86, 86);
                    }
                """)
                
                pedido_actual = str(fila["Pedido"])
                btn_editar.clicked.connect(lambda _, p=pedido_actual: self.abrirEditorPedido(p))
                self.tablaPedidos.setCellWidget(posicion_tabla, 9, btn_editar)
            else:
                # Agregar una celda vacía para mantener alineación visual
                self.tablaPedidos.setItem(posicion_tabla, 9, QtWidgets.QTableWidgetItem(""))

            # Botón ELIMINAR
            btn_eliminar = QtWidgets.QPushButton("Eliminar")
            btn_eliminar.setCursor(QtCore.Qt.PointingHandCursor)

            btn_eliminar.setStyleSheet("""
                QPushButton {
                    background-color: rgb(180, 0, 0);
                    color: white;
                    border-radius: 10px;
                    padding: 3px 8px;
                }
                QPushButton:hover {
                    background-color: rgb(220, 0, 0);
                }
            """)

            pedido_actual = str(fila["Pedido"])
            btn_eliminar.clicked.connect(lambda _, p=pedido_actual: self.confirmarEliminarPedido(p))

            self.tablaPedidos.setCellWidget(posicion_tabla, 11, btn_eliminar)

        # Reactivar ordenamiento
        #self.tablaPedidos.setSortingEnabled(True)
        QTimer.singleShot(0, self.tablaPedidos.resizeColumnsToContents)

    def confirmarEliminarPedido(self, pedido):
        respuesta = QMessageBox.question(
            self,
            "Eliminar pedido",
            f"¿Está seguro que desea eliminar el pedido {pedido}?\n\n"
            "Esta acción no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if respuesta == QMessageBox.Yes:
            self.eliminarPedido(pedido)

    def eliminarPedido(self, pedido):
        ruta = "bases_de_datos/pedidos.csv"

        try:
            df = pd.read_csv(ruta, encoding="utf-8-sig")
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))
            return

        df = df[df["Pedido"] != pedido]

        try:
            df.to_csv(ruta, index=False, encoding="utf-8-sig")
        except PermissionError:
            QMessageBox.warning(
                self,
                "Archivo en uso",
                "Cierre pedidos.csv antes de continuar."
            )
            return

        QMessageBox.information(
            self,
            "Pedido eliminado",
            f"El pedido {pedido} fue eliminado correctamente."
        )

        self.cargarTablaPedidos()

    def abrirEditorDesdeBoton(self, pedido):
        self.abrirEditorPedido(pedido)

    def abrirEditor(self, fila, columna):
        pedido = self.tablaPedidos.item(fila, 0).text()
        self.abrirEditorPedido(pedido)

    def abrirEditorPedido(self, pedido):
        # Buscar en el DF
        idx_real_list = self.df_pedidos[self.df_pedidos["Pedido"] == pedido].index
        if len(idx_real_list) == 0:
            QMessageBox.warning(self, "Error", f"No se encontró el pedido {pedido}.")
            return

        idx_real = idx_real_list[0]
        registro = self.df_pedidos.loc[idx_real]

        # Abrir editor
        editor = EditarPedidoDialog(registro, self)
        resultado = editor.exec_()

        if not resultado:
            return  # usuario canceló

        # Obtener datos
        datos = editor.obtener_datos()

        # Validar teléfono
        if str(datos["Telefono"]).isdigit():
            datos["Telefono"] = int(datos["Telefono"])

        # Actualizar DF
        self.df_pedidos.loc[idx_real] = datos

        # Guardar CSV
        nombre_archivo = "bases_de_datos/pedidos.csv"
        try:
            self.df_pedidos.to_csv(nombre_archivo, index=False, encoding="utf-8-sig")
        except PermissionError:
            QMessageBox.warning(
                self,
                "Archivo en uso",
                "No se puede modificar el pedido porque 'pedidos.csv' está abierto.\n"
                "Ciérrelo e intente de nuevo."
            )
            # Reabrir editor porque no se guardó nada
            self.abrirEditorPedido(pedido)
            return

        # Mensaje de éxito:
        QMessageBox.information(self, "Carnicería", f"Pedido {pedido} actualizado exitosamente.")

        # Refrescar vista actual (filtros activos o tabla completa)
        if hasattr(self, "df_filtrado_actual") and not self.df_filtrado_actual.empty:
            self.filtrarTabla()
        else:
            self.mostrarTabla(self.df_pedidos)
  
    def ordenarPorColumna(self, indice):
        nombre_columna = self.tablaPedidos.horizontalHeaderItem(indice).text()
        
        #LIMPIAR EL NOMBRE DE LA COLUMNA (quitar ▲/▼)
        nombre_columna_limpio = nombre_columna.replace(" ▲", "").replace(" ▼", "")

        # Si la columna es de botones o columnas especiales
        if nombre_columna_limpio in ["Modificar", "Imprimir"]:
            return

        #DETERMINAR DIRECCIÓN DEL ORDEN
        # Si es la misma columna, alternar dirección
        if self._columna_orden_actual == nombre_columna_limpio:
            self._orden_ascendente_actual = not self._orden_ascendente_actual
        else:
            # Si es una columna diferente, orden ascendente por defecto
            self._orden_ascendente_actual = True
            self._columna_orden_actual = nombre_columna_limpio

        #ACTUALIZAR INDICADOR VISUAL
        self.actualizarIndicadorOrden(indice, self._orden_ascendente_actual)

        # Tomar el DF actual (filtrado o completo)
        if hasattr(self, "df_filtrado_actual"):
            df_a_ordenar = self.df_filtrado_actual.copy()
        else:
            df_a_ordenar = self.df_pedidos.copy()
        
        df_ordenado = df_a_ordenar.copy()

        # Detectar si la columna es fecha por su nombre
        columnas_fecha = ["Encargo", "Entrega"]

        if nombre_columna_limpio in columnas_fecha:
            try:
                # Convertir a datetime asegurando el formato día-mes-año
                df_ordenado["_fecha_tmp"] = pd.to_datetime(
                    df_ordenado[nombre_columna_limpio],
                    format="%d-%m-%Y",
                    errors="coerce"
                )
                
                # Eliminar filas con fechas inválidas
                df_ordenado = df_ordenado[df_ordenado["_fecha_tmp"].notna()]
                
                # Ordenar con datetime
                df_ordenado = df_ordenado.sort_values(
                    by="_fecha_tmp",
                    ascending=self._orden_ascendente_actual,
                    ignore_index=True
                )

                # Eliminar columna auxiliar
                df_ordenado.drop(columns=["_fecha_tmp"], inplace=True)
                
            except Exception as e:
                print(f"Error al ordenar fechas: {e}")
                # Fallback: ordenamiento normal
                df_ordenado = df_ordenado.sort_values(
                    by=nombre_columna_limpio,
                    ascending=self._orden_ascendente_actual,
                    ignore_index=True
                )

        else:
            # Orden normal para columnas no fecha
            df_ordenado = df_ordenado.sort_values(
                by=nombre_columna_limpio,
                ascending=self._orden_ascendente_actual,
                ignore_index=True
            )

        # Guardar nuevo DF ordenado
        self.df_filtrado_actual = df_ordenado.copy()

        # Mostrar tabla ordenada
        self.mostrarTabla(df_ordenado)

    def actualizarIndicadorOrden(self, indice_columna, ascendente):
        #Actualiza el indicador visual de orden en el encabezado
        header = self.tablaPedidos.horizontalHeader()
        
        #LIMPIAR INDICADORES ANTERIORES
        for i in range(self.tablaPedidos.columnCount()):
            item_actual = self.tablaPedidos.horizontalHeaderItem(i)
            if item_actual:
                nombre_actual = item_actual.text()
                # Remover flechas anteriores
                nombre_limpio = nombre_actual.replace(" ▲", "").replace(" ▼", "")
                if nombre_limpio != nombre_actual:  # Si tenía indicador
                    item_actual.setText(nombre_limpio)
        
        #AGREGAR NUEVO INDICADOR
        item_actual = self.tablaPedidos.horizontalHeaderItem(indice_columna)
        if item_actual:
            nombre_actual = item_actual.text()
            nombre_limpio = nombre_actual.replace(" ▲", "").replace(" ▼", "")  # Limpiar por si acaso
            
            if ascendente:
                nuevo_nombre = f"{nombre_limpio} ▲"
            else:
                nuevo_nombre = f"{nombre_limpio} ▼"
            
            item_actual.setText(nuevo_nombre)
    
    def mantenerCoherenciaFechasIngreso(self):
        if self.fechaIngresoDesde.date().toPyDate() > self.fechaIngresoHasta.date().toPyDate():
            self.fechaIngresoHasta.setDate(self.fechaIngresoDesde.date().toPyDate())
        else:
            return
        
    def mantenerCoherenciaFechasEntrega(self):
        if self.fechaEntregaDesde.date().toPyDate() > self.fechaEntregaHasta.date().toPyDate():
            self.fechaEntregaHasta.setDate(self.fechaEntregaDesde.date().toPyDate())
        else:
            return

    def actualizarPantalla(self):
        self.cargarTablaPedidos()
      
class EditarPedidoDialog(QtWidgets.QDialog):
    def __init__(self, registro, parent=None):
        super().__init__(parent)
        loadUi(resource_path("interfaces/modificacionPedidosDialog.ui"), self)
        
        #Se guardan los cambios o se cancela la modificación
        self.btnCancelar.clicked.connect(self.reject)
        self.btnGuardarCambios.clicked.connect(self.guardarCambios)
        
        #Cargar artículos disponibles
        self.archivo_articulos = "bases_de_datos/articulos.csv"
        if os.path.exists(self.archivo_articulos):
            self.df_articulos = pd.read_csv(self.archivo_articulos)
            self.df_articulos = self.df_articulos.fillna("")
        else:
            QMessageBox.warning(self, "Error", "No se encontró la base de datos de artículos.")
            self.df_articulos = pd.DataFrame(columns=["id", "Nombre", "Familia", "Unidad"])
            self.df_articulos = self.df_articulos.fillna("")

        #Familias únicas
        self.familias = [""] + sorted(self.df_articulos["Familia"].dropna().unique().tolist())
        
        #Configurar combos dinámicos
        for i in range(1, 21):
            box_familia = getattr(self, f"boxFamilia{i}")
            box_producto = getattr(self, f"producto{i}")
            id_producto = getattr(self, f"idProducto{i}")
            unidad_producto = getattr(self, f"unidad{i}")
            cantidad = getattr(self, f"cantidad{i}")
            observacion = getattr(self, f"observaciones{i}")

            # Cargar familias
            box_familia.clear()
            box_familia.addItems(self.familias)

            # Inicializar productos vacíos
            box_producto.clear()
            box_producto.addItem("")

            # Conectar dinámicas
            box_familia.currentTextChanged.connect(lambda fam, i=i: self.actualizarProductos(i, fam))
            box_producto.currentTextChanged.connect(lambda prod, i=i: self.actualizarInfoProducto(i, prod))
        
        #Cargar datos del pedido
        self.cargarDatosPedido(registro)
        
        #Imprimir pedido
        self.btnImprimirPedido.clicked.connect(self.imprimirPedido)
        
    def cargarDatosPedido(self, registro):
        #reemplazar nan por cadena vacía en el registro
        registro = {k: ("" if pd.isna(v) else v) for k, v in registro.items()}
        
        # Datos generales
        self.txtNumPedido.setText(registro["Pedido"])
        self.txtNombreCliente.setText(registro["Nombre"])
        self.txtApellidoCliente.setText(registro["Apellido"])
        self.txtTelefonoCliente.setText(str(registro["Telefono"]))

        #Fechas
        try:
            fecha_encargo = QDate.fromString(str(registro["Encargo"]), "dd-MM-yyyy")
            if fecha_encargo.isValid():
                self.fechaIngresoPedido.setDate(fecha_encargo)
        except Exception:
            pass

        try:
            fecha_entrega = QDate.fromString(str(registro["Entrega"]), "dd-MM-yyyy")
            if fecha_entrega.isValid():
                self.fechaEntregaPedido.setDate(fecha_entrega)
        except Exception:
            pass
        
        #Observaciones y elaborado y entregado
        self.txtObservaciones.setPlainText("" if pd.isna(registro["Observaciones"]) else str(registro["Observaciones"]))
        self.boxElaborado.setChecked(bool(registro["Elaborado"]))
        self.boxEntregado.setChecked(bool(registro["Entregado"]))

        #Cargar productos del pedido
        for i in range(1, 21):
            familia_col = f"Familia{i}"
            producto_col = f"Producto{i}"
            id_col = f"ID{i}"
            cantidad_col = f"Cantidad{i}"
            unidad_col = f"Unidad{i}"
            obs_col = f"Obs{i}"

            if familia_col in registro and str(registro[familia_col]).strip():
                box_familia = getattr(self, f"boxFamilia{i}")
                box_producto = getattr(self, f"producto{i}")
                id_producto = getattr(self, f"idProducto{i}")
                unidad_producto = getattr(self, f"unidad{i}")
                cantidad = getattr(self, f"cantidad{i}")
                observacion = getattr(self, f"observaciones{i}")

                # Asignar familia (si no está en lista, agregar)
                familia_val = str(registro[familia_col]).strip()
                if familia_val not in self.familias:
                    box_familia.addItem(familia_val)
                box_familia.setCurrentText(familia_val)

                # Cargar productos asociados a esa familia
                self.actualizarProductos(i, familia_val)

                # Asignar producto
                producto_val = str(registro[producto_col]).strip()
                box_producto.setCurrentText(producto_val)

                # Asignar datos relacionados
                id_producto.setText(str(registro.get(id_col, "")))
                cantidad.setText(str(registro.get(cantidad_col, "")))
                unidad_producto.setText(str(registro.get(unidad_col, "")))
                observacion.setText(str(registro.get(obs_col, "")))
                
                # Si está elaborado o entregado → bloquear edición
                if bool(registro["Elaborado"]) or bool(registro["Entregado"]):
                    self.bloquearCampos()

    def bloquearCampos(self):
        # Bloquear campos generales
        self.txtNombreCliente.setReadOnly(True)
        self.txtApellidoCliente.setReadOnly(True)
        self.txtTelefonoCliente.setReadOnly(True)
        self.fechaIngresoPedido.setEnabled(False)
        self.fechaEntregaPedido.setEnabled(False)
        self.txtObservaciones.setReadOnly(True)

        # Bloquear los checkboxes
        self.boxElaborado.setEnabled(False)
        self.boxEntregado.setEnabled(False)

        # Bloquear productos (todos los 20)
        for i in range(1, 21):
            getattr(self, f"boxFamilia{i}").setEnabled(False)
            getattr(self, f"producto{i}").setEnabled(False)
            getattr(self, f"idProducto{i}").setReadOnly(True)
            getattr(self, f"unidad{i}").setReadOnly(True)
            getattr(self, f"cantidad{i}").setReadOnly(True)
            getattr(self, f"observaciones{i}").setReadOnly(True)

        # También desactivar botones
        self.btnGuardarCambios.setEnabled(False)
    
    #Se actualizan los combobox Productos al seleccionar una familia        
    def actualizarProductos(self, i, familia):
        box_producto = getattr(self, f"producto{i}")
        box_producto.blockSignals(True)
        box_producto.clear()
        box_producto.addItem("")

        if familia and familia in self.df_articulos["Familia"].values:
            productos = sorted(
                self.df_articulos.loc[self.df_articulos["Familia"] == familia, "Nombre"].dropna().unique().tolist()
            )
            box_producto.addItems(productos)

        box_producto.blockSignals(False)
    
    #Se actualiza el id producto y unidad según el producto seleccionado 
    def actualizarInfoProducto(self, i, producto):
        id_producto = getattr(self, f"idProducto{i}")
        unidad_producto = getattr(self, f"unidad{i}")

        if producto and producto in self.df_articulos["Nombre"].values:
            fila = self.df_articulos[self.df_articulos["Nombre"] == producto].iloc[0]
            id_producto.setText(str(fila["id"]))
            unidad_producto.setText(str(fila["Unidad"]))
        else:
            id_producto.clear()
            unidad_producto.clear()
    
    def guardarCambios(self):
        #Validar datos obligatorios
        if not self.txtNumPedido.text().strip():
            QMessageBox.warning(self, "Error", "El número de pedido no puede estar vacío.")
            return

        productos_validos = 0  # Contador de filas de productos completas
        
        #Validar consistencia en filas
        for i in range(1, 21):
            familia = getattr(self, f"boxFamilia{i}").currentText().strip()
            producto = getattr(self, f"producto{i}").currentText().strip()
            id_producto = getattr(self, f"idProducto{i}").text().strip()
            cantidad = getattr(self, f"cantidad{i}").text().strip()
            unidad = getattr(self, f"unidad{i}").text().strip()

            campos = [familia, producto, id_producto, cantidad, unidad]
            
            if any(campos) and not all(campos):
                QMessageBox.warning(self, "Error", f"Completa todos los campos del producto #{i} o déjalo completamente vacío.")
                return
            
            if all(campos):
                #Validar que las cantidades sí sean números
                try:
                    valor_cantidad = float(cantidad)
                except ValueError:
                    QMessageBox.warning(self, "Error", f"La cantidad del producto #{i} debe ser un número entero o decimal.")
                    return
                
                productos_validos += 1
                
        #Validar que haya al menos un producto
        if productos_validos == 0:
            QMessageBox.warning(self, "Error", "Debe haber al menos un producto completo en el pedido antes de guardar los cambios.")
            return
        
        
        #Mensaje de pedido actualizado
        self.done(1)
    
    #Guardar los cambios en el csv  
    def obtener_datos(self):
        datos = {
            "Pedido": self.txtNumPedido.text(),
            "Nombre": self.txtNombreCliente.text(),
            "Apellido": self.txtApellidoCliente.text(),
            "Telefono": self.txtTelefonoCliente.text(),
            "Encargo": self.fechaIngresoPedido.dateTime().toString("dd-MM-yyyy"),
            "Entrega": self.fechaEntregaPedido.dateTime().toString("dd-MM-yyyy"),
            "Observaciones": self.txtObservaciones.toPlainText().strip(),
            "Elaborado": self.boxElaborado.isChecked(),
            "Entregado": self.boxEntregado.isChecked()
        }

        # Agregar productos
        for i in range(1, 21):
            def limpiar(valor):
                return "" if (pd.isna(valor) or valor is None) else str(valor).strip()

            datos[f"Familia{i}"] = limpiar(getattr(self, f"boxFamilia{i}").currentText())
            datos[f"Producto{i}"] = limpiar(getattr(self, f"producto{i}").currentText())
            datos[f"ID{i}"] = limpiar(getattr(self, f"idProducto{i}").text())
            datos[f"Cantidad{i}"] = limpiar(getattr(self, f"cantidad{i}").text())
            datos[f"Unidad{i}"] = limpiar(getattr(self, f"unidad{i}").text())
            datos[f"Obs{i}"] = limpiar(getattr(self, f"observaciones{i}").text())

        return datos

    #Imprimir pedido    
    def imprimirPedido(self):
        numero_pedido = self.txtNumPedido.text().strip()

        if not numero_pedido:
            QMessageBox.warning(self, "Error", "No se pudo identificar el número de pedido.")
            return

        imprimir_pedido_por_numero(numero_pedido)
    
def imprimir_pedido_por_numero(numero_pedido):
    nombre_archivo = "bases_de_datos/pedidos.csv"

    if not os.path.exists(nombre_archivo):
        QMessageBox.warning(None, "Error", "No se encontró la base de datos de pedidos.")
        return

    df = pd.read_csv(nombre_archivo, dtype=str, encoding="utf-8-sig")
    df.columns = df.columns.str.strip()

    fila = df[df["Pedido"] == numero_pedido]

    if fila.empty:
        QMessageBox.warning(None, "Error", f"No se encontró el pedido {numero_pedido}.")
        return

    pedido = fila.iloc[0]

    with tempfile.NamedTemporaryFile(
        suffix=".pdf",
        delete=False,
        prefix=f"Pedido_{numero_pedido}_"
    ) as temp_file:
        temp_filename = temp_file.name

    c = canvas.Canvas(temp_filename, pagesize=letter)
    width, height = letter

    # REUTILIZA exactamente el mismo formato
    ElaboracionPedidos.dibujarPDF(
        None,  # no se usa self
        c,
        pedido,
        width,
        height
    )

    c.save()

    # Abrir / imprimir
    sistema = platform.system()
    try:
        if sistema == "Windows":
            os.startfile(temp_filename)
        elif sistema == "Darwin":
            subprocess.run(["lpr", temp_filename])
        elif sistema == "Linux":
            subprocess.run(["lp", temp_filename])
    except Exception as e:
        QMessageBox.warning(None, "Error", str(e))
        return

    QMessageBox.information(None, "Impresión", "Pedido enviado a impresión.")
    
class ConsultaCompras(QMainWindow):
    def __init__(self, stacked):
        super(ConsultaCompras, self).__init__()
        loadUi(resource_path("interfaces/consultaCompras.ui"), self)
        self.stacked = stacked
        self.nav = nav

        # Navegación entre pantallas
        self.menuPantallaPrincipal.clicked.connect(lambda: self.nav.go(0))
        self.menuIntroduccionPedidos.clicked.connect(lambda: self.nav.go(1))
        self.menuElaboracionPedidos.clicked.connect(lambda: self.nav.go(2))
        self.menuEntregaPedidos.clicked.connect(lambda: self.nav.go(3))
        self.menuConsultaPedidos.clicked.connect(lambda: self.nav.go(4))
        self.menuConsultaCompras.clicked.connect(lambda: self.nav.go(5))
        self.menuConsultaArticulos.clicked.connect(lambda: self.nav.go(6))

        # Filtros
        self.txtNombreProducto.textChanged.connect(self.filtrarTabla)
        self.txtFamiliaProducto.textChanged.connect(self.filtrarTabla)
        self.txtIdArticulo.textChanged.connect(self.filtrarTabla)
        self.fechaEntregaDesde.dateChanged.connect(self.filtrarTabla)
        self.fechaEntregaHasta.dateChanged.connect(self.filtrarTabla)
        
        #Fecha Hasta no puede ser menor a Desde
        self.fechaEntregaDesde.dateChanged.connect(self.mantenerCoherenciaFechas)
        
        #Limpiar filtros, actualizar tabla, imprimir tabla y exportar PDF
        self.btnLimpiar.clicked.connect(self.limpiarFiltros)
        self.btnActualizar.clicked.connect(self.cargarTablaCompras)
        self.btnImprimir.clicked.connect(self.imprimirTabla)
        self.btnGuardarPDF.clicked.connect(self.exportarPDF)
        
        #Por defecto se muestra con la fecha del día de mañana
        self.fechaEntregaHasta.setDate(QDate.currentDate().addDays(+1))
        self.fechaEntregaDesde.setDate(QDate.currentDate().addDays(+1))

        # Para ordenamiento
        self.tablaCompras.horizontalHeader().sectionClicked.connect(self.ordenarPorColumna)
        self._orden_desc = False

        # Cargar datos inicial
        self.cargarTablaCompras()

    #Cargar datos y sumarizar productos
    def cargarTablaCompras(self):
        
        self.tablaCompras.setSortingEnabled(False)
        
        nombre_archivo = "bases_de_datos/pedidos.csv"

        if not os.path.exists(nombre_archivo):
            self.df_compras = pd.DataFrame(columns=["FechaEntrega","Familia","Producto","ID","Cantidad","Unidad"])
            self.mostrarTabla(self.df_compras)
            return

        try:
            df = pd.read_csv(nombre_archivo, dtype=str, encoding="utf-8-sig")
        except Exception as e:
            print("Error al leer CSV:", e)
            self.df_compras = pd.DataFrame(columns=["FechaEntrega","Familia","Producto","ID","Cantidad","Unidad"])
            self.mostrarTabla(self.df_compras)
            return

        # Normalizar columnas y vacíos
        df.columns = df.columns.str.strip()
        df = df.fillna("").astype(str)

        # Parse fecha (guardamos la versión datetime para agrupar y luego la convertimos a string)
        df["Entrega_dt"] = pd.to_datetime(df["Entrega"], format="%d-%m-%Y", dayfirst=True, errors="coerce")

        productos = []

        def normalizar_texto(v):
            v = str(v).strip()
            if v.lower() in ["", "0", "nan", "none", ".", "-", "null"]:
                return ""
            return v

        # Un mapa opcional para normalizar unidades
        unidad_map = {
            "kilos": "kg",
            "kilogramos": "kg",
            "gramos": "Gramos",
            "gr": "Gramos",
            "unidad": "unidades",
            "uds": "unidades",
        }

        for _, row in df.iterrows():
            fecha_entrega = row["Entrega_dt"]

            for i in range(1, 21):
                fam = normalizar_texto(row.get(f"Familia{i}", ""))
                prod = normalizar_texto(row.get(f"Producto{i}", ""))
                art_id = normalizar_texto(row.get(f"ID{i}", ""))
                unidad_raw = normalizar_texto(row.get(f"Unidad{i}", ""))

                # normalizar unidad
                unidad = unidad_map.get(unidad_raw.lower(), unidad_raw)

                # cantidad convertir con seguridad
                cant_raw = str(row.get(f"Cantidad{i}", "")).replace(",", ".").strip()
                try:
                    cant = float(cant_raw) if cant_raw != "" else 0.0
                except:
                    cant = 0.0

                # Añadir sólo si hay un nombre de producto válido (no añadir si es "")
                if prod == "":
                    continue

                # Ignorar cantidades cero
                if cant == 0:
                    continue

                productos.append({
                    "FechaEntrega": fecha_entrega,
                    "Familia": fam,
                    "Producto": prod,
                    "ID": art_id,
                    "Cantidad": cant,
                    "Unidad": unidad
                })

        df_prod = pd.DataFrame(productos)

        # Si quedó vacío, crear df con columnas esperadas para no romper la UI
        if df_prod.empty:
            self.df_compras = pd.DataFrame(columns=["FechaEntrega","Familia","Producto","ID","Cantidad","Unidad"])
            self.df_filtrado_actual = self.df_compras.copy()
            self.mostrarTabla(self.df_compras)
            return

        # Normalizar columnas de texto antes del groupby (strip + lower si quieres)
        df_prod["Producto"] = df_prod["Producto"].astype(str).str.strip()
        df_prod["Familia"] = df_prod["Familia"].astype(str).str.strip()
        df_prod["ID"] = df_prod["ID"].astype(str).str.strip()
        df_prod["Unidad"] = df_prod["Unidad"].astype(str).str.strip()

        # Evitar filas donde Producto esté vacío (paranoia)
        df_prod = df_prod[df_prod["Producto"] != ""].reset_index(drop=True)

        # AGRUPAR: agrupar por fecha (datetime) y atributos relevantes, sumar Cantidad
        df_sum = df_prod.groupby(
            ["FechaEntrega", "Familia", "Producto", "ID", "Unidad"],
            as_index=False
        )["Cantidad"].sum()

        # Convertir fecha a texto para mostrar y filtrar (formato dd-mm-yyyy)
        df_sum["FechaEntrega"] = df_sum["FechaEntrega"].dt.strftime("%d-%m-%Y")

        # Guardar
        self.df_compras = df_sum.copy()
        self.df_filtrado_actual = df_sum.copy()

        # Mostrar
        self.mostrarTabla(self.df_compras)
        self.filtrarTabla()
        self.tablaCompras.setSortingEnabled(True)

    def filtrarTabla(self):
        self.tablaCompras.setSortingEnabled(False)
        # Si no hay datos, salir rápido
        if not hasattr(self, "df_compras") or self.df_compras.empty:
            # Mostrar estructura vacía para evitar restos en la UI
            self.mostrarTabla(pd.DataFrame(columns=["FechaEntrega","Familia","Producto","ID","Cantidad","Unidad"]))
            return

        df_f = self.df_compras.copy()

        # Filtros de texto
        filtro_nombre = self.txtNombreProducto.text().strip()
        filtro_familia = self.txtFamiliaProducto.text().strip()
        filtro_id = self.txtIdArticulo.text().strip()

        if filtro_nombre:
            df_f = df_f[df_f["Producto"].str.lower().str.contains(filtro_nombre.lower(), regex=False)]

        if filtro_familia:
            df_f = df_f[df_f["Familia"].str.lower().str.contains(filtro_familia.lower(), regex=False)]

        if filtro_id:
            df_f = df_f[df_f["ID"].str.lower().str.contains(filtro_id.lower(), regex=False)]

        # Filtro por fecha exacta (convertir QDate a string dd-mm-yyyy)
        fecha_desde = self.fechaEntregaDesde.date().toPyDate()
        fecha_hasta = self.fechaEntregaHasta.date().toPyDate()
        # Convertir columna a datetime
        df_f["_Entrega_dt"] = pd.to_datetime(df_f["FechaEntrega"], format="%d-%m-%Y", dayfirst=True, errors="coerce")
        
        # Aplicar rango
        df_f = df_f[
            (df_f["_Entrega_dt"] >= pd.to_datetime(fecha_desde)) &
            (df_f["_Entrega_dt"] <= pd.to_datetime(fecha_hasta))
        ]

        # Obtener fecha mínima y máxima del rango para cada producto
        df_f["_Entrega_dt"] = pd.to_datetime(df_f["FechaEntrega"], format="%d-%m-%Y", dayfirst=True, errors="coerce")

        agrupar = df_f.groupby(
            ["Familia", "Producto", "ID", "Unidad"],
            as_index=False
        ).agg({
            "Cantidad": "sum",
            "_Entrega_dt": ["min", "max"]
        })

        # Reparar columnas multiíndice
        agrupar.columns = ["Familia", "Producto", "ID", "Unidad", "Cantidad", "FechaMin", "FechaMax"]

        # Convertir rango de fechas a texto
        agrupar["FechaEntrega"] = agrupar["FechaMin"].dt.strftime("%d-%m-%Y") + " - " + agrupar["FechaMax"].dt.strftime("%d-%m-%Y")

        # Ordenar columnas en el orden esperado por la tabla
        agrupar = agrupar[["FechaEntrega", "Familia", "Producto", "ID", "Cantidad", "Unidad"]]

        self.df_filtrado_actual = agrupar.copy()
        self.mostrarTabla(agrupar)
        self.tablaCompras.setSortingEnabled(True)
        return

        # Evitar mostrar filas "fantasma" — quitar filas donde todas las columnas visuales estén vacías
        if not df_f.empty:
            # considera columnas que realmente muestras en la UI
            cols_visuales = ["FechaEntrega", "Familia", "Producto", "ID", "Cantidad", "Unidad"]
            # crear máscara donde exista por lo menos un valor no vacío
            mask_valid = df_f[cols_visuales].astype(str).apply(lambda row: any([c.strip() != "" and c.strip().lower() not in ["nan","none"] for c in row]), axis=1)
            df_f = df_f[mask_valid].reset_index(drop=True)

        self.df_filtrado_actual = df_f.copy()
        self.mostrarTabla(df_f)
        self.tablaCompras.setSortingEnabled(True)

    def mostrarTabla(self, df):
        self.tablaCompras.setSortingEnabled(False)
        # Asegurarse de que df tenga las columnas esperadas (para que la tabla no quede "desalineada")
        expected_cols = ["FechaEntrega","Familia","Producto","ID","Cantidad","Unidad"]
        if df is None or df.empty:
            # crear DataFrame vacío con columnas esperadas para evitar "filas sobrantes"
            df_to_show = pd.DataFrame(columns=expected_cols)
        else:
            # Hacer una copia y reset index
            df_to_show = df.copy().reset_index(drop=True)

            # Si faltan columnas, añadirlas vacías (defensa)
            for c in expected_cols:
                if c not in df_to_show.columns:
                    df_to_show[c] = ""

            # Mantener sólo las columnas esperadas (ordenarlas)
            df_to_show = df_to_show[expected_cols]

        # Limpieza completa de la tabla antes de pintar
        self.tablaCompras.setSortingEnabled(False)
        self.tablaCompras.clear()
        self.tablaCompras.setRowCount(0)
        self.tablaCompras.setColumnCount(0)

        columnas = list(df_to_show.columns)
        self.tablaCompras.setColumnCount(len(columnas))
        self.tablaCompras.setHorizontalHeaderLabels(columnas)
        self.tablaCompras.setRowCount(len(df_to_show))

        # Rellenar filas con seguridad (usar iloc para evitar índices no continuos)
        for i in range(len(df_to_show)):
            row = df_to_show.iloc[i]
            for j, col in enumerate(columnas):
                valor = "" if pd.isna(row[col]) else str(row[col])
                item = QtWidgets.QTableWidgetItem(valor)
                self.tablaCompras.setItem(i, j, item)

        self.tablaCompras.setSortingEnabled(True)
        QTimer.singleShot(0, self.tablaCompras.resizeColumnsToContents)

    #Ordenar Tabla
    def ordenarPorColumna(self, indice):
        self.tablaCompras.setSortingEnabled(False)
        df = (
            self.df_filtrado_actual.copy()
            if hasattr(self, "df_filtrado_actual") and not self.df_filtrado_actual.empty
            else self.df_compras.copy()
        )

        columna = df.columns[indice]
        asc = not self._orden_desc
        self._orden_desc = asc

        df_ord = df.sort_values(columna, ascending=asc, ignore_index=True)
        self.df_filtrado_actual = df_ord.copy()
        self.mostrarTabla(df_ord)
        self.filtrarTabla
        self.tablaCompras.setSortingEnabled(True)

    #Limpiar filtros
    def limpiarFiltros(self):
        self.txtNombreProducto.clear()
        self.txtFamiliaProducto.clear()
        self.txtIdArticulo.clear()
        self.fechaEntregaDesde.setDate(QDate.currentDate().addDays(+1))
        self.fechaEntregaHasta.setDate(QDate.currentDate().addDays(+1))

        self.df_filtrado_actual = self.df_compras.copy()
        self.mostrarTabla(self.df_compras)
        self.filtrarTabla()

    #Imprimir tabla
    def imprimirTabla(self):
        from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
        from PyQt5.QtGui import QTextDocument

        row_count = self.tablaCompras.rowCount()
        col_count = self.tablaCompras.columnCount()

        if row_count == 0:
            QtWidgets.QMessageBox.warning(self, "Sin datos", "No hay datos para imprimir.")
            return

        # Construir tabla HTML
        html = """
        <html>
        <head>
            <style>
                table {
                    border-collapse: collapse;
                    width: 100%;
                    font-size: 12px;
                }
                th, td {
                    border: 1px solid #555;
                    padding: 4px;
                    text-align: left;
                }
                th {
                    background-color: #ddd;
                    font-weight: bold;
                }
            </style>
        </head>
        <body>
            <h2>Reporte de Compras</h2>
            <p>Mostrando datos filtrados actualmente en pantalla.</p>
            <table>
                <tr>
        """

        # Encabezados
        for col in range(col_count):
            html += f"<th>{self.tablaCompras.horizontalHeaderItem(col).text()}</th>"
        html += "</tr>"

        # Filas visibles
        for row in range(row_count):
            html += "<tr>"
            for col in range(col_count):
                item = self.tablaCompras.item(row, col)
                valor = item.text() if item else ""
                html += f"<td>{valor}</td>"
            html += "</tr>"

        html += "</table></body></html>"

        # Crear documento imprimible
        document = QTextDocument()
        document.setHtml(html)

        printer = QPrinter()
        printer.setPageSize(QPrinter.A4)
        printer.setOrientation(QPrinter.Portrait)

        dialog = QPrintDialog(printer, self)
        if dialog.exec_() == QPrintDialog.Accepted:
            document.print_(printer)

    #Generar tabla en HTML solo para guardarlo en el PDF
    def generarHTMLTabla(self):
        row_count = self.tablaCompras.rowCount()
        col_count = self.tablaCompras.columnCount()

        if row_count == 0:
            return None

        html = """
        <html>
        <head>
            <style>
                table {
                    border-collapse: collapse;
                    width: 100%;
                    font-size: 12px;
                }
                th, td {
                    border: 1px solid #555;
                    padding: 4px;
                    text-align: left;
                }
                th {
                    background-color: #ddd;
                    font-weight: bold;
                }
            </style>
        </head>
        <body>
            <h2>Reporte de Compras</h2>
            <p>Mostrando datos filtrados actualmente en pantalla.</p>
            <table>
                <tr>
        """

        # ENCABEZADOS
        for col in range(col_count):
            header = self.tablaCompras.horizontalHeaderItem(col).text()
            html += f"<th>{header}</th>"
        html += "</tr>"

        # FILAS
        for row in range(row_count):
            html += "<tr>"
            for col in range(col_count):
                item = self.tablaCompras.item(row, col)
                valor = item.text() if item else ""
                html += f"<td>{valor}</td>"
            html += "</tr>"

        html += "</table></body></html>"
        return html

    #Exportar a PDF
    def exportarPDF(self):
        html = self.generarHTMLTabla()

        if html is None:
            QtWidgets.QMessageBox.warning(self, "Sin datos", "No hay datos para exportar.")
            return

        # Obtener fechas para el nombre
        fecha_desde = self.fechaEntregaDesde.date().toString("dd-MM-yyyy")
        fecha_hasta = self.fechaEntregaHasta.date().toString("dd-MM-yyyy")

        nombre_archivo = f"ReporteCompras - {fecha_desde} - {fecha_hasta}.pdf"

        # Crear documento imprimible
        document = QTextDocument()
        document.setHtml(html)

        printer = QPrinter()
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(nombre_archivo)
        printer.setPageSize(QPrinter.A4)
        printer.setPageMargins(12, 12, 12, 12, QPrinter.Millimeter)

        try:
            document.print_(printer)
            QtWidgets.QMessageBox.information(
                self,
                "PDF generado",
                f"El archivo se guardó como:\n{nombre_archivo}"
            )
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Error", f"No se pudo generar el PDF:\n{e}"
            )

    #Mantener fechas coherentes (Fecha Hasta no puede ser menor a Desde)
    def mantenerCoherenciaFechas(self):
        if self.fechaEntregaDesde.date().toPyDate() > self.fechaEntregaHasta.date().toPyDate():
            self.fechaEntregaHasta.setDate(self.fechaEntregaDesde.date().toPyDate())
        else:
            return

    def actualizarPantalla(self):
            self.cargarTablaCompras()

class ConsultaArticulos(QMainWindow):
    def __init__(self, stacked):
        super(ConsultaArticulos, self).__init__()
        loadUi(resource_path("interfaces/consultaArticulos.ui"), self)
        self.stacked = stacked
        self.nav = nav
        
        #Botones para pasar de una ventana a otra
        self.menuPantallaPrincipal.clicked.connect(lambda: self.nav.go(0))
        self.menuIntroduccionPedidos.clicked.connect(lambda: self.nav.go(1))
        self.menuElaboracionPedidos.clicked.connect(lambda: self.nav.go(2))
        self.menuEntregaPedidos.clicked.connect(lambda: self.nav.go(3))
        self.menuConsultaPedidos.clicked.connect(lambda: self.nav.go(4))
        self.menuConsultaCompras.clicked.connect(lambda: self.nav.go(5))
        self.menuConsultaArticulos.clicked.connect(lambda: self.nav.go(6))
        
        #Se carga automáticamente la tabla articulos
        self.cargarTablaArticulos()
        self.btnActualizar.clicked.connect(self.cargarTablaArticulos)
        
        # Conectar el clic del encabezado con la función personalizada de orden
        self.tablaArticulos.horizontalHeader().sectionClicked.connect(self.ordenarPorColumna)
        
        # Variable auxiliar para alternar ascendente/descendente
        self._orden_desc = False
        
        #Agregar artículo
        self.btnAgregaArticulo.clicked.connect(self.agregarArticulo)
        #Agregar familias
        self.btnAgregarFamilia.clicked.connect(self.agregarFamilia)
        
        #Se llaman los filtros
        self.txtIdProducto.textChanged.connect(self.filtrarTabla)
        self.txtFamilia.textChanged.connect(self.filtrarTabla)
        self.txtNombre.textChanged.connect(self.filtrarTabla)
        self.txtUnidad.textChanged.connect(self.filtrarTabla)

        #boton de limpiar
        self.btnLimpiar.clicked.connect(self.limpiarFiltros)
        
    def filtrarTabla(self):
        # Desactivar ordenamiento temporalmente para evitar conflicto durante el filtrado
        self.tablaArticulos.setSortingEnabled(False)

        # Obtener valores de los widgets de filtro
        filtro_id = self.txtIdProducto.text().strip().lower()
        filtro_familia = self.txtFamilia.text().strip().lower()
        filtro_Nombre = self.txtNombre.text().strip().lower()
        filtro_Unidad = self.txtUnidad.text().strip().lower()

        # Si todos los filtros están vacíos, mostrar todo
        if not any([filtro_id, filtro_familia, filtro_Nombre, filtro_Unidad]):
            self.mostrarTabla(self.df_articulos)
            self.tablaArticulos.setSortingEnabled(True)
            return
            
        # Crear copia del DataFrame original
        df_filtrado = self.df_articulos.copy()

        # Filtros de texto
        if filtro_id:
            df_filtrado = df_filtrado[df_filtrado["id"].astype(str).str.lower().str.contains(filtro_id, regex=False)]
        if filtro_familia:
            df_filtrado = df_filtrado[df_filtrado["Familia"].astype(str).str.lower().str.contains(filtro_familia, regex=False)]
        if filtro_Nombre:
            df_filtrado = df_filtrado[df_filtrado["Nombre"].astype(str).str.lower().str.contains(filtro_Nombre, regex=False)]
        if filtro_Unidad:
            df_filtrado = df_filtrado[df_filtrado["Unidad"].astype(str).str.lower().str.contains(filtro_Unidad, regex=False)]

        # Evitar filas vacías y resetear índices
        df_filtrado = df_filtrado.dropna(how="all").reset_index(drop=True)
        
        #Guardamos el resultado filtrado actual
        self.df_filtrado_actual = df_filtrado.copy()

        # Mostrar el DataFrame filtrado
        self.mostrarTabla(df_filtrado)

        # Reactivar el ordenamiento después del filtrado
        self.tablaArticulos.setSortingEnabled(True)
     
    def limpiarFiltros(self):
        #Limpia todos los QLineEdit de los filtros
        self.txtIdProducto.clear()
        self.txtNombre.clear()
        self.txtFamilia.clear()
        self.txtUnidad.clear()
        self.cargarTablaArticulos()
            
    def mostrarTabla(self, df):
        self.df_filtrado_actual = df.copy()
        # Desactivar ordenamiento mientras se actualiza la tabla
        self.tablaArticulos.setSortingEnabled(False)
        self.tablaArticulos.clearContents()
        
        #Ahora agregamos una columna extra para los botones
        columnas_originales = list(df.columns)
        self.tablaArticulos.setColumnCount(len(columnas_originales) + 2)
        self.tablaArticulos.setHorizontalHeaderLabels(columnas_originales + ["Modificar"] + ["Eliminar"])
    
        self.tablaArticulos.setRowCount(len(df))
        
        for i, fila in df.iterrows():
            # Rellenar las columnas según el DataFrame
            for j, col in enumerate(columnas_originales):
                valor = str(fila[col]) if not pd.isna(fila[col]) else ""
                item = QtWidgets.QTableWidgetItem(valor)
                self.tablaArticulos.setItem(i, j, item)
            
            #Botón de modificar
            btn_modificar = QtWidgets.QPushButton("Modificar")
            id_actual = str(fila["id"])
            btn_modificar.clicked.connect(lambda _, id_art=id_actual: self.abrirEditor(id_art))
            btn_modificar.setStyleSheet("""
                    QPushButton {
                        background-color: rgb(0, 0, 0);
                        color: white;
                        border-radius: 10px;
                        padding: 3px 8px;
                    }

                    QPushButton:hover {
                        background-color: rgb(86, 86, 86);
                    }
                """)
            self.tablaArticulos.setCellWidget(i, len(columnas_originales), btn_modificar)
            
            #Botón de eliminar
            btn_eliminar = QtWidgets.QPushButton("Eliminar")
            id_actual = str(fila["id"])
            btn_eliminar.clicked.connect(lambda _, id_art=id_actual: self.eliminarArticulo(id_art))
            btn_eliminar.setStyleSheet("""
                    QPushButton {
                        background-color: rgb(0, 0, 0);
                        color: white;
                        border-radius: 10px;
                        padding: 3px 8px;
                    }

                    QPushButton:hover {
                        background-color: rgb(86, 86, 86);
                    }
                """)
            self.tablaArticulos.setCellWidget(i, (len(columnas_originales))+1, btn_eliminar)
        
        # Reactivar ordenamiento
        self.tablaArticulos.setSortingEnabled(True)
        QTimer.singleShot(0, self.tablaArticulos.resizeColumnsToContents)

    def cargarTablaArticulos(self):
        
        nombre_archivo = "bases_de_datos/articulos.csv"
        
        if not os.path.exists(nombre_archivo):
            self.tablaArticulos.setRowCount(0)
            self.tablaArticulos.setColumnCount(0)
            self.df_articulos = pd.DataFrame()
            return

        try:
            df = pd.read_csv(nombre_archivo, dtype=str, encoding="utf-8-sig")
        except Exception as e:
            print(f"Error al leer CSV: {e}")
            df = pd.DataFrame()

        df.columns = df.columns.str.strip()
        self.df_articulos = df.copy()
        
        hay_filtros = any([
            self.txtIdProducto.text().strip(),
            self.txtFamilia.text().strip(),
            self.txtNombre.text().strip(),
            self.txtUnidad.text().strip()
        ])
        
        if hay_filtros:
            # Reaplica el filtrado automáticamente
            self.filtrarTabla()
        else:
            # Si no hay filtros, muestra todo
            self.mostrarTabla(self.df_articulos)
        
    def agregarArticulo(self):
        #Abre el diálogo para agregar artículos
        agregar = AgregarArticulosDialog(self)
        agregar.exec_()
        self.cargarTablaArticulos()

    def agregarFamilia(self):
        #Abre el diálogo para agregar artículos
        agregar = AgregarFamiliaDialog(self)
        agregar.exec_()
        self.cargarTablaArticulos()
        
    def ordenarPorColumna(self, indice):
        # Si la columna es la de botones, no hacer nada
        if self.tablaArticulos.horizontalHeaderItem(indice).text() == "Modificar" or self.tablaArticulos.horizontalHeaderItem(indice).text() == "Eliminar":
            return  # Ignorar ordenamiento en esta columna
        
    
        # Obtener el DataFrame actual mostrado (filtrado o completo)
        if hasattr(self, "df_filtrado_actual") and not self.df_filtrado_actual.empty:
            df_a_ordenar = self.df_filtrado_actual.copy()
        else:
            df_a_ordenar = self.df_pedidos.copy()

        # Obtener el nombre real de la columna
        nombre_columna = df_a_ordenar.columns[indice]

        # Alternar entre ascendente y descendente
        ascending = not self._orden_desc
        self._orden_desc = ascending

        # Ordenar el DataFrame visible
        df_ordenado = df_a_ordenar.sort_values(
            by=nombre_columna,
            ascending=ascending,
            ignore_index=True
        )

        # Guardar el nuevo DataFrame ordenado como el actual
        self.df_filtrado_actual = df_ordenado.copy()

        # Refrescar la tabla
        self.mostrarTabla(df_ordenado)

    def eliminarArticulo(self, id_art):
        respuesta = QMessageBox.question(
            self, "Confirmar eliminación",
            f"¿Desea eliminar el artículo con ID {id_art}?",
            QMessageBox.Yes | QMessageBox.No
        )
        if respuesta == QMessageBox.Yes:
            self.df_articulos = self.df_articulos[self.df_articulos["id"] != id_art]
            
            try:
                self.df_articulos.to_csv("bases_de_datos/articulos.csv", index=False, encoding="utf-8-sig")
            except PermissionError:
                QMessageBox.warning(self, "Archivo en uso",
                    "No se puede eliminar el artículo porque 'articulos.csv' está abierto.\n"
                    "Ciérrelo e intente de nuevo.")
                return
            
            self.cargarTablaArticulos()

    def abrirEditor(self, pedido):
        #Abre el diálogo de edición desde el botón de la tabla.
         # Buscar el índice real del pedido en el DataFrame completo
        idx_real = self.df_articulos[self.df_articulos["id"] == pedido].index
        if len(idx_real) == 0:
            QMessageBox.warning(self, "Error", f"No se encontró el pedido {pedido}.")
            return

        idx_real = idx_real[0]
        registro = self.df_articulos.loc[idx_real]

        # Abrir editor
        editor = EditarArticuloDialog(registro, self)
        if editor.exec_():
            datos = editor.obtener_datos()

            # Actualizar y guardar
            self.df_articulos.loc[idx_real] = datos
            nombre_archivo = "bases_de_datos/articulos.csv"
            self.df_articulos.to_csv(nombre_archivo, index=False, encoding="utf-8-sig")

            try:
                self.df_articulos.to_csv(nombre_archivo, index=False, encoding="utf-8-sig")
            except PermissionError:
                QMessageBox.warning(self, "Archivo en uso",
                    "No se puede editar el artículo porque 'articulos.csv' está abierto.\n"
                    "Ciérrelo e intente de nuevo.")
                return

            # Refrescar la tabla con filtros activos si los hay
            if hasattr(self, "df_filtrado_actual") and not self.df_filtrado_actual.empty:
                self.filtrarTabla()
            else:
                self.mostrarTabla(self.df_articulos)

    def actualizarPantalla(self):
            self.cargarTablaArticulos()

class EditarArticuloDialog(QtWidgets.QDialog):
    def __init__(self, registro, parent=None):
        super().__init__(parent)
        loadUi(resource_path("interfaces/modificarArticulo.ui"), self)
        
        #Se guardan los cambios o se cancela la modificación
        self.btnCancelar.clicked.connect(self.reject)
        self.btnGuardarCambios.clicked.connect(self.accept)
        
        #cargar las familias al comboBox
        try:
            df_familias = pd.read_csv("bases_de_datos/familias.csv", encoding="utf-8-sig")
            self.boxFamilia.clear()
            for f in df_familias["Familia"].dropna().unique():
                self.boxFamilia.addItem(f)
        except Exception as e:
            print(f"Error cargando familias.csv: {e}")
            
        #cargar las unidades al comboBox
        try:
            df_unidades = pd.read_csv("bases_de_datos/unidades.csv", encoding="utf-8-sig")
            self.boxUnidad.clear()
            # Asegurarte de usar el nombre correcto de la columna
            columna_unidad = [c for c in df_unidades.columns if "unidad" in c.lower()][0]
            for u in df_unidades[columna_unidad].dropna().unique():
                self.boxUnidad.addItem(u)
        except Exception as e:
            print(f"Error cargando unidades.csv: {e}")
        
        #Se cargan los datos
        self.txtIdProducto.setText(registro["id"])
        self.txtNombreProducto.setText(registro["Nombre"])
        
        #Se selecciona la familia y unidad actual del registro
        familia_actual = str(registro["Familia"])
        unidad_actual = str(registro["Unidad"])
        
        index_familia = self.boxFamilia.findText(familia_actual, QtCore.Qt.MatchFixedString)
        if index_familia >= 0:
            self.boxFamilia.setCurrentIndex(index_familia)

        index_unidad = self.boxUnidad.findText(unidad_actual, QtCore.Qt.MatchFixedString)
        if index_unidad >= 0:
            self.boxUnidad.setCurrentIndex(index_unidad)
        
    def obtener_datos(self):
        return {
            "id": self.txtIdProducto.text(),
            "Nombre": self.txtNombreProducto.text(),
            "Familia": self.boxFamilia.currentText(),
            "Unidad": self.boxUnidad.currentText(),
        }

class AgregarArticulosDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi(resource_path("interfaces/agregarArticulo.ui"), self)
        
        self.btnGuardarCambios.clicked.connect(self.agregarArticulo)
        self.btnCancelar.clicked.connect(self.reject)
        
        #cargar familias al comboBox
        self.cargar_familias()
        
        #cargar familias al comboBox
        self.cargar_unidades()
        
        #Numero de pedido automático
        nombre_archivo = "bases_de_datos/articulos.csv"
        if os.path.exists(nombre_archivo):
                df = pd.read_csv(nombre_archivo)
                #Si no hay filas, reiniciamos el contador
                if df.empty:
                    ultimo_num = 0
                else:
                    #extraemos el último número de pedido
                    ultimo_articulo = df['id'].iloc[-1]
                    ultimo_num = int(ultimo_articulo[1:])
        else:
            #si no existe, empezamos de cero
            ultimo_num = 0
        nuevo_num = ultimo_num + 1
        self.txtIdProducto.setText(f"A{nuevo_num:03d}")
    
    def cargar_familias(self):
        nombre_archivo = "bases_de_datos/familias.csv"
        
        if not os.path.exists(nombre_archivo):
            QMessageBox.warning(self, "Archivo no encontrado", "No se encontró el archivo familias.csv.")
            return
        
        try:
            # Leer el CSV
            df = pd.read_csv(nombre_archivo, encoding="utf-8-sig")

            # Limpiar el combo por si se recarga varias veces
            self.boxFamilia.clear()

            # Verificar que existe la columna 'Familia'
            if "Familia" not in df.columns:
                QMessageBox.warning(self, "Error de formato", "El archivo familias.csv no contiene la columna 'Familia'.")
                return

            # Agregar cada familia al combo
            for familia in df["Familia"].dropna().unique():
                self.boxFamilia.addItem(str(familia))

        except Exception as e:
            QMessageBox.critical(self, "Error al leer CSV", f"No se pudo cargar el archivo:\n{e}")
            
    def cargar_unidades(self):
        nombre_archivo = "bases_de_datos/unidades.csv"
        
        if not os.path.exists(nombre_archivo):
            QMessageBox.warning(self, "Archivo no encontrado", "No se encontró el archivo familias.csv.")
            return
        
        try:
            # Leer el CSV
            df = pd.read_csv(nombre_archivo, encoding="utf-8-sig")

            # Limpiar el combo por si se recarga varias veces
            self.boxUnidad.clear()

            # Verificar que existe la columna 'Familia'
            if "unidades" not in df.columns:
                QMessageBox.warning(self, "Error de formato", "El archivo unidades.csv no contiene la columna 'unidades'.")
                return

            # Agregar cada familia al combo
            for familia in df["unidades"].dropna().unique():
                self.boxUnidad.addItem(str(familia))

        except Exception as e:
            QMessageBox.critical(self, "Error al leer CSV", f"No se pudo cargar el archivo:\n{e}")
      
    def agregarArticulo(self):
        nombre_archivo = "bases_de_datos/articulos.csv"
                        
        #Se obtienen los datos del cliente
        idArticulo = self.txtIdProducto.text()
        nombreArticulo = self.txtNombreProducto.text()
        familia = self.boxFamilia.currentText()
        tipoUnidad = self.boxUnidad.currentText()
        
        #VALIDACIONES OBLIGATORIAS
        if not nombreArticulo:
            QMessageBox.warning(self, "Campo obligatorio", "Por favor ingrese el apellido del cliente.")
            return
        
        #Creamos el diccionario con los datos
        nuevoArticulo = [{'id': idArticulo, 
                    'Nombre': nombreArticulo, 
                    'Familia': familia, 
                    'Unidad': tipoUnidad, 
                }]

        if os.path.exists(nombre_archivo):
            #añadir nueva fila al archivo
            df = pd.read_csv(nombre_archivo)
            df = pd.concat([df, pd.DataFrame(nuevoArticulo)], ignore_index=True)
        else:
            #crear nuevo archivo
            df = pd.DataFrame(nuevoArticulo)
                
        try:
            df.to_csv(nombre_archivo, index=False, encoding='utf-8-sig')
        except PermissionError:
            QMessageBox.warning(self, "Archivo en uso",
                "No se puede agregar el artículo porque 'articulos.csv' está abierto.\n"
                "Ciérrelo e intente de nuevo.")
            return
        
        #Se muestra un mensaje de agregado y se limpian los campos
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Carnicería - Artículo Agregado")
        msg.setText(f"Artículo {idArticulo} agregado exitosamente.")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
        
        self.reject()    

class AgregarFamiliaDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi(resource_path("interfaces/agregarFamilia.ui"), self)
        
        self.btnGuardarCambios.clicked.connect(self.agregarFamilia)
        self.btnCancelar.clicked.connect(self.reject)
    
    def agregarFamilia(self):
        nombre_archivo = "bases_de_datos/familias.csv"
        
        # Se obtiene el nombre de la familia
        nombreFamilia = self.txtFamilia.text().strip()
        
        # VALIDACIÓN OBLIGATORIA
        if not nombreFamilia:
            QMessageBox.warning(self, "Campo obligatorio", "Por favor ingrese el nombre de la familia.")
            return
        
        # Verificar si la familia ya existe
        if os.path.exists(nombre_archivo):
            df_existente = pd.read_csv(nombre_archivo, encoding="utf-8-sig")
            if nombreFamilia in df_existente["Familia"].values:
                QMessageBox.warning(self, "Familia existente", f"La familia '{nombreFamilia}' ya existe en la base de datos.")
                return
        
        # Crear el diccionario con los datos
        nuevaFamilia = [{'Familia': nombreFamilia}]
        
        if os.path.exists(nombre_archivo):
            # Añadir nueva fila al archivo
            df = pd.read_csv(nombre_archivo, encoding="utf-8-sig")
            df = pd.concat([df, pd.DataFrame(nuevaFamilia)], ignore_index=True)
        else:
            # Crear nuevo archivo
            df = pd.DataFrame(nuevaFamilia)
        
        # Guardar el archivo
        try:
            df.to_csv(nombre_archivo, index=False, encoding='utf-8-sig')
        except PermissionError:
            QMessageBox.warning(self, "Archivo en uso",
                "No se puede agregar la familia porque 'familias.csv' está abierto.\n"
                "Ciérrelo e intente de nuevo.")
            return
        
        # Mensaje de confirmación
        QMessageBox.information(self, "Carnicería - Familia Agregada", f"Familia '{nombreFamilia}' agregada exitosamente.")
        
        self.accept()

#main    
app = QApplication(sys.argv)
widget = QStackedWidget()

nav = Navigator(widget)

mainwindow = mainWindow(widget)
introduccionPedidos = IntroduccionPedidos(widget)
elaboracionPedidos = ElaboracionPedidos(widget)
entregaPedidos = EntregaPedidos(widget)
consultaPedidos = ConsultaPedidos(widget)
consultaCompras = ConsultaCompras(widget)
consultaArticulos = ConsultaArticulos(widget)

widget.addWidget(mainwindow) #index 0
widget.addWidget(introduccionPedidos) #index 1
widget.addWidget(elaboracionPedidos) #index 2
widget.addWidget(entregaPedidos) #index 3
widget.addWidget(consultaPedidos) #index 4
widget.addWidget(consultaCompras) #index 5
widget.addWidget(consultaArticulos) #index 6

#registramos los titlos de cada ventana
nav.set_title(0, "Pantalla principal")
nav.set_title(1, "Introducción de pedidos")
nav.set_title(2, "Elaboración de pedidos")
nav.set_title(3, "Entrega de pedidos")
nav.set_title(4, "Consulta y modificación de pedidos")
nav.set_title(5, "Consulta de compras")
nav.set_title(6, "Consulta y modificación de artículos")



widget.setMinimumSize(1280, 720)

widget.setWindowTitle("Carnicería - Pantalla principal")
icon = QtGui.QIcon(resource_path('imagenes/logo.ico'))
widget.setWindowIcon(icon)
widget.show()

try:
    sys.exit(app.exec_())
except:
    print("Exiting")