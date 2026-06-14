"""
main.py
Punto de entrada del juego Defensa y Asalto de Base.
Ejecutar este archivo para iniciar la aplicación.
"""

import tkinter as tk
from ui.login_window import LoginWindow
from src.players import Player


def on_login_success(player1: Player, player2: Player):
    """
    Callback que se invoca cuando ambos jugadores se autentican.
    Aquí se cerrará la ventana de login y se abrirá la ventana de selección
    de facciones / juego principal (por implementar).
    """
    print(f"[OK] Jugador 1: {player1.username}")
    print(f"[OK] Jugador 2: {player2.username}")

    # TODO: abrir la ventana de selección de facciones
    # from ui.faction_window import FactionWindow
    # FactionWindow(root, player1, player2)

    # Por ahora mostramos un mensaje temporal
    import tkinter.messagebox as mb
    mb.showinfo(
        "¡Jugadores listos!",
        f"Jugador 1: {player1.username}\n"
        f"Jugador 2: {player2.username}\n\n"
        "La selección de facciones se implementará a continuación."
    )


def main():
    root = tk.Tk()
    LoginWindow(root, on_login_success)
    root.mainloop()


if __name__ == "__main__":
    main()
