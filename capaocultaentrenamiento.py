"""
Este código entrena un modelo de reconocimiento facial utilizando el algoritmo EigenFace de OpenCV, 
basado en un conjunto de imágenes faciales almacenadas en una carpeta. 
1. Carga y procesa imágenes de una carpeta de datos, asociándolas con un ID único por persona.
2. Entrena un modelo de reconocimiento facial EigenFace usando estas imágenes.
3. Mide y muestra el tiempo de lectura y de entrenamiento.
4. Al finalizar, guarda el modelo en un archivo XML para usarlo en reconocimiento facial futuro.
"""

import cv2 as cv #Procesa imágenes y videos con herramientas de visión por computadora.
import os #Interactúa con el sistema operativo (archivos, directorios, comandos).
import numpy as np #manejar arreglos multidimensionales (arrays) y realizar operaciones matemáticas y estadísticas eficientes sobre grandes volúmenes de datos.
from time import time #Maneja tiempo y pausas en la ejecución del programa.

# Define la ruta donde se almacenan las imágenes de los rostros.
dataRuta = './Data'
# Lista los subdirectorios en la ruta de datos, cada uno correspondiente a un conjunto de imágenes de una persona.
listaData = os.listdir(dataRuta)

# Inicializa las listas para almacenar los IDs y los datos de los rostros.
ids = []
rostrosData = []
id = 0  # Inicializa el ID de cada persona.

# Marca el tiempo inicial para medir la duración de la lectura de datos.
tiempoInicial = time()

# Itera sobre cada subdirectorio en la lista de datos.
for fila in listaData:
    rutacompleta = dataRuta + '/' + fila
    print('Iniciando lectura...')
    
    # Itera sobre cada archivo de imagen en el subdirectorio.
    for archivo in os.listdir(rutacompleta):
        print('Imagenes: ', fila + '/' + archivo)
        
        # Asocia el ID de la persona a cada imagen.
        ids.append(id)
        # Lee la imagen en escala de grises y la agrega a la lista de datos de rostros.
        rostrosData.append(cv.imread(rutacompleta + '/' + archivo, 0))
    
    # Incrementa el ID para la siguiente persona.
    id += 1
    
    # Mide y muestra el tiempo transcurrido para la lectura de los datos.
    tiempofinalLectura = time()
    tiempoTotalLectura = tiempofinalLectura - tiempoInicial
    print('Tiempo total lectura: ', tiempoTotalLectura)

# Inicializa el modelo de reconocimiento facial EigenFace.
entrenamientoEigenFaceRecognizer = cv.face.EigenFaceRecognizer_create()
print('Iniciando el entrenamiento...espere')

# Entrena el modelo con los datos de rostros y sus IDs.
entrenamientoEigenFaceRecognizer.train(rostrosData, np.array(ids))

# Calcula el tiempo total del entrenamiento y lo muestra.
TiempofinalEntrenamiento = time()
tiempoTotalEntrenamiento = TiempofinalEntrenamiento - tiempoTotalLectura
print('Tiempo entrenamiento total: ', tiempoTotalEntrenamiento)

# Guarda el modelo entrenado en un archivo XML.
entrenamientoEigenFaceRecognizer.write('EntrenamientoEigenFaceRecognizer.xml')
print('Entrenamiento concluido')
