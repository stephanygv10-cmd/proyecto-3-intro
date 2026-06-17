"""
login_window.py
Ventana de inicio de sesión y registro de jugadores.
Soporta el flujo de dos jugadores antes de iniciar la partida.
"""

import tkinter as tk
from tkinter import ttk, messagebox

# Importación relativa para cuando se usa desde main.py
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.players import register_player, login_player, Player


# ── Paleta de colores ──────────────────────────────────────────────────────
COLORS = {
    "bg":        "#1A1A2E",   # fondo oscuro azul-noche
    "panel":     "#16213E",   # panel interior
    "accent":    "#E94560",   # rojo-coral para botones principales
    "accent2":   "#0F3460",   # azul profundo para botones secundarios
    "text":      "#EAEAEA",   # texto claro
    "text_dim":  "#8892A4",   # texto atenuado
    "entry_bg":  "#0F3460",   # fondo de entradas
    "success":   "#4CAF50",   # verde para mensajes de éxito
    "error":     "#E94560",   # rojo para errores
    "gold":      "#F5A623",   # dorado para título
}

FONT_TITLE  = ("Courier New", 22, "bold")
FONT_SUB    = ("Courier New", 11)
FONT_LABEL  = ("Courier New", 10, "bold")
FONT_ENTRY  = ("Courier New", 11)
FONT_BTN    = ("Courier New", 10, "bold")
FONT_SMALL  = ("Courier New", 9)


