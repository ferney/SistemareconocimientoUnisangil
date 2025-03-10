
"""
Este código realiza una captura de rostros desde una cámara en tiempo real, 
detectando y almacenando imágenes de cada rostro capturado en una carpeta 
específica.
1. Inicia la cámara y utiliza un clasificador de cascada para detectar rostros.
2. Al detectar un rostro, lo recorta, redimensiona y guarda en la carpeta específica.
3. Continúa el proceso hasta capturar 350 rostros o hasta que se interrumpa la ejecución.
"""

import cv2 as cv #Procesa imágenes y videos con herramientas de visión por computadora.
import os #Interactúa con el sistema operativo (archivos, directorios, comandos).
import imutils #Simplifica operaciones comunes de manipulación de imágenes con OpenCV.
import subprocess #Ejecuta comandos del sistema operativo y captura su salida.

# Define el nombre del modelo (directorio para almacenar las imágenes).
modelo = 'FotosWilliam'
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

# Bucle principal para capturar imágenes de la cámara en tiempo real.
while True:
    # Lee un frame de la cámara.
    respuesta, captura = camara.read()
    if respuesta == False:
        break

    # Redimensiona la imagen capturada a un ancho de 640 píxeles.
    captura = imutils.resize(captura, width=640)

    # Convierte la imagen a escala de grises (necesario para la detección de rostros).
    grises = cv.cvtColor(captura, cv.COLOR_BGR2GRAY)
    # Crea una copia de la captura en color original.
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
        # Incrementa el ID para el siguiente rostro.
        id += 1
    
    # Muestra la captura en tiempo real con el rectángulo alrededor de cada rostro detectado.
    cv.imshow("Resultado rostro", captura)

    # Termina el bucle después de capturar 350 rostros.
    if id == 1:
        break

# Libera la cámara y cierra las ventanas de OpenCV.
camara.release()
cv.destroyAllWindows()
# Llama al segundo archivo automáticamente para entrenar
subprocess.run(["python", "capaocultaentrenamiento.py"])