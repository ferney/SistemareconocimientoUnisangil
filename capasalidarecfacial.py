"""
Este código realiza el reconocimiento facial en un video o transmisión en tiempo real, 
utilizando un modelo preentrenado de EigenFace.
1. Carga el modelo de EigenFace para el reconocimiento facial y un clasificador para la detección de rostros.
2. Lee cada cuadro de video y convierte la imagen a escala de grises para detección.
3. Al detectar un rostro, realiza la predicción y determina si coincide con algún rostro entrenado.
4. Si es reconocido, muestra el nombre; si no, indica "No encontrado".
5. Se ejecuta en bucle hasta que el usuario presione 's' o termine el video.
"""

import cv2 as cv #Procesa imágenes y videos con herramientas de visión por computadora.
import os #Interactúa con el sistema operativo (archivos, directorios, comandos).
import imutils #Simplifica operaciones comunes de manipulación de imágenes con OpenCV.

# Define la ruta donde se almacenan las imágenes de los rostros.
dataRuta = './Data/'
# Lista los nombres de cada persona (subcarpetas) en la carpeta de datos.
listaData = os.listdir(dataRuta)

# Carga el modelo de reconocimiento facial previamente entrenado.
entrenamientoEigenFaceRecognizer = cv.face.EigenFaceRecognizer_create()
entrenamientoEigenFaceRecognizer.read('EntrenamientoEigenFaceRecognizer.xml')

# Carga el clasificador de cascada para detectar rostros en la imagen.
ruidos = cv.CascadeClassifier('./Ruidos/data/haarcascades/haarcascade_frontalface_default.xml')

# Inicia la captura de video (en este caso, desde un archivo 'desco.mp4').
camara = cv.VideoCapture(0)

# Bucle principal para leer cada cuadro del video.
while True:
    respuesta, captura = camara.read()
    if respuesta == False:
        break
    
    # Redimensiona el cuadro para estandarizar el tamaño.
    captura = imutils.resize(captura, width=640)
    
    # Convierte el cuadro a escala de grises (necesario para la detección y reconocimiento de rostros).
    grises = cv.cvtColor(captura, cv.COLOR_BGR2GRAY)
    idcaptura = grises.copy()

    # Detecta rostros en el cuadro.
    cara = ruidos.detectMultiScale(grises, 1.3, 5)

    # Itera sobre cada rostro detectado.
    for (x, y, e1, e2) in cara:
        # Recorta el rostro de la imagen en escala de grises.
        rostrocapturado = idcaptura[y:y + e2, x:x + e1]
        # Redimensiona el rostro capturado a 160x160 píxeles, el tamaño esperado por el modelo.
        rostrocapturado = cv.resize(rostrocapturado, (160, 160), interpolation=cv.INTER_CUBIC)
        
        # Realiza la predicción utilizando el modelo de EigenFace.
        resultado = entrenamientoEigenFaceRecognizer.predict(rostrocapturado)
        
        # Muestra en la imagen el resultado de la predicción (ID y distancia).
        cv.putText(captura, '{}'.format(resultado), (x, y - 5), 1, 1.3, (0, 255, 0), 1, cv.LINE_AA)
        
        # Si la distancia es menor a 8000, se considera un rostro reconocido.
        if resultado[1] < 8000:
            cv.putText(captura, '{}'.format(listaData[resultado[0]]), (x, y - 20), 2, 1.1, (0, 255, 0), 1, cv.LINE_AA)
            cv.rectangle(captura, (x, y), (x + e1, y + e2), (255, 0, 0), 2)
        else:
            # Si la distancia es mayor o igual a 8000, el rostro no es reconocido.
            cv.putText(captura, "No encontrado", (x, y - 20), 2, 0.7, (0, 255, 0), 1, cv.LINE_AA)
            cv.rectangle(captura, (x, y), (x + e1, y + e2), (255, 0, 0), 2)

    # Muestra el cuadro procesado con el reconocimiento en una ventana.
    cv.imshow("windows_ventana", captura)
    cv.setWindowProperty("windows_ventana",cv.WND_PROP_TOPMOST,1)

    # Espera a que el usuario presione 's' para salir del bucle.
    if cv.waitKey(1) == ord('s'):
        break

# Libera el video y cierra todas las ventanas de OpenCV.
camara.release()
cv.destroyAllWindows()
