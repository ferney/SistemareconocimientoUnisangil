import cv2 as cv
import os
import imutils
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import csv

# ==============================================
# NUEVA CONFIGURACIÓN DE INTERFAZ
# ==============================================
class RecognitionUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Reconocimiento Facial")
        
        # Cargar datos del CSV
        self.datos_usuarios = self.cargar_datos_csv()
        
        # Configurar interfaz
        self.setup_ui()
        
        # Iniciar cámara
        self.camara = cv.VideoCapture(0)
        self.ruidos = cv.CascadeClassifier('./Ruidos/data/haarcascades/haarcascade_frontalface_default.xml')
        self.entrenamiento = cv.face.EigenFaceRecognizer_create()
        self.entrenamiento.read('EntrenamientoEigenFaceRecognizer.xml')
        
        # Iniciar actualización de video
        self.update_video()

    def cargar_datos_csv(self):
        datos = {}
        with open('registros_biometricos.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                datos[row['./Data/']] = row
        return datos

    def setup_ui(self):
        # Frame de video
        self.video_frame = ttk.Frame(self.root)
        self.video_frame.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Label para video
        self.video_label = ttk.Label(self.video_frame)
        self.video_label.pack()
        
        # Frame de formulario
        self.form_frame = ttk.Frame(self.root)
        self.form_frame.pack(side=tk.RIGHT, padx=10, pady=10)
        
        # Campos de datos
        campos = [
            "Nombre completo", "Documento de identidad",
            "Carrera que estudia", "Correo electrónico", "Teléfono"
        ]
        
        self.labels = {}
        for i, campo in enumerate(campos):
            lbl = ttk.Label(self.form_frame, text=f"{campo}:", font=('Arial', 10))
            lbl.grid(row=i, column=0, sticky="w", pady=2)
            
            val = ttk.Label(self.form_frame, text="", font=('Arial', 10, 'bold'))
            val.grid(row=i, column=1, sticky="w", pady=2)
            self.labels[campo.split()[0].lower()] = val

    def update_video(self):
        ret, frame = self.camara.read()
        if ret:
            frame = imutils.resize(frame, width=640)
            gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            
            # Detección facial
            faces = self.ruidos.detectMultiScale(gray, 1.3, 5)
            
            for (x, y, w, h) in faces:
                rostro = gray[y:y+h, x:x+w]
                rostro = cv.resize(rostro, (160, 160), interpolation=cv.INTER_CUBIC)
                
                id_pred, conf = self.entrenamiento.predict(rostro)
                if conf < 8000:
                    nombre_carpeta = os.listdir('D:/xx/reconocimientofacial1/Data')[id_pred]
                    self.mostrar_datos_usuario(nombre_carpeta)
                
                cv.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # Mostrar video en Tkinter
            img = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            imgtk = ImageTk.PhotoImage(image=img)
            
            self.video_label.config(image=imgtk)
            self.video_label.image = imgtk
        
        self.root.after(10, self.update_video)

    def mostrar_datos_usuario(self, nombre_carpeta):
        datos = self.datos_usuarios.get(nombre_carpeta, {})
        for key in self.labels:
            self.labels[key].config(text=datos.get(key, ""))

# ==============================================
# EJECUCIÓN
# ==============================================
if __name__ == "__main__":
    root = tk.Tk()
    app = RecognitionUI(root)
    root.mainloop()



# ==============================================
# data
# ==============================================


