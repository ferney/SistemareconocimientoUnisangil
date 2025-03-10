import tkinter as tk
from tkinter import ttk

def guardar_datos():
    # Obtener datos de los campos
    datos = {
        'nombre': entries['nombre'].get(),
        'documento': entries['documento'].get(),
        'carrera': entries['carrera'].get(),
        'correro': entries['correro'].get(),  # Nota: "correro" está escrito así en el formulario
        'telefono': entries['telefono'].get()
    }
    
    # Guardar en archivo
    with open('datos_usuarios.txt', 'a', encoding='utf-8') as archivo:
        archivo.write(f"{datos['nombre']},{datos['documento']},{datos['carrera']},{datos['correro']},{datos['telefono']}\n"+"-" * 30 + "\n")
       
    # Limpiar campos después de guardar
    for entry in entries.values():
        entry.delete(0, tk.END)

# Configuración inicial
root = tk.Tk()
root.title("Formulario de Registro")
root.geometry("400x300")

main_frame = ttk.Frame(root, padding=20)
main_frame.pack(expand=True, fill='both')

# Campos del formulario
campos = [
    ("Nombre completo", 0),
    ("Documento de identidad", 1),
    ("Carrera que estudia", 2),
    ("correro", 3),  # Campo con nombre como en la imagen
    ("Telefono", 4)
]

entries = {}

for texto, fila in campos:
    ttk.Label(main_frame, text=texto + ":").grid(row=fila, column=0, padx=5, pady=5, sticky="w")
    entry = ttk.Entry(main_frame, width=30)
    entry.grid(row=fila, column=1, padx=5, pady=5, sticky="ew")
    entries[texto.lower().split()[0]] = entry  # Usamos la primera palabra como clave

# Botón Guardar
btn_guardar = ttk.Button(main_frame, text="Guardar", command=guardar_datos, style='Accent.TButton')
btn_guardar.grid(row=5, column=0, columnspan=2, pady=15, sticky="ew")

# Estilo
style = ttk.Style()
style.configure('Accent.TButton', foreground='white', background='#0078d4')
main_frame.columnconfigure(1, weight=1)

root.mainloop()