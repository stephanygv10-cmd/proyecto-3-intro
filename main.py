"""
main.py
Punto de entrada del juego Defensa y Asalto de Base.
Ejecutar: python main.py
"""

import sys
import os

# Asegura que Python encuentre los módulos src/ y ui/
# sin importar desde qué carpeta se ejecute el script.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sys
import os

# Asegura que Python encuentre los módulos src/ y ui/
# sin importar desde qué carpeta se ejecute el script.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
from ui.login_window   import LoginWindow
from ui.faction_window import FactionWindow
from ui.game_window    import GameWindow
from src.players       import Player, update_wins
from src.factions      import Faction


root = tk.Tk()


def _reset_root():
    """
    Limpia el root para la siguiente pantalla.
    Destruye los widgets hijos Y resetea el estado de tamaño/resizable
    que pudo haber quedado fijado por la ventana anterior.
    """
    for widget in root.winfo_children():
        widget.destroy()
    root.resizable(True, True)
    root.minsize(1, 1)
    # geometry "" libera cualquier tamaño/posición fijado antes,
    # dejando que la próxima ventana calcule su propio tamaño desde cero.
    root.geometry("")


def on_game_over(winner: Player, role: str):
    """Actualiza victorias y vuelve al login para otra partida."""
    update_wins(winner.username, role)
    _reset_root()
    LoginWindow(root, on_login_success)


def on_faction_selected(p1: Player, f1: Faction, p2: Player, f2: Faction):
    """Abre la ventana principal del juego."""
    _reset_root()
    GameWindow(root, p1, f1, p2, f2, on_game_over)


def on_login_success(player1: Player, player2: Player):
    """Abre la selección de facciones."""
    _reset_root()
    FactionWindow(root, player1, player2, on_faction_selected)


LoginWindow(root, on_login_success)
root.mainloop()