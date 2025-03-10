import os
import face_recognition
import cv2
import numpy
import numpy as np


video_capture = cv2.VideoCapture(0)

# Create arrays of known face encodings and their names
known_face_encodings = []

for filename in os.listdir("train_dir"):
    if filename.endswith((".jpg", ".jpeg", ".png")):
        image_path = os.path.join("train_dir", filename)
        image = face_recognition.load_image_file(image_path)
        image_encoding = face_recognition.face_encodings(image)[0]
        known_face_encodings.append(image_encoding)

with open("names.txt", "r") as name_file:
    known_face_names = name_file.readlines()
    known_face_names = [name.strip() for name in known_face_names]

# Initialize some variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True

while True:
    # Grab a single frame of video
    ret, frame = video_capture.read()

    # Only process every other frame of video to save time
    if process_this_frame:
        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        #rgb_small_frame = small_frame[:, :, ::-1]
        rgb_small_frame = numpy.ascontiguousarray(small_frame[:, :, ::-1])

        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Desconocido"

            # # If a match was found in known_face_encodings, just use the first one.
            # if True in matches:
            #     first_match_index = matches.index(True)
            #     name = known_face_names[first_match_index]

            # Or instead, use the known face with the smallest distance to the new face
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]

            face_names.append(name)

    process_this_frame = not process_this_frame

    # Display the results
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Draw a label with a name below the face
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    # Display the resulting image
    cv2.imshow('Video', frame)

    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()


'''
import os
import face_recognition
import cv2
import numpy as np
from datetime import datetime

# Capturar video desde la cámara web
video_capture = cv2.VideoCapture(0)

# Crear arreglos para las codificaciones faciales conocidas y sus nombres
known_face_encodings = []
known_face_names = []

# Cargar codificaciones faciales conocidas y sus nombres
for filename in os.listdir("train_dir"):
    if filename.endswith((".jpg", ".jpeg", ".png")):
        image_path = os.path.join("train_dir", filename)
        try:
            image = face_recognition.load_image_file(image_path)
            image_encodings = face_recognition.face_encodings(image)
            if image_encodings:
                known_face_encodings.append(image_encodings[0])
                known_face_names.append(filename.split('.')[0])  # Usar el nombre del archivo sin extensión como el nombre
            else:
                print(f"Warning: No faces found in {image_path}")
        except Exception as e:
            print(f"Error processing {image_path}: {e}")

if not known_face_names:
    raise ValueError("No known faces loaded. Please check the 'train_dir' and 'names.txt' files.")

# Inicializar algunas variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True
attendance_marked = set()  # Conjunto para mantener un registro de las personas cuya asistencia ya se ha marcado

# Función para marcar asistencia
def mark_attendance(name):
    with open("asistencia.txt", "a") as file:
        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"{name},{dt_string}\n")

while True:
    # Capturar un solo frame del video
    ret, frame = video_capture.read()

    # Procesar solo cada otro frame de video para ahorrar tiempo
    if process_this_frame:
        # Redimensionar el frame del video a 1/4 de su tamaño para un procesamiento más rápido
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Convertir la imagen de color BGR (que usa OpenCV) a color RGB (que usa face_recognition)
        rgb_small_frame = np.ascontiguousarray(small_frame[:, :, ::-1])

        # Encontrar todas las caras y sus codificaciones en el frame de video actual
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # Verificar si la cara es una coincidencia con alguna de las caras conocidas
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Desconocido"

            # O en su lugar, usar la cara conocida con la menor distancia a la nueva cara
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]

            face_names.append(name)
            # Marcar asistencia si la cara es reconocida y aún no se ha registrado
            if name != "Desconocido" and name not in attendance_marked:
                mark_attendance(name)
                attendance_marked.add(name)

    process_this_frame = not process_this_frame

    # Mostrar los resultados
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Escalar de nuevo las ubicaciones de las caras ya que el frame detectado estaba a 1/4 de tamaño
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Dibujar un cuadro alrededor de la cara
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Dibujar una etiqueta con el nombre debajo de la cara
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    # Mostrar la imagen resultante
    cv2.imshow('Video', frame)

    # Presionar 'q' en el teclado para salir
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar el manejo de la cámara web
video_capture.release()
cv2.destroyAllWindows()


'''