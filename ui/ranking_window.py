"""
ranking_window.py
Ventana que muestra el top 5 de jugadores como defensor y como atacante.
"""

import tkinter as tk
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.players import get_top_players, Player


FONT_TITLE  = ("Courier New", 16, "bold")
FONT_SUB    = ("Courier New", 10)
FONT_LABEL  = ("Courier New", 11, "bold")
FONT_ROW    = ("Courier New", 10)
FONT_BTN    = ("Courier New", 10, "bold")

BG      = "#1A1A2E"
PANEL   = "#16213E"
TEXT    = "#EAEAEA"
DIM     = "#8892A4"
GOLD    = "#F5A623"
SILVER  = "#C0C0C0"
BRONZE  = "#CD7F32"
ACCENT  = "#E94560"
SUCCESS = "#4CAF50"

MEDAL = {0: ("🥇", GOLD), 1: ("🥈", SILVER), 2: ("🥉", BRONZE)}


class RankingWindow:
    """
    Muestra el top 5 de jugadores por victorias como defensor y como atacante.

    Args:
        root: Ventana Tk raíz.
        on_close: Callable opcional al cerrar la ventana.
    """

    def __init__(self, root: tk.Tk, on_close=None):
        self.win = tk.Toplevel(root)
        self.win.title("🏆 Ranking de Jugadores")
        self.win.configure(bg=BG)
        self.win.resizable(False, False)
        self.on_close = on_close
        self.win.protocol("WM_DELETE_WINDOW", self._close)
        self._center(560, 520)
        self._build_ui()

    def _build_ui(self):
        # Título
        tk.Label(self.win, text="🏆  RANKING DE JUGADORES",
                 font=FONT_TITLE, fg=GOLD, bg=BG).pack(pady=(24, 4))
        tk.Label(self.win, text="Top 5 por rol",
                 font=FONT_SUB, fg=DIM, bg=BG).pack(pady=(0, 16))

        # Contenedor de dos tablas lado a lado
        tables = tk.Frame(self.win, bg=BG)
        tables.pack(padx=20, fill="x")

        self._build_table(tables, "🛡 Defensores", "defender", 0)
        self._build_table(tables, "⚔ Atacantes",  "attacker", 1)
        tables.columnconfigure(0, weight=1)
        tables.columnconfigure(1, weight=1)

        # Botón cerrar
        tk.Button(
            self.win, text="Cerrar",
            font=FONT_BTN,
            bg=ACCENT, fg=TEXT,
            activebackground=DIM, activeforeground=BG,
            relief="flat", bd=0, pady=8,
            cursor="hand2",
            command=self._close
        ).pack(padx=40, fill="x", pady=20)

    def _build_table(self, parent, title: str, role: str, col: int):
        """Construye una tabla de ranking para el rol dado."""
        frame = tk.Frame(parent, bg=PANEL, padx=12, pady=12)
        frame.grid(row=0, column=col, padx=8, sticky="nsew")

        tk.Label(frame, text=title, font=FONT_LABEL,
                 fg=GOLD, bg=PANEL).pack(anchor="w", pady=(0, 8))

        players = get_top_players(role, top_n=5)

        if not players:
            tk.Label(frame, text="Sin datos aún.",
                     font=FONT_ROW, fg=DIM, bg=PANEL).pack(anchor="w")
            return

        for i, player in enumerate(players):
            wins = player.wins_defender if role == "defender" else player.wins_attacker
            medal_sym, medal_color = MEDAL.get(i, ("  ", TEXT))

            row_frame = tk.Frame(frame, bg=PANEL)
            row_frame.pack(fill="x", pady=3)

            tk.Label(row_frame, text=medal_sym,
                     font=("Courier New", 13), bg=PANEL,
                     fg=medal_color, width=2).pack(side="left")

            tk.Label(row_frame,
                     text=f"{i+1}. {player.username}",
                     font=FONT_ROW, fg=TEXT, bg=PANEL,
                     anchor="w").pack(side="left", padx=6, fill="x", expand=True)

            tk.Label(row_frame,
                     text=f"{wins} vic.",
                     font=FONT_ROW, fg=medal_color, bg=PANEL).pack(side="right")

        # Línea separadora al final
        tk.Frame(frame, bg=GOLD, height=1).pack(fill="x", pady=(10, 0))

    def _close(self):
        if self.on_close:
            self.on_close()
        self.win.destroy()

    def _center(self, w: int, h: int):
        self.win.update_idletasks()
        sw = self.win.winfo_screenwidth()
        sh = self.win.winfo_screenheight()
        self.win.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
