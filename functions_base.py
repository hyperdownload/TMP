from tkinter import *
from tkinter import messagebox
import customtkinter as ctk
from PIL import Image
from barcode import EAN13
from barcode.writer import ImageWriter
from random import randint

''' 
    Clase que contiene funciones auxiliares para la gestión de imágenes y códigos de barras 
''' 
class FunctionsExtras:

    ''' 
        Carga una imagen y la escala según los parámetros dados 
        Parámetros: 
        nameImage: Nombre del archivo de imagen a cargar 
        scale: Tupla que representa el tamaño de la imagen (ancho, alto) 
        Retorna: 
        img: Objeto imagen que se puede usar en un botón o widget 
    '''  
    def image_button(self, nameImage, scale=tuple):
        return ctk.CTkImage(
            light_image=Image.open(f"image/{nameImage}"),
            dark_image=Image.open(f"image/{nameImage}"),
            size=(scale),
        ) 
    ''' 
        Carga una imagen de código de barras y la escala 
        Parámetros: 
        nameImage: Nombre del archivo de código de barras a cargar 
        scale: Tupla que representa el tamaño de la imagen (ancho, alto) 
        Retorna: 
        img: Objeto imagen que se puede usar en un widget 
    '''  
    def image_barcode(self, nameImage, scale=tuple):
        return ctk.CTkImage(
            light_image=Image.open(f"barCodes/{nameImage}"),
            dark_image=Image.open(f"barCodes/{nameImage}"),
            size=(scale),
        )
    ''' 
        Genera un código de barras EAN13 basado en un lote de producto 
        Parámetros: 
        id_product: Identificador del lote del producto 
        Retorna: 
        numbers: Número generado para el código de barras 
    '''  
    def generate_barCode(self, id_product):
        if id_product == "": # Si no se proporciona un lote, muestra un mensaje de advertencia
            messagebox.showinfo("Please select", message="Por favor, informe el lote del producto!")
        elif messagebox.askyesno("Generate Barcode", message=f"Generar codigo de barras para el lote: {id_product}"):
            try:
                numbers = "".join(str(randint(1, 9)) for _ in range(12))
                # Genera el código de barras EAN13 y lo guarda como una imagen 
                code = EAN13(numbers, writer=ImageWriter())
                code.save(f"barCodes/{id_product}")

                messagebox.showinfo("Success", message="Código de barras generado con exito!")

                return numbers
            except FileNotFoundError:
                messagebox.showerror("Invalid", message="Lote inválido!")
        ''' 
        Desactiva la opción de copiar texto en un widget de entrada de texto. 
        Permite la copia cuando el estado es correcto. 
        Parámetros: 
        event: Evento que dispara la función 
        Retorna: 
        "break" si la acción está deshabilitada, None si está permitida 
        '''                      
    def entry_off(self, event):
        if (event.state==12 and event.keysym== "c"):
            return  # Permite copiar cuando se presiona 'Ctrl+C
        else:
            return "break"
