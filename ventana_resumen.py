import contextlib
from tkinter import *
from tkinter import ttk
import customtkinter as ctk
from datetime import date
from datetime import datetime
from PIL import Image, ImageTk
from tkinter import CENTER
from tkinter import ttk

from con_database import *
from functions_base import *
from functions_base import *


class FunctionsResumen(Database):

    def __init__(self):
        super().__init__()

        with open("sucursal.txt", "r") as file:
            linea = file.readline()

            self.id_sucursal = linea.strip()
    
    def select_database(self, query_sql, view_target):
        view_target.delete(*view_target.get_children())

        data_return = Database().dql_database(query_sql)
        for dados in data_return:
            view_target.insert("", END, values=dados)

    def filter_todos(self, Resumen=False):
        query_select =f"""
            SELECT 
                id, producto, grupo, medida, lote, stock, 
                valor_stock, fecha_entrada, status, barcode
            FROM 
                stock
            WHERE 
                activo != 'borrado' AND id_sucursal = {self.id_sucursal}
        """
        data_return = Database().dql_database(query_select)

        if Resumen:
            self.total_itens = len(data_return)
            for dados in data_return:
                self.valor_itens += dados[6]
        else:
            for dados in data_return:
                self.lista_todos.insert("", END, values=dados)
    
    def search_todos(self):
        self.lista_todos.delete(*self.lista_todos.get_children())
        
        if self.busca.get() == "" \
            and self.busca_grupo_listBox.get() == "" \
                and self.busca_status_listBox.get() == "":
                
                sql = f"""
                    SELECT
                        id, producto, grupo, medida, lote, stock, 
                        valor_stock, fecha_entrada, status, barcode
                    FROM
                        stock
                    WHERE 
                        activo != 'borrado' AND id_sucursal = {self.id_sucursal}
                """
        else:
            if self.busca.get():
                buscar = f"""
                    producto LIKE '%{self.busca.get()}%'
                    OR lote LIKE '%{self.busca.get()}%' 
                    OR barcode LIKE '%{self.busca.get()}%'
                    AND activo != 'borrado' AND id_sucursal = {self.id_sucursal}  
                """
            
            elif self.busca_grupo_listBox.get():
                buscar = f"grupo LIKE '%{self.busca_grupo_listBox.get()}%' AND activo != 'borrado' AND id_sucursal = {self.id_sucursal} ORDER BY id"
            
            elif self.busca_status_listBox.get():
                buscar = f"status LIKE '%{self.busca_status_listBox.get()}%' AND activo != 'borrado' AND id_sucursal = {self.id_sucursal} ORDER BY stock DESC"
        
            sql = f"""
                SELECT
                    id, producto, grupo, medida, lote, stock, 
                    valor_stock, fecha_entrada, status, barcode
                FROM
                    stock
                WHERE
                    {buscar}
            """
            
        data_return = Database().dql_database(sql)
        if data_return is not None:
            for dados in data_return:
                self.lista_todos.insert("", END, values=dados)
        
        self.clear_search()

    def filter_reponer(self, Resumen=False):
        query_select = f"""
            SELECT 
                id, status, producto, grupo, medida, lote, stock, 
                stock_mín, reponer, costo_unitario, costo_reponer, proveedor, barcode
            FROM 
                stock 
            WHERE
                activo != 'borrado' AND id_sucursal = {self.id_sucursal}
                ORDER BY status DESC
            
        """
        data_return = Database().dql_database(query_select)

        for dados in data_return:
            if dados[6] <= dados[7]:
                if Resumen:
                    self.total_reponer += 1
                    self.valor_reponer += dados[9]
                else:
                    self.lista_reponer.insert("", END, values=dados)
    
    def search_reponer(self):
        self.lista_reponer.delete(*self.lista_reponer.get_children())

        if self.busca.get() == "" \
            and self.busca_grupo_listBox.get() == "" \
                and self.busca_status_listBox.get() == "":

            sql = f"""
                    SELECT
                        id, status, producto, grupo, medida, lote, stock, 
                        stock_mín, reponer, costo_unitario, costo_reponer, proveedor, barcode
                    FROM
                        stock 
                    WHERE
                        activo != 'borrado' AND id_sucursal = {self.id_sucursal} 
                            
                    ORDER BY status DESC
                """
        else:
            if self.busca.get():
                buscar = f"""
                    producto LIKE '%{self.busca.get()}%'
                    OR lote LIKE '%{self.busca.get()}%'
                    OR barcode LIKE '%{self.busca.get()}%'
                    AND activo != 'borrado' AND id_sucursal = {self.id_sucursal}
                """

            elif self.busca_grupo_listBox.get():
                buscar = f"grupo LIKE '%{self.busca_grupo_listBox.get()}%' AND activo != 'borrado' AND id_sucursal = {self.id_sucursal} ORDER BY id"

            elif self.busca_status_listBox.get():
                buscar = f"status LIKE '%{self.busca_status_listBox.get()}%' AND activo != 'borrado' AND id_sucursal = {self.id_sucursal} ORDER BY stock DESC"

            sql = f"""
                SELECT
                    id, status, producto, grupo, medida, lote, stock,
                    stock_mín, reponer, costo_unitario, costo_reponer, proveedor, barcode
                FROM
                    stock
                WHERE
                    {buscar}
            """

        data_return = Database().dql_database(sql)
        if data_return is not None:
            for dados in data_return:
                if dados[6] <= dados[7]:
                    self.lista_reponer.insert("", END, values=dados)
        
        self.clear_search()

    def filter_facturación(self, Resumen=False):
        query_select = f"""
            SELECT 
                id, fecha_salida, producto, grupo, medida, lote, 
                stock, salidas, valor_venta, facturación, status
            FROM 
                stock
            WHERE
                activo != 'borrado' AND id_sucursal = {self.id_sucursal}  
                ORDER BY fecha_salida DESC
        """
        data_return = Database().dql_database(query_select)

        for dados in data_return:
            if dados[7] > 0:
                if Resumen:
                    self.total_movimentos += 1
                    self.valor_facturacion += dados[9]
                else:
                    self.lista_facturacion.insert("", END, values=dados)

    def search_facturación(self):
        self.lista_facturacion.delete(*self.lista_facturacion.get_children())

        if self.busca.get() == "" \
            and self.busca_grupo_listBox.get() == "" \
                and self.busca_status_listBox.get() == "":

            sql = f"""
                    SELECT
                        id, fecha_salida, producto, grupo, medida, lote, 
                        stock, salidas, valor_venta, facturación, status
                    FROM
                        stock 
                    WHERE
                        activo != 'borrado' AND id_sucursal = {self.id_sucursal}
                        ORDER BY fecha_salida DESC
                """
        else:
            if self.busca.get():
                buscar = f"""
                    producto LIKE '%{self.busca.get()}%'
                    OR lote LIKE '%{self.busca.get()}%'
                    OR barcode LIKE '%{self.busca.get()}%'
                    AND activo != 'borrado' AND id_sucursal = {self.id_sucursal}
                """

            elif self.busca_grupo_listBox.get():
                buscar = f"grupo LIKE '%{self.busca_grupo_listBox.get()}%' AND activo = 'borrado' AND id_sucursal = {self.id_sucursal} ORDER BY id"

            sql = f"""
                SELECT
                    id, fecha_salida, producto, grupo, medida, lote, 
                    stock, salidas, valor_venta, facturación, status
                FROM
                    stock
                WHERE
                    {buscar}
            """

        data_return = Database().dql_database(sql)
        if data_return is not None:
            for dados in data_return:
                if dados[7] > 0:
                    self.lista_facturacion.insert("", END, values=dados)

        self.clear_search()
    
    def filter_nuevos(self, Resumen=False):
        query_select = f"""
                SELECT 
                    id, fecha_entrada, producto, medida, lote, entradas, 
                    costo_unitario, costo_total, stock, status, grupo, proveedor
                FROM 
                    stock 
                WHERE
                    activo = 'borrado' AND id_sucursal = {self.id_sucursal}
                ORDER BY fecha_entrada DESC
            """
        data_return = Database().dql_database(query_select)

        for dados in data_return:
            if dados[1] is None or dados[1] == "":
                continue
            try:
            # Parsea la cadena de texto en formato dd/mm/yyyy y obtiene los valores enteros
                Fecha = datetime.strptime(dados[1], "%d/%m/%Y")
                año, mes, dia = Fecha.year, Fecha.month, Fecha.day

            except ValueError:

                continue
            # entradas realizadas en los últimos 30 días
            data_atual = date.today()
            fecha_entrada = date(año, mes, dia)
            data_diferenca = data_atual - fecha_entrada            

            if Fecha.days <= 30:
                if Resumen:
                    self.total_nuevos += 1
                    self.valor_nuevos += dados[7]
                else:
                    self.lista_nuevos.insert("", END, values=dados)
    
    def search_nuevos(self):

        self.lista_nuevos.delete(*self.lista_nuevos.get_children())

        if self.busca.get() == "" \
                and self.busca_grupo_listBox.get() == "" \
                    and self.busca_status_listBox.get() == "":

            sql = f"""
                    SELECT
                        id, fecha_entrada, producto, medida, lote, entradas, 
                        costo_unitario, costo_total, stock, status, grupo, proveedor
                    FROM
                        stock 
                    WHERE
                        activo = 'borrado' AND id_sucursal = {self.id_sucursal}
                    ORDER BY fecha_entrada DESC
                """
        else:
            if self.busca.get():
                buscar = f"""
                    producto LIKE '%{self.busca.get()}%' 
                    OR lote LIKE '%{self.busca.get()}%'
                    OR barcode LIKE '%{self.busca.get()}%'
                    AND activo = 'borrado' AND id_sucursal = {self.id_sucursal}
                """

            elif self.busca_grupo_listBox.get():
                buscar = f"grupo LIKE '%{self.busca_grupo_listBox.get()}%' AND activo = 'borrado' AND id_sucursal = {self.id_sucursal} ORDER BY id"

            sql = f"""
                SELECT
                    id, fecha_entrada, producto, medida, lote, entradas,
                    costo_unitario, costo_total, stock, status, grupo, proveedor
                FROM
                    stock
                WHERE
                    {buscar}
            """

        data_return = Database().dql_database(sql)
        if data_return is not None:
            for dados in data_return:
                if dados[1] is None or dados[1] == "":
                    continue
                try:
                    # Analiza la cadena de texto en formato dd/mm/aaaa y obtener los valores ingresados
                    Fecha = datetime.strptime(dados[1], "%d/%m/%Y")
                    año, mes, dia = Fecha.year, Fecha.month, Fecha.day

                    # Buscar entradas realizadas en los últimos 30 días
                    data_atual = date.today()
                    fecha_entrada = date(año, mes, dia)
                    data_diferenca = data_atual - fecha_entrada

                    if data_diferenca.days <= 30:
                        self.lista_nuevos.insert("", END, values=dados)

                except ValueError:
                    continue

        self.clear_search()

    def filter_parados(self, Resumen=False):
        sql = f"""
            SELECT 
                id, fecha_salida, producto, lote, medida, salidas, 
                stock, valor_stock, grupo, proveedor
            FROM 
                stock 
            WHERE
                activo = 'borrado' AND id_sucursal = {self.id_sucursal}
                ORDER BY fecha_salida DESC
        """
        data_return = Database().dql_database(sql)

        for dados in data_return:
            if dados[1] is None or dados[1] == "":
                continue

            try:
                # Analiza la cadena de texto en formato dd/mm/aaaa hh:mm:ss y obtiene los valores ingresados
                Fecha = datetime.strptime(dados[1], "%d/%m/%Y %H:%M:%S")
                año, mes, dia = Fecha.year, Fecha.month, Fecha.day

                # Búsqueda de salidas realizadas hace más de 90 días
                data_atual = datetime.now()
                fecha_salida = datetime(año, mes, dia, hour=0, minute=0, second=0)
                data_diferenca = data_atual - fecha_salida

                if data_diferenca.days >= 90:
                    if Resumen:
                        self.total_parados += 1
                        self.valor_parados += dados[7]
                    else:
                        self.lista_parados.insert("", END, values=dados)
            except ValueError:
                continue
                    
    def search_parados(self):
        self.lista_parados.delete(*self.lista_parados.get_children())

        if self.busca.get() == "" \
                and self.busca_grupo_listBox.get() == "" \
                    and self.busca_status_listBox.get() == "":

            sql = f"""
                    SELECT
                        id, fecha_salida, producto, lote, medida, salidas, 
                        stock, valor_stock, grupo, proveedor
                    FROM
                        stock 
                    WHERE
                        activo = 'borrado' AND id_sucursal = {self.id_sucursal}
                        ORDER BY fecha_salida DESC
                """
        else:
            if self.busca.get():
                buscar = f"""
                    producto LIKE '%{self.busca.get()}%'
                    OR lote LIKE '%{self.busca.get()}%'
                    OR barcode LIKE '%{self.busca.get()}%'
                    AND activo != 'borrado' AND id_sucursal = {self.id_sucursal}

                """

            elif self.busca_grupo_listBox.get():
                buscar = f"grupo LIKE '%{self.busca_grupo_listBox.get()}%' AND activo = 'borrado' AND id_sucursal = {self.id_sucursal} ORDER BY id"

            sql = f"""
                SELECT
                    id, fecha_salida, producto, lote, medida, salidas, 
                    stock, valor_stock, grupo, proveedor
                FROM
                    stock
                WHERE
                    {buscar}
            """

        data_return = Database().dql_database(sql)
        if data_return is not None:
            for dados in data_return:
                if dados[1] is None or dados[1] == "":
                    continue

                try:
                    Fecha = datetime.strptime(dados[1], "%d/%m/%Y %H:%M:%S")
                    año, mes, dia = Fecha.year, Fecha.month, Fecha.day

                    data_atual = datetime.now()
                    fecha_salida = datetime(año, mes, dia, hour=0, minute=0, second=0)
                    data_diferenca = data_atual - fecha_salida

                    if data_diferenca.days >= 90:
                        self.lista_parados.insert("", END, values=dados)

                except ValueError:
                    continue

        self.clear_search()
    def clear_search(self):
        with contextlib.suppress(Exception):
            self.busca.delete(0, END)
            self.busca.configure(placeholder_text="Buscar Producto, Nº Lote, Código de Barras")
            self.busca_grupo_listBox.set("")
            self.busca_status_listBox.set("")
            self.busca_mes.delete(0, END)
            self.busca_mes.configure(placeholder_text="Mes")
            self.busca_año.delete(0, END)
            self.busca_año.configure(placeholder_text="Año")
            self.busca_facturación.set("")
