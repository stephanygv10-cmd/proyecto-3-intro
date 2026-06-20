"""
game_window.py
Ventana principal del juego: muestra el mapa 10x10, panel lateral de compras
y gestiona las fases de construcción y ataque.
"""

import tkinter as tk
from tkinter import messagebox
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.players  import Player
from src.factions import Faction
from src.map_grid import MapGrid, Base
from src.towers   import Tower, Wall, create_tower, TOWER_COSTS, TOWER_SPECIAL_DESC
from src.units    import Unit, create_unit, UNIT_COSTS, UNIT_SPECIAL_DESC
from src.economy  import Economy


# ── Dimensiones del mapa ──────────────────────────────────────────────────────
CELL_SIZE   = 44          # píxeles por casilla
GRID_ROWS   = 10
GRID_COLS   = 10
CANVAS_W    = CELL_SIZE * GRID_COLS
CANVAS_H    = CELL_SIZE * GRID_ROWS

# ── Colores base (se sobreescriben con los de la facción) ──────────────────────
C = {
    "bg":        "#1A1A2E",
    "panel":     "#16213E",
    "cell_even": "#1E2A40",
    "cell_odd":  "#1A2235",
    "grid_line": "#2A3A55",
    "text":      "#EAEAEA",
    "text_dim":  "#8892A4",
    "gold":      "#F5A623",
    "accent":    "#E94560",
    "success":   "#4CAF50",
    "danger":    "#E94560",
    "hp_bar_bg": "#333",
    "hp_bar_fg": "#4CAF50",
    "selected":  "#FFD700",
    "hover":     "#2A3F60",
    "attacker_row": "#2A1A1A",
}

FONT_TITLE  = ("Courier New", 11, "bold")
FONT_LABEL  = ("Courier New", 9, "bold")
FONT_SMALL  = ("Courier New", 8)
FONT_BTN    = ("Courier New", 8, "bold")
FONT_CELL   = ("Courier New", 15)
FONT_MINI   = ("Courier New", 6)


class GameWindow:
    """
    Ventana principal del juego.

    Parámetros:
        root: Ventana Tk raíz.
        player1, player2: Objetos Player.
        faction1, faction2: Objetos Faction (p1=defensor, p2=atacante por defecto).
        on_game_over: Callable(winner: Player, role: str) llamado al terminar la partida.
    """

    def __init__(self, root: tk.Tk,
                 player1: Player, faction1: Faction,
                 player2: Player, faction2: Faction,
                 on_game_over=None):
        self.root = root
        self.player_def  = player1   # jugador defensor
        self.faction_def = faction1
        self.player_att  = player2   # jugador atacante
        self.faction_att = faction2
        self.on_game_over = on_game_over

        # Estado del juego
        self.map     = MapGrid()
        self.eco_def = Economy("defender")
        self.eco_att = Economy("attacker")
        self.round   = 1
        self.wins_def = 0
        self.wins_att = 0
        self.phase   = "build"      # "build" | "attack" | "combat"
        self.selected_item = None   # nombre del item seleccionado para colocar

        # Log de eventos
        self.log_lines: list[str] = []

        # Celdas que activaron su habilidad especial en el último turno
        # (para resaltarlas visualmente en el mapa con un anillo dorado).
        self.special_fx_cells: set[tuple[int, int]] = set()

        self._build_ui()
        self._refresh_map()
        self._set_phase("build")

    # ══════════════════════════════════════════════════════════════════════════
    # CONSTRUCCIÓN DE LA UI
    # ══════════════════════════════════════════════════════════════════════════

    def _build_ui(self):
        self.root.title("Defensa y Asalto de Base")
        self.root.configure(bg=C["bg"])
        self.root.resizable(True, True)

        # ── Barra superior de estado ──────────────────────────────────────────
        top = tk.Frame(self.root, bg=C["panel"], pady=6)
        top.pack(fill="x")

        self.lbl_round = tk.Label(top, text="Ronda 1", font=FONT_TITLE,
                                   fg=C["gold"], bg=C["panel"])
        self.lbl_round.pack(side="left", padx=16)

        self.lbl_phase = tk.Label(top, text="", font=FONT_LABEL,
                                   fg=C["accent"], bg=C["panel"])
        self.lbl_phase.pack(side="left", padx=8)

        # Marcador
        self.lbl_score = tk.Label(top, text="", font=FONT_LABEL,
                                   fg=C["text"], bg=C["panel"])
        self.lbl_score.pack(side="right", padx=16)

        # ── Cuerpo principal ─────────────────────────────────────────────────
        body = tk.Frame(self.root, bg=C["bg"])
        body.pack(fill="both", expand=True)

        # Canvas del mapa
        map_frame = tk.Frame(body, bg=C["bg"], padx=4, pady=4)
        map_frame.pack(side="left")

        self.canvas = tk.Canvas(
            map_frame, width=CANVAS_W, height=CANVAS_H,
            bg=C["cell_even"], highlightthickness=0
        )
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self._on_cell_click)
        self.canvas.bind("<Motion>",   self._on_hover)

        # Panel lateral derecho (ancho fijo, no compite por espacio con el mapa)
        side = tk.Frame(body, bg=C["panel"], width=260, padx=12, pady=10)
        side.pack(side="left", fill="y")
        side.pack_propagate(False)

        self._build_side_panel(side)

        # ── Forzar el tamaño final de la ventana DESPUÉS de armar todo ────────
        # (si se hace antes, la ventana heredada del login puede pisar este tamaño)
        self.root.update_idletasks()

        # IMPORTANTE: como "side" usa pack_propagate(False), su altura
        # "pedida" (winfo_reqheight) NO refleja la suma real de sus widgets
        # internos, sino que queda atada a la altura del canvas del mapa.
        # Si el panel lateral necesita más alto que el canvas (por ejemplo,
        # al mostrar una ficha de torre/unidad), sus widgets de más abajo
        # (botón de fase, log de eventos) se quedan sin espacio y Tkinter
        # deja de dibujarlos, aunque el resto de la ventana tenga margen.
        # Por eso medimos la altura real necesaria del panel lateral
        # sumando sus hijos directamente, e incluimos esa medida en el
        # cálculo del alto total de la ventana.
        side_children_h = sum(
            child.winfo_reqheight() for child in side.winfo_children()
        )
        side_needed_h = side_children_h + 2 * 10   # + pady del frame "side"

        needed_w = self.root.winfo_reqwidth()
        needed_h = max(self.root.winfo_reqheight(), side_needed_h + top.winfo_reqheight())

        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        w = min(needed_w + 10, sw - 40)   # pequeño margen de seguridad
        h = min(needed_h + 20, sh - 60)
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.root.minsize(w, h)
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def _build_side_panel(self, parent):
        """Construye el panel lateral con info de jugadores, tienda y log."""

        # ── Info jugadores ────────────────────────────────────────────────────
        info_frame = tk.Frame(parent, bg=C["panel"])
        info_frame.pack(fill="x", pady=(0, 8))

        # Defensor
        def_color = self.faction_def.colors["accent"]
        tk.Label(info_frame,
                 text=f"🛡 {self.player_def.username} (Defensor)",
                 font=FONT_LABEL, fg=def_color, bg=C["panel"],
                 anchor="w", wraplength=230, justify="left").pack(fill="x")
        self.lbl_money_def = tk.Label(
            info_frame, text="", font=FONT_SMALL,
            fg=C["text_dim"], bg=C["panel"], anchor="w"
        )
        self.lbl_money_def.pack(fill="x")

        tk.Frame(parent, bg=C["grid_line"], height=1).pack(fill="x", pady=6)

        # Atacante
        att_color = self.faction_att.colors["accent"]
        tk.Label(info_frame,
                 text=f"⚔ {self.player_att.username} (Atacante)",
                 font=FONT_LABEL, fg=att_color, bg=C["panel"],
                 anchor="w", wraplength=230, justify="left").pack(fill="x")
        self.lbl_money_att = tk.Label(
            info_frame, text="", font=FONT_SMALL,
            fg=C["text_dim"], bg=C["panel"], anchor="w"
        )
        self.lbl_money_att.pack(fill="x")

        # HP de la base
        tk.Frame(parent, bg=C["grid_line"], height=1).pack(fill="x", pady=6)
        tk.Label(parent, text="Base Central", font=FONT_LABEL,
                 fg=C["gold"], bg=C["panel"], anchor="w").pack(fill="x")
        self.lbl_base_hp = tk.Label(parent, text="", font=FONT_SMALL,
                                     fg=C["text"], bg=C["panel"], anchor="w")
        self.lbl_base_hp.pack(fill="x", pady=(0, 6))

        # ── Tienda ────────────────────────────────────────────────────────────
        tk.Frame(parent, bg=C["grid_line"], height=1).pack(fill="x", pady=4)
        self.lbl_shop_title = tk.Label(parent, text="🏪 Tienda",
                                        font=FONT_LABEL, fg=C["gold"],
                                        bg=C["panel"], anchor="w")
        self.lbl_shop_title.pack(fill="x", pady=(0, 4))

        self.shop_frame = tk.Frame(parent, bg=C["panel"])
        self.shop_frame.pack(fill="x")

        self.shop_buttons: dict[str, tk.Button] = {}
        self._build_shop_buttons()

        # Ítem seleccionado — contenedor de ALTURA FIJA para que el botón
        # de fase y el log de abajo nunca pierdan su espacio, sin importar
        # cuán largo sea el texto de la ficha (antes, una ficha larga
        # empujaba el botón "Defensor listo" fuera del panel y Tkinter
        # dejaba de dibujarlo por completo).
        selected_container = tk.Frame(parent, bg=C["panel"], height=110)
        selected_container.pack(fill="x", pady=8)
        selected_container.pack_propagate(False)

        self.lbl_selected = tk.Label(
            selected_container, text="Selecciona un ítem y\nhaz clic en el mapa",
            font=FONT_SMALL, fg=C["text_dim"], bg=C["panel"],
            justify="left", wraplength=230, anchor="n"
        )
        self.lbl_selected.pack(fill="both", expand=True)

        # Botón de acción de fase
        tk.Frame(parent, bg=C["grid_line"], height=1).pack(fill="x", pady=4)
        self.btn_phase = tk.Button(
            parent, text="", font=FONT_BTN,
            bg=C["success"], fg=C["bg"],
            activebackground=C["text"], activeforeground=C["bg"],
            relief="flat", bd=0, pady=8, cursor="hand2",
            command=self._advance_phase
        )
        self.btn_phase.pack(fill="x", pady=4)

        # ── Log de eventos ────────────────────────────────────────────────────
        tk.Frame(parent, bg=C["grid_line"], height=1).pack(fill="x", pady=4)
        tk.Label(parent, text="📋 Eventos", font=FONT_LABEL,
                 fg=C["text_dim"], bg=C["panel"], anchor="w").pack(fill="x")

        self.log_text = tk.Text(
            parent, height=10, font=("Courier New", 8),
            bg=C["bg"], fg=C["text_dim"],
            relief="flat", state="disabled",
            wrap="word"
        )
        self.log_text.pack(fill="both", expand=True, pady=(2, 0))

    def _build_shop_buttons(self):
        """Crea los botones de la tienda según la fase actual."""
        for w in self.shop_frame.winfo_children():
            w.destroy()
        self.shop_buttons.clear()

        if self.phase == "build":
            items = {
                "Básica":  f"Torre Básica  ${TOWER_COSTS['Básica']}",
                "Pesada":  f"Torre Pesada  ${TOWER_COSTS['Pesada']}",
                "Mágica":  f"Torre Mágica  ${TOWER_COSTS['Mágica']}",
                "Muro":    f"Muro          ${TOWER_COSTS['Muro']}",
            }
        else:  # attack
            items = {
                "Soldado":       f"Soldado       ${UNIT_COSTS['Soldado']}",
                "Tanque":        f"Tanque        ${UNIT_COSTS['Tanque']}",
                "Unidad Rápida": f"Unid. Rápida  ${UNIT_COSTS['Unidad Rápida']}",
            }

        for key, label in items.items():
            btn = tk.Button(
                self.shop_frame, text=label,
                font=FONT_SMALL, anchor="w",
                bg=C["cell_odd"], fg=C["text"],
                activebackground=C["hover"], activeforeground=C["text"],
                relief="flat", bd=0, pady=5, padx=6,
                cursor="hand2",
                command=lambda k=key: self._select_item(k)
            )
            btn.pack(fill="x", pady=2)
            self.shop_buttons[key] = btn

    # ══════════════════════════════════════════════════════════════════════════
    # RENDERIZADO DEL MAPA
    # ══════════════════════════════════════════════════════════════════════════

    def _refresh_map(self):
        """Redibuja todo el canvas del mapa."""
        self.canvas.delete("all")
        faction = self.faction_def if self.phase == "build" else self.faction_att

        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                x0 = c * CELL_SIZE
                y0 = r * CELL_SIZE
                x1 = x0 + CELL_SIZE
                y1 = y0 + CELL_SIZE

                # Color de fondo de celda
                if r <= 1 and self.phase in ("attack", "combat"):
                    bg = C["attacker_row"]
                elif (r + c) % 2 == 0:
                    bg = C["cell_even"]
                else:
                    bg = C["cell_odd"]

                self.canvas.create_rectangle(
                    x0, y0, x1, y1,
                    fill=bg, outline=C["grid_line"], width=1
                )

                # Destello visual: la celda usó su habilidad especial este turno
                if (r, c) in self.special_fx_cells:
                    self.canvas.create_rectangle(
                        x0 + 2, y0 + 2, x1 - 2, y1 - 2,
                        outline=C["selected"], width=3
                    )

                obj = self.map.grid[r][c]
                if obj is None:
                    continue

                cx = x0 + CELL_SIZE // 2
                cy = y0 + CELL_SIZE // 2

                if isinstance(obj, Base):
                    sym = faction.symbols["base"]
                    color = faction.colors["base"]
                    self._draw_cell_content(cx, cy, sym, color,
                                            f"{obj.hp}/{obj.max_hp}")

                elif isinstance(obj, Tower):
                    sym = faction.symbols.get(obj.TOWER_TYPE, "🗼")
                    color = faction.colors["tower"]
                    self._draw_cell_content(cx, cy, sym, color,
                                            f"{obj.hp}/{obj.max_hp}")

                elif isinstance(obj, Wall):
                    sym = faction.symbols["wall"]
                    color = faction.colors["wall"]
                    self._draw_cell_content(cx, cy, sym, color,
                                            f"{obj.hp}/{obj.max_hp}")

                elif isinstance(obj, Unit):
                    sym = faction.symbols.get(obj.UNIT_TYPE, "⚔")
                    color = self.faction_att.colors["unit"]
                    frozen = " ❄" if obj.is_frozen else ""
                    self._draw_cell_content(cx, cy, sym, color,
                                            f"{obj.hp}/{obj.max_hp}{frozen}")

                # Etiqueta de texto sobre celdas que activaron su especial
                if (r, c) in self.special_fx_cells:
                    self.canvas.create_text(
                        cx, y0 + 9, text="✨ ESPECIAL",
                        font=("Courier New", 7, "bold"),
                        fill=C["selected"]
                    )

        # Coordenadas de bordes
        self._draw_grid_labels()
        self._refresh_side_info()

    def _draw_cell_content(self, cx, cy, symbol, color, hp_text=""):
        """Dibuja símbolo + barra de HP en una celda."""
        # Fondo de color suave
        self.canvas.create_rectangle(
            cx - 22, cy - 22, cx + 22, cy + 22,
            fill=color, outline="", stipple="gray25"
        )
        # Símbolo
        self.canvas.create_text(cx, cy - 4, text=symbol,
                                 font=FONT_CELL, fill="white")
        # HP
        if hp_text:
            self.canvas.create_text(cx, cy + 18, text=hp_text,
                                     font=FONT_MINI, fill="#CCCCCC")

    def _draw_grid_labels(self):
        """Dibuja las etiquetas de fila/columna en los bordes del canvas."""
        for c in range(GRID_COLS):
            x = c * CELL_SIZE + CELL_SIZE // 2
            self.canvas.create_text(x, 4, text=str(c),
                                     font=FONT_MINI, fill=C["text_dim"])
        for r in range(GRID_ROWS):
            y = r * CELL_SIZE + CELL_SIZE // 2
            self.canvas.create_text(4, y, text=str(r),
                                     font=FONT_MINI, fill=C["text_dim"])

    def _refresh_side_info(self):
        """Actualiza los labels del panel lateral."""
        self.lbl_money_def.config(
            text=f"💰 ${self.eco_def.money}"
        )
        self.lbl_money_att.config(
            text=f"💰 ${self.eco_att.money}"
        )
        base = self.map.base
        self.lbl_base_hp.config(
            text=f"❤ {base.hp} / {base.max_hp} HP"
        )
        self.lbl_round.config(text=f"Ronda {self.round}")
        self.lbl_score.config(
            text=f"🛡 {self.wins_def}  —  ⚔ {self.wins_att}"
        )

    # ══════════════════════════════════════════════════════════════════════════
    # INTERACCIÓN CON EL MAPA
    # ══════════════════════════════════════════════════════════════════════════

    def _on_cell_click(self, event):
        """Maneja el clic en el canvas: coloca el ítem seleccionado."""
        col = event.x // CELL_SIZE
        row = event.y // CELL_SIZE

        if not self.map.in_bounds(row, col):
            return

        if self.selected_item is None:
            self._show_cell_info(row, col)
            return

        if self.phase == "build":
            self._place_defense(row, col)
        elif self.phase == "attack":
            self._place_unit_click(row, col)

    def _on_hover(self, event):
        """Resalta la celda bajo el cursor."""
        col = event.x // CELL_SIZE
        row = event.y // CELL_SIZE
        if not self.map.in_bounds(row, col):
            return
        x0 = col * CELL_SIZE
        y0 = row * CELL_SIZE
        self.canvas.delete("hover_rect")
        self.canvas.create_rectangle(
            x0 + 1, y0 + 1, x0 + CELL_SIZE - 1, y0 + CELL_SIZE - 1,
            outline=C["selected"], width=2, tags="hover_rect"
        )

    def _show_cell_info(self, row, col):
        """Muestra info del objeto en la celda en el log."""
        obj = self.map.grid[row][col]
        if obj is None:
            self._log(f"Celda ({row},{col}): vacía")
        else:
            self._log(f"Celda ({row},{col}): {repr(obj)}")

    # ── Colocación de defensas ────────────────────────────────────────────────

    def _place_defense(self, row, col):
        """Intenta colocar el ítem seleccionado en (row, col) durante fase build."""
        if self.selected_item == "Muro":
            cost = TOWER_COSTS["Muro"]
            if not self.eco_def.can_afford(cost):
                self._log(f"Sin dinero para muro (${cost}).")
                return
            wall = Wall()
            ok, msg = self.map.place_wall(wall, row, col)
            if ok:
                self.eco_def.spend(cost)
                self._log(f"🧱 Muro colocado en ({row},{col}).")
            else:
                self._log(f"No se puede colocar muro: {msg}")
        else:
            cost = TOWER_COSTS.get(self.selected_item, 0)
            if not self.eco_def.can_afford(cost):
                self._log(f"Sin dinero para {self.selected_item} (${cost}).")
                return
            try:
                tower = create_tower(self.selected_item)
            except ValueError as e:
                self._log(str(e))
                return
            ok, msg = self.map.place_tower(tower, row, col)
            if ok:
                self.eco_def.spend(cost)
                self._log(f"🗼 {tower.name} colocada en ({row},{col}).")
            else:
                self._log(f"No se puede colocar torre: {msg}")

        self._refresh_map()

    # ── Colocación de unidades ────────────────────────────────────────────────

    def _place_unit_click(self, row, col):
        """Intenta colocar una unidad en (row, col) durante fase attack."""
        if row > 1:
            self._log("Las unidades solo se colocan en filas 0 o 1.")
            return

        cost = UNIT_COSTS.get(self.selected_item, 0)
        if not self.eco_att.can_afford(cost):
            self._log(f"Sin dinero para {self.selected_item} (${cost}).")
            return

        try:
            unit = create_unit(self.selected_item)
        except ValueError as e:
            self._log(str(e))
            return

        ok, msg = self.map.place_unit(unit, row, col)
        if ok:
            self.eco_att.spend(cost)
            self._log(f"⚔ {unit.name} colocada en ({row},{col}).")
        else:
            self._log(f"No se puede colocar unidad: {msg}")

        self._refresh_map()

    # ── Selección de ítem ─────────────────────────────────────────────────────

    def _select_item(self, key: str):
        """Marca el ítem seleccionado en la tienda y muestra su ficha completa."""
        self.selected_item = key

        # Resaltar botón activo
        for k, btn in self.shop_buttons.items():
            btn.config(bg=C["selected"] if k == key else C["cell_odd"],
                       fg=C["bg"] if k == key else C["text"])

        if self.phase == "build":
            self._show_tower_info(key)
        else:
            self._show_unit_info(key)

    def _show_tower_info(self, key: str):
        """Construye y muestra la ficha de una torre o muro."""
        if key == "Muro":
            wall = Wall()
            text = (
                f"🧱 MURO — ${wall.cost}\n"
                f"❤ HP: {wall.hp}\n"
                f"Bloquea el paso de unidades.\n"
                f"No ataca, solo absorbe daño."
            )
        else:
            tower = create_tower(key)
            text = (
                f"🗼 TORRE {key.upper()} — ${tower.cost}\n"
                f"❤ HP: {tower.hp}  ⚔ Daño: {tower.damage}  "
                f"🎯 Alcance: {tower.attack_range}\n"
                f"⏱ Especial cada {tower.special_cooldown} turnos:\n"
                f"{TOWER_SPECIAL_DESC.get(key, '—')}"
            )

        self.lbl_selected.config(text=text, fg=C["selected"])

    def _show_unit_info(self, key: str):
        """Construye y muestra la ficha de una unidad atacante."""
        unit = create_unit(key)
        text = (
            f"⚔ {key.upper()} — ${unit.cost}\n"
            f"❤ HP: {unit.hp}  ⚔ Daño: {unit.damage}  "
            f"🏃 Vel: {unit.speed}\n"
            f"⏱ Especial cada {unit.special_cooldown} turnos:\n"
            f"{UNIT_SPECIAL_DESC.get(key, '—')}"
        )
        self.lbl_selected.config(text=text, fg=C["selected"])

    # ══════════════════════════════════════════════════════════════════════════
    # FASES DEL JUEGO
    # ══════════════════════════════════════════════════════════════════════════

    def _set_phase(self, phase: str):
        """Cambia la fase y actualiza la UI."""
        self.phase = phase
        self.selected_item = None

        if phase == "build":
            self.lbl_phase.config(text="📐 FASE: Construcción del Defensor")
            self.btn_phase.config(
                text=f"✔ Defensor listo → Fase de Ataque",
                bg=C["success"]
            )
            self.lbl_selected.config(
                text=f"Turno de: {self.player_def.username}\n"
                     f"Coloca torres y muros.",
                fg=C["text_dim"]
            )
        elif phase == "attack":
            self.lbl_phase.config(text="⚔ FASE: Despliegue del Atacante")
            self.btn_phase.config(
                text=f"⚡ Atacante listo → ¡COMBATE!",
                bg=C["accent"]
            )
            self.lbl_selected.config(
                text=f"Turno de: {self.player_att.username}\n"
                     f"Coloca unidades en filas 0-1.",
                fg=C["text_dim"]
            )
        elif phase == "combat":
            self.lbl_phase.config(text="💥 FASE: Combate")
            self.btn_phase.config(text="▶ Siguiente turno", bg=C["gold"])
            self.lbl_selected.config(text="", fg=C["text_dim"])

        self._build_shop_buttons()
        self._refresh_map()

    def _advance_phase(self):
        """Botón principal: avanza entre fases."""
        if self.phase == "build":
            self._set_phase("attack")
        elif self.phase == "attack":
            self._set_phase("combat")
            self._log("=" * 28)
            self._log(f"⚔ ¡COMBATE INICIADO! Ronda {self.round}")
            self._log("=" * 28)
            self._run_combat_turn()
        elif self.phase == "combat":
            self._run_combat_turn()

    # ══════════════════════════════════════════════════════════════════════════
    # COMBATE (turno a turno)
    # ══════════════════════════════════════════════════════════════════════════

    def _run_combat_turn(self):
        """Ejecuta un turno de combate y actualiza el mapa."""
        if not self.map.units:
            self._log("No hay unidades en el campo.")
            self._check_round_end()
            return

        # 1. Torres atacan a unidades en rango.
        # Para que una sola unidad no concentre TODO el fuego de todas las
        # torres del mapa (lo que la mataba antes de avanzar), pero sin
        # eliminar la concentración de fuego por completo (que volvería
        # trivial avanzar con muchas unidades baratas), se permite que
        # como máximo 2 torres distintas compartan el mismo objetivo
        # priorizado por turno. La 3ra torre en adelante busca otra
        # amenaza viva en su rango si la hay.
        self.special_fx_cells.clear()
        target_hit_count: dict[int, int] = {}   # id(unit) -> nº de torres que ya la golpearon
        MAX_TOWERS_PER_TARGET = 2

        for tower in list(self.map.towers):
            if not tower.is_alive:
                continue
            targets = self.map.units_in_range(tower.row, tower.col, tower.attack_range)
            targets = [u for u in targets if u.is_alive]
            if not targets:
                tower.tick()
                continue

            # Preferir unidades que aún no llegaron al límite de torres
            # apuntándoles; si todas lo alcanzaron, atacar la más cercana.
            free_targets = [u for u in targets
                            if target_hit_count.get(id(u), 0) < MAX_TOWERS_PER_TARGET]
            target = free_targets[0] if free_targets else targets[0]
            target_hit_count[id(target)] = target_hit_count.get(id(target), 0) + 1

            if tower.special_ready:
                msg = tower.use_special([target], self.map.towers)
                self._log(f"✨ {msg}")
                self.special_fx_cells.add((tower.row, tower.col))
            else:
                dmg = tower.attack(target)
                self._log(f"🗼 {tower.name} → {target.name}: {dmg} dmg")
                tower.tick()

        # 2. Unidades se mueven y atacan
        for unit in list(self.map.units):
            if not unit.is_alive:
                continue

            unit.tick()

            # Revisar PRIMERO si ya hay una defensa en rango desde la
            # posición actual. Si la hay, atacar sin moverse este turno.
            # (Antes se llamaba a move_unit() incondicionalmente, lo que
            # podía desplazar a la unidad fuera de rango de un objetivo
            # que ya tenía al alcance, dejándola sin atacar ese turno.)
            defenses_before_move = self.map.defenses_in_range(unit.row, unit.col, 1)

            if defenses_before_move:
                target = defenses_before_move[0]
                if unit.special_ready:
                    msg = unit.use_special(defenses_before_move)
                    self._log(f"⚡ {msg}")
                    self.special_fx_cells.add((unit.row, unit.col))
                else:
                    dmg = unit.attack(target)
                    self.eco_att.reward_damage_tower()
                    self._log(f"⚔ {unit.name} → {target.name}: {dmg} dmg")
                continue

            result_ok, result_msg = self.map.move_unit(unit)

            if result_msg == "reached_base":
                # La unidad llegó a la base
                dmg = unit.attack(self.map.base)
                bonus = self.eco_att.reward_base_damage(dmg)
                self._log(f"💥 {unit.name} golpea la BASE: {dmg} dmg "
                           f"(+${bonus} para atacante)")
                if not self.map.base.is_alive:
                    self._end_round(winner="attacker")
                    return
            else:
                # Atacar la primera defensa en rango tras moverse
                # (cubre el caso de que el movimiento la haya acercado
                # lo suficiente como para atacar en el mismo turno).
                defenses = self.map.defenses_in_range(unit.row, unit.col, 1)
                if defenses:
                    target = defenses[0]
                    if unit.special_ready:
                        msg = unit.use_special(defenses)
                        self._log(f"⚡ {msg}")
                        self.special_fx_cells.add((unit.row, unit.col))
                    else:
                        dmg = unit.attack(target)
                        self.eco_att.reward_damage_tower()
                        self._log(f"⚔ {unit.name} → {target.name}: {dmg} dmg")

        # 3. Limpiar muertos
        removed = self.map.clean_dead()

        if removed["towers"] > 0:
            reward = self.eco_att.reward_destroy_tower() * removed["towers"]
            self._log(f"💀 {removed['towers']} torre(s) destruida(s) (+${reward} atacante)")

        if removed["walls"] > 0:
            reward = self.eco_att.reward_destroy_wall() * removed["walls"]
            self._log(f"💀 {removed['walls']} muro(s) destruido(s) (+${reward} atacante)")

        if removed["units"] > 0:
            total_reward = 0
            for dead_unit in removed["dead_units"]:
                total_reward += self.eco_def.reward_kill(dead_unit.name)
            self._log(f"☠ {removed['units']} unidad(es) eliminada(s) "
                       f"(+${total_reward} defensor)")

        self._refresh_map()
        self._check_round_end()

    def _check_round_end(self):
        """Verifica si la ronda terminó por falta de unidades o dinero del atacante."""
        alive_units = [u for u in self.map.units if u.is_alive]

        if not alive_units:
            # Sin unidades: el defensor gana la ronda
            if self.eco_att.money <= 0:
                self._log("💸 El atacante se quedó sin dinero. ¡Defensor gana la ronda!")
            else:
                self._log("🛡 Todas las unidades eliminadas. ¡Defensor gana la ronda!")
            self._end_round(winner="defender")

    def _end_round(self, winner: str):
        """Cierra la ronda, actualiza el marcador y decide si la partida termina."""
        if winner == "defender":
            self.wins_def += 1
            self._log(f"🏆 RONDA {self.round}: DEFENSOR gana ({self.wins_def} victorias)")
        else:
            self.wins_att += 1
            self._log(f"🏆 RONDA {self.round}: ATACANTE gana ({self.wins_att} victorias)")

        self._refresh_side_info()

        # ¿Alguien ganó 3 rondas?
        if self.wins_def >= 3:
            self._end_game(self.player_def, "defender")
        elif self.wins_att >= 3:
            self._end_game(self.player_att, "attacker")
        else:
            # Nueva ronda
            self.root.after(1200, self._start_new_round)

    def _start_new_round(self):
        """Prepara el mapa para la siguiente ronda."""
        self.round += 1
        self.map.reset()

        # Dar dinero de inicio de ronda
        earned_def = self.eco_def.add_round_bonus(self.round)
        earned_att = self.eco_att.add_round_bonus(self.round)

        self._log(f"── Ronda {self.round} iniciada ──")
        self._log(f"💰 Defensor recibe ${earned_def}")
        self._log(f"💰 Atacante recibe ${earned_att}")

        self._set_phase("build")

    def _end_game(self, winner: Player, role: str):
        """Muestra pantalla de fin de partida."""
        role_text = "Defensor" if role == "defender" else "Atacante"
        msg = (f"🏆 ¡{winner.username} gana la partida!\n"
               f"Rol: {role_text}\n\n"
               f"Marcador final:\n"
               f"🛡 {self.player_def.username}: {self.wins_def} rondas\n"
               f"⚔ {self.player_att.username}: {self.wins_att} rondas")

        messagebox.showinfo("¡Fin de la partida!", msg)

        if self.on_game_over:
            self.on_game_over(winner, role)

    # ══════════════════════════════════════════════════════════════════════════
    # UTILIDADES
    # ══════════════════════════════════════════════════════════════════════════

    def _log(self, msg: str):
        """Añade una línea al log de eventos."""
        self.log_lines.append(msg)
        if len(self.log_lines) > 80:
            self.log_lines = self.log_lines[-80:]

        self.log_text.config(state="normal")
        self.log_text.insert("end", msg + "\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")
