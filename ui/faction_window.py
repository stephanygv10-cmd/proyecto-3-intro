"""
faction_window.py
Ventana donde cada jugador elige su facción antes de iniciar la partida.
El atacante y el defensor no pueden usar la misma facción.
"""

import tkinter as tk
from tkinter import messagebox
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.players import Player
from src.factions import FACTIONS, Faction, faction_names


FONT_TITLE  = ("Courier New", 18, "bold")
FONT_SUB    = ("Courier New", 10)
FONT_LABEL  = ("Courier New", 11, "bold")
FONT_BTN    = ("Courier New", 10, "bold")
FONT_SMALL  = ("Courier New", 9)
FONT_DESC   = ("Courier New", 9, "italic")

BG          = "#1A1A2E"
PANEL       = "#16213E"
TEXT        = "#EAEAEA"
TEXT_DIM    = "#8892A4"
GOLD        = "#F5A623"
ACCENT      = "#E94560"
SUCCESS     = "#4CAF50"
DISABLED    = "#3A3A5A"


class FactionWindow:
    """
    Ventana de selección de facciones para los dos jugadores.

    Flujo:
        1. Jugador 1 elige facción (defensor o atacante, según sorteo/orden).
        2. Jugador 2 elige entre las facciones restantes.
        3. Se llama on_faction_selected(player1, faction1, player2, faction2).

    Args:
        root: Ventana Tk raíz.
        player1: Objeto Player del jugador 1.
        player2: Objeto Player del jugador 2.
        on_faction_selected: Callable con firma
            (p1: Player, f1: Faction, p2: Player, f2: Faction) -> None
    """

    def __init__(self, root: tk.Tk, player1: Player, player2: Player,
                 on_faction_selected):
        self.root = root
        self.players = [player1, player2]
        self.on_faction_selected = on_faction_selected

        self.selections: list[Faction | None] = [None, None]
        self.current = 0   # índice del jugador que elige ahora (0 o 1)

        self._build_ui()

    # ── Construcción de UI ────────────────────────────────────────────────────

    def _build_ui(self):
        self.root.title("Defensa y Asalto de Base — Selección de Facción")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)
        self._center_window(640, 560)

        # Título
        tk.Label(self.root, text="⚔  ELIGE TU FACCIÓN",
                 font=FONT_TITLE, fg=GOLD, bg=BG).pack(pady=(24, 4))

        # Indicador del jugador actual
        self.turn_label = tk.Label(
            self.root, text="", font=("Courier New", 12, "bold"),
            fg=ACCENT, bg=BG
        )
        self.turn_label.pack(pady=(0, 12))

        # Contenedor de tarjetas de facciones
        cards_frame = tk.Frame(self.root, bg=BG)
        cards_frame.pack(padx=24, fill="x")

        self.faction_buttons: dict[str, tk.Button] = {}
        self.card_frames: dict[str, tk.Frame] = {}

        names = faction_names()
        for i, fname in enumerate(names):
            faction = FACTIONS[fname]
            card = self._make_faction_card(cards_frame, faction, i)
            card.grid(row=0, column=i, padx=10, pady=8, sticky="nsew")
            cards_frame.columnconfigure(i, weight=1)
            self.card_frames[fname] = card

        # Resumen de selecciones
        summary_frame = tk.Frame(self.root, bg=PANEL, padx=20, pady=14)
        summary_frame.pack(padx=24, pady=16, fill="x")

        self.summary_labels: list[tk.Label] = []
        for i in range(2):
            lbl = tk.Label(
                summary_frame,
                text=f"Jugador {i+1} ({self.players[i].username}): —",
                font=FONT_SMALL, fg=TEXT_DIM, bg=PANEL
            )
            lbl.pack(anchor="w")
            self.summary_labels.append(lbl)

        # Botón de confirmar (inactivo hasta que ambos elijan)
        self.confirm_btn = tk.Button(
            self.root, text="Iniciar partida →",
            font=FONT_BTN,
            bg=DISABLED, fg=TEXT_DIM,
            activebackground=SUCCESS, activeforeground=BG,
            relief="flat", bd=0, pady=10,
            state="disabled", cursor="arrow",
            command=self._confirm
        )
        self.confirm_btn.pack(padx=24, fill="x", pady=(0, 20))

        self._update_turn_label()

    def _make_faction_card(self, parent, faction: Faction, idx: int) -> tk.Frame:
        """Crea la tarjeta visual de una facción."""
        card = tk.Frame(parent, bg=PANEL, padx=14, pady=14,
                        relief="flat", bd=2)

        # Emoji grande de la base como ícono de la facción
        tk.Label(card, text=faction.symbols["base"],
                 font=("Courier New", 32), bg=PANEL).pack()

        # Nombre
        tk.Label(card, text=faction.name,
                 font=FONT_LABEL, fg=faction.colors["accent"],
                 bg=PANEL).pack(pady=(4, 2))

        # Descripción
        tk.Label(card, text=faction.description,
                 font=FONT_DESC, fg=TEXT_DIM, bg=PANEL,
                 wraplength=160, justify="center").pack(pady=(0, 8))

        # Muestra de unidades
        units_text = (
            f"{faction.symbols['soldier']} {faction.symbols['tank']} "
            f"{faction.symbols['fast']}  |  "
            f"{faction.symbols['tower_basic']} {faction.symbols['tower_heavy']} "
            f"{faction.symbols['tower_magic']}"
        )
        tk.Label(card, text=units_text,
                 font=("Courier New", 14), bg=PANEL).pack(pady=(0, 10))

        # Botón de selección
        btn = tk.Button(
            card, text="Elegir",
            font=FONT_BTN,
            bg=faction.colors["accent"], fg=TEXT,
            activebackground=faction.colors["text"],
            activeforeground=BG,
            relief="flat", bd=0, pady=8,
            cursor="hand2",
            command=lambda f=faction: self._select_faction(f)
        )
        btn.pack(fill="x")
        self.faction_buttons[faction.name] = btn

        return card

    # ── Lógica de selección ───────────────────────────────────────────────────

    def _select_faction(self, faction: Faction):
        """Registra la elección del jugador actual."""
        player = self.players[self.current]
        self.selections[self.current] = faction

        # Actualizar resumen
        self.summary_labels[self.current].config(
            text=f"Jugador {self.current+1} ({player.username}): "
                 f"{faction.symbols['base']} {faction.name}",
            fg=faction.colors["accent"]
        )

        if self.current == 0:
            # Desactivar la facción elegida por J1 para J2
            btn = self.faction_buttons[faction.name]
            btn.config(state="disabled", bg=DISABLED, fg=TEXT_DIM,
                       cursor="arrow", text="Elegida")

            self.current = 1
            self._update_turn_label()
        else:
            # Ambos jugadores eligieron
            self._unlock_confirm()

    def _update_turn_label(self):
        player = self.players[self.current]
        self.turn_label.config(
            text=f"🎮  Jugador {self.current + 1} ({player.username}) — elige tu facción"
        )

    def _unlock_confirm(self):
        """Activa el botón de confirmar cuando ambos jugadores eligieron."""
        self.confirm_btn.config(
            state="normal", bg=SUCCESS, fg=BG,
            cursor="hand2"
        )
        self.turn_label.config(
            text="✔  ¡Ambos jugadores listos! Pulsa para iniciar.",
            fg=SUCCESS
        )
        # Desactivar todos los botones de facción
        for btn in self.faction_buttons.values():
            btn.config(state="disabled")

    def _confirm(self):
        """Cierra la ventana y llama al callback con las selecciones."""
        p1, p2 = self.players
        f1, f2 = self.selections
        self.on_faction_selected(p1, f1, p2, f2)

    # ── Utilidades ────────────────────────────────────────────────────────────

    def _center_window(self, width: int, height: int):
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - width) // 2
        y = (sh - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")