class LoginWindow:
    """
    Ventana principal de autenticación.
    Gestiona el login y registro de los dos jugadores antes de iniciar el juego.

    Al completarse, llama a on_login_success(player1, player2) con los
    objetos Player de ambos jugadores.
    """

    def __init__(self, root: tk.Tk, on_login_success):
        """
        Args:
            root: Ventana raíz de Tkinter.
            on_login_success: Callable(player1: Player, player2: Player).
        """
        self.root = root
        self.on_login_success = on_login_success
        self.players: list[Player] = []   # acumula hasta 2 jugadores autenticados
        self.current_slot = 1             # 1 o 2 (jugador actual)

        self._build_ui()

    # ── Construcción de la UI ────────────────────────────────────────────────

    def _build_ui(self):
        """Construye todos los widgets de la ventana."""
        self.root.title("Defensa y Asalto de Base — Login")
        self.root.configure(bg=COLORS["bg"])
        self.root.resizable(False, False)
        self._center_window(480, 580)

        # ── Título del juego ──
        title_frame = tk.Frame(self.root, bg=COLORS["bg"])
        title_frame.pack(pady=(30, 10))

        tk.Label(
            title_frame, text="⚔  DEFENSA Y ASALTO",
            font=FONT_TITLE, fg=COLORS["gold"], bg=COLORS["bg"]
        ).pack()
        tk.Label(
            title_frame, text="DE BASE",
            font=FONT_TITLE, fg=COLORS["gold"], bg=COLORS["bg"]
        ).pack()
        tk.Label(
            title_frame, text="— Inicio de sesión —",
            font=FONT_SUB, fg=COLORS["text_dim"], bg=COLORS["bg"]
        ).pack(pady=(4, 0))

        # ── Indicador de turno de jugador ──
        self.slot_label = tk.Label(
            self.root,
            text="🎮  Jugador 1",
            font=("Courier New", 13, "bold"),
            fg=COLORS["accent"], bg=COLORS["bg"]
        )
        self.slot_label.pack(pady=(18, 0))

        # ── Panel central ──
        panel = tk.Frame(self.root, bg=COLORS["panel"],
                         bd=0, relief="flat",
                         padx=36, pady=28)
        panel.pack(padx=40, pady=12, fill="x")

        # Campo usuario
        tk.Label(panel, text="Usuario", font=FONT_LABEL,
                 fg=COLORS["text_dim"], bg=COLORS["panel"],
                 anchor="w").pack(fill="x")
        self.entry_user = self._make_entry(panel)
        self.entry_user.pack(fill="x", pady=(2, 12))

        # Campo contraseña
        tk.Label(panel, text="Contraseña", font=FONT_LABEL,
                 fg=COLORS["text_dim"], bg=COLORS["panel"],
                 anchor="w").pack(fill="x")
        self.entry_pass = self._make_entry(panel, show="●")
        self.entry_pass.pack(fill="x", pady=(2, 18))

        # Mensaje de estado (errores / éxito)
        self.msg_label = tk.Label(
            panel, text="", font=FONT_SMALL,
            fg=COLORS["error"], bg=COLORS["panel"],
            wraplength=360, justify="center"
        )
        self.msg_label.pack(pady=(0, 10))

        # Botones de acción
        btn_frame = tk.Frame(panel, bg=COLORS["panel"])
        btn_frame.pack(fill="x")

        self._make_button(
            btn_frame, "Iniciar sesión", self._handle_login,
            COLORS["accent"]
        ).pack(fill="x", pady=(0, 8))

        self._make_button(
            btn_frame, "Registrarse", self._handle_register,
            COLORS["accent2"]
        ).pack(fill="x")

        # ── Progreso de jugadores ──
        progress_frame = tk.Frame(self.root, bg=COLORS["bg"])
        progress_frame.pack(pady=12)

        self.player_indicators = []
        for i in range(2):
            ind = tk.Label(
                progress_frame,
                text=f"Jugador {i+1}: —",
                font=FONT_SMALL,
                fg=COLORS["text_dim"], bg=COLORS["bg"]
            )
            ind.grid(row=0, column=i, padx=20)
            self.player_indicators.append(ind)

        # Enfocar el campo de usuario al abrir
        self.entry_user.focus_set()

        # Enter en contraseña = login
        self.entry_pass.bind("<Return>", lambda e: self._handle_login())

    # ── Widgets helpers ──────────────────────────────────────────────────────

    def _make_entry(self, parent, show="") -> tk.Entry:
        entry = tk.Entry(
            parent, font=FONT_ENTRY,
            bg=COLORS["entry_bg"], fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief="flat", bd=6,
            show=show
        )
        return entry

    def _make_button(self, parent, text: str, command, color: str) -> tk.Button:
        return tk.Button(
            parent, text=text, command=command,
            font=FONT_BTN,
            bg=color, fg=COLORS["text"],
            activebackground=COLORS["text_dim"],
            activeforeground=COLORS["bg"],
            relief="flat", bd=0,
            pady=9, cursor="hand2"
        )

    # ── Lógica de autenticación ──────────────────────────────────────────────

    def _handle_login(self):
        """Intenta iniciar sesión con las credenciales ingresadas."""
        username = self.entry_user.get()
        password = self.entry_pass.get()

        success, result = login_player(username, password)

        if not success:
            self._show_message(result, error=True)
            return

        player: Player = result

        # Verificar que ambos jugadores sean distintos
        if self.players and self.players[0].username == player.username:
            self._show_message(
                "El jugador 2 debe ser diferente al jugador 1.", error=True
            )
            return

        self._accept_player(player)

    def _handle_register(self):
        """Registra un nuevo jugador y lo acepta automáticamente."""
        username = self.entry_user.get()
        password = self.entry_pass.get()

        success, msg = register_player(username, password)

        if not success:
            self._show_message(msg, error=True)
            return

        # Tras el registro, hacer login automático
        _, player = login_player(username, password)

        if self.players and self.players[0].username == player.username:
            self._show_message(
                "El jugador 2 debe ser diferente al jugador 1.", error=True
            )
            return

        self._show_message(f"¡Bienvenido, {username}! Cuenta creada.", error=False)
        self._accept_player(player)

    def _accept_player(self, player: Player):
        """Acepta un jugador autenticado y avanza al siguiente paso."""
        self.players.append(player)
        idx = len(self.players) - 1

        # Actualizar indicador visual
        self.player_indicators[idx].config(
            text=f"Jugador {idx + 1}: ✔ {player.username}",
            fg=COLORS["success"]
        )

        if len(self.players) == 2:
            # Ambos jugadores listos → continuar al juego
            self.root.after(600, self._proceed_to_game)
        else:
            # Pedir al jugador 2
            self.current_slot = 2
            self.slot_label.config(text="🎮  Jugador 2")
            self._clear_fields()
            self._show_message(
                f"¡{player.username} listo! Ahora ingrese el Jugador 2.",
                error=False
            )

    def _proceed_to_game(self):
        """Destruye la ventana de login y llama al callback con los dos jugadores."""
        self.on_login_success(self.players[0], self.players[1])

    # ── Utilidades ───────────────────────────────────────────────────────────

    def _show_message(self, msg: str, error: bool = True):
        color = COLORS["error"] if error else COLORS["success"]
        self.msg_label.config(text=msg, fg=color)

    def _clear_fields(self):
        self.entry_user.delete(0, tk.END)
        self.entry_pass.delete(0, tk.END)
        self.msg_label.config(text="")
        self.entry_user.focus_set()

    def _center_window(self, width: int, height: int):
        """Centra la ventana en la pantalla."""
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - width) // 2
        y = (sh - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")