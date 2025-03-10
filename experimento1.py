import cv2 as cv
import os
import imutils
import tkinter as tk
from tkinter import ttk, Label
import threading
import time
import subprocess
from PIL import Image, ImageTk
import csv
from datetime import datetime

# ==============================================
# MÓDULO DE CAPTURA FACIAL Y CONFIGURACIÓN INICIAL
# ==============================================
modelo = 'FotosC'
ruta1 = 'D:/xx/reconocimientofacial1/Data'
rutacompleta = os.path.join(ruta1, modelo)

# Configuración de directorios
if not os.path.exists(rutacompleta):
    os.makedirs(rutacompleta)

# Inicialización de componentes de visión por computadora
camara = cv.VideoCapture(0)
ruidos = cv.CascadeClassifier('D:/xx/reconocimientofacial1/Ruidos/data/haarcascades/haarcascade_frontalface_default.xml')

# Variables globales
id_captura = 0
datos_usuario = {}

# ==============================================
# MÓDULO DE INTERFAZ GRÁFICA
# ==============================================
class Aplicacion:
    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("Sistema Integrado de Registro")
        self.ventana.geometry("1200x800")
        
        # Contenedores principales
        self.frame_formulario = ttk.Frame(ventana, padding=20)
        self.frame_camara = ttk.Frame(ventana)
        
        self.configurar_formulario()
        self.configurar_camara()
        
        # Estado inicial
        self.mostrar_formulario()

    def configurar_formulario(self):
        # Componentes del formulario
        self.entries = {}
        campos = [
            ("Nombre completo", 0),
            ("Documento de identidad", 1),
            ("Carrera que estudia", 2),
            ("Correo electrónico", 3),
            ("Teléfono", 4)
        ]

        for texto, fila in campos:
            ttk.Label(self.frame_formulario, text=f"{texto}:").grid(row=fila, column=0, padx=5, pady=5, sticky="w")
            entry = ttk.Entry(self.frame_formulario, width=40)
            entry.grid(row=fila, column=1, padx=5, pady=5, sticky="ew")
            self.entries[texto.split()[0].lower()] = entry

        # Botón de guardado
        self.btn_guardar = ttk.Button(
            self.frame_formulario,
            text="Iniciar Registro Biométrico",
            command=self.iniciar_proceso_completo,
            style='Accent.TButton'
        )
        self.btn_guardar.grid(row=5, column=0, columnspan=2, pady=20, sticky="ew")

    def configurar_camara(self):
        # Componentes de la cámara
        self.label_video = Label(self.frame_camara)
        self.label_video.pack()
        
        self.contador = tk.IntVar()
        self.label_contador = Label(
            self.frame_camara,
            textvariable=self.contador,
            font=("Arial", 50),
            fg="red"
        )
        self.label_contador.place(relx=0.5, rely=0.5, anchor="center")

    # ==============================================
    # LÓGICA DE FLUJO DE APLICACIÓN
    # ==============================================
    def mostrar_formulario(self):
        self.frame_camara.pack_forget()
        self.frame_formulario.pack(expand=True, fill=tk.BOTH)

    def mostrar_camara(self):
        self.frame_formulario.pack_forget()
        self.frame_camara.pack(expand=True, fill=tk.BOTH)
        self.actualizar_frame()
        threading.Thread(target=self.proceso_captura_facial, daemon=True).start()

    # ==============================================
    # FUNCIONALIDADES COMBINADAS
    # ==============================================
    def iniciar_proceso_completo(self):
        # Guardar datos en CSV
        self.guardar_datos_csv()
        # Iniciar proceso biométrico
        self.mostrar_camara()

    def guardar_datos_csv(self):
        global datos_usuario
        datos = {key: entry.get() for key, entry in self.entries.items()}
        datos['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        datos_usuario = datos
        
        with open('registros_biometricos.csv', 'a', newline='', encoding='utf-8') as archivo:
            writer = csv.DictWriter(archivo, fieldnames=datos.keys())
            if archivo.tell() == 0:
                writer.writeheader()
            writer.writerow(datos)

    # ==============================================
    # MÓDULO DE CAPTURA FACIAL (MODIFICADO)
    # ==============================================
    def proceso_captura_facial(self):
        global id_captura
        for i in range(5, 0, -1):
            self.contador.set(i)
            time.sleep(1)
        
        self.contador.set("¡Sonría!")
        time.sleep(1)
        self.capturar_rostros()
        self.ejecutar_entrenamiento()

    def capturar_rostros(self):
        global id_captura
        for _ in range(30):  # Capturar 30 muestras
            respuesta, captura = camara.read()
            if respuesta:
                captura = imutils.resize(captura, width=640)
                grises = cv.cvtColor(captura, cv.COLOR_BGR2GRAY)
                
                caras = ruidos.detectMultiScale(grises, 1.3, 5)
                for (x, y, w, h) in caras:
                    cv.rectangle(captura, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    rostro = grises[y:y+h, x:x+w]
                    rostro = cv.resize(rostro, (160, 160), interpolation=cv.INTER_CUBIC)
                    
                    # Nombre de archivo único con documento de identidad
                    nombre_archivo = f"{datos_usuario['documento']}_{id_captura}.jpg"
                    cv.imwrite(os.path.join(rutacompleta, nombre_archivo), rostro)
                    id_captura += 1

    def ejecutar_entrenamiento(self):
        subprocess.run(["python", "capaocultaentrenamiento.py"])
        self.ventana.destroy()

    # ==============================================
    # ACTUALIZACIÓN DE INTERFAZ EN TIEMPO REAL
    # ==============================================
    def actualizar_frame(self):
        respuesta, captura = camara.read()
        if respuesta:
            captura = imutils.resize(captura, width=640)
            captura_rgb = cv.cvtColor(captura, cv.COLOR_BGR2RGB)
            imagen_pil = Image.fromarray(captura_rgb)
            imagen_tk = ImageTk.PhotoImage(image=imagen_pil)
            
            self.label_video.config(image=imagen_tk)
            self.label_video.image = imagen_tk
        
        self.ventana.after(10, self.actualizar_frame)

# ==============================================
# INICIALIZACIÓN Y EJECUCIÓN DE LA APLICACIÓN
# ==============================================
if __name__ == "__main__":
    root = tk.Tk()
    app = Aplicacion(root)
    
    # Configuración de estilos
    estilo = ttk.Style()
    estilo.configure('Accent.TButton', 
                    foreground='white', 
                    background='#0078d4',
                    font=('Arial', 12, 'bold'))
    
    # Liberación segura de recursos al cerrar
    root.protocol("WM_DELETE_WINDOW", lambda: [camara.release(), cv.destroyAllWindows(), root.destroy()])
    root.mainloop()