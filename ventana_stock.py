from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import customtkinter as ctk
import awesometkinter as atk
from tkcalendar import DateEntry
import os

from con_database import *
from functions_base import *

def verificar_entrada_usuario():
    try:
        with open("usuario.txt", "r") as file:
            contenido = file.readlines()

            if contenido:
                return int(contenido[0])
            else:
                return -1
    except :
        return -1

class FunctionsEstoque(Database):

    def __init__(self):
        super().__init__()
        with open("sucursal.txt", "r") as file:
            linea = file.readline()

            self.id_sucursal = linea.strip()

    def add_barcode(self):
        if self.producto_entry.get() == "":
            messagebox.showinfo("Description", message="¡Por favor ingrese la descripción del producto!")
        else:
            self.num_barcode.delete(0, END)

            numbers = self.generate_barCode(self.lote_entry.get())
            if numbers:
                self.num_barcode.insert(END, numbers)

    def variables_entries(self):
        self.código = self.cod_entry.get()
        self.producto = self.producto_entry.get()
        self.grupo = self.grupo_listBox.get()
        self.medida = self.medida_listBox.get()
        self.proveedor = self.proveedor_listBox.get()
        self.gestor = self.gestor_listBox.get()
        self.lote = self.lote_entry.get()
        self.stock = self.stock_entry.get()
        self.min = self.min_entry.get()
        self.costo = self.costo_entry.get()
        self.reventa = self.reventa_entry.get()

        self.Fecha = self.data_registro.get()
        self.barcode = self.num_barcode.get()

        self.activo = self.activo_checkbox.get()

    def clear_entries(self):
        self.cod_entry.configure(state=NORMAL)
        self.cod_entry.delete(0, END)
        self.producto_entry.delete(0, END)
        self.grupo_listBox.set("")
        self.medida_listBox.set("")
        self.proveedor_listBox.set("")
        self.gestor_listBox.set("")
        self.lote_entry.delete(0, END)
        self.stock_entry.delete(0, END)
        self.min_entry.delete(0, END)
        self.costo_entry.delete(0, END)
        self.reventa_entry.delete(0, END)

        self.num_barcode.delete(0, END)
        self.img_barcode.configure(image=None)

    def select_database(self):

        self.lista_productos.delete(*self.lista_productos.get_children())

        query_select = f"""
            SELECT 
                id, fecha_entrada, producto, medida, grupo, proveedor, lote, stock, stock_mín, 
                status, responsable, costo_unitario, valor_venta, barcode, activo
            FROM stock
            Where activo != 'borrado' AND id_sucursal = {self.id_sucursal}
        """

        data_return = Database().dql_database(query_select)

        if data_return is not None:
            for dado in data_return:
                self.lista_productos.insert("", "end", values=dado)

        self.total_registries()

    def on_doubleClick(self, event):
        self.clear_entries()
        self.lista_productos.selection()

        for row in self.lista_productos.selection():
            c1, c2, c3, c4, c5, c6, c7, c8, \
                c9, c10, c11, c12, c13, c14, c15 = \
                    self.lista_productos.item(row, "values")
            self.cod_entry.insert(END, c1)
            self.cod_entry.configure(state=DISABLED)
            self.producto_entry.insert(END, c3)
            self.medida_listBox.set(c4)
            self.grupo_listBox.set(c5)
            self.proveedor_listBox.set(c6)
            self.lote_entry.insert(END, c7)
            self.n_lote = self.lote_entry.get()  # Guardar número de lote para ACTUALIZAR
            self.stock_entry.insert(END, c8)
            self.min_entry.insert(END, c9)
            self.gestor_listBox.set(c11)
            self.costo_entry.insert(END, c12)
            self.reventa_entry.insert(END, c13)

            self.num_barcode.insert(END, c14)
            if self.num_barcode.get() != "":
                try:
                    self.img_barcode.configure(image=self.image_barcode(f"{self.lote_entry.get()}.png", (222, 125)))
                except:
                    messagebox.showinfo("Not found", message="¡No se encontró la imagen del código de barras!")

            self.check_var.set(c15)

    def register_product(self):
        self.variables_entries()

        if self.producto_entry.get() == "":
            messagebox.showinfo("Aviso", message="¡Ingrese la descripción del producto!")

        else:
            query_sql = """
                INSERT INTO stock (
                    producto, grupo, medida, proveedor, responsable, lote, stock, 
                    stock_mín, costo_unitario, valor_venta, fecha_entrada, entradas, barcode, activo, id_sucursal
                    )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) """

            if self.stock == "":
                self.stock = 0
            if self.costo == "":
                self.costo = 0
            if self.reventa == "":
                self.reventa = 0
            if self.min == "":
                self.min = 0
            
            lista_dados = [self.producto, self.grupo, self.medida, self.proveedor,
                           self.gestor, self.lote, self.stock, self.min, self.costo, 
                           self.reventa, self.Fecha, self.stock, self.barcode, self.activo, self.id_sucursal]

            self.dml_database(query_sql, lista_dados)

            self.widgets_top()
            self.select_database()

    def update_product(self):

        self.variables_entries()

        if self.código == "" or not self.código.isdigit():
            messagebox.showerror("ID invalid", message="¡Seleccione el producto a actualizar!")
        else:
            if self.producto == "":
                messagebox.showinfo("Aviso", message="¡Ingrese la descripción del producto!")
            
            else:
                if self.lote == "":
                    try:
                        self.barcode = ""
                        self.img_barcode.configure(image=None)
                        os.remove(f"barCodes/{self.n_lote}.png")
                    except:
                        pass
                
                query_sql = """
                    UPDATE stock SET
                        producto=?, grupo=?, medida=?, lote=?, proveedor=?, responsable=?, stock=?, 
                        stock_mín=?, costo_unitario=?, valor_venta=?, fecha_entrada=?, entradas=?, barcode=?, activo=?
                    WHERE id=?
                """
                
                if self.stock == "":
                    self.stock = 0
                if self.costo == "":
                    self.costo = 0
                if self.reventa == "":
                    self.reventa = 0
                if self.min == "":
                    self.min = 0
                
                lista_dados = [self.producto, self.grupo, self.medida, self.lote, self.proveedor, 
                               self.gestor, self.stock, self.min, self.costo, self.reventa, 
                               self.Fecha, self.stock, self.barcode, self.activo,
                               self.código]

                if messagebox.askyesno("Update", message="Actualizar Registro?"):
                    self.dml_database(query_sql, lista_dados)

                self.widgets_top()
                self.select_database()

    def delete_product(self):
        self.variables_entries()

        if self.código == "" or not self.código.isdigit():
            messagebox.showerror("ID invalid", message="¡Seleccione el producto a eliminar!")
        else:
            if messagebox.askyesno("Delete", message=f"Eliminar el registro: {self.cod_entry.get()}?"):
                self.dml_delete(self.código)
                self.img_barcode.configure(image=None)
                try:
                    os.remove(f"barCodes/{self.lote_entry.get()}.png")
                except:
                    pass

                self.widgets_top()
                self.select_database()

    def search_database(self):
        self.lista_productos.delete(*self.lista_productos.get_children())

        if self.producto_entry.get() == "" \
            and self.grupo_listBox.get() == "" \
                and self.lote_entry.get() == "" \
                    and self.proveedor_listBox.get() == "":

            self.select_database()
        else:
            if self.producto_entry.get():
                self.producto_entry.insert(END, "%")
                target = "producto"
                busca = self.producto_entry.get()

            elif self.grupo_listBox.get():
                self.grupo_listBox.set(self.grupo_listBox.get() + "%")
                target = "grupo"
                busca = self.grupo_listBox.get()

            elif self.lote_entry.get():
                self.lote_entry.insert(END, "%")
                target = "lote"
                busca = self.lote_entry.get()

            elif self.proveedor_listBox.get():
                self.proveedor_listBox.set(self.proveedor_listBox.get() + "%")
                target = "proveedor"
                busca = self.proveedor_listBox.get()

            data_query = f"""
                        SELECT
                            id, fecha_entrada, producto, medida, grupo, proveedor, lote, stock, stock_mín,
                            status, responsable, costo_unitario, valor_venta, barcode, activo
                        FROM
                            stock WHERE {target} LIKE '%{busca}%' 
                            AND activo != 'borrado' AND id_sucursal = {self.id_sucursal}
                        ORDER BY producto ASC
                        """
            data_return = self.dql_database(data_query)

            for dados in data_return:
                self.lista_productos.insert("", END, values=dados)

            self.total_registries()

        self.clear_entries()


