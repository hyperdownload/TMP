from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import customtkinter as ctk
import awesometkinter as atk
from tkcalendar import DateEntry

from con_database import *
from functions_base import *


class Functions(Database):
    
    def __init__(self):
        super().__init__()
        with open("sucursal.txt", "r") as file:
            linea = file.readline()

            self.id_sucursal = linea.strip()

    def variables_entries(self):
        self.code = self.cod_entry.get()
        self.Fecha = self.data_entry.get()
        self.producto = self.producto_entry.get()
        self.grupo = self.grupo_listBox.get()
        self.proveedor = self.proveedor_listBox.get()
        self.gestor = self.gestor_listBox.get()
        self.lote = self.lote_entry.get()
        self.barcode = self.barcode_entry.get()
        self.reventa = self.reventa_entry.get()
        self.Salida = self.cnt_Salida.get()
        self.stock = self.stock_entry.get()
        self.min = self.min_entry.get()
        self.status = self.status_entry.get()
    
    def clear_entries(self):
        self.cod_entry.delete(0, END)
        self.data_entry.delete(0, END)
        self.producto_entry.delete(0, END)
        self.grupo_listBox.set("")
        self.proveedor_listBox.set("")
        self.gestor_listBox.set("")
        self.lote_entry.delete(0, END)
        self.lb_activo.configure(text="")
        self.img_barcode.configure(image=None)
        self.barcode_entry.delete(0, END)
        self.barcode_entry.configure(placeholder_text="Código de Barras")
        self.reventa_entry.delete(0, END)
        self.reventa_entry.configure(placeholder_text="$")
        self.cnt_Salida.delete(0, END)
        self.stock_entry.delete(0, END)
        self.medida_listBox.set("")
        self.min_entry.delete(0, END)
        self.status_entry.delete(0, END)
    
    def on_doubleClick(self, event):
        self.clear_entries()
        
        for row in self.lista_productos.selection():
            c1, c2, c3, c4, c5, c6, c7, c8, \
                c9, c10, c11, c12, c13, c14, c15, c16 = \
                    self.lista_productos.item(row, "values")
            
            self.cod_entry.insert(END, c1)
            self.producto_entry.insert(END, c2)
            self.lote_entry.insert(END, c3)
            self.medida_listBox.set(c4)
            self.stock_entry.insert(END, c5)
            self.min_entry.insert(END, c6)
            self.proveedor_listBox.set(c8)
            self.grupo_listBox.set(c9)
            self.status_entry.insert(END, c10)
            self.data_entry.insert(END, c11)
            
            self.barcode_entry.insert(END, c12)
            if self.barcode_entry.get() != "":
                try:
                    self.img_barcode.configure(image=self.image_barcode(f"{self.lote_entry.get()}.png", (222, 100)))
                except:
                    messagebox.showinfo(
                        "Not found", message="La imagen de codigo de barras no fue encontrada!")
            
            self.reventa_entry.insert(END, f"$ {float(c13):.2f}")
            self.últimas_salidas = c14
            self.gestor_listBox.set(c15)
            self.lote_on_off(c16)
    
    def select_database(self):
        self.lista_productos.delete(*self.lista_productos.get_children())
        
        sql = f"""
            SELECT
                id, producto, lote, medida, stock, stock_mín, valor_stock, proveedor, 
                grupo, status, fecha_salida, barcode, valor_venta, salidas, responsable, activo
            FROM
                stock
            WHERE
                activo != 'borrado' AND id_sucursal = {self.id_sucursal}
        """
        data_return = Database().dql_database(sql)
        
        if data_return is not None:
            for dados in data_return:
                self.lista_productos.insert("", "end", values=dados)
        
        self.total_registros()
    
    def search_database(self):
        self.lista_productos.delete(*self.lista_productos.get_children())

        if self.busca.get() == "" \
            and self.busca_grupo_listBox.get() == "Departamento":
                
                self.select_database()

        else:
            if self.busca.get():
                self.busca.insert(END, "%")
                busca = self.busca.get()

                query_select = f"""
                            SELECT
                                id, producto, lote, medida, stock, stock_mín, valor_stock, proveedor, 
                                grupo, status, fecha_salida, barcode, valor_venta, salidas, responsable, activo
                            FROM
                                stock
                            WHERE
                                producto LIKE '%{busca}%'
                                OR lote LIKE '%{busca}%'
                                OR barcode LIKE '%{busca}%'
                                AND activo != 'borrado' AND id_sucursal = {self.id_sucursal}
                                ORDER BY producto ASC
                            """

            elif self.busca_grupo_listBox.get() != "Departamento":
                self.busca_grupo_listBox.set(self.busca_grupo_listBox.get() + "%")
                busca = self.busca_grupo_listBox.get()

                query_select = f"""
                            SELECT
                                id, producto, lote, medida, stock, stock_mín, valor_stock, proveedor,
                                grupo, status, fecha_salida, barcode, valor_venta, salidas, responsable, activo
                            FROM
                                stock
                            WHERE
                                grupo LIKE '%{busca}%' AND activo != 'borrado' AND id_sucursal = {self.id_sucursal}
                                ORDER BY producto ASC
                            """

            data_return = self.dql_database(query_select)

            if data_return is not None:
                for dados in data_return:
                    self.lista_productos.insert("", END, values=dados)

            self.total_registros()

        self.clear_search()
    
    def clear_search(self):
        self.busca.delete(0, END)
        self.busca.configure(placeholder_text="Buscar Producto, Nº Lote, Código de Barras")
        
        self.busca_grupo_listBox.set("Departamento")
    
    def save_register(self):
        self.variables_entries()
        
        if self.code == "":
            messagebox.showerror(
                "ID invalid", message="Seleccione el producto para la salida!"
            )
        elif self.Salida == "" or not self.Salida.isdigit():
            messagebox.showerror(
                "Invalid input", message="Informe la cantidad de salida!"
            )
        
        else:
            if self.radio_button_var.get() == 0:
                messagebox.showerror(
                    "Invalid input", message="Selecione el tipo de Salida: \n\n  facturación \n  Consumo Interno"
                )
            else:
                self.stock = int(self.stock) - int(self.Salida)
                
                
                
                sql = """
                    UPDATE stock SET
                        stock=?, salidas=?, fecha_salida=?, responsable=?
                    WHERE
                        id=?
                """
                dados = [self.stock, self.Salida, self.fecha_salida.get(), self.gestor,
                         self.code]
                self.dml_database(sql, dados)
            
            self.clear_entries()
            self.select_database()
    
    def lote_on_off(self, activo=""):
        if activo == "off":
            self.cnt_Salida.configure(state=DISABLED)
            self.r_button_facturación.configure(state=DISABLED)
            self.r_button_consumo.configure(state=DISABLED)

            self.lb_activo.configure(text="LOTE INactivo")

        else:
            self.cnt_Salida.configure(state=NORMAL)
            self.r_button_facturación.configure(state=NORMAL)
            self.r_button_consumo.configure(state=NORMAL)

            if activo == "on":
                self.lb_activo.configure(text="LOTE activo")


