import cv2 as cv
import os
import imutils
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import csv
from datetime import datetime

# --- Configuraciones Globales ---
DATA_RUTA = './Data'
CSV_REGISTROS = 'registros_biometricos.csv'
UMBRAL = 8000  # Umbral de similitud para reconocimiento

# --- Cargar lista de directorios (identificadores) ---
listaData = os.listdir(DATA_RUTA)

# --- Cargar el modelo de reconocimiento facial y el clasificador ---
recognizer = cv.face.EigenFaceRecognizer_create()
recognizer.read('EntrenamientoEigenFaceRecognizer.xml')
cascade = cv.CascadeClassifier('./Ruidos/data/haarcascades/haarcascade_frontalface_default.xml')

# --- Función para buscar en el CSV el registro que coincida con el identificador ---
def buscar_registro_por_id(identificador):
    if not os.path.exists(CSV_REGISTROS):
        return None
    with open(CSV_REGISTROS, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Se asume que en el CSV se guardó el nombre de carpeta en el campo "carpeta_fotos"
            if row.get("carpeta_fotos", "").strip() == identificador:
                return row
    return None

# --- Función opcional para registrar el acceso en otro CSV ---
def registrar_acceso(registro):
    archivo = "registro_acceso.csv"
    cabecera = ["Nombre completo", "Documento de identidad", "Carrera que estudia",
                "Correo electrónico", "Teléfono", "Timestamp"]
    registro["Timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    escribir_cabecera = not os.path.exists(archivo)
    with open(archivo, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=cabecera)
        if escribir_cabecera:
            writer.writeheader()
        writer.writerow(registro)

# --- Clase para la interfaz integrada ---
class InterfazIntegrada:
    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("Sistema de Reconocimiento Facial Integrado")
        self.ventana.geometry("900x600")
        self.registro_actual = None  # Para evitar registros múltiples del mismo usuario
        
        # Crear dos marcos: uno para la transmisión y otro para el formulario
        self.frame_video = ttk.Frame(self.ventana)
        self.frame_video.pack(side=tk.LEFT, padx=10, pady=10, expand=True, fill=tk.BOTH)
        
        self.frame_formulario = ttk.Frame(self.ventana, padding=10)
        self.frame_formulario.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.Y)
        
        # Label para mostrar video
        self.label_video = ttk.Label(self.frame_video)
        self.label_video.pack(expand=True, fill=tk.BOTH)
        
        # Configuración del formulario con los campos requeridos
        campos = [
            ("Nombre completo", "nombre"),
            ("Documento de identidad", "documento"),
            ("Carrera que estudia", "carrera"),
            ("Correo electrónico", "correo"),
            ("Teléfono", "telefono")
        ]
        self.entries = {}
        row = 0
        ttk.Label(self.frame_formulario, text="Datos del Usuario", font=("Arial", 14, "bold")).grid(row=row, column=0, columnspan=2, pady=10)
        row += 1
        for etiqueta, key in campos:
            ttk.Label(self.frame_formulario, text=etiqueta + ":").grid(row=row, column=0, sticky="w", pady=5)
            entry = ttk.Entry(self.frame_formulario, width=30)
            entry.grid(row=row, column=1, pady=5)
            self.entries[key] = entry
            row += 1
        
        # Botón opcional para guardar manualmente el registro (además del registro automático)
        self.btn_guardar = ttk.Button(self.frame_formulario, text="Guardar Acceso", command=self.guardar_acceso)
        self.btn_guardar.grid(row=row, column=0, columnspan=2, pady=20)
        
        # Inicializar cámara y variable para controlar el registro
        self.camara = cv.VideoCapture(0)
        self.usuario_registrado = False
        
        # Iniciar la actualización del video
        self.actualizar_video()

    def actualizar_video(self):
        ret, frame = self.camara.read()
        if ret:
            frame = imutils.resize(frame, width=640)
            gris = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            # Detección de rostros
            rostros = cascade.detectMultiScale(gris, 1.3, 5)
            for (x, y, w, h) in rostros:
                # Extraer la región facial y redimensionar a 160x160
                rostro = gris[y:y+h, x:x+w]
                try:
                    rostro_resized = cv.resize(rostro, (160, 160), interpolation=cv.INTER_CUBIC)
                except Exception:
                    continue
                # Realizar la predicción
                resultado = recognizer.predict(rostro_resized)
                cv.putText(frame, f"{resultado}", (x, y - 5), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1, cv.LINE_AA)
                if resultado[1] < UMBRAL:
                    # Se reconoce al usuario
                    identificador = listaData[resultado[0]]
                    cv.putText(frame, f"{identificador}", (x, y - 20), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2, cv.LINE_AA)
                    cv.rectangle(frame, (x, y), (x+w, y+h), (255,0,0), 2)
                    
                    # Sólo se llena el formulario si aún no se ha hecho para este usuario
                    if not self.usuario_registrado:
                        registro = buscar_registro_por_id(identificador)
                        if registro:
                            self.llenar_formulario(registro)
                            self.registro_actual = registro
                            self.usuario_registrado = True
                            # Opcional: Registrar el acceso en otro CSV
                            registrar_acceso(registro)
                        else:
                            # Si no se encuentra el registro, se muestra un mensaje
                            print("Registro no encontrado para el ID:", identificador)
                else:
                    cv.putText(frame, "No encontrado", (x, y - 20), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2, cv.LINE_AA)
                    cv.rectangle(frame, (x, y), (x+w, y+h), (255,0,0), 2)
                    # Reinicia la variable para permitir registrar a otro usuario en futuras detecciones
                    self.usuario_registrado = False
            # Convertir a RGB para Tkinter
            frame_rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            imagen = Image.fromarray(frame_rgb)
            imagen_tk = ImageTk.PhotoImage(image=imagen)
            self.label_video.configure(image=imagen_tk)
            self.label_video.image = imagen_tk
        self.ventana.after(10, self.actualizar_video)

    def llenar_formulario(self, datos):
        """Llena los campos del formulario con los datos del registro encontrado."""
        self.entries["nombre"].delete(0, tk.END)
        self.entries["nombre"].insert(0, datos.get("Nombre completo", ""))
        self.entries["documento"].delete(0, tk.END)
        self.entries["documento"].insert(0, datos.get("Documento de identidad", ""))
        self.entries["carrera"].delete(0, tk.END)
        self.entries["carrera"].insert(0, datos.get("Carrera que estudia", ""))
        self.entries["correo"].delete(0, tk.END)
        self.entries["correo"].insert(0, datos.get("Correo electrónico", ""))
        self.entries["telefono"].delete(0, tk.END)
        self.entries["telefono"].insert(0, datos.get("Teléfono", ""))
        messagebox.showinfo("Usuario Reconocido", "El formulario se ha completado automáticamente.")

    def guardar_acceso(self):
        """Guarda manualmente (o confirma) el registro de acceso usando el contenido del formulario."""
        datos = {
            "Nombre completo": self.entries["nombre"].get(),
            "Documento de identidad": self.entries["documento"].get(),
            "Carrera que estudia": self.entries["carrera"].get(),
            "Correo electrónico": self.entries["correo"].get(),
            "Teléfono": self.entries["telefono"].get(),
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        registrar_acceso(datos)
        messagebox.showinfo("Registro Guardado", "El acceso ha sido registrado en el CSV.")

    def cerrar(self):
        self.camara.release()
        self.ventana.destroy()

# --- Inicialización de la interfaz ---
if __name__ == "__main__":
    root = tk.Tk()
    app = InterfazIntegrada(root)
    root.protocol("WM_DELETE_WINDOW", app.cerrar)
    root.mainloop()