class VentanaStock(FunctionsEstoque, FunctionsExtras):
    def __init__(self, root, id, rol):
        self.root = root
        self.id = id

        with open("sucursal.txt", "r") as file:
            linea = file.readline()

            self.id_sucursal = linea.strip()

        self.buttons_header()
        self.widgets_top()
        self.widgets_bottom()

    def realizar_consulta(self, columna):
        return self.dql_database(f"SELECT {columna} FROM stock WHERE activo != 'borrado' AND id_sucursal = {self.id_sucursal}", column_names=True)

    def buttons_header(self):
        self.agarrar_datos_usuario = Database().recaudar_datos_usuario(self.id)

        self.frame_buttons = ctk.CTkFrame(self.root,
                                          width=990, height=40,
                                          fg_color="#363636")
        self.frame_buttons.place(x=1, y=1)

        btn_add = ctk.CTkButton(self.frame_buttons, text="", width=30, corner_radius=3,
                                image=self.image_button("add.png", (26, 26)),
                                compound=LEFT, anchor=NW, fg_color="transparent",
                                hover_color=("#D3D3D3", "#4F4F4F"),
                                command=self.register_product)
        btn_add.place(x=2, y=2)
        atk.tooltip(btn_add, "Registrar Producto")

        btn_search = ctk.CTkButton(self.frame_buttons, text="", width=30, corner_radius=3,
                                   image=self.image_button("search.png", (26, 26)),
                                   compound=LEFT, anchor=NW, fg_color="transparent",
                                   hover_color=("#D3D3D3", "#4F4F4F"),
                                   command=self.search_database)
        btn_search.place(x=42, y=2)
        atk.tooltip(btn_search, "Buscar Registro \n (Busca por: producto/departamento/proveedor/lote/NF)")

        btn_update = ctk.CTkButton(self.frame_buttons, text="", width=30, corner_radius=3,
                                   image=self.image_button("update.png", (26, 26)),
                                   compound=LEFT, anchor=NW, fg_color="transparent",
                                   hover_color=("#D3D3D3", "#4F4F4F"),
                                   command=self.update_product)
        btn_update.place(x=82, y=2)
        atk.tooltip(btn_update, "Actualizar Registro")
        
        ##modificacion para empleado
        btn_delete = ctk.CTkButton(self.frame_buttons, text="", width=30, corner_radius=3,
                                   image=self.image_button("delete.png", (26, 26)),
                                   compound=LEFT, anchor=NW, fg_color="transparent",
                                   hover_color=("#D3D3D3", "#4F4F4F"), command=self.delete_product)
        atk.tooltip(btn_delete, "Borrar Registro")

        separador = ctk.CTkLabel(self.frame_buttons, text="||",
                     font=("Arial", 30), text_color="#696969",
                     fg_color="transparent")

        btn_clear = ctk.CTkButton(self.frame_buttons, text="", width=30, corner_radius=3,
                                  image=self.image_button("clear-entries.png", (26, 26)),
                                  compound=LEFT, anchor=NW, fg_color="transparent",
                                  hover_color=("#D3D3D3", "#4F4F4F"), command=self.clear_entries)
        atk.tooltip(btn_clear, "Limpiar campos de datos")

        if self.agarrar_datos_usuario[4] in ["admin", "gerente"]:
            btn_delete.place(x=122, y=2)
            separador.place(x=162)
            btn_clear.place(x=180, y=2)
        else:
            separador.place(x=122)
            btn_clear.place(x=142, y=2)
    def widgets_top(self):
        self.frame_top = ctk.CTkFrame(self.root,
                                      width=990, height=200)
        self.frame_top.place(y=40)

        ctk.CTkLabel(self.frame_top, text="Código",
                     font=("Cascadia Code", 12.5)
                     ).place(x=5, y=5)
        self.cod_entry = ctk.CTkEntry(self.frame_top, width=45, justify=CENTER,
                                      font=("Cascadia Code", 13, "bold"), text_color="#A9A9A9",
                                      fg_color="transparent")
        self.cod_entry.place(x=5, y=30)

        ctk.CTkLabel(self.frame_top, text="Producto",
                     font=("Cascadia Code", 13)
                     ).place(x=55, y=5)
        self.producto_entry = ctk.CTkEntry(self.frame_top, width=350, font=("Cascadia Code", 13),
                                          placeholder_text=("Nombre/Descripción del producto (obligatorio)"),
                                          fg_color="transparent")
        self.producto_entry.place(x=55, y=30)


        with sqlite3.connect("StockDatabase.db") as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM sucursales WHERE id_sucursal = ?", (int(self.agarrar_datos_usuario[5]), ))
            result = cursor.fetchone()

            conn.commit()

        lista = self.realizar_consulta("grupo")
        ctk.CTkLabel(self.frame_top, text="Departamento",
                     font=("Cascadia Code", 13)
                     ).place(x=410, y=5)
        self.grupo_listBox = ctk.CTkComboBox(self.frame_top, width=200, state="readonly", values=[str(result[1])],
                                             font=("Cascadia Code", 13)) #abcd

        self.grupo_listBox.set(str(result[1]))
        self.grupo_listBox.place(x=410, y=30)

        lista = self.realizar_consulta("medida")
        ctk.CTkLabel(self.frame_top, text="Medida",
                     font=("Cascadia Code", 13)
                     ).place(x=630, y=5)
        self.medida_listBox = ctk.CTkComboBox(self.frame_top, width=115, values=lista,
                                              font=("Cascadia Code", 13), justify=CENTER)
        self.medida_listBox.set("")
        self.medida_listBox.place(x=630, y=30)
       
        lista = self.realizar_consulta("proveedor")
        
        ctk.CTkLabel(self.frame_top, text="proveedor",
                     font=("Cascadia Code", 13)
                     ).place(x=5, y=60)
        self.proveedor_listBox = ctk.CTkComboBox(self.frame_top, width=200, values=["Nike","Adidas","Puma","Avura","Lacoste"], state="readonly",
                                                  font=("Cascadia Code", 13))
        self.proveedor_listBox.set("")
        self.proveedor_listBox.place(x=5, y=85)

        ctk.CTkLabel(self.frame_top, text="Nº Lote",
                     font=("Cascadia Code", 13)
                     ).place(x=245, y=60)
        self.lote_entry = ctk.CTkEntry(self.frame_top, width=65, justify=CENTER,
                                       font=("Cascadia Code", 13),
                                       fg_color="transparent")
        self.lote_entry.place(x=245, y=85)

        self.check_var = ctk.StringVar(value="on")
        self.activo_checkbox = ctk.CTkCheckBox(self.frame_top, text="LOTE activo", checkbox_width=20, checkbox_height=20,
                                              font=("Cascadia Code", 12, "bold"), corner_radius=15,
                                              command=None, variable=self.check_var,
                                              onvalue="on", offvalue="off")
        self.activo_checkbox.place(x=315, y=87)

        lista_gestor = self.realizar_consulta("responsable")
        ctk.CTkLabel(self.frame_top, text="responsable",
                     font=("Cascadia Code", 13)
                     ).place(x=5, y=115)
        self.gestor_listBox = ctk.CTkComboBox(self.frame_top,
                                                  width=170,
                                                  values=[str(self.agarrar_datos_usuario[1])],
                                                  state="readonly",
                                                  font=("Cascadia Code", 13)) #ABCD
        self.gestor_listBox.set(str(self.agarrar_datos_usuario[1]))
        self.gestor_listBox.place(x=5, y=140)

        # SUB-FRAME ESTOQUE -------------------------------------------------------------------------------------------
        self.sub_frame = atk.Frame3d(self.frame_top, width=285, height=130)
        self.sub_frame.place(x=475, y=65)

        ctk.CTkLabel(self.sub_frame, text="stock Lote",
                     font=("Cascadia Code", 13),
                     fg_color="#363636"
                     ).place(x=15, y=5)
        self.stock_entry = ctk.CTkEntry(self.sub_frame, width=100, justify=CENTER,
                                          font=("Cascadia Code", 13),
                                          fg_color="#363636", bg_color="#363636")
        self.stock_entry.place(x=15, y=30)

        ctk.CTkLabel(self.sub_frame, text="stock Mín.",
                     font=("Cascadia Code", 13),
                     fg_color="#363636"
                     ).place(x=165, y=5)
        self.min_entry = ctk.CTkEntry(self.sub_frame, width=100, justify=CENTER,
                                      font=("Cascadia Code", 13),
                                      fg_color="#363636", bg_color="#363636")
        self.min_entry.place(x=165, y=30)

        ctk.CTkLabel(self.sub_frame, text="VALOR DE ENTRADA",
                     font=("Cascadia Code", 12, "bold"),
                     fg_color="#363636"
                     ).place(x=15, y=60)
        self.costo_entry = ctk.CTkEntry(self.sub_frame, width=100,
                                        justify=CENTER, placeholder_text="$ costos",
                                        font=("Cascadia Code", 13),
                                        fg_color="#363636", bg_color="#363636")
        self.costo_entry.place(x=15, y=85)

        ctk.CTkLabel(self.sub_frame, text="VALOR DE SALIDA",
                     font=("Cascadia Code", 12, "bold"),
                     fg_color="#363636").place(x=165, y=60)
        self.reventa_entry = ctk.CTkEntry(self.sub_frame, width=100, justify=CENTER,
                                          placeholder_text="$ reventa", font=("Cascadia Code", 13),
                                          fg_color="#363636", bg_color="#363636")
        self.reventa_entry.place(x=165, y=85)
        # --------------------------------------------------------------------------------------------------------------

        ctk.CTkLabel(self.frame_top, text="¡DOBLE CLIC para seleccionar un producto!",
                     font=("Cascadia Code", 12, "bold")
                     ).place(x=10, y=179)

        # CÓDIGO DE BARRAS --------------------------------------------------------------------------------------------
        self.num_barcode = ctk.CTkEntry(self.frame_top, width=220, height=20,
                                        justify=CENTER, placeholder_text="Código de Barras",
                                        font=("Cascadia Code", 13, "bold"),
                                        corner_radius=3)
        self.num_barcode.bind("<Key>", lambda e: self.entry_off(e))
        self.num_barcode.place(x=765, y=160)

        self.img_barcode = ctk.CTkLabel(self.frame_top, text="",
                                        width=222, height=125)
        self.img_barcode.place(x=765, y=30)

        btn_generate_code = ctk.CTkButton(self.frame_top, text="",width=20,
                                          image=self.image_button(
                                              "add_barcode.png", (27, 27)),
                                          compound=LEFT, anchor=NW,
                                          fg_color="transparent",
                                          hover_color=("#D3D3D3", "#363636"),
                                          command=self.add_barcode)
        btn_generate_code.place(x=943, y=119)
        atk.tooltip(btn_generate_code, "Gerar Código de Barras")

    def widgets_bottom(self):
        self.frame_bottom = ctk.CTkFrame(self.root,
                                         width=990, height=308,
                                         fg_color="#363636")
        self.frame_bottom.place(y=245)

        ctk.CTkLabel(self.frame_bottom, text="Fecha",
                     font=("Cascadia Code", 15, "bold")
                     ).place(x=15, y=275)
        self.data_registro = DateEntry(self.frame_bottom)
        self.data_registro.place(x=60, y=280)

        # TREEVIEW ------------------------------------------------------------------------
        self.lista_productos = ttk.Treeview(self.frame_bottom, height=3, column=(
            'id', 'fecha_entrada', 'producto', 'medida', 'grupo', 'proveedor', 'lote',
            'stock', 'stock_mín', 'status', 'responsable', 'costo',
            'reventa', 'barcode', 'activo'
        ))
        self.lista_productos.heading("#0", text="")
        self.lista_productos.heading("id", text="Cód.")
        self.lista_productos.heading("fecha_entrada", text="Últ.Registro")
        self.lista_productos.heading("producto", text="Producto")
        self.lista_productos.heading("medida", text="Medida")
        self.lista_productos.heading("grupo", text="Departamento")
        self.lista_productos.heading("proveedor", text="proveedor")
        self.lista_productos.heading("lote", text="Nº Lote")
        self.lista_productos.heading("stock", text="stock")
        self.lista_productos.heading("stock_mín", text="stk.Mín.")
        self.lista_productos.heading("status", text="Status")

        self.lista_productos.heading("responsable", text="")
        self.lista_productos.heading("costo", text="")
        self.lista_productos.heading("reventa", text="")
        self.lista_productos.heading("barcode", text="")
        self.lista_productos.heading("activo", text="")

        self.lista_productos.column("#0", width=0, stretch=False)
        self.lista_productos.column("id", width=35, anchor=CENTER)
        self.lista_productos.column("fecha_entrada", width=75, anchor=CENTER)
        self.lista_productos.column("producto", width=270)
        self.lista_productos.column("medida", width=85, anchor=CENTER)
        self.lista_productos.column("grupo", width=125)
        self.lista_productos.column("proveedor", width=150)
        self.lista_productos.column("lote", width=50, anchor=CENTER)
        self.lista_productos.column("stock", width=50, anchor=CENTER)
        self.lista_productos.column("stock_mín", width=50, anchor=CENTER)
        self.lista_productos.column("status", width=70, anchor=CENTER)

        self.lista_productos.column("responsable", width=0, stretch=False)
        self.lista_productos.column("costo", width=0, stretch=False)
        self.lista_productos.column("reventa", width=0, stretch=False)
        self.lista_productos.column("barcode", width=0, stretch=False)
        self.lista_productos.column("activo", width=0, stretch=False)

        self.lista_productos.place(width=970, height=255)
        # ----------------------------------------------------------------------------------

        scrollbar_y = ttk.Scrollbar(self.frame_bottom,
                                    orient="vertical",
                                    command=self.lista_productos.yview)
        scrollbar_x = ttk.Scrollbar(self.frame_bottom,
                                    orient="horizontal",
                                    command=self.lista_productos.xview)
        self.lista_productos.configure(
            yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        scrollbar_y.place(x=970, y=0, width=20, height=255)
        scrollbar_x.place(x=0, y=254, width=990, height=20)

        self.lista_productos.bind("<Double-1>", self.on_doubleClick)

        self.select_database()

    def total_registries(self):
        total_registros = len(self.lista_productos.get_children())
        ctk.CTkLabel(self.frame_bottom, width=200, text=f"Total de Registros: {total_registros}",
                     font=("Cascadia Code", 15, "bold")
                     ).place(x=750, y=279)