class VentanaSalidas(Functions, FunctionsExtras):
    def __init__(self, root, id):
        self.root = root
        self.id = id

        with open("sucursal.txt", "r") as file:
            linea = file.readline()

            self.id_sucursal = linea.strip()
        
        self.buttons_header()
        self.widgets_top()
        self.widgets_bottom()
        self.view_bottom()
    
    def realizar_consulta(self, columna):
        return self.dql_database(f"SELECT {columna} FROM stock WHERE activo != 'borrado' AND id_sucursal = {self.id_sucursal}", column_names=True)
    
    def buttons_header(self):
        self.agarrar_datos_usuario = Database().recaudar_datos_usuario(self.id)

        # with sqlite3.connect("StockDatabase.db") as conn:
        #     cursor = conn.cursor()

        #     cursor.execute("SELECT * FROM sucursales WHERE id_sucursal = ?", (int(self.agarrar_datos_usuario[5]), ))
        #     result = cursor.fetchone()

        #     conn.commit()

        self.frame_buttons = ctk.CTkFrame(self.root,
                                          width=990, height=40,
                                          fg_color="#363636")
        self.frame_buttons.place(x=1, y=1)

        btn_save = ctk.CTkButton(self.frame_buttons, text="",
                                 width=30,
                                 corner_radius=3,
                                 image=self.image_button("save.png", (26, 26)),
                                 compound=LEFT, anchor=NW,
                                 fg_color="transparent",
                                 hover_color=("#D3D3D3", "#4F4F4F"),
                                 command=self.save_register)
        btn_save.place(x=3, y=3)
        atk.tooltip(btn_save, "Guardar Registro")

        ctk.CTkLabel(self.frame_buttons, text="||",
                     font=("Arial", 30), text_color="#696969",
                     fg_color="transparent").place(x=40)

        btn_clear = ctk.CTkButton(self.frame_buttons, text="",
                                  width=30,
                                  corner_radius=3,
                                  image=self.image_button("clear-entries.png", (26, 26)),
                                  compound=LEFT, anchor=NW,
                                  fg_color="transparent",
                                  hover_color=("#D3D3D3", "#4F4F4F"),
                                  command=self.clear_entries)
        btn_clear.place(x=57, y=3)
        atk.tooltip(btn_clear, "Borrar campo de datos")
        
    def widgets_top(self):
        self.frame_top = ctk.CTkFrame(self.root,
                                      width=990, height=195)
        self.frame_top.place(y=45)
        
        ctk.CTkLabel(self.frame_top, text="Código",
                     font=("Cascadia Code", 13)
                     ).place(x=5, y=5)
        self.cod_entry = ctk.CTkEntry(self.frame_top,
                                      width=55,
                                      justify=CENTER,
                                      font=("Cascadia Code", 13), text_color="#A9A9A9",
                                      fg_color="transparent")
        self.cod_entry.bind("<Key>", lambda e: self.entry_off(e))
        self.cod_entry.place(x=5, y=30)

        ctk.CTkLabel(self.frame_top, text="Últ. Salida",
                     font=("Cascadia Code", 13)
                     ).place(x=70, y=5)
        self.data_entry = ctk.CTkEntry(self.frame_top,
                                       width=105,
                                       justify=CENTER,
                                       font=("Cascadia Code", 13), text_color="#A9A9A9",
                                       fg_color="transparent")
        self.data_entry.bind("<Key>", lambda e: self.entry_off(e))
        self.data_entry.place(x=70, y=30)

        ctk.CTkLabel(self.frame_top, text="Producto",
                     font=("Cascadia Code", 13)
                     ).place(x=185, y=5)
        self.producto_entry = ctk.CTkEntry(self.frame_top,
                                          width=350,
                                          font=("Cascadia Code", 13), text_color="#A9A9A9",
                                          fg_color="transparent")
        self.producto_entry.bind("<Key>", lambda e: self.entry_off(e))
        self.producto_entry.place(x=185, y=30)

        lista_grupo = self.realizar_consulta("grupo")
        ctk.CTkLabel(self.frame_top, text="Departamento",
                     font=("Cascadia Code", 13)
                     ).place(x=545, y=5)
        
        with sqlite3.connect("StockDatabase.db") as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM sucursales WHERE id_sucursal = ?", (int(self.agarrar_datos_usuario[5]), ))
            result = cursor.fetchone()

            conn.commit()

        self.grupo_listBox = ctk.CTkComboBox(self.frame_top,
                                             width=200,
                                             values=[str(result[1])],
                                             font=("Cascadia Code", 13), text_color="#A9A9A9",state="readonly")#abcd
        self.grupo_listBox.set(str(result[1]))
        self.grupo_listBox.bind("<Key>", lambda e: self.entry_off(e))
        self.grupo_listBox.place(x=545, y=30)

        lista_proveedor = self.realizar_consulta("proveedor")
        ctk.CTkLabel(self.frame_top, text="proveedor",
                     font=("Cascadia Code", 13)
                     ).place(x=245, y=70)
        self.proveedor_listBox = ctk.CTkComboBox(self.frame_top,
                                                  width=200,
                                                  values=["Nike","Adidas","Puma","Avura","Lacoste"], state="readonly",
                                                  font=("Cascadia Code", 13), text_color="#A9A9A9")
        self.proveedor_listBox.set("")
        self.proveedor_listBox.bind("<Key>", lambda e: self.entry_off(e))
        self.proveedor_listBox.place(x=245, y=95)
        
        lista_gestor = self.realizar_consulta("responsable")
        ctk.CTkLabel(self.frame_top, text="responsable",
                     font=("Cascadia Code", 13)
                     ).place(x=245, y=135)
        self.gestor_listBox = ctk.CTkComboBox(self.frame_top,
                                              width=170,
                                              values=[str(self.agarrar_datos_usuario[1])],
                                              font=("Cascadia Code", 13))#abcd
        self.gestor_listBox.set(str(self.agarrar_datos_usuario[1]))
        self.gestor_listBox.place(x=245, y=160)

        ctk.CTkLabel(self.frame_top, text="Nº Lote", 
                     font=("Cascadia Code", 13)
                     ).place(x=505, y=70)
        self.lote_entry = ctk.CTkEntry(self.frame_top,
                                       width=65,
                                       justify=CENTER,
                                       font=("Cascadia Code", 13), text_color="#A9A9A9",
                                       fg_color="transparent")
        self.lote_entry.bind("<Key>", lambda e: self.entry_off(e))
        self.lote_entry.place(x=505, y=95)
        
        self.lb_activo = ctk.CTkLabel(self.frame_top, text="",
                                     width=105, height=28,
                                     font=("Cascadia Code", 15, "bold"),
                                     text_color="#ADFF2F",
                                     anchor="nw")
        self.lb_activo.place(x=575, y=98)
        
        self.img_barcode = ctk.CTkLabel(self.frame_top, text="",
                                        width=222, height=100)
        self.img_barcode.place(x=5, y=63)

        self.barcode_entry = ctk.CTkEntry(self.frame_top,
                                          width=220, height=20,
                                          justify=CENTER,
                                          placeholder_text="Código de Barras",
                                          font=("Cascadia Code", 13, "bold"), text_color="#A9A9A9",
                                          corner_radius=3)
        self.barcode_entry.bind("<Key>", lambda e: self.entry_off(e))
        self.barcode_entry.place(x=5, y=165)
        
        self.radio_button_var = IntVar(value=0)
        self.r_button_facturación = ctk.CTkRadioButton(self.frame_top, text="Facturación", 
                                                       font=("Cascadia Code", 13, "bold"), 
                                                       radiobutton_width=20, radiobutton_height=20,
                                                       fg_color="#ADFF2F",
                                                       hover_color="#ADFF2F",
                                                       variable=self.radio_button_var, 
                                                       value=1)
        self.r_button_facturación.place(x=480, y=140)
        self.r_button_consumo = ctk.CTkRadioButton(self.frame_top, text="Consumo Interno", 
                                                   font=("Cascadia Code", 13, "bold"),
                                                   radiobutton_width=20, radiobutton_height=20,
                                                   fg_color="#ADFF2F",
                                                   hover_color="#ADFF2F",
                                                   variable=self.radio_button_var,
                                                   value=2)
        self.r_button_consumo.place(x=480, y=165)

        ctk.CTkLabel(self.frame_top, text="VALOR DE SALIDA",
                     font=("Cascadia Code", 12, "bold")
                     ).place(x=635, y=130)
        self.reventa_entry = ctk.CTkEntry(self.frame_top,
                                          width=110,
                                          justify=CENTER,
                                          font=("Cascadia Code", 13), text_color="#A9A9A9",
                                          placeholder_text="$",
                                          fg_color="transparent")
        self.reventa_entry.bind("<Key>", lambda e: self.entry_off(e))
        self.reventa_entry.place(x=635, y=160)

        # SUB_FRAME salidas ---------------------------------------------------------------------------------
        self.frame_salidas = atk.Frame3d(self.frame_top)
        self.frame_salidas.place(x=755, y=5, width=230, height=185)

        ctk.CTkLabel(self.frame_salidas, text="Cnt. Salida",
                     font=("Cascadia Code", 13),
                     fg_color="#363636", bg_color="#363636"
                     ).place(x=10, y=10)
        self.cnt_Salida = ctk.CTkEntry(self.frame_salidas,
                                        width=75,
                                        justify=CENTER,
                                        font=("Cascadia Code", 13),
                                        fg_color="#363636", bg_color="#363636")
        self.cnt_Salida.place(x=10, y=35)

        ctk.CTkLabel(self.frame_salidas, text="Lote Actual",
                     font=("Cascadia Code", 13),
                     fg_color="#363636", bg_color="#363636"
                     ).place(x=10, y=65)
        self.stock_entry = ctk.CTkEntry(self.frame_salidas,
                                          width=75,
                                          justify=CENTER,
                                          font=("Cascadia Code", 13, "bold"), text_color="#A9A9A9",
                                          fg_color="#363636", bg_color="#363636",
                                          corner_radius=3)
        self.stock_entry.bind("<Key>", lambda e: self.entry_off(e))
        self.stock_entry.place(x=10, y=90)
        
        lista_medida = self.realizar_consulta("medida")
        
        ctk.CTkLabel(self.frame_salidas, text="Medida",
                     font=("Cascadia Code", 13),
                     fg_color="#363636", bg_color="#363636"
                     ).place(x=120, y=65)
        self.medida_listBox = ctk.CTkComboBox(self.frame_salidas,
                                              width=100,
                                              values=lista_medida,
                                              font=("Cascadia Code", 13), text_color="#A9A9A9",
                                              fg_color="#363636", bg_color="#363636",
                                              justify=CENTER)
        self.medida_listBox.set("")
        self.medida_listBox.bind("<Key>", lambda e: self.entry_off(e))
        self.medida_listBox.place(x=120, y=90)

        ctk.CTkLabel(self.frame_salidas, text="Stock Mín.",
                     font=("Cascadia Code", 13),
                     fg_color="#363636", bg_color="#363636"
                     ).place(x=10, y=120)
        self.min_entry = ctk.CTkEntry(self.frame_salidas,
                                      width=75,
                                      justify=CENTER,
                                      font=("Cascadia Code", 13, "bold"), text_color="#A9A9A9",
                                      fg_color="#363636", bg_color="#363636",
                                      corner_radius=3)
        self.min_entry.bind("<Key>", lambda e: self.entry_off(e))
        self.min_entry.place(x=10, y=145)

        ctk.CTkLabel(self.frame_salidas, text="Estado de Lote",
                     font=("Cascadia Code", 13),
                     fg_color="#363636", bg_color="#363636"
                     ).place(x=126, y=120)
        self.status_entry = ctk.CTkEntry(self.frame_salidas,
                                         width=100,
                                         justify=CENTER,
                                         font=("Cascadia Code", 13, "bold"), text_color="#A9A9A9",
                                         fg_color="#363636", bg_color="#363636",
                                         corner_radius=2)
        self.status_entry.bind("<Key>", lambda e: self.entry_off(e))
        self.status_entry.place(x=120, y=145)
        # -----------------------------------------------------------------------------------------------------
    
    def widgets_bottom(self):
        self.frame_bottom = ctk.CTkFrame(self.root,
                                         width=990, height=315,
                                         fg_color="#363636")
        self.frame_bottom.place(y=240)

        ctk.CTkLabel(self.frame_bottom, text="Seguimiento de Lotes - (DOBLE CLICK para seleccionar un producto!)",
                     font=("Cascadia Code", 12, "bold")
                     ).place(x=10, y=1)

        self.busca = ctk.CTkEntry(self.frame_bottom,
                                  width=350,
                                  placeholder_text="Buscar Producto, Nº Lote, Código de Barras",
                                  font=("Cascadia Code", 13))
        self.busca.place(x=10, y=50)
        
        lista_grupo = self.realizar_consulta("grupo")
        self.busca_grupo_listBox = ctk.CTkComboBox(self.frame_bottom, 
                                                   width=200,
                                                   values=lista_grupo,
                                                   font=("Cascadia Code", 13))
        self.busca_grupo_listBox.set("Departamento")
        self.busca_grupo_listBox.place(x=370, y=50)

        ctk.CTkButton(self.frame_bottom, text="BUSCAR",
                      width=60,
                      font=("Cascadia Code", 13, "bold"),
                      fg_color="#696969",
                      hover_color=("#D3D3D3", "#1C1C1C"),
                      command=self.search_database).place(x=640, y=50)

        ctk.CTkButton(self.frame_bottom, text="LIMPIAR",
                      width=60,
                      font=("Cascadia Code", 13, "bold"),
                      fg_color="#696969",
                      hover_color=("#D3D3D3", "#1C1C1C"),
                      command=self.clear_search).place(x=710, y=50)

        ctk.CTkLabel(self.frame_bottom, text="Fecha",
                     font=("Cascadia Code", 15, "bold")
                     ).place(x=15, y=286)
        self.fecha_salida = DateEntry(self.frame_bottom)
        self.fecha_salida.place(x=60, y=290)
    
    def view_bottom(self):
        self.lista_productos = ttk.Treeview(self.frame_bottom, height=3, column=(
            'id', 'producto', 'lote', 'medida', 'stock', 'mínimo', 
            'valor', 'proveedor', 'grupo', 'status', 'fecha_salida', 
            'barcode', 'reventa', 'salidas', 'gestor', 'activo'
        ))

        self.lista_productos.heading("#0", text="")
        self.lista_productos.heading("id", text="Cód.")
        self.lista_productos.heading("producto", text="Producto")
        self.lista_productos.heading("lote", text="Nº Lote")
        self.lista_productos.heading("medida", text="Medida")
        self.lista_productos.heading("stock", text="stock")
        self.lista_productos.heading("mínimo", text="cnt.Mín")
        self.lista_productos.heading("valor", text="Valor stock")
        self.lista_productos.heading("proveedor", text="proveedor")
        self.lista_productos.heading("grupo", text="Departamento")
        self.lista_productos.heading("status", text="Status")
        self.lista_productos.heading("fecha_salida", text="")
        self.lista_productos.heading("barcode", text="Código de Barras")
        self.lista_productos.heading("reventa", text="")
        self.lista_productos.heading("salidas", text="")
        self.lista_productos.heading("gestor", text="")
        self.lista_productos.heading("activo", text="")

        self.lista_productos.column("#0", width=0, stretch=False)
        self.lista_productos.column("id", width=35, anchor=CENTER)
        self.lista_productos.column("producto", width=270)
        self.lista_productos.column("lote", width=50, anchor=CENTER)
        self.lista_productos.column("medida", width=85, anchor=CENTER)
        self.lista_productos.column("stock", width=55, anchor=CENTER)
        self.lista_productos.column("mínimo", width=55, anchor=CENTER)
        self.lista_productos.column("valor", width=80, anchor=CENTER)
        self.lista_productos.column("proveedor", width=150)
        self.lista_productos.column("grupo", width=125)
        self.lista_productos.column("status", width=70, anchor=CENTER)
        self.lista_productos.column("fecha_salida", width=0, stretch=False)
        self.lista_productos.column("barcode", width=100, anchor=CENTER)
        self.lista_productos.column("reventa", width=0, stretch=False)
        self.lista_productos.column("salidas", width=0, stretch=False)
        self.lista_productos.column("gestor", width=0, stretch=False)
        self.lista_productos.column("activo", width=0, stretch=False)
        
        self.lista_productos.place(y=88, width=970, height=180)

        # SCROLLBAR -----------------------------------------------------------------------------------------
        scrollbar_y = ttk.Scrollbar(self.frame_bottom,
                                    orient="vertical",
                                    command=self.lista_productos.yview)
        scrollbar_x = ttk.Scrollbar(self.frame_bottom,
                                    orient="horizontal",
                                    command=self.lista_productos.xview)
        self.lista_productos.configure(yscrollcommand=scrollbar_y.set,
                                      xscrollcommand=scrollbar_x.set)
        scrollbar_y.place(x=970, y=88, width=20, height=200)
        scrollbar_x.place(x=0, y=268, width=970, height=20)
        # ---------------------------------------------------------------------------------------------------
        
        self.lista_productos.bind("<Double-1>", self.on_doubleClick)
        
        self.select_database()
        
    def total_registros(self):
        total_registros = len(self.lista_productos.get_children())
        ctk.CTkLabel(self.frame_bottom, text=f"Total de Registros: {total_registros}",
                     width=200,
                     font=("Cascadia Code", 15, "bold")
                     ).place(x=750, y=288)