# ----------------------------------------------------------------------------------------------------------------- #


class VentanaResumen(FunctionsResumen, FunctionsExtras):
    def __init__(self, root):
        self.root = root

        with open("sucursal.txt", "r") as file:
            linea = file.readline()

            self.id_sucursal = linea.strip()

        self.widgets_top()
        self.crear_informacion("Seguimiento de productos registrados!", 1)

    def crear_treview(self):
        #self.lista_todos, self.lista_reponer, lista_facturacion, lista_nuevos, lista_parados
        columns = ('id', 'status', 'producto', 'grupo', 'medida', 'lote', 
                    'stock', 'mín', 'reponer', 'costo', 'total', 'proveedor', 'barcode')
 
        self.lista_todos = ttk.Treeview(self.frame_informacion, height=3, column=columns)
        self.lista_reponer = ttk.Treeview(self.frame_informacion, height=3, column=columns)
        self.lista_facturacion = ttk.Treeview(self.frame_informacion, height=3, column=columns)
        self.lista_nuevos = ttk.Treeview(self.frame_informacion, height=3, column=columns)
        self.lista_parados = ttk.Treeview(self.frame_informacion, height=3, column=columns)

        self.listas_treviews = [self.lista_todos, self.lista_reponer, self.lista_facturacion,
                           self.lista_nuevos, self.lista_parados]

    def crear_informacion(self, anuncio, eleccion):

        self.frame_informacion = ctk.CTkFrame(self.root, width=990, height=425, fg_color="#363636")
        self.frame_informacion.place(x=0, y=125)

        self.crear_treview()

        self.anuncio =ctk.CTkLabel(self.frame_informacion, text=anuncio,
                     font=("Cascadia Code", 13), text_color="#D3D3D3")
        self.anuncio.place(x=5, y=5)

        ctk.CTkLabel(self.frame_informacion, text="Producto",
                     font=("Cascadia Code", 13)).place(x=5, y=50)
        
        self.busca = ctk.CTkEntry(self.frame_informacion, width=350, placeholder_text="Buscar Producto, Nº Lote, Código de Barras",
                                  font=("Cascadia Code", 13))
        self.busca.place(x=5, y=75)
    
        ctk.CTkLabel(self.frame_informacion, text="Departamento",
                     font=("Cascadia Code", 13)).place(x=365, y=50)
        
        lista_grupo = self.dql_database("SELECT grupo FROM stock", column_names=True)
        
        self.busca_grupo_listBox = ctk.CTkComboBox(self.frame_informacion, width=200, values=lista_grupo, font=("Cascadia Code", 13))
        self.busca_grupo_listBox.set("")
        self.busca_grupo_listBox.place(x=365, y=75)

        lista_widgets_unicos = [self.view_todos_adicional, self.view_reponer_adicionales, self.view_facturacion_adicionales,
                                self.view_nuevos_adicionales, self.view_parados_adicionales]


        lista_widgets_unicos[eleccion]()

        self.configurar_treeview(eleccion)

    def configurar_treeview(self, eleccion):
        """
        Configura el Treeview para la visualización de productos con columnas y encabezados personalizados.
        """
        # Definir encabezados y anchos de las columnas
        column_headers = {
            "id": "Cód.", "status": "Status", "producto": "Producto", "grupo": "Departamento",
            "medida": "Medida", "lote": "Nº Lote", "stock": "stock", "mín": "Est.Mín", "reponer": "reponer", 
            "costo": "costo Unit.", "total": "costo Total", "proveedor": "proveedor", "barcode": "Código de Barras"
        }

        column_widths = {
            "id": (35, CENTER), "status": (70, CENTER), "producto": (150, CENTER),
            "grupo": (125, CENTER), "medida": (85, CENTER), "lote": (50, CENTER), "stock": (50, CENTER),
            "mín": (50, CENTER), "reponer": (50, CENTER), "costo": (80, CENTER), "total": (80, CENTER),
            "proveedor": (150, CENTER), "barcode": (100, CENTER)
        }

        self.listas_treviews[eleccion].column("#0", width=0, stretch=False)  
        self.listas_treviews[eleccion].heading("#0", text="") 

        # Configurar las columnas y encabezados en el Treeview
        for col, heading in column_headers.items():
            self.listas_treviews[eleccion].heading(col, text=heading)
        for col, (width, anchor) in column_widths.items():
            self.listas_treviews[eleccion].column(col, width=width, anchor=anchor, stretch=False)

        self.listas_treviews[eleccion].place(y=110, width=970, height=315)


        # Añadir scrollbars
        # Llamar a la función de filtro adecuada
        lista_funciones = [self.filter_todos, self.filter_reponer, self.filter_facturación, self.filter_nuevos, self.filter_parados]
        lista_funciones[eleccion]()

    def realizar_consulta_sql(self):
        return self.dql_database(f"SELECT grupo FROM stock WHERE activo = 'borrado' AND id_sucursal = {self.id_sucursal}", column_names=True)

    def widgets_top(self):
        ctk.CTkLabel(self.root, text="Analisis de Stock",
                     font=("Constantia", 25), text_color=("#1C1C1C", "#D3D3D3")
                     ).place(x=20, y=10)

        self.frame_top = ctk.CTkFrame(self.root, width=985, height=75)
        self.frame_top.place(x=1, y=50)

        self.total_itens = 0
        self.valor_itens = 0
        self.filter_todos(Resumen=True)
        todos = f"TODOS \n{self.total_itens} productos\n$ {self.valor_itens:.2f}"

        self.total_reponer = 0
        self.valor_reponer = 0
        self.filter_reponer(Resumen=True)
        reponer = f"REPONER \n{self.total_reponer} productos\n$ {self.valor_reponer:.2f}"

        self.total_movimentos = 0
        self.valor_facturacion = 0
        self.filter_facturación(Resumen=True)
        facturación = f"FACTURACIÓN \n{self.total_movimentos} productos\n$ {self.valor_facturacion:.2f}"

        self.total_nuevos = 0
        self.valor_nuevos = 0
        self.filter_nuevos(Resumen=True)
        nuevos = f"NUEVOS \n{self.total_nuevos} productos\n$ {self.valor_nuevos:.2f}"

        self.total_parados = 0
        self.valor_parados = 0
        self.filter_parados(Resumen=True)
        parados = f"PARADOS \n{self.total_parados} productos\n$ {self.valor_parados:.2f}"

        estilos_botones = {"width": 175, "font":("Cascadia Code", 15), "text_color":"black"}

        ##viev_todos_variables 
        anuncio = "Seguimiento de productos registrados!"

        ctk.CTkButton(self.frame_top, text=todos, fg_color="#000080", **estilos_botones,
                      command=lambda :self.crear_informacion(anuncio, 0)).grid(column=0, row=0)
        
        ##view_reponer_variables
        anuncio_rep = "¡Recomendaciones de productos para reposición de stock!"

        ctk.CTkButton(self.frame_top, text=reponer, **estilos_botones, fg_color="#FF4500",
                      command=lambda :self.crear_informacion(anuncio_rep, 1)).grid(column=1, row=0, padx=10)
        
        ##view_facturacion_variables
        anuncio_fac = "Buscar Producto, Nº Lote, Código de Barras"

        ctk.CTkButton(self.frame_top, text=facturación, **estilos_botones, fg_color="#FFD700",
                      command=lambda :self.crear_informacion(anuncio_fac, 2)).grid(column=2, row=0)
        
        ##view_nuevos_variables
        anuncio_nue = "¡Registros de entradas realizadas en los últimos 30 días!"

        ctk.CTkButton(self.frame_top, text=nuevos, **estilos_botones , fg_color="#32CD32",
                      command=lambda :self.crear_informacion(anuncio_nue, 3)).grid(column=3, row=0, padx=10)
        
        #view_parados_variables
        anuncio_par = "¡Seguimiento de Lotes sin salida por más de 90 días!"
        
        ctk.CTkButton(self.frame_top, text=parados, **estilos_botones, fg_color="#D8BFD8",
                      command=lambda :self.crear_informacion(anuncio_par, 4)).grid(column=4, row=0)

        ##creacion del menu de arriba

        ctk.CTkButton(self.frame_top, text="", width=50, image=self.image_button("./actualizar.png", (34, 34)),  
                      compound=LEFT, anchor=NW, fg_color="transparent", hover_color=("#D3D3D3", "#363636"),
                      command=self.widgets_top).grid(column=5, row=0, padx=10)
