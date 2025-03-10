import tkinter as tk #Crea interfaces gráficas para aplicaciones.
from tkinter import Frame, Button #Crea interfaces gráficas para aplicaciones.
#import os #Interactúa con el sistema operativo (archivos, directorios, comandos).
import subprocess #Ejecuta comandos del sistema operativo y captura su salida.

# Función para abrir la ventana de registro (inicio.py)
def abrir_registrar():
    try:
        # Ejecutar el script de inicio.py
        subprocess.Popen(['python', 'experimento2.py'])
    except Exception as e:
        print(f"Error al abrir el archivo de registro: {e}")

# Función para abrir la ventana de reconocimiento (capasalidarecfacial.py)
def abrir_reconocimiento():
    try:
        # Ejecutar el script de capasalidarecfacial.py
        subprocess.Popen(['python', 'capasalidarecfacial.py'])
    except Exception as e:
        print(f"Error al abrir el archivo de reconocimiento: {e}")

# Función para mostrar el contenido correspondiente al botón presionado
def cambiar_contenido(contenido):
    # Limpiar el frame principal
    for widget in frame_contenido.winfo_children():
        widget.destroy()

    # Agregar el nuevo contenido al frame principal
    if contenido == 'registrar':
        registrar_label = tk.Label(frame_contenido, text="Ventana de Registro", font=("Arial", 20))
        registrar_label.pack(pady=50)
        # Puedes agregar más widgets aquí según lo que necesites para la ventana de registro
    elif contenido == 'reconocimiento':
        reconocimiento_label = tk.Label(frame_contenido, text="Ventana de Reconocimiento", font=("Arial", 20))
        reconocimiento_label.pack(pady=50)
        # Puedes agregar más widgets aquí según lo que necesites para la ventana de reconocimiento

# Configuración de la ventana principal
ventana = tk.Tk()
ventana.title("Interfaz con Menú Lateral")
ventana.geometry("900x700")

# Marco para el menú lateral izquierdo
menu_lateral = Frame(ventana, width=200, height=600, bg="#2f4f4f")
menu_lateral.grid(row=0, column=0, sticky="ns")

# Botón Registrar
boton_registrar = Button(menu_lateral, text="Registrarse", font=("Arial", 14), bg="#4CAF50", fg="white", width=20, command=lambda: [cambiar_contenido('registrar'), abrir_registrar()])
boton_registrar.pack(pady=20)

# Botón Reconocimiento
boton_reconocimiento = Button(menu_lateral, text="Marcar Entrada", font=("Arial", 14), bg="#008CBA", fg="white", width=20, command=lambda: [cambiar_contenido('reconocimiento'), abrir_reconocimiento()])
boton_reconocimiento.pack(pady=20)

# Marco para el área de contenido principal
frame_contenido = Frame(ventana, width=600, height=600, bg="white")
frame_contenido.grid(row=0, column=1, padx=20, pady=20)

# Iniciar con el contenido vacío
cambiar_contenido('')

# Ejecutar la interfaz gráfica
ventana.mainloop()
