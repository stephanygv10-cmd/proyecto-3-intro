"""
test_geometry.py
Prueba aislada: ¿el geometry() de Tkinter realmente funciona en esta PC?
Construye una ventana con un mapa + panel lateral, igual que el juego,
y al final fuerza el tamaño. Si esta ventana SÍ sale ancha, el problema
está en cómo main.py reutiliza el root entre ventanas.
Si esta ventana SIGUE saliendo angosta, el problema es de Windows/Tkinter.

Ejecutar: python test_geometry.py
"""

import tkinter as tk

root = tk.Tk()
root.title("Test de geometría")
root.configure(bg="#1A1A2E")
root.resizable(True, True)

# Simular el mapa (canvas grande)
canvas = tk.Canvas(root, width=460, height=460, bg="#1E2A40", highlightthickness=0)
canvas.pack(side="left")

# Simular el panel lateral
side = tk.Frame(root, bg="#16213E", width=260)
side.pack(side="left", fill="y")
side.pack_propagate(False)

tk.Label(side, text="PANEL LATERAL\n(si ves esto completo,\nel ancho funcionó)",
          bg="#16213E", fg="white", font=("Courier New", 11)).pack(pady=30)

# Forzar tamaño AL FINAL, como en el fix
root.update_idletasks()
sw = root.winfo_screenwidth()
sh = root.winfo_screenheight()
w = min(960, sw - 40)
h = min(660, sh - 60)
x = (sw - w) // 2
y = (sh - h) // 2
root.minsize(900, 600)
root.geometry(f"{w}x{h}+{x}+{y}")

# Mostrar info de diagnóstico en el título
root.title(f"Test — pantalla {sw}x{sh} — ventana pedida {w}x{h}")

print(f"Pantalla detectada: {sw}x{sh}")
print(f"Ventana pedida: {w}x{h}")
print(f"Geometry string enviado: {w}x{h}+{x}+{y}")

root.mainloop()

# Imprime el tamaño REAL que quedó después de cerrar la ventana
print(f"Tamaño real final: {root.winfo_width()}x{root.winfo_height()}")