#-----------------------------------------------------------------------------------------------------------------
    def view_todos_adicional(self):
        ctk.CTkLabel(self.frame_informacion, text="Status",
                     font=("Cascadia Code", 13)).place(x=575, y=50)
        lista_status = ['OK', 'VACIO', 'CRÍTICO'] 
        self.busca_status_listBox = ctk.CTkComboBox(self.frame_informacion, width=100, values=lista_status, font=("Cascadia Code", 13))
        self.busca_status_listBox.set("")
        self.busca_status_listBox.place(x=575, y=75)

        ctk.CTkLabel(self.frame_informacion, text="Fecha",
                     font=("Cascadia Code", 13)).place(x=685, y=50)
        
        self.busca_mes = ctk.CTkEntry(self.frame_informacion, width=50, justify=CENTER, placeholder_text="Mes",
                                      font=("Cascadia Code", 13))
        self.busca_mes.place(x=685, y=75)
        
        ctk.CTkLabel(self.frame_informacion, text="/",
                     font=("Cascadia Code", 20, "bold"), text_color="#A9A9A9",
                     ).place(x=735, y=75)
        self.busca_año = ctk.CTkEntry(self.frame_informacion, width=50, justify=CENTER,
                                      placeholder_text="Año", font=("Cascadia Code", 13))
        self.busca_año.place(x=748, y=75)
        
        ctk.CTkButton(self.frame_informacion, text="BUSCAR", width=60, font=("Cascadia Code", 13, "bold"),
                      fg_color="#696969", hover_color=("#D3D3D3", "#1C1C1C"),
                      command=self.search_todos).place(x=820, y=75)

        ctk.CTkButton(self.frame_informacion, text="LIMPIAR", width=60, font=("Cascadia Code", 13, "bold"),
                      fg_color="#696969", hover_color=("#D3D3D3", "#1C1C1C"),
                      command=self.clear_search).place(x=890, y=75)
    

    def view_reponer_adicionales(self):
        ctk.CTkLabel(self.frame_informacion, text="Status",
                     font=("Cascadia Code", 13)).place(x=575, y=50)
        lista_status = ['VACIO', 'CRÍTICO'] 
        self.busca_status_listBox = ctk.CTkComboBox(self.frame_informacion, width=100,
                                                    values=lista_status, font=("Cascadia Code", 13))
        self.busca_status_listBox.set("")
        self.busca_status_listBox.place(x=575, y=75)
        
        ctk.CTkButton(self.frame_informacion, text="BUSCAR", width=60, font=("Cascadia Code", 13, "bold"),
                      fg_color="#696969", hover_color=("#D3D3D3", "#1C1C1C"),
                      command=self.search_reponer).place(x=700, y=75)
        
        ctk.CTkButton(self.frame_informacion, text="LIMPIAR",width=60, font=("Cascadia Code", 13, "bold"),
                      fg_color="#696969",
                      hover_color=("#D3D3D3", "#1C1C1C"),
                      command=self.clear_search).place(x=770, y=75)
        

    def view_facturacion_adicionales(self):
        ctk.CTkLabel(self.frame_informacion, text="salidas",
                     font=("Cascadia Code", 13)).place(x=575, y=50)
        lista_facturacion = ["Mayor Valor", "Menor Valor", "Mayor cnt", "Menor cnt"]
        self.busca_facturación = ctk.CTkComboBox(self.frame_informacion, width=125, values=lista_facturacion, font=("Cascadia Code", 13))
        self.busca_facturación.set("")
        self.busca_facturación.place(x=575, y=75)

        ctk.CTkLabel(self.frame_informacion, text="Fecha",
                     font=("Cascadia Code", 13)).place(x=705, y=50)
        
        self.busca_mes = ctk.CTkEntry(self.frame_informacion, width=50, justify=CENTER, placeholder_text="Mes", font=("Cascadia Code", 13))
        self.busca_mes.place(x=710, y=75)

        ctk.CTkLabel(self.frame_informacion, text="/", font=("Cascadia Code", 20, "bold"), text_color="#A9A9A9",).place(x=760, y=75)
        self.busca_año = ctk.CTkEntry(self.frame_informacion, width=50, justify=CENTER, placeholder_text="año", font=("Cascadia Code", 13))
        self.busca_año.place(x=773, y=75)

        ctk.CTkButton(self.frame_informacion, text="BUSCAR", width=60, font=("Cascadia Code", 13, "bold"),
                      fg_color="#696969", hover_color=("#D3D3D3", "#1C1C1C"),
                      command=self.search_facturación).place(x=837, y=75)

        ctk.CTkButton(self.frame_informacion, text="LIMPIAR", width=60,
                      font=("Cascadia Code", 13, "bold"), fg_color="#696969",
                      hover_color=("#D3D3D3", "#1C1C1C"), command=self.clear_search).place(x=907, y=75)

    def view_nuevos_adicionales(self):
        ctk.CTkLabel(self.frame_informacion, text="Fecha",
                     font=("Cascadia Code", 13)).place(x=575, y=50)
        self.busca_mes = ctk.CTkEntry(self.frame_informacion, width=50, justify=CENTER,
                                      placeholder_text="Mes", font=("Cascadia Code", 13))
        self.busca_mes.place(x=575, y=75)

        ctk.CTkLabel(self.frame_informacion, text="/",
                     font=("Cascadia Code", 20, "bold"), text_color="#A9A9A9",
                     ).place(x=625, y=75)
        
        self.busca_año = ctk.CTkEntry(self.frame_informacion, width=50, justify=CENTER,
                                      placeholder_text="año", font=("Cascadia Code", 13))
        self.busca_año.place(x=638, y=75)

        ctk.CTkButton(self.frame_informacion, text="BUSCAR", width=60,font=("Cascadia Code", 13, "bold"),
                      fg_color="#696969", hover_color=("#D3D3D3", "#1C1C1C"),
                      command=self.search_nuevos).place(x=710, y=75)

        ctk.CTkButton(self.frame_informacion, text="LIMPIAR", width=60,
                      font=("Cascadia Code", 13, "bold"),fg_color="#696969", hover_color=("#D3D3D3", "#1C1C1C"),
                      command=self.clear_search).place(x=780, y=75)


    def view_parados_adicionales(self):
        ctk.CTkLabel(self.frame_informacion, text="Fecha", font=("Cascadia Code", 13)).place(x=575, y=50)

        self.busca_mes = ctk.CTkEntry(self.frame_informacion, width=50, justify=CENTER,placeholder_text="Mes",
                                      font=("Cascadia Code", 13))
        self.busca_mes.place(x=575, y=75)

        ctk.CTkLabel(self.frame_informacion, text="/",
                     font=("Cascadia Code", 20, "bold"), text_color="#A9A9A9").place(x=625, y=75)
        self.busca_año = ctk.CTkEntry(self.frame_informacion, width=50, justify=CENTER,
                                      placeholder_text="año", font=("Cascadia Code", 13))
        self.busca_año.place(x=638, y=75)

        ctk.CTkButton(self.frame_informacion, text="BUSCAR", width=60, font=("Cascadia Code", 13, "bold"),
                      fg_color="#696969", hover_color=("#D3D3D3", "#1C1C1C"),
                      command=self.search_parados).place(x=710, y=75)

        ctk.CTkButton(self.frame_informacion, text="LIMPIAR", width=60, font=("Cascadia Code", 13, "bold"),
                      fg_color="#696969", hover_color=("#D3D3D3", "#1C1C1C"),
                      command=self.clear_search).place(x=780, y=75)
    
