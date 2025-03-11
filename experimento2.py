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
# CONFIGURACIÓN BASE Y CONSTANTES
# ==============================================
ruta_base = './Data'

# Inicialización de componentes de visión por computadora
camara = cv.VideoCapture(0)
ruidos = cv.CascadeClassifier('./Ruidos/data/haarcascades/haarcascade_frontalface_default.xml')

# Variables globales
id_captura = 0
datos_usuario = {}

# ==============================================
# CLASE PRINCIPAL DE LA APLICACIÓN
# ==============================================
class Aplicacion:
    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("Sistema Biométrico Integrado")
        self.ventana.geometry("600x600")
        
        # Variables de instancia
        self.modelo = ""
        self.rutacompleta = ""
        
        # Configuración de componentes
        self.configurar_interfaz()
        self.configurar_estilos()
        
        # Estado inicial
        self.mostrar_formulario()

    def configurar_interfaz(self):
        # Contenedores principales
        self.frame_formulario = ttk.Frame(self.ventana, padding=20)
        self.frame_camara = ttk.Frame(self.ventana)
        
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
            ttk.Label(self.frame_formulario, text=f"{texto}:").grid(
                row=fila, column=0, padx=5, pady=5, sticky="w")
            entry = ttk.Entry(self.frame_formulario, width=40)
            entry.grid(row=fila, column=1, padx=5, pady=5, sticky="ew")
            self.entries[texto.split()[0].lower()] = entry

        # Botón de acción principal
        self.btn_principal = ttk.Button(
            self.frame_formulario,
            text="Iniciar Registro Biométrico",
            command=self.iniciar_proceso_completo,
            style='Accent.TButton'
        )
        self.btn_principal.grid(row=5, column=0, columnspan=2, pady=20, sticky="ew")

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

    def configurar_estilos(self):
        estilo = ttk.Style()
        estilo.configure('Accent.TButton', 
                        foreground='white', 
                        background='#0078d4',
                        font=('Arial', 12, 'bold'))

    # ==============================================
    # FLUJO DE LA APLICACIÓN
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
    # LÓGICA DE NEGOCIO
    # ==============================================
    def generar_nombre_carpeta(self, datos):
        """Genera el nombre de carpeta basado en los datos del usuario"""
        nombre_completo = datos['nombre'].strip()
        documento = datos['documento'].strip().replace(" ", "")
        
        primer_nombre = nombre_completo.split()[0]
        primer_nombre = primer_nombre.replace(" ", "_").replace("/", "-")
        
        return f"{primer_nombre}_{documento}"

    def crear_directorio_fotos(self):
        """Crea el directorio para almacenar las fotos del usuario"""
        if not os.path.exists(self.rutacompleta):
            os.makedirs(self.rutacompleta)
            print(f"Directorio creado: {self.rutacompleta}")

    def iniciar_proceso_completo(self):
        # Paso 1: Guardar datos en CSV y crear directorio
        if self.validar_formulario():
            self.guardar_datos_csv()
            self.crear_directorio_fotos()
            self.mostrar_camara()

    def validar_formulario(self):
        """Valida que todos los campos requeridos estén completos"""
        campos_requeridos = ['nombre', 'documento']
        for campo in campos_requeridos:
            if not self.entries[campo].get().strip():
                tk.messagebox.showerror("Error", f"El campo {campo} es obligatorio")
                return False
        return True

    def guardar_datos_csv(self):
        """Guarda los datos del usuario y genera nombre de carpeta"""
        global datos_usuario
        datos = {key: entry.get() for key, entry in self.entries.items()}
        
        # Generar nombre de carpeta único
        self.modelo = self.generar_nombre_carpeta(datos)
        self.rutacompleta = os.path.join(ruta_base, self.modelo)
        
        # Añadir metadatos
        datos['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        datos['carpeta_fotos'] = self.modelo
        datos_usuario = datos
        
        # Escribir en CSV
        with open('registros_biometricos.csv', 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=datos.keys())
            if f.tell() == 0:
                writer.writeheader()
            writer.writerow(datos)

    # ==============================================
    # CAPTURA Y PROCESAMIENTO DE IMÁGENES
    # ==============================================
    def proceso_captura_facial(self):
        """Maneja todo el flujo de captura facial"""
        self.contador_regresivo()
        self.capturar_rostros()
        self.ejecutar_entrenamiento()

    def contador_regresivo(self):
        """Muestra cuenta regresiva antes de la captura"""
        for i in range(5, 0, -1):
            self.contador.set(i)
            time.sleep(1)
        self.contador.set("Mira varios puntos de la pantalla\n¡Sonría!")
        time.sleep(1)

    def capturar_rostros(self):
        """Captura 30 muestras faciales del usuario"""
        global id_captura
        for _ in range(10):
            respuesta, captura = camara.read()
            if respuesta:
                self.procesar_frame(captura)
        self.contador.set("Captura completada!")


    def procesar_frame(self, captura):
        """Procesa cada frame para detección facial"""
        captura = imutils.resize(captura, width=640)
        grises = cv.cvtColor(captura, cv.COLOR_BGR2GRAY)
        caras = ruidos.detectMultiScale(grises, 1.3, 5)

        for (x, y, w, h) in caras:
            self.dibujar_rectangulo(captura, x, y, w, h)
            self.guardar_rostro(grises, y, h, x, w)

        

    def dibujar_rectangulo(self, frame, x, y, w, h):
        """Dibuja rectángulo alrededor del rostro detectado"""
        cv.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

    def guardar_rostro(self, frame_gris, y, h, x, w):
        """Guarda el rostro detectado en el directorio del usuario"""
        global id_captura
        rostro = frame_gris[y:y+h, x:x+w]
        rostro = cv.resize(rostro, (160, 160), interpolation=cv.INTER_CUBIC)
        
        nombre_archivo = f"{self.modelo}_{id_captura:04d}.jpg"
        ruta_completa = os.path.join(self.rutacompleta, nombre_archivo)
        cv.imwrite(ruta_completa, rostro)
        id_captura += 1

    # ==============================================
    # EJECUCIÓN POSTERIOR Y LIMPIEZA
    # ==============================================
    def ejecutar_entrenamiento(self):
        """Ejecuta el script de entrenamiento y cierra la aplicación"""
        subprocess.run(["python", "capaocultaentrenamiento.py"])
        self.ventana.destroy()

    def actualizar_frame(self):
        """Actualiza la vista previa de la cámara en tiempo real"""
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
# INICIALIZACIÓN SEGURA DE LA APLICACIÓN
# ==============================================
if __name__ == "__main__":
    root = tk.Tk()
    app = Aplicacion(root)
    
    # Manejo seguro del cierre
    root.protocol("WM_DELETE_WINDOW", lambda: [
        camara.release(),
        root.destroy(),
        cv.destroyAllWindows()        
    ])
    
    root.mainloop()