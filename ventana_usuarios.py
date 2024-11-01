import customtkinter as ctk
# from PIL import Image
import PIL.Image
from tkinter import *
from tkinter import messagebox
import tkinter as tk
from tkinter import ttk
import awesometkinter as atk
import sqlite3

class VentanaUsuarios:
    def __init__(self, root, id_usuario):
        self.root = root
        self.id_user = id_usuario
        
        self.buttons_header()
        self.recaudar_datos_usuario()
        self.ingresar_usuarios()
        self.tabla_usuarios()
        self.modificar_usuario()

    def recaudar_datos_usuario(self):
        with sqlite3.connect("StockDatabase.db") as conn:
            sql_recuadar_datos = "SELECT * FROM usuarios WHERE id_usuario = ? "
            sql_datos_todos = """SELECT u.id_usuario, u.nombre_usuario, u.user, u.password_usuario, 
                                u.nivel_permiso, s.nombre_sucursal 
                            FROM usuarios u, sucursales s 
                            WHERE u.id_sucursal = s.id_sucursal AND u.borrado = 0;"""
            cursor = conn.cursor()

            cursor.execute(sql_recuadar_datos, (self.id_user, ))
            self.datos_usuario = cursor.fetchone()
            
            cursor.execute(sql_datos_todos)
            self.datos_usuarios_todos = cursor.fetchall()

    def buttons_header(self):
        self.frame_buttons = ctk.CTkFrame(self.root,
                                          width=990, height=40,
                                          fg_color="#363636")
        self.frame_buttons.place(x=1, y=1)

        btn_save = ctk.CTkButton(self.frame_buttons, text="", width=30, corner_radius=3, image=self.image_button("./image/delete.png", (26, 26)),
                                 compound=LEFT, anchor=NW, fg_color="transparent", hover_color=("#D3D3D3", "#4F4F4F"),
                                 command=self.borrar_usuario)
        btn_save.place(x=3, y=3)
        atk.tooltip(btn_save, "Borrar registro")

        ctk.CTkLabel(self.frame_buttons, text="||",
                     font=("Arial", 30), text_color="#696969",
                     fg_color="transparent").place(x=40)

    def image_button(self, image_path, size):
        try:
            image = ctk.CTkImage(light_image=PIL.Image.open(image_path), size=size)  
            return image
        
        except Exception as e:
            (f"Error al cargar la imagen: {e}")
            return None

    def borrar_usuario(self):
        if not self.valores:
            messagebox.showinfo("Error", message="Elija un usuario")
            return

        with sqlite3.connect("StockDatabase.db") as conn:
            query_eliminar = "UPDATE usuarios SET borrado = 1 WHERE id_usuario = ?"
            
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM usuarios WHERE nivel_permiso = 'admin'")
            verificar = cursor.fetchone()
            
            if verificar[0] == 1:
                messagebox.showinfo("Error", message="No puede eliminar al ultimo admin")
                return

            cursor.execute(query_eliminar, (self.valores[0],))
            conn.commit() 

            self.frame_tabla.destroy()
            self.recaudar_datos_usuario()
            self.tabla_usuarios()
            
    def ingresar_usuarios(self):

        self.frame_carac_user = ctk.CTkFrame(self.root, border_color="black", border_width=2, width=450, height=220)
        self.frame_carac_user.place(x=38, rely=0.1)

        label_nombre = ctk.CTkLabel(self.frame_carac_user, text="Nombre Usuario:", fg_color="transparent", text_color="black", font=("Arial", 12))
        label_user = ctk.CTkLabel(self.frame_carac_user, text="Usuario:", fg_color="transparent", text_color="black", font=("Arial", 12))
        label_password = ctk.CTkLabel(self.frame_carac_user, text="Contraseña:", fg_color="transparent", text_color="black", font=("Arial", 12))

        # Posicionar etiquetas
        label_nombre.place(x=10, y=10)
        label_user.place(x=10, y=50)
        label_password.place(x=10, y=90)


        self.entry_nombre = ctk.CTkEntry(self.frame_carac_user, width=250, font=("Arial", 15))
        self.entry_user = ctk.CTkEntry(self.frame_carac_user, width=250, font=("Arial", 15))
        self.entry_password = ctk.CTkEntry(self.frame_carac_user, width=250, font=("Arial", 15))  
        self.entry_permiso = ctk.CTkComboBox(self.frame_carac_user, values=["empleado", "gerente", "admin"], 
                                            corner_radius=5, width=125, font=("Arial", 15), fg_color="#FFFFFF", text_color="#000000",
                                            state="readonly")
        self.entry_sucursal = ctk.CTkComboBox(self.frame_carac_user, values=["San Miguel", "Belgrano", "La Roca"], 
                                            corner_radius=5, width=125, font=("Arial", 15), fg_color="#FFFFFF", text_color="#000000",
                                            state="readonly")
        
        self.entry_nombre.place(x=150, y=10)
        self.entry_user.place(x=150, y=50)
        self.entry_password.place(x=150, y=90)
        self.entry_permiso.place(x=150, y=130)  
        self.entry_sucursal.place(x=275, y=130)  

        btn_guardar = ctk.CTkButton(self.frame_carac_user, text="Ingresar usuario", command=self.guardar_usuario)
        btn_guardar.place(x=150, y=170)

    def guardar_usuario(self):
        localidades = ["San Miguel", "Belgrano", "La Roca"]

        nombre = self.entry_nombre.get()
        usuario = self.entry_user.get()
        password = self.entry_password.get()
        permiso = self.entry_permiso.get()
        sucursal = self.entry_sucursal.get()

        if len(nombre) < 4 : messagebox.showinfo("Error", message="El nombre debe contener al menos 4 digitos");return
        if len(usuario) < 4 :  messagebox.showinfo("Error", message="El usuario debe contener al menos 4 digitos");return
        if len(password) < 4 :  messagebox.showinfo("Error", message="La contraseña debe contener al menos 4 digitos");return

        if not nombre or not usuario or not password or not permiso or not sucursal:
            messagebox.showinfo("Error", message="Todos los campos son obligatorios")
            return
        
        sucursal = 0

        for i, x in enumerate(localidades):
            if self.entry_sucursal.get() == x:
                sucursal = i+1

        with sqlite3.connect("StockDatabase.db") as conn:
            cursor = conn.cursor()

            verificar_existencia_usuario = "SELECT user FROM usuarios WHERE user = ? AND borrado = 0"
            cursor.execute(verificar_existencia_usuario, (usuario, ))

            existencia = cursor.fetchone()
            
            if not existencia:
                sql_insertar = """INSERT INTO usuarios (nombre_usuario, user, password_usuario, nivel_permiso, id_sucursal, borrado)
                                VALUES (?, ?, ?, ?, ?, ?)"""
                cursor.execute(sql_insertar, (nombre, usuario, password, permiso, sucursal, 0))
                conn.commit()
                self.frame_tabla.destroy()
                self.recaudar_datos_usuario()
                self.tabla_usuarios()
            else:
                messagebox.showinfo("Error", message="El usuario ya existe")
                return

    def modificar_usuario(self):
        self.frame_editar = ctk.CTkFrame(self.root, border_color="black", border_width=2, width=400, height=220)
        self.frame_editar.place(x=527, rely=0.1)

        label_rol = ctk.CTkLabel(self.frame_editar, text="Nivel Permiso:", fg_color="transparent", text_color="black", font=("Arial", 15))
        label_sucursal = ctk.CTkLabel(self.frame_editar, text="Sucursal:", fg_color="transparent", text_color="black", font=("Arial", 15))
        label_password = ctk.CTkLabel(self.frame_editar, text="Nueva Contraseña:", fg_color="transparent", text_color="black", font=("Arial", 15))

        label_rol.place(x=10, y=20)
        label_sucursal.place(x=10, y=70)
        label_password.place(x=10, y=120)

        self.entry_rol_nueva = ctk.CTkComboBox(self.frame_editar, values=["empleado", "gerente", "admin"], 
                                         corner_radius=5, width=200, font=("Arial", 15), fg_color="#FFFFFF", 
                                         text_color="#000000",state="readonly")
        self.entry_rol_nueva.place(x=150, y=20)

        self.entry_sucursal_nueva = ctk.CTkComboBox(self.frame_editar, values=["San Miguel", "Belgrano", "La Roca"], 
                                              corner_radius=5, width=200, font=("Arial", 15), fg_color="#FFFFFF",
                                              text_color="#000000", state="readonly")
        self.entry_sucursal_nueva.place(x=150, y=70)

        self.entry_password_nueva = ctk.CTkEntry(self.frame_editar, width=200, show="*")
        self.entry_password_nueva.place(x=150, y=120)

        # Botón para guardar los cambios
        btn_guardar = ctk.CTkButton(self.frame_editar, text="Guardar Cambios",command=self.guardar_cambios )
        btn_guardar.place(x=150, y=170)

    def guardar_cambios(self):
        if not self.valores:
            messagebox.showinfo("Error", message="Elija un usuario")
            return
        # Asignar los valores actuales si no se modifican
        nuevo_rol = self.valores[4]  
        nueva_password = self.valores[3]  
        nueva_sucursal = self.valores[5]  

        localidades = ["San Miguel", "Belgrano", "La Roca"]

        if self.entry_rol_nueva.get():
            nuevo_rol = self.entry_rol_nueva.get()

        if self.entry_sucursal_nueva.get():
            nueva_sucursal = self.entry_sucursal_nueva.get()

        if self.entry_password_nueva.get():
            nueva_password = self.entry_password_nueva.get()

        if len(nueva_password) < 4 and nueva_password:
            messagebox.showinfo("Error", message="La contraseña debe tener al menos 4 caracteres")
            return

        if nuevo_rol or nueva_sucursal or nueva_password:
            nueva_sucursal_id = 0

            for i, x in enumerate(localidades):
                if self.entry_sucursal_nueva.get() == x:
                    nueva_sucursal_id = i + 1

            with sqlite3.connect("StockDatabase.db") as conn:
                cursor = conn.cursor()

                sql_modificar = """UPDATE usuarios 
                                SET nivel_permiso = ?, id_sucursal = ?, password_usuario = ? 
                                WHERE id_usuario = ?"""

                cursor.execute(sql_modificar, (nuevo_rol, nueva_sucursal_id, nueva_password, self.valores[0]))
                conn.commit()

                self.frame_tabla.destroy()
                self.recaudar_datos_usuario()
                self.tabla_usuarios()
        else:
            messagebox.showinfo("Error", message="Ingrese algún campo")
            return


#----------Tabla----------

    def tabla_usuarios(self):
        self.frame_tabla = ctk.CTkFrame(self.root)
        self.frame_tabla.place(x=1, rely=0.53)

        columnas = ["ID Usuario", "Nombre Usuario", "Usuario", "Contraseña", "Nivel Permiso", "ID Sucursal"]

        # Crear el Treeview
        self.tabla = ttk.Treeview(self.frame_tabla, columns=columnas, show="headings", selectmode="browse", height=400)

        for col in columnas:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=160, anchor=tk.CENTER)

        # Crear la barra de desplazamiento
        self.scrollbar = ttk.Scrollbar(self.frame_tabla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=self.scrollbar.set)

        # Insertar los datos en la tabla
        for id_usuario, nombre, user, password, permiso, sucursal in self.datos_usuarios_todos:
            self.tabla.insert("", tk.END, values=(id_usuario, nombre, user, password, permiso, sucursal))
        
        # Empaquetar el Treeview y la barra de desplazamiento
        self.tabla.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Vincular el evento de doble clic con la función para seleccionar una fila
        self.tabla.bind("<Double-1>", self.on_double_click)


    def on_double_click(self, event):
        selected_item = self.tabla.selection()
        if selected_item:
            self.valores = self.tabla.item(selected_item, "values")