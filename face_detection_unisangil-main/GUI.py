#-*- coding utf-8 -*-
import tkinter as tk
from tkinter import ttk
import subprocess

def ejecutar_capture():
    subprocess.Popen(["python", "capture_old2.py"])

def ejecutar_main():
    subprocess.Popen(["python", "main.py"])
    


# Creamos la ventana
root = tk.Tk()
root.title("Mi formulario")

# Evitar modificar tamaño de la ventana
root.resizable(500, 500) 

# Creamos frame principal
vp = ttk.Frame(root)

# Posicionamos frame en ventana principal
vp.grid(column=0, row=0, padx=(20, 20), pady=(10, 10))

# Cargar imagen y modifico tamaño
img = tk.PhotoImage(file="unisangil.png")
img = img.subsample(5)

# Creo el label para el logo o imagen
lblLogo = ttk.Label(vp, image=img)
lblLogo.grid(row=0, column=0, columnspan=2, pady=(10, 10))

# Crear botones
btn_capture = ttk.Button(vp, text="CAPTURAR", command=ejecutar_capture)
btn_capture.grid(row=1, column=0, padx=(0, 5), pady=(10, 10))

btn_main = ttk.Button(vp, text="RECONOCER", command=ejecutar_main)
btn_main.grid(row=1, column=1, padx=(5, 0), pady=(10, 10))





# Finalmente el bucle de la aplicación
root.mainloop()
