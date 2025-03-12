import cv2 as cv
import os
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import csv
from datetime import datetime
import threading

# --- Configuraciones Globales ---
DATA_RUTA = './Data'
CSV_REGISTROS = 'registros_biometricos.csv'
UMBRAL = 8000  # Umbral de similitud para reconocimiento

# --- Cargar lista de directorios (identificadores) ---
listaData = os.listdir(DATA_RUTA)

# --- Función para buscar en el CSV el registro que coincida con el identificador ---
def buscar_registro_por_id(identificador):
    print("Identificador a buscar: " , identificador)
    if not os.path.exists(CSV_REGISTROS):
        print("No se pudo abrir el archivo ", CSV_REGISTROS)
        return None
    with open(CSV_REGISTROS, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Se asume que en el CSV se guardó el nombre de carpeta en el campo "carpeta_fotos"
            if row.get("identificador", "").strip() == identificador:
                return row
    return None

# --- Función opcional para registrar el acceso en otro CSV ---
def registrar_acceso(registro):
    archivo = "registro_acceso.csv"
    cabecera = ["nombre", "documento", "carrera",
                "correo", "telefono", "timestamp", "identificador"]
    registro["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
        self.usuario_registrado = False

        # Inicializar variables para cámara y modelos
        self.camara = None
        self.recognizer = None
        self.cascade = None

        # Iniciar carga diferida en hilos para la cámara y los modelos
        threading.Thread(target=self.inicializar_camara, daemon=True).start()
        threading.Thread(target=self.cargar_modelos, daemon=True).start()

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

        # Botón para guardar manualmente el registro (además del registro automático)
        self.btn_guardar = ttk.Button(self.frame_formulario, text="Guardar Acceso", command=self.guardar_acceso)
        self.btn_guardar.grid(row=row, column=0, columnspan=2, pady=20)

        # Iniciar la actualización del video
        self.actualizar_video()

    def inicializar_camara(self):
        """Inicializa la cámara en un hilo separado para evitar bloquear la GUI.
           Ajusta el backend según tu sistema operativo:
           - Windows: cv.CAP_DSHOW
           - Linux: cv.CAP_V4L2
           - macOS: cv.CAP_AVFOUNDATION
        """
        # Ejemplo usando cv.CAP_V4L2 (Linux); ajusta según tu entorno.
        self.camara = cv.VideoCapture(0, cv.CAP_DSHOW)
        if not self.camara.isOpened():
            print("Error al abrir la cámara")
        else:
            self.camara.set(cv.CAP_PROP_FRAME_WIDTH, 640)
            self.camara.set(cv.CAP_PROP_FRAME_HEIGHT, 480)
            print("Cámara inicializada correctamente.")

    def cargar_modelos(self):
        """Carga en segundo plano los modelos pesados de reconocimiento facial."""
        print("Cargando modelos de reconocimiento facial...")
        self.recognizer = cv.face.EigenFaceRecognizer_create()
        self.recognizer.read('EntrenamientoEigenFaceRecognizer.xml')
        self.cascade = cv.CascadeClassifier('./Ruidos/data/haarcascades/haarcascade_frontalface_default.xml')
        print("Modelos cargados.")

    def actualizar_video(self):
        """Actualiza la vista previa del video y procesa el reconocimiento si los modelos están listos."""
        if self.camara is not None and self.camara.isOpened():
            ret, frame = self.camara.read()
            if ret:
                # Redimensionar la imagen usando cv.resize
                frame = cv.resize(frame, (640, int(frame.shape[0] * 640 / frame.shape[1])))
                gris = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
                # Si los modelos están cargados, realizar detección y reconocimiento
                if self.recognizer is not None and self.cascade is not None:
                    rostros = self.cascade.detectMultiScale(gris, 1.3, 5)
                    for (x, y, w, h) in rostros:
                        rostro = gris[y:y+h, x:x+w]
                        try:
                            rostro_resized = cv.resize(rostro, (160, 160), interpolation=cv.INTER_CUBIC)
                        except Exception:
                            continue
                        resultado = self.recognizer.predict(rostro_resized)
                        cv.putText(frame, f"{resultado}", (x, y - 5), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv.LINE_AA)
                        if resultado[1] < UMBRAL:
                            # El label devuelto es un índice que usamos para obtener el identificador
                            identificador = listaData[resultado[0]]
                            cv.putText(frame, f"{identificador}", (x, y - 20), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv.LINE_AA)
                            cv.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                            
                            if not self.usuario_registrado:
                                registro = buscar_registro_por_id(identificador)
                                if registro:
                                    print(registro)
                                    self.llenar_formulario(registro)
                                    self.registro_actual = registro
                                    self.usuario_registrado = True
                                    registrar_acceso(registro)
                                else:
                                    print("Registro no encontrado para el ID:", identificador)
                        else:
                            cv.putText(frame, "No encontrado", (x, y - 20), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv.LINE_AA)
                            cv.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                self.usuario_registrado = False
                # Convertir a RGB y actualizar el label de la interfaz
                frame_rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
                imagen = Image.fromarray(frame_rgb)
                imagen_tk = ImageTk.PhotoImage(image=imagen)
                self.label_video.configure(image=imagen_tk)
                self.label_video.image = imagen_tk
        else:
            print("Esperando a que la cámara se inicialice...")
        self.ventana.after(30, self.actualizar_video)

    def llenar_formulario(self, datos):
        """Llena el formulario con los datos del usuario reconocido."""
        self.entries["nombre"].delete(0, tk.END)
        self.entries["nombre"].insert(0, datos.get("nombre", ""))
        
        self.entries["documento"].delete(0, tk.END)
        self.entries["documento"].insert(0, datos.get("documento", ""))
        
        self.entries["carrera"].delete(0, tk.END)
        self.entries["carrera"].insert(0, datos.get("carrera", ""))
        
        self.entries["correo"].delete(0, tk.END)
        self.entries["correo"].insert(0, datos.get("correo", ""))
        
        self.entries["telefono"].delete(0, tk.END)
        self.entries["telefono"].insert(0, datos.get("telefono", ""))
        
        messagebox.showinfo("Usuario Reconocido", "El formulario se ha completado automáticamente.")
        self.ventana.destroy()

    def guardar_acceso(self):
        """Guarda el registro de acceso usando los datos del formulario."""
        datos = {
            "nombre": self.entries["nombre"].get(),
            "documento": self.entries["documento"].get(),
            "carrera": self.entries["carrera"].get(),
            "correo": self.entries["correo"].get(),
            "telefono": self.entries["telefono"].get(),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        registrar_acceso(datos)
        messagebox.showinfo("Registro Guardado", "El acceso ha sido registrado en el CSV.")

    def cerrar(self):
        """Maneja el cierre seguro de la aplicación."""
        if self.camara is not None:
            self.camara.release()
        cv.destroyAllWindows()
        self.ventana.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = InterfazIntegrada(root)
    root.protocol("WM_DELETE_WINDOW", app.cerrar)
    root.mainloop()
