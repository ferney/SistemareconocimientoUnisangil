import cv2 as cv #Procesa imágenes y videos con herramientas de visión por computadora.
import os #Interactúa con el sistema operativo (archivos, directorios, comandos).
import imutils #Simplifica operaciones comunes de manipulación de imágenes con OpenCV.
import tkinter as tk #Crea interfaces gráficas para aplicaciones.
from tkinter import Label #Muestra texto o imágenes en una interfaz gráfica.
import threading #Ejecuta tareas en paralelo mediante hilos.
import time
import subprocess

# Define el nombre del modelo (directorio para almacenar las imágenes).
modelo = 'FotosC'
# Ruta base donde se almacenarán las imágenes.
ruta1 = 'D:/xx/reconocimientofacial1/Data'
# Ruta completa del directorio de almacenamiento, combinando ruta base y nombre del modelo.
rutacompleta = ruta1 + '/' + modelo

# Verifica si el directorio existe; si no, lo crea.
if not os.path.exists(rutacompleta):
    os.makedirs(rutacompleta)

# Inicializa la cámara.
camara = cv.VideoCapture(0)

# Carga el clasificador de cascada para detectar rostros frontales.
ruidos = cv.CascadeClassifier('D:/xx/reconocimientofacial1/Ruidos/data/haarcascades/haarcascade_frontalface_default.xml')

# ID para las imágenes capturadas, empezando en 0.
id = 0

# Función para el contador regresivo
def contador_regresivo():
    global contador
    for i in range(5, 0, -1):
        contador.set(i)
        time.sleep(1)
    tomar_imagen()

# Función para tomar una imagen
def tomar_imagen():
    global id
    respuesta, captura = camara.read()
    if respuesta == False:
        return
    captura = imutils.resize(captura, width=640)
    grises = cv.cvtColor(captura, cv.COLOR_BGR2GRAY)
    idcaptura = captura.copy()

    # Detecta rostros en la imagen en escala de grises.
    cara = ruidos.detectMultiScale(grises, 1.3, 5)

    # Itera sobre las coordenadas de cada rostro detectado.
    for (x, y, e1, e2) in cara:
        # Dibuja un rectángulo verde alrededor del rostro detectado.
        cv.rectangle(captura, (x, y), (x + e1, y + e2), (0, 255, 0), 2)
        # Recorta el área del rostro de la imagen original.
        rostrocapturado = idcaptura[y:y + e2, x:x + e1]
        # Redimensiona el rostro a 160x160 píxeles.
        rostrocapturado = cv.resize(rostrocapturado, (160, 160), interpolation=cv.INTER_CUBIC)
        # Guarda la imagen del rostro en la carpeta designada con un nombre único.
        cv.imwrite(rutacompleta + '/imagen_{}.jpg'.format(id), rostrocapturado)
        id += 1

    # Muestra la imagen con el rostro detectado
    cv.imshow("Resultado rostro", captura)

# Función para actualizar el frame de la cámara en la interfaz gráfica
def actualizar_frame():
    global contador
    respuesta, captura = camara.read()
    if respuesta:
        captura = imutils.resize(captura, width=640)
        captura_rgb = cv.cvtColor(captura, cv.COLOR_BGR2RGB)
        captura_imagen = ImageTk.PhotoImage(image=Image.fromarray(captura_rgb))
        label_video.config(image=captura_imagen)
        label_video.image = captura_imagen
    ventana.after(10, actualizar_frame)

# Crear ventana principal
ventana = tk.Tk()

ventana.title("Captura de Rostro con Cuenta Atrás")
ventana.geometry("800x600")
ventana.lift()
ventana.attributes("-topmost", True)
ventana.after(1000, lambda: ventana.attributes("-topmost", False))


# Crear etiqueta para mostrar el contador
contador = tk.IntVar()
contador.set(5)
label_contador = Label(ventana, textvariable=contador, font=("Arial", 50), fg="red")
label_contador.place(x=350, y=250)

# Crear etiqueta para mostrar la imagen de la cámara
from PIL import Image, ImageTk
label_video = Label(ventana)
label_video.pack()

# Iniciar contador en un hilo separado
threading.Thread(target=contador_regresivo, daemon=True).start()

# Iniciar la actualización del frame de la cámara
actualizar_frame()

# Ejecutar la interfaz gráfica
ventana.mainloop()


# Llama al segundo archivo automáticamente para entrenar
subprocess.run(["python", "capaocultaentrenamiento.py"])

# Liberar la cámara cuando se cierra la ventana
camara.release()
cv.destroyAllWindows()

