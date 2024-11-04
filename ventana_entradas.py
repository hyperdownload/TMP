from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import customtkinter as ctk
import awesometkinter as atk
from tkcalendar import DateEntry

from con_database import *
from functions_base import *


class FunctionsEntradas(Database):

    def __init__(self):
        super().__init__()
        with open("sucursal.txt", "r") as file:
            linea = file.readline()

            self.id_sucursal = linea.strip()

    def variables_entries(self):
        self.code = self.cod_entry.get()
        self.Fecha = self.data_entry.get()
        self.producto = self.producto_entry.get()
        self.lote = self.lote_entry.get()

        self.medida = self.medida_listBox.get()
        self.grupo = self.grupo_listBox.get()
        self.proveedor = self.proveedor_listBox.get()
        self.gestor = self.gestor_listBox.get()

        self.cnt = self.cnt_entrada.get()
        self.stock = self.stock_entry.get()
        self.min = self.min_entry.get()
        self.status = self.status_entry.get()

        self.costo = self.costo_entry.get()
        self.reventa = self.reventa_entry.get()

        self.barcode = self.barcode_entry.get()

    def clear_entries(self):
        self.lote_on_off()

        self.cod_entry.delete(0, END)
        self.data_entry.delete(0, END)
        self.producto_entry.delete(0, END)
        self.lote_entry.delete(0, END)
        self.lb_activo.configure(text="")

        self.medida_listBox.set("")
        self.grupo_listBox.set("")
        self.proveedor_listBox.set("")
        self.gestor_listBox.set("")

        self.cnt_entrada.delete(0, END)
        self.stock_entry.delete(0, END)
        self.min_entry.delete(0, END)
        self.status_entry.delete(0, END)

        self.costo_entry.delete(0, END)
        self.costo_entry.configure(placeholder_text="$")
        self.reventa_entry.delete(0, END)
        self.reventa_entry.configure(placeholder_text="$")

        self.barcode_entry.delete(0, END)
        self.barcode_entry.configure(placeholder_text="Código de Barras")
        self.img_barcode.configure(image=None)

    def select_database(self):
        self.lista_productos.delete(*self.lista_productos.get_children())

        query_select = f"""
            SELECT 
                id, producto, medida, lote, stock, stock_mín, 
                valor_stock, proveedor, grupo, status, fecha_entrada, 
                barcode, costo_unitario, valor_venta, activo, responsable
            FROM 
                stock
            WHERE activo != 'borrado' AND id_sucursal = {self.id_sucursal}
        """
        data_return = Database().dql_database(query_select)

        if data_return is not None:
            for dados in data_return:
                self.lista_productos.insert("", "end", values=dados)

        self.total_registries()

    def on_doubleClick(self, event):
        self.clear_entries()

        for row in self.lista_productos.selection():
            c1, c2, c3, c4, c5, c6, c7, c8, c9, \
                    c10, c11, c12, c13, c14, c15, c16 = \
                    self.lista_productos.item(row, "values")

            self.cod_entry.insert(END, c1)
            self.producto_entry.insert(END, c2)
            self.medida_listBox.set(c3)
            self.lote_entry.insert(END, c4)
            self.stock_entry.insert(END, c5)
            self.min_entry.insert(END, c6)
            self.proveedor_listBox.set(c8)
            self.grupo_listBox.set(c9)
            self.status_entry.insert(END, c10)
            self.data_entry.insert(END, c11)
            self.barcode_entry.insert(END, c12)
            self.costo_entry.insert(END, c13)
            self.reventa_entry.insert(END, c14)

            if self.barcode_entry.get() != "":
                try:
                    self.img_barcode.configure(image=self.image_barcode(f"{self.lote_entry.get()}.png", (222, 100)))
                except Exception:
                    messagebox.showinfo("Not found", message="La imagen del código de barras no fue encontrada!")

            self.lote_on_off(c15)
            self.gestor_listBox.set(c16)

    def save_register(self):
        self.variables_entries()

        if self.code == "":
            messagebox.showerror("ID invalid", message="Seleccione un producto para entrada!")
        elif self.cnt == "" or not self.cnt.isdigit():
            messagebox.showerror("Invalid input", message="Informe a quantidade de entrada do producto!")

        else:
            try:
                self._extracted_from_save_register_11()
            except Exception:
                messagebox.showerror("Error", message="Algo deu errado! :( \n Não foi possível realizar o registro")

        self.clear_entries()
        self.select_database()

    def _extracted_from_save_register_11(self):
        add_stock = int(self.cnt) + int(self.stock)

        query_update = f"""
                    UPDATE stock SET
                        proveedor=?, lote=?, medida=?, stock=?, costo_unitario=?, valor_venta=?, fecha_entrada=?, responsable=?
                    WHERE id=? AND activo != 'borrado AND id_sucursal = {self.id_sucursal}'
                """

        if self.costo == "":
            self.costo = 0
        if self.reventa == "":
            self.reventa = 0

        dados = [self.proveedor, self.lote, self.medida, add_stock, 
                 self.costo, self.reventa, self.fecha_entrada.get(), self.gestor,
                 self.code]
        self.dml_database(query_update, dados)

    def search_database(self):
        self.lista_productos.delete(*self.lista_productos.get_children())

        if self.busca.get() == "" \
                and self.busca_mes.get() == "" \
                    and self.busca_año.get() == "" \
                        and self.status_listBox.get() == "Status":

            self.select_database()

        else:
            if self.busca.get():
                self.busca.insert(END, "%")
                busca = self.busca.get()

                query_select = f"""
                            SELECT
                                id, producto, medida, lote, stock, stock_mín,
                                valor_stock, proveedor, grupo, status, fecha_entrada,
                                barcode, costo_unitario, valor_venta, activo, responsable
                            FROM
                                stock
                            WHERE
                                producto LIKE '%{busca}%'
                                OR lote LIKE '%{busca}%'
                                OR barcode LIKE '%{busca}%'
                                AND activo != 'borrado'
                                AND id_sucursal = {self.id_sucursal}
                                ORDER BY producto ASC
                            """

            elif self.status_listBox.get() != "Status":
                self.status_listBox.set(f"{self.status_listBox.get()}%")
                busca = self.status_listBox.get()

                query_select = f"""
                            SELECT
                                id, producto, medida, lote, stock, stock_mín,
                                valor_stock, proveedor, grupo, status, fecha_entrada,
                                barcode, costo_unitario, valor_venta, activo, responsable
                            FROM
                                stock
                            WHERE
                                status LIKE '%{busca}%' AND activo != 'borrado' AND id_Sucursal = {self.id_sucursal}
                                ORDER BY producto ASC
                            """

            data_return = self.dql_database(query_select)

            if data_return is not None:
                for dados in data_return:
                    self.lista_productos.insert("", END, values=dados)

            self.total_registries()

        self.clear_search()

    def clear_search(self):
        self.busca.delete(0, END)
        self.busca_mes.delete(0, END)
        self.busca_año.delete(0, END)

        self.busca.configure(placeholder_text="Buscar Producto, Nº Lote, Código de Barras")
        self.busca_mes.configure(placeholder_text="Mes")
        self.busca_año.configure(placeholder_text="año")
        self.status_listBox.set("Status")

    def lote_on_off(self, activo=""):
        if activo == "off":
            self._extracted_from_lote_on_off_3(DISABLED)
            self.lb_activo.configure(text="LOTE INactivo")

        else:
            self._extracted_from_lote_on_off_3(NORMAL)
            if activo == "on":
                self.lb_activo.configure(text="LOTE activo")

    def _extracted_from_lote_on_off_3(self, state):
        self.medida_listBox.configure(state=state)
        self.proveedor_listBox.configure(state=state)
        self.lote_entry.configure(state=state)
        self.cnt_entrada.configure(state=state)
        self.costo_entry.configure(state=state)
        self.reventa_entry.configure(state=state)

class VentanaEntradas(FunctionsEntradas, FunctionsExtras):
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
        self.total_registries()

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

        btn_clear = ctk.CTkButton(self.frame_buttons, text="", width=30,
                                  corner_radius=3,
                                  image=self.image_button("clear-entries.png", (26, 26)),
                                  compound=LEFT, anchor=NW,
                                  fg_color="transparent",
                                  hover_color=("#D3D3D3", "#4F4F4F"),
                                  command=self.clear_entries)
        btn_clear.place(x=57, y=3)
        atk.tooltip(btn_clear, "Limpiar campos de datos")

    def widgets_top(self):
        self.frame_top = ctk.CTkFrame(self.root,
                                      width=990, height=195,)
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

        ctk.CTkLabel(self.frame_top, text="Últ. Entrada",
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

        self.realizar_consulta("grupo")
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
                                             values=[result[1]],
                                             font=("Cascadia Code", 13), text_color="#A9A9A9")#abcd
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
                                                  font=("Cascadia Code", 13))
        self.proveedor_listBox.set("")
        self.proveedor_listBox.place(x=245, y=95)
        
        lista_gestor = self.realizar_consulta("responsable")
        ctk.CTkLabel(self.frame_top, text="responsable",
                     font=("Cascadia Code", 13)
                     ).place(x=245, y=135)
        
        self.gestor_listBox = ctk.CTkComboBox(self.frame_top,
                                                  width=170,
                                                  values=[str(self.agarrar_datos_usuario[1])],state="readonly",
                                                  font=("Cascadia Code", 13))#abcd
        self.gestor_listBox.set(str(self.agarrar_datos_usuario[1]))
        self.gestor_listBox.place(x=245, y=160)

        ctk.CTkLabel(self.frame_top, text="Nº Lote",
                     font=("Cascadia Code", 13)
                     ).place(x=505, y=70)
        self.lote_entry = ctk.CTkEntry(self.frame_top, width=65, justify=CENTER,
                                       font=("Cascadia Code", 13),
                                       fg_color="transparent")
        self.lote_entry.place(x=505, y=95)
        
        self.lb_activo = ctk.CTkLabel(self.frame_top, text="", width=105, height=28,
                                     font=("Cascadia Code", 15, "bold"),
                                     text_color="#ADFF2F",
                                     anchor="nw")
        self.lb_activo.place(x=575, y=98)

        self.img_barcode = ctk.CTkLabel(self.frame_top, text="",
                                        width=222, height=100)
        self.img_barcode.place(x=5, y=63)
        
        self.barcode_entry = ctk.CTkEntry(self.frame_top, width=220, height=20, justify=CENTER,
                                          placeholder_text="Código de Barras",
                                          font=("Cascadia Code", 13, "bold"), text_color="#A9A9A9",
                                          corner_radius=3)
        self.barcode_entry.bind("<Key>", lambda e: self.entry_off(e))
        self.barcode_entry.place(x=5, y=165)

        ctk.CTkLabel(self.frame_top, text="VALOR DE ENTRADA",
                     font=("Cascadia Code", 12, "bold")
                     ).place(x=505, y=135)
        self.costo_entry = ctk.CTkEntry(self.frame_top,
                                        width=110,
                                        justify=CENTER,
                                        font=("Cascadia Code", 13),
                                        placeholder_text="$",
                                        fg_color="transparent")
        self.costo_entry.place(x=505, y=160)

        ctk.CTkLabel(self.frame_top, text="VALOR DE SALIDA",
                     font=("Cascadia Code", 12, "bold")
                     ).place(x=635, y=135)
        self.reventa_entry = ctk.CTkEntry(self.frame_top,
                                          width=110,
                                          justify=CENTER,
                                          font=("Cascadia Code", 13),
                                          placeholder_text="$",
                                          fg_color="transparent")
        self.reventa_entry.place(x=635, y=160)

        # SUB_FRAME ENTRADAS ---------------------------------------------------------------------------------
        self.frame_entradas = atk.Frame3d(self.frame_top)
        self.frame_entradas.place(x=755, y=5, width=230, height=185)

        ctk.CTkLabel(self.frame_entradas, text="cnt. Entrada",
                     font=("Cascadia Code", 13),
                     fg_color="#363636", bg_color="#363636"
                     ).place(x=10, y=10)
        self.cnt_entrada = ctk.CTkEntry(self.frame_entradas,
                                        width=75,
                                        justify=CENTER,
                                        font=("Cascadia Code", 13),
                                        fg_color="#363636", bg_color="#363636")
        self.cnt_entrada.place(x=10, y=35)

        ctk.CTkLabel(self.frame_entradas, text="stock Lote",
                     font=("Cascadia Code", 13),
                     fg_color="#363636", bg_color="#363636"
                     ).place(x=10, y=65)
        self.stock_entry = ctk.CTkEntry(self.frame_entradas,
                                          width=75,
                                          justify=CENTER,
                                          font=("Cascadia Code", 13, "bold"), text_color="#A9A9A9",
                                          fg_color="#363636", bg_color="#363636",
                                          corner_radius=3)
        self.stock_entry.bind("<Key>", lambda e: self.entry_off(e))
        self.stock_entry.place(x=10, y=90)
        
        lista_medida = self.realizar_consulta("medida")
        ctk.CTkLabel(self.frame_entradas, text="Medida",
                     font=("Cascadia Code", 13),
                     fg_color="#363636", bg_color="#363636"
                     ).place(x=120, y=65)
        self.medida_listBox = ctk.CTkComboBox(self.frame_entradas,
                                              width=100,
                                              values=lista_medida,
                                              font=("Cascadia Code", 13),
                                              fg_color="#363636", bg_color="#363636",
                                              justify=CENTER)
        self.medida_listBox.set("")
        self.medida_listBox.place(x=120, y=90)

        ctk.CTkLabel(self.frame_entradas, text="stock Mín.",
                     font=("Cascadia Code", 13),
                     fg_color="#363636", bg_color="#363636"
                     ).place(x=10, y=120)
        self.min_entry = ctk.CTkEntry(self.frame_entradas,
                                      width=75,
                                      justify=CENTER,
                                      font=("Cascadia Code", 13, "bold"), text_color="#A9A9A9",
                                      fg_color="#363636", bg_color="#363636",
                                      corner_radius=3)
        self.min_entry.bind("<Key>", lambda e: self.entry_off(e))
        self.min_entry.place(x=10, y=145)

        ctk.CTkLabel(self.frame_entradas, text="Status Lote",
                     font=("Cascadia Code", 13),
                     fg_color="#363636", bg_color="#363636"
                     ).place(x=120, y=120)
        self.status_entry = ctk.CTkEntry(self.frame_entradas,
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

        ctk.CTkLabel(self.frame_bottom, text="Seguimiento de Lotes - (¡DOBLE CLIC para seleccionar un producto!)",
                     font=("Cascadia Code", 12, "bold")
                     ).place(x=10, y=1)

        self.busca = ctk.CTkEntry(self.frame_bottom,
                                  width=350,
                                  placeholder_text="Buscar Producto, Nº Lote, Código de Barras",
                                  font=("Cascadia Code", 13))
        self.busca.place(x=10, y=50)

        self.busca_mes = ctk.CTkEntry(self.frame_bottom,
                                      width=50,
                                      justify=CENTER,
                                      placeholder_text="Mes",
                                      font=("Cascadia Code", 13))
        self.busca_mes.place(x=380, y=50)
        ctk.CTkLabel(self.frame_bottom, text="/",
                     font=("Cascadia Code", 20, "bold")
                     ).place(x=435, y=50)
        self.busca_año = ctk.CTkEntry(self.frame_bottom,
                                      width=50,
                                      justify=CENTER,
                                      placeholder_text="año",
                                      font=("Cascadia Code", 13))
        self.busca_año.place(x=450, y=50)

        lista_status = ['OK', 'VACIO', 'CRÍTICO']
        self.status_listBox = ctk.CTkComboBox(self.frame_bottom,
                                              width=100,
                                              values=lista_status,
                                              font=("Cascadia Code", 13))
        self.status_listBox.set("Status")
        self.status_listBox.place(x=520, y=50)

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
        self.fecha_entrada = DateEntry(self.frame_bottom)
        self.fecha_entrada.place(x=60, y=290)

    def view_bottom(self):
        self.lista_productos = ttk.Treeview(self.frame_bottom, height=3, column=(
            'id', 'producto', 'medida', 'lote', 'stock', 'mín',
            'valor', 'proveedor', 'grupo', 'status', 'Fecha', 
            'barcode', 'costo', 'reventa', 'activo', 'responsable'
        ))

        self.lista_productos.heading("#0", text="")
        self.lista_productos.heading("id", text="Cód.")
        self.lista_productos.heading("producto", text="Producto")
        self.lista_productos.heading("medida", text="Medida")
        self.lista_productos.heading("lote", text="Nº Lote")
        self.lista_productos.heading("stock", text="stock")
        self.lista_productos.heading("mín", text="cnt.Mín.")
        self.lista_productos.heading("valor", text="Valor stock")
        self.lista_productos.heading("proveedor", text="proveedor")
        self.lista_productos.heading("grupo", text="Departamento")
        self.lista_productos.heading("status", text="Status")
        self.lista_productos.heading("Fecha", text="")
        self.lista_productos.heading("barcode", text="Código de Barras")
        self.lista_productos.heading("costo", text="")
        self.lista_productos.heading("reventa", text="")
        self.lista_productos.heading("activo", text="")
        self.lista_productos.heading("responsable", text="")

        self.lista_productos.column("#0", width=0, stretch=False)
        self.lista_productos.column("id", width=35, anchor=CENTER)
        self.lista_productos.column("producto", width=270)
        self.lista_productos.column("medida", width=85, anchor=CENTER)
        self.lista_productos.column("lote", width=50, anchor=CENTER)
        self.lista_productos.column("stock", width=50, anchor=CENTER)
        self.lista_productos.column("mín", width=55, anchor=CENTER)
        self.lista_productos.column("valor", width=80, anchor=CENTER)
        self.lista_productos.column("proveedor", width=150)
        self.lista_productos.column("grupo", width=125)
        self.lista_productos.column("status", width=70, anchor=CENTER)
        self.lista_productos.column("Fecha", width=0, stretch=False)
        self.lista_productos.column("barcode", width=100, anchor=CENTER)
        self.lista_productos.column("costo", width=0, stretch=False)
        self.lista_productos.column("reventa", width=0, stretch=False)
        self.lista_productos.column("activo", width=0, stretch=False)
        self.lista_productos.column("responsable", width=0, stretch=False)

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

    def total_registries(self):
        total_registros = len(self.lista_productos.get_children())
        ctk.CTkLabel(self.frame_bottom, text=f"Total de Registros: {total_registros}",
                     width=200,
                     font=("Cascadia Code", 15, "bold")
                     ).place(x=750, y=288)
