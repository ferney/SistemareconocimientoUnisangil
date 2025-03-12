import cv2 as cv
import os
import tkinter as tk
from tkinter import ttk, Label, messagebox
import threading
import subprocess
from PIL import Image, ImageTk
import csv
from datetime import datetime
import time

# ==============================================
# CONFIGURACIÓN BASE Y CONSTANTES
# ==============================================
ruta_base = './Data'
print("Interfaz capturar iniciada")

print("Cargando ruidos")
# Cargamos el clasificador Haar para detección facial
ruidos = cv.CascadeClassifier('./Ruidos/data/haarcascades/haarcascade_frontalface_default.xml')

# Variables globales
id_captura = 0
datos_usuario = {}

def resize_image(image, width=640):
    """Redimensiona la imagen manteniendo la relación de aspecto."""
    ratio = width / image.shape[1]
    dim = (width, int(image.shape[0] * ratio))
    return cv.resize(image, dim, interpolation=cv.INTER_AREA)

# ==============================================
# CLASE PRINCIPAL DE LA APLICACIÓN
# ==============================================
class Aplicacion:
    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("Sistema Biométrico Integrado")
        self.ventana.geometry("600x600")
        
        # Variables de instancia
        self.identificador = ""   # Identificador único del usuario
        self.rutacompleta = ""
        
        # Inicialmente la cámara es None; se asignará en un hilo aparte.
        self.camara = None
        # Variable para el recurso pesado (modelo de reconocimiento)
        self.modelo_reconocimiento = None

        # Inicia la inicialización de la cámara en un hilo en segundo plano.
        threading.Thread(target=self.inicializar_camara, daemon=True).start()

        # Inicia la carga en segundo plano (lazy loading)
        self.preload_thread = threading.Thread(target=self.lazy_load_recognition_resources, daemon=True)
        self.preload_thread.start()
        
        # Configuración de componentes
        self.configurar_interfaz()
        self.configurar_estilos()
        
        # Estado inicial
        self.mostrar_formulario()


    def inicializar_camara(self):
        """- Windows: cv.CAP_DSHOW
        - Linux: cv.CAP_V4L2
        - macOS: cv.CAP_AVFOUNDATION
        """
        print("Inicializando camara")
        self.camara = cv.VideoCapture(0, cv.CAP_DSHOW)
        if not self.camara.isOpened():
            print("Error al abrir la cámara")
        else:
            # Configura la resolución deseada para agilizar la captura
            print("Cámara inicializada correctamente.")


    def lazy_load_recognition_resources(self):
        """Carga en segundo plano el modelo u otros recursos pesados."""
        print("Iniciando carga de recursos pesados...")
        # Aquí colocarías la carga real del modelo, por ejemplo:
        # self.modelo_reconocimiento = cargar_modelo_reconocimiento()
        time.sleep(5)  # Simulación de carga
        self.modelo_reconocimiento = "Modelo de reconocimiento precargado"
        print("Carga de recursos completada.")

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
            # Se guarda el entry usando la primera palabra en minúsculas (ej: "nombre", "documento", etc.)
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
        
        self.contador = tk.StringVar()
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
        # Inicia la cuenta regresiva sin bloquear la GUI
        self.iniciar_cuenta_regresiva(5)

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
                messagebox.showerror("Error", f"El campo {campo} es obligatorio")
                return False
        return True

    def guardar_datos_csv(self):
        """Guarda los datos del usuario y genera el identificador único"""
        global datos_usuario
        datos = {key: entry.get() for key, entry in self.entries.items()}
        
        # Generar identificador único para el usuario
        self.identificador = self.generar_nombre_carpeta(datos)
        self.rutacompleta = os.path.join(ruta_base, self.identificador)
        
        # Añadir metadatos
        datos['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        datos['carpeta_fotos'] = self.identificador
        datos_usuario = datos
        
        # Definir el orden de los campos que se guardarán en el CSV
        fieldnames = ["nombre", "documento", "carrera", "correo", "teléfono", "timestamp", "carpeta_fotos"]
        with open('registros_biometricos.csv', 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if f.tell() == 0:
                writer.writeheader()
            writer.writerow(datos)

    # ==============================================
    # CAPTURA Y PROCESAMIENTO DE IMÁGENES
    # ==============================================
    def iniciar_cuenta_regresiva(self, contador):
        """Cuenta regresiva sin bloquear la GUI utilizando after."""
        if contador > 0:
            self.contador.set(str(contador))
            self.ventana.after(1000, lambda: self.iniciar_cuenta_regresiva(contador - 1))
        else:
            self.contador.set("Mira varios puntos de la pantalla\n¡Sonría!")
            self.ventana.after(1000, self.iniciar_captura_facial_thread)

    def iniciar_captura_facial_thread(self):
        """Inicia la captura facial en un hilo separado"""
        threading.Thread(target=self.capturar_y_entrenar, daemon=True).start()

    def capturar_y_entrenar(self):
        """Captura rostros y ejecuta el entrenamiento posteriormente"""
        self.capturar_rostros()
        self.ejecutar_entrenamiento()

    def capturar_rostros(self):
        """Captura 10 muestras faciales del usuario"""
        global id_captura
        for _ in range(10):
            respuesta, captura = self.camara.read()
            if respuesta:
                self.procesar_frame(captura)
        self.contador.set("Captura completada!")

    def procesar_frame(self, captura):
        """Procesa cada frame para detección facial"""
        captura = resize_image(captura, width=640)
        grises = cv.cvtColor(captura, cv.COLOR_BGR2GRAY)
        # Ajusta scaleFactor y minNeighbors si se requiere mayor velocidad
        caras = ruidos.detectMultiScale(grises, scaleFactor=1.3, minNeighbors=5)

        if len(caras) == 0:
            print("⚠ No se detectaron caras en este frame. Omitiendo...")
            return

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
        
        nombre_archivo = f"{self.identificador}_{id_captura:04d}.jpg"
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
        respuesta, captura = self.camara.read()
        if respuesta:
            captura = resize_image(captura, width=640)
            captura_rgb = cv.cvtColor(captura, cv.COLOR_BGR2RGB)
            imagen_pil = Image.fromarray(captura_rgb)
            imagen_tk = ImageTk.PhotoImage(image=imagen_pil)
            
            self.label_video.config(image=imagen_tk)
            self.label_video.image = imagen_tk
        
        self.ventana.after(30, self.actualizar_frame)

    def cerrar(self):
        """Maneja el cierre seguro de la aplicación."""
        if self.camara is not None:
            self.camara.release()
        cv.destroyAllWindows()
        self.ventana.destroy()

# ==============================================
# INICIALIZACIÓN SEGURA DE LA APLICACIÓN
# ==============================================
if __name__ == "__main__":
    root = tk.Tk()
    app = Aplicacion(root)
    
    # Manejo seguro del cierre
    root.protocol("WM_DELETE_WINDOW", app.cerrar)
    
    root.mainloop()
