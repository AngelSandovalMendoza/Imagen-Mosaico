import os
import random
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import numpy as np

class AplicacionFotoMosaico:
    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("Fotomosaico")
        
        self.imagen_base = None
        self.tamano_bloque = 20
        self.carpeta_imagenes = None
        self.mosaico_final = None

        # Frame para los controles en la parte superior
        self.frame_superior = tk.Frame(self.ventana)
        self.frame_superior.pack(fill=tk.X, padx=10, pady=10)

        # Botón para cargar la imagen base
        self.boton_cargar_imagen = tk.Button(self.frame_superior, text="Cargar imagen base", command=self.cargar_imagen)
        self.boton_cargar_imagen.pack(side=tk.LEFT, padx=5)

        # Botón para cargar la carpeta de imágenes de mosaico
        self.boton_cargar_carpeta = tk.Button(self.frame_superior, text="Cargar carpeta de imágenes", command=self.cargar_carpeta_imagenes)
        self.boton_cargar_carpeta.pack(side=tk.LEFT, padx=5)

        # Entrada para el tamaño de bloque
        tk.Label(self.frame_superior, text="Tamaño de bloque:").pack(side=tk.LEFT, padx=5)
        self.entrada_tamano_bloque = tk.Entry(self.frame_superior, width=5)
        self.entrada_tamano_bloque.insert(0, str(self.tamano_bloque))
        self.entrada_tamano_bloque.pack(side=tk.LEFT, padx=5)

        # Menú desplegable para elegir el método de selección
        tk.Label(self.frame_superior, text="Método de selección:").pack(side=tk.LEFT, padx=5)
        self.opcion_metodo = ttk.Combobox(self.frame_superior, values=["Exacto", "Aleatorio entre mejores 10"], width=25)
        self.opcion_metodo.current(0)  # Selección predeterminada
        self.opcion_metodo.pack(side=tk.LEFT, padx=5)

        # Botón para generar el fotomosaico
        self.boton_generar_mosaico = tk.Button(self.frame_superior, text="Generar fotomosaico", command=self.generar_mosaico)
        self.boton_generar_mosaico.pack(side=tk.LEFT, padx=5)

        # Botón para guardar el mosaico
        self.boton_guardar_mosaico = tk.Button(self.frame_superior, text="Guardar fotomosaico", command=self.guardar_mosaico)
        self.boton_guardar_mosaico.pack(side=tk.LEFT, padx=5)

        # Barra de progreso para mostrar el avance
        self.barra_progreso = ttk.Progressbar(self.ventana, orient="horizontal", length=800, mode="determinate")
        self.barra_progreso.pack(pady=5)

        # Lienzo para mostrar la imagen
        self.lienzo = tk.Canvas(self.ventana, width=800, height=600)
        self.lienzo.pack()

    def cargar_imagen(self):
        ruta_archivo = filedialog.askopenfilename()
        if ruta_archivo:
            self.imagen_base = Image.open(ruta_archivo)
            self.mostrar_imagen(self.imagen_base)

    def cargar_carpeta_imagenes(self):
        self.carpeta_imagenes = filedialog.askdirectory()
        if self.carpeta_imagenes:
            print(f"Carpeta de imágenes cargada: {self.carpeta_imagenes}")
    
    def mostrar_imagen(self, imagen):
        imagen = imagen.resize((800, 600), Image.Resampling.LANCZOS)
        self.imagen_tk = ImageTk.PhotoImage(imagen)
        self.lienzo.create_image(0, 0, anchor=tk.NW, image=self.imagen_tk)
    
    def obtener_color_promedio(self, imagen):
        imagen = imagen.resize((1, 1), Image.Resampling.LANCZOS)
        return imagen.getpixel((0, 0))
    
    def calcular_distancia(self, color1, color2):
        return np.sqrt(sum((color1[i] - color2[i]) ** 2 for i in range(3)))
    
    def cargar_imagenes_mosaico(self):
        imagenes_mosaico = []
        if not self.carpeta_imagenes:
            messagebox.showerror("Error", "Cargue una carpeta de imágenes primero")
            return []

        for nombre_archivo in os.listdir(self.carpeta_imagenes):
            if nombre_archivo.lower().endswith((".png", ".jpg", ".jpeg")):
                imagen = Image.open(os.path.join(self.carpeta_imagenes, nombre_archivo)).resize((self.tamano_bloque, self.tamano_bloque))
                imagenes_mosaico.append((imagen, self.obtener_color_promedio(imagen)))
        return imagenes_mosaico
    
    def generar_mosaico(self):
        try:
            self.tamano_bloque = int(self.entrada_tamano_bloque.get())
            if self.tamano_bloque <= 0:
                raise ValueError("El tamaño debe ser positivo")
        except ValueError:
            messagebox.showerror("Error", "Ingrese un tamaño de bloque válido (entero positivo)")
            return

        if not self.imagen_base or not self.carpeta_imagenes:
            messagebox.showerror("Error", "Cargue una imagen base y una carpeta de imágenes")
            return

        imagenes_mosaico = self.cargar_imagenes_mosaico()
        self.mosaico_final = Image.new("RGB", self.imagen_base.size)
        
        bloques_x = self.imagen_base.width // self.tamano_bloque
        bloques_y = self.imagen_base.height // self.tamano_bloque
        total_bloques = bloques_x * bloques_y
        contador = 0
        
        for y in range(0, self.imagen_base.height, self.tamano_bloque):
            for x in range(0, self.imagen_base.width, self.tamano_bloque):
                caja = (x, y, x + self.tamano_bloque, y + self.tamano_bloque)
                seccion_recortada = self.imagen_base.crop(caja)
                color_promedio = self.obtener_color_promedio(seccion_recortada)
                
                # Buscar la imagen más cercana (o una aleatoria entre las 10 mejores)
                distancias = sorted(imagenes_mosaico, key=lambda img: self.calcular_distancia(color_promedio, img[1]))
                
                if self.opcion_metodo.get() == "Exacto":
                    mosaico_cercano = distancias[0][0]
                else:
                    mejores_10 = distancias[:10]
                    random.shuffle(mejores_10)  # Mezclar las mejores para evitar repeticiones consecutivas
                    mosaico_cercano = mejores_10[0][0]  # Tomar una de las 10 aleatoriamente

                self.mosaico_final.paste(mosaico_cercano, caja)
                
                # Actualizar barra de progreso
                contador += 1
                progreso = int((contador / total_bloques) * 100)
                self.barra_progreso["value"] = progreso
                self.ventana.update_idletasks()
        
        self.mostrar_imagen(self.mosaico_final)

    def guardar_mosaico(self):
        if self.mosaico_final:
            ruta_guardar = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
            if ruta_guardar:
                self.mosaico_final.save(ruta_guardar)
                messagebox.showinfo("Éxito", "Fotomosaico guardado con éxito")
        else:
            messagebox.showerror("Error", "No se ha generado ningún fotomosaico para guardar")

ventana = tk.Tk()
app = AplicacionFotoMosaico(ventana)
ventana.mainloop()
