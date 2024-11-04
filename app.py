from tkinter import *  
from tkinter import ttk, IntVar, messagebox
import customtkinter as ctk  
import sqlite3
import subprocess 


try:
    import customtkinter
except ImportError:
    subprocess.call(["pip","install","customtkinter"])

try:
    import barcode
except ImportError:
    subprocess.call(["pip","install","python-barcode"])

try:
    import tkcalendar
except ImportError:
    subprocess.call(["pip","install","tkcalendar"])

try:
    import awesometkinter
except ImportError:
    subprocess.call(["pip","install","awesometkinter"])

try:
    import PIL
except ImportError:
    subprocess.call(["pip","install","pillow"])


from ventana_resumen import VentanaResumen  
from ventana_stock import VentanaStock 
from ventana_entradas import VentanaEntradas  
from ventana_salida import VentanaSalidas  
from ventana_usuarios import VentanaUsuarios
from con_database import *  

# NOMBRE EMPRESA: HAWK  
# RUBRO: INDUMENTARIA Y CALZADO  

# PARA EL FUNCIONAMIENTO CORRECTO DEL CODIGO ES NECESARIO INSTALAR LAS SIGUIENTES LIBRERIAS.
# pip install customtkinter barcode pillow python-barcode tkcalendar awesometkinter



def ingresar_admin():
    with sqlite3.connect("StockDatabase.db") as conn:
        verificar_agregado_admin = "SELECT * FROM usuarios WHERE id_usuario = ?"

        cursor = conn.cursor()

        cursor.execute(verificar_agregado_admin, (1,))

        result = cursor.fetchone()

        if not result:
            sql_agregar_admin = """INSERT INTO usuarios (nombre_usuario, user, password_usuario, 
        nivel_permiso, id_sucursal, borrado) VALUES (?, ?, ?, ?, ?, ? ) 
        """
            cursor.execute(sql_agregar_admin, ("Mateo Marcos", "admin", "123456", "admin", 1, 0))
            conn.commit()

def verificar_entrada_usuario():
    try:
        with open("usuario.txt", "r") as file:
            return int(contenido[0]) if (contenido := file.readlines()) else -1
    except Exception:
        return -1

def escribir_numero_en_archivo(numero):
    
    with open("usuario.txt", "w") as file:
        file.write(str(numero)) 

def insertar_sucursales():
    database_conexion = sqlite3.connect("StockDatabase.db")
    cursor = database_conexion.cursor()

    # Verificar si la tabla sucursales ya tiene datos
    check_query = "SELECT COUNT(*) FROM sucursales"
    cursor.execute(check_query)
    result = cursor.fetchone()

    # Si no hay sucursales (COUNT(*) == 0), insertar los datos
    if result[0] == 0:
        insert_query = "INSERT INTO sucursales (nombre_sucursal, direccion_sucursal, telefono_sucursal) VALUES (?, ?, ?)"

        # Definir las localidades a insertar
        localidades = [
            ("San Miguel", "Dirección 1", "123456789"),
            ("Belgrano", "Dirección 2", "987654321"),
            ("La Roca", "Dirección 3", "456789123")
        ]

        # Insertar las localidades
        cursor.executemany(insert_query, localidades)
        database_conexion.commit()

    database_conexion.close()
    

class Application(ctk.CTk):  
    def __init__(self, id):
        super().__init__()
        self.title("Administrador de Stock")  
        x = (self.winfo_screenwidth() // 2) - (1000 // 2)
        y = (self.winfo_screenheight() // 2) - (630 // 2)
        self.geometry(f"1000x630+{x}+{y}")
        self.resizable(False, False) 

        if id != -1:
            self.iniciar_main(id)
        else:
            self.registro()

    def iniciar_main(self, id):  
        ''' 
        Método que inicializa la aplicación principal y configura los componentes de la interfaz gráfica
        '''


        self.id = id

        self.menu_bar()  # Método comentado que añade una barra de menú  (funcion para futuro, sirve para cambiar de blanco a negro y demas, pero hay que tener cuidado  porque si lo apretas muchas veces deja de funcionar, es una funcion admin)
        self.tabs_application()  # Inicializa las pestañas de la aplicación  

        self.mainloop()  
    def menu_bar(self):  
        ''' 
        Método para crear una barra de menú 
        Añade opciones como "Editar" y "Configuración" 
        '''  
        menu_bar = Menu(self)  # Crea la barra de menú  
        self.configure(menu=menu_bar)  # Asigna la barra de menú a la ventana principal  
        
        edite = Menu(menu_bar)  # Crea un submenú para las opciones de edición  
        edite2 = Menu(menu_bar)
        sucursales = Menu(menu_bar)

        menu_bar.add_cascade(label="Editar", menu=edite)  # Añade el submenú "Editar" 
        edite.add_command(label="Configuración", command=WindowConfig)  # Añade la opción "Configuración" que abre una nueva ventana  
        
        menu_bar.add_cascade(label="Sesion", menu=edite2) 
        edite2.add_command(label="Cerrar sesion", command= self.cerrar_sesion)

        # menu_bar.add_cascade(label="Sucursales", menu=sucursales)
        # sucursales.add_command(label="San Miguel" , command=lambda:self.cambiar_sucursal("San Miguel"))
        # sucursales.add_command(label="Belgrano" , command=lambda:self.cambiar_sucursal("Belgrano"))
        # sucursales.add_command(label="La Roca" , command=lambda:self.cambiar_sucursal("La Roca"))

    def cambiar_sucursal(self, sucursal):
        sucursales = {
                "San Miguel": 1,
                "Belgrano": 2,
                "La Roca": 3
            }
    
        # Verificar si la sucursal existe en el diccionario
        id_sucursal = sucursales[sucursal]

        with open("sucursal.txt", "w") as file:
            file.write(str(id_sucursal))

        self.tabs_application()
            

    def tabs_application(self):
        ''' 
        Método que crea y recrea las pestañas principales de la aplicación 
        Se añaden las pestañas "Resumen", "Productos y Stock", "Entradas" y "Salidas" 
        '''  
        # Destruir el `tabs_view` si ya existe y borrar todas las ventanas anteriores
        if hasattr(self, 'tabs_view'):
            self.tabs_view.destroy() 
            self.tabs_view = None 

        # Borrar referencias a las clases asociadas con las pestañas
        self.ventana_resumen = None
        self.ventana_usuario = None
        self.ventana_stock = None
        self.ventana_entradas = None
        self.ventana_salidas = None

        # Conectar a la base de datos para obtener el rol del usuario
        with sqlite3.connect("StockDatabase.db") as conn:
            cursor = conn.cursor()

            query_rol_usuario = "SELECT nivel_permiso FROM usuarios WHERE id_usuario=?"
            cursor.execute(query_rol_usuario, (self.id,))
            
            rol = cursor.fetchone()[0]  

        self.tabs_view = ctk.CTkTabview(self, width=1000, height=600,  
                                        anchor="w",  
                                        text_color=('#000', '#FFF'))  
        self.tabs_view.pack() 

        # Crear pestañas y asignar nuevas instancias a las variables, según el rol
        if rol in ["admin", "gerente", "empleado"]:
            self.tabs_view.add("Resumen") 
            self.ventana_resumen = VentanaResumen(self.tabs_view.tab("Resumen"))  

        if rol in ["admin"]:
            self.tabs_view.add("Gestion usuarios")
            self.ventana_usuario = VentanaUsuarios(self.tabs_view.tab("Gestion usuarios"), self.id)  

        if rol in ["gerente", "admin", "empleado"]:
            self.tabs_view.add("Productos y Stock") 
            self.ventana_stock = VentanaStock(self.tabs_view.tab("Productos y Stock"), self.id, rol)  

        if rol in ["gerente", "admin", "empleado"]:
            self.tabs_view.add("Entradas") 
            self.ventana_entradas = VentanaEntradas(self.tabs_view.tab("Entradas"), self.id)  
        
        if rol in ["gerente", "admin", "empleado"]:
            self.tabs_view.add("Salidas")  
            self.ventana_salidas = VentanaSalidas(self.tabs_view.tab("Salidas"), self.id) 

        # Establecer la pestaña predeterminada según el rol
        if rol == "admin":
            self.tabs_view.set("Resumen")  
        elif rol == "gerente":
            self.tabs_view.set("Entradas")  
        elif rol == "empleado":
            self.tabs_view.set("Productos y Stock")


    def cerrar_sesion(self):
        if respuesta := messagebox.askyesno(
            "Cerrar sesión", "¿Estás seguro de que deseas cerrar sesión?"
        ):
            for widget in self.winfo_children():
                widget.destroy()

            with open("usuario.txt", "w") as file:
                file.write("")

            self.registro()

#--------------------------------------------------------------------------------------------------------------------

    def registro(self):

        self.login_frame = ctk.CTkFrame(self, fg_color="grey", corner_radius=15, border_width=2)
        self.register_frame = ctk.CTkFrame(self, width=300, height=450, corner_radius=15,
                                            border_width=2, border_color="black")
        
        self.combo_value = "San Miguel"


        self.show_login()

        self.database_conexion = sqlite3.connect("StockDatabase.db")
        self.cursor = self.database_conexion.cursor()

    def insertar_sucursales(self):
        # Verificar si la tabla sucursales ya tiene datos
        check_query = "SELECT COUNT(*) FROM sucursales"
        self.cursor.execute(check_query)
        result = self.cursor.fetchone()

        # Si no hay sucursales (COUNT(*) == 0), insertar los datos
        if result[0] == 0:
            insert_query = "INSERT INTO sucursales (nombre_sucursal, direccion_sucursal, telefono_sucursal) VALUES (?, ?, ?)"

            # Definir las localidades a insertar
            localidades = [
                ("San Miguel", "Dirección 1", "123456789"),
                ("Belgrano", "Dirección 2", "987654321"),
                ("La Roca", "Dirección 3", "456789123")
            ]

            # Insertar las localidades
            self.cursor.executemany(insert_query, localidades)
            self.database_conexion.commit()

    def show_login(self):
        self.clear_frame()
        self.check_var = IntVar(value=0)

        self.login_frame.configure(width=300, height=400, fg_color="#F0F0F0", border_color="black") 
        self.login_frame.place(x=350, y=115)

        title_label = ctk.CTkLabel(self.login_frame, text="Login", font=("Arial", 20), text_color="#000000")  
        title_label.place(x=120, y=30)

        user_label = ctk.CTkLabel(self.login_frame, text="Usuario:", text_color="#404040")  
        user_label.place(x=50, y=70)
        self.user_entry = ctk.CTkEntry(self.login_frame, corner_radius=5, width=200, 
                                    font=("Arial", 15), fg_color="#FFFFFF", text_color="#000000")  
        self.user_entry.place(x=50, y=95)

        password_label = ctk.CTkLabel(self.login_frame, text="Contraseña:", text_color="#404040")
        password_label.place(x=50, y=130)
        self.password_entry = ctk.CTkEntry(self.login_frame, show="*", corner_radius=5, 
                                        width=200, font=("Arial", 15), fg_color="#FFFFFF", text_color="#000000")  
        self.password_entry.place(x=50, y=155)

        self.label_sucursal = ctk.CTkLabel(self.login_frame, text="Sucursales:", font=("Arial", 15), text_color="#404040")
        self.label_sucursal.place(x=50, y=190)

        self.entry_sucursal = ctk.CTkComboBox(self.login_frame, values=["San Miguel", "Belgrano", "La Roca"], 
                                            corner_radius=5, width=200, font=("Arial", 15), fg_color="#FFFFFF", text_color="#000000",
                                            state="readonly")
        self.entry_sucursal.place(x=50, y=215) 

        checkbox = ctk.CTkCheckBox(self.login_frame, text="Mantener la sesión abierta", 
                                variable=self.check_var, onvalue=1, offvalue=0, fg_color="black", text_color="#404040", hover=False)
        checkbox.place(x=50, y=265)

        login_button = ctk.CTkButton(self.login_frame, text="Iniciar sesión", command=self.login, fg_color="#000000", text_color="#FFFFFF", hover_color="#404040")
        login_button.place(x=80, y=315)

    def show_register(self):
        self.clear_frame()
        self.combo_value = ""

        self.register_frame.configure(fg_color="#F0F0F0")
        self.register_frame.place(x=350, y=90)

        title_label = ctk.CTkLabel(self.register_frame, text="Registro", font=("Arial", 20), text_color="#000000")
        title_label.place(relx=0.5, y=40, anchor="center") 

        name_label = ctk.CTkLabel(self.register_frame, text="Nombre:", text_color="#404040")
        name_label.place(x=50, y=70)
        self.name_entry = ctk.CTkEntry(self.register_frame, corner_radius=5, width=200, font=("Arial", 15), fg_color="#FFFFFF", text_color="#000000")
        self.name_entry.place(x=50, y=100)

        user_label = ctk.CTkLabel(self.register_frame, text="Usuario:", text_color="#404040")
        user_label.place(x=50, y=135)
        self.user_entry = ctk.CTkEntry(self.register_frame, corner_radius=5, width=200, font=("Arial", 15), fg_color="#FFFFFF", text_color="#000000")
        self.user_entry.place(x=50, y=165)

        branch_label = ctk.CTkLabel(self.register_frame, text="Sucursal:", text_color="#404040")
        branch_label.place(x=50, y=200)
        self.branch_entry = ctk.CTkComboBox(self.register_frame, values=["San Miguel", "Belgrano", "La Roca"], 
                                            corner_radius=5, width=200, font=("Arial", 15), fg_color="#FFFFFF", text_color="#000000",
                                            command=self.combobox_callback)
        self.branch_entry.place(x=50, y=230)

        password_label = ctk.CTkLabel(self.register_frame, text="Contraseña:", text_color="#404040")
        password_label.place(x=50, y=265)
        self.password_entry = ctk.CTkEntry(self.register_frame, show="*", corner_radius=5, width=200, font=("Arial", 15), fg_color="#FFFFFF", text_color="#000000")
        self.password_entry.place(x=50, y=295)

        register_button = ctk.CTkButton(self.register_frame, text="Registrar", command=self.register, fg_color="#000000", text_color="#FFFFFF", hover_color="#404040")
        register_button.place(x=150, y=360, anchor= "center")

        login_button = ctk.CTkButton(self.register_frame, text="Ya tengo una cuenta", command=self.show_login, fg_color="transparent", hover=False, text_color="#000000")
        login_button.place(x=150, y=410, anchor= "center")

    def combobox_callback(self, choice):
            self.combo_value = choice

    def clear_frame(self):
        for widget in self.winfo_children():
            widget.place_forget()

    def login(self): 
        localidades = ["San Miguel", "Belgrano", "La Roca"]
        
        if not self.entry_sucursal.get():
            messagebox.showinfo("Error", message="Agregue una sucursal");return

        loguear_usuario =  "SELECT * FROM usuarios WHERE user=? AND password_usuario=? AND borrado = 0"
        self.cursor.execute(loguear_usuario, (self.user_entry.get(), self.password_entry.get()))
        result = self.cursor.fetchone()

        if result is None:
            messagebox.showinfo("Error", message="Usuario incorrecto o no encontrado")
            return


        if localidades[result[5]-1] != self.entry_sucursal.get():
            messagebox.showinfo("Error", message="Este usuario no pertenece a esta sucursal");return

        if result:
            if self.check_var.get() == 1:
                escribir_numero_en_archivo(result[0])
            
            with open("sucursal.txt", "w") as file:
                file.write(str(result[5]))

            self.clear_frame()
            self.iniciar_main(result[0])
        else:
            messagebox.showinfo("Error", message="Usuario incorrecto");return


    def register(self):
        localidades = ["San Miguel", "Belgrano", "La Roca"]

        if len(self.name_entry.get()) < 4 : messagebox.showinfo("Error", message="El nombre debe contener al menos 4 digitos");return
        if len(self.user_entry.get()) < 4 :  messagebox.showinfo("Error", message="El usuario debe contener al menos 4 digitos");return
        if len(self.password_entry.get()) < 4 :  messagebox.showinfo("Error", message="La contraseña debe contener al menos 4 digitos");return
        if self.combo_value not in localidades: messagebox.showinfo("Error", message="Debe agregar un localidad valida");return

        sucursal = 0

        for i, x in enumerate(localidades):
            if self.combo_value == x:
                sucursal = i+1


        verificar_existencia_usuario = "SELECT user FROM usuarios WHERE user = ? AND borrado = 0"
        self.cursor.execute(verificar_existencia_usuario, (self.user_entry.get(), ))

        if existencia := self.cursor.fetchone():
            messagebox.showinfo("Error", message="El usuario ya existe")
            return

        registrar_usuario = "INSERT INTO usuarios (nombre_usuario, user, password_usuario, nivel_permiso, id_sucursal, borrado) VALUES (?, ?, ?, ?, ?, ?)"
        self.cursor.execute(registrar_usuario, (self.name_entry.get(), self.user_entry.get(),
                                                self.password_entry.get(),"empleado", sucursal, 0))

        self.database_conexion.commit()
        messagebox.showinfo("Exito", message="Usuario registrado exitosamente.")
        self.show_login()


class WindowConfig(ctk.CTkToplevel):  
    ''' 
    Constructor de la clase WindowConfig 
    Crea una ventana independiente para la configuración de la aplicación 
    Parámetros: 
    self: necesario para todos los métodos, hace referencia a la instancia de la clase 
    '''  
    def __init__(self):  
        ''' 
        Método que inicializa la ventana de configuración 
        '''  
        super().__init__()
        
        self.layout_config()   
        self.appearance_theme() 
        self.confirm_config()  

    def layout_config(self):  
        ''' 
        Método que configura el layout de la ventana de configuración 
        Define el tamaño mínimo y máximo de la ventana 
        '''  
        self.geometry("300x400")  # Tamaño de la ventana de configuración  
        self.minsize(300, 400)  # Tamaño mínimo de la ventana  
        self.maxsize(300, 400)  # Tamaño máximo de la ventana  
        self.focus()
        self.grab_set()
    
    def appearance_theme(self):
        ''' 
        Método para configurar el tema de apariencia de la aplicación 
        Permite seleccionar entre los temas "System", "Light" y "Dark"
        '''
        ctk.set_default_color_theme("dark-blue")  # Establece el tema de color por defecto
        ctk.set_appearance_mode("system")  # Establece el modo de apariencia basado en el sistema

        ctk.CTkLabel(self, text="Tema",  
                     font=("Cascadia Code", 15, "bold")
                     ).place(x=50, y=50)  # Crea una etiqueta para el selector de tema y la coloca en la ventana
        
        ctk.CTkOptionMenu(self, width=90, height=20,  
                          values=['System', 'Light', 'Dark'],  
                          font=("Cascadia Code", 15),  
                          command=ctk.set_appearance_mode  
                          ).place(x=50, y=100)  # Crea un menú desplegable para seleccionar el tema y lo coloca en la ventana
    
    def confirm_config(self):
        ''' 
        Método que configura los botones para aplicar o cancelar los cambios de configuración 
        '''
        ctk.CTkButton(self, text="APLICAR", width=75, font=("Cascadia Code", 15, "bold"), command=None).place(x=100, y=360)  
        
        ctk.CTkButton(self, text="CANCELAR",  width=75, font=("Cascadia Code", 15, "bold"), command=self.destroy ).place(x=185, y=360)  

if __name__ == "__main__":
    #create_table()
    #ingresar_admin()
    #insertar_sucursales()
    id = verificar_entrada_usuario()
    
    aplicacion = Application(id)
    aplicacion.mainloop()