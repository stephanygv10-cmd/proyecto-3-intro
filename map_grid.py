"""
map_grid.py
Cuadrícula 10x10 del mapa de juego.
Gestiona la colocación de torres, muros, unidades y la base central.
"""

from src.towers import Tower, Wall
from src.units import Unit


# Tipos de celda
EMPTY   = "empty"
BASE    = "base"
TOWER   = "tower"
WALL    = "wall"
UNIT    = "unit"


class Base:
    """
    Base central del defensor. Si es destruida, el atacante gana la ronda.

    Atributos:
        hp (int): Vida actual de la base.
        max_hp (int): Vida máxima.
        row / col (int): Posición fija en el mapa.
    """

    def __init__(self, hp: int = 300, row: int = 5, col: int = 5):
        self.hp = hp
        self.max_hp = hp
        self.row = row
        self.col = col
        self.name = "Base Central"

    @property
    def is_alive(self) -> bool:
        return self.hp > 0

    def take_damage(self, amount: int) -> int:
        real = min(amount, self.hp)
        self.hp -= real
        return real

    def __repr__(self):
        return f"Base(hp={self.hp}/{self.max_hp}, pos=({self.row},{self.col}))"


class MapGrid:
    """
    Cuadrícula 10x10 que representa el campo de batalla.

    Cada celda puede contener:
        - None           → vacía
        - Base           → base central (fija)
        - Tower/Wall     → defensa colocada por el defensor
        - Unit           → unidad atacante

    La base se ubica en el centro del mapa (fila 5, columna 5 por defecto).
    Las unidades atacantes entran por la fila 0 (parte superior).
    """

    ROWS = 10
    COLS = 10
    BASE_ROW = 5
    BASE_COL = 5

    def __init__(self):
        # Matriz principal: None = vacío, o el objeto colocado
        self.grid: list[list] = [[None] * self.COLS for _ in range(self.ROWS)]

        # Listas rápidas de cada tipo de objeto en el mapa
        self.towers: list[Tower] = []
        self.walls: list[Wall]   = []
        self.units: list[Unit]   = []

        # Crear y colocar la base central
        self.base = Base(row=self.BASE_ROW, col=self.BASE_COL)
        self.grid[self.BASE_ROW][self.BASE_COL] = self.base

    # ── Consultas de celda ────────────────────────────────────────────────────

    def in_bounds(self, row: int, col: int) -> bool:
        return 0 <= row < self.ROWS and 0 <= col < self.COLS

    def is_empty(self, row: int, col: int) -> bool:
        return self.in_bounds(row, col) and self.grid[row][col] is None

    def cell_type(self, row: int, col: int) -> str:
        """Retorna el tipo de contenido de una celda."""
        if not self.in_bounds(row, col):
            return "out_of_bounds"
        obj = self.grid[row][col]
        if obj is None:
            return EMPTY
        if isinstance(obj, Base):
            return BASE
        if isinstance(obj, Tower):
            return TOWER
        if isinstance(obj, Wall):
            return WALL
        if isinstance(obj, Unit):
            return UNIT
        return EMPTY

    def get_cell(self, row: int, col: int):
        """Retorna el objeto en la celda (None si está vacía o fuera de rango)."""
        if not self.in_bounds(row, col):
            return None
        return self.grid[row][col]

    # ── Colocación de defensas ────────────────────────────────────────────────

    def place_tower(self, tower: Tower, row: int, col: int) -> tuple[bool, str]:
        """
        Coloca una torre en (row, col).
        Retorna (True, "OK") o (False, motivo).
        """
        if not self.in_bounds(row, col):
            return False, "Posición fuera del mapa."
        if not self.is_empty(row, col):
            return False, "La celda ya está ocupada."
        if row == self.BASE_ROW and col == self.BASE_COL:
            return False, "No puedes colocar una torre sobre la base."

        tower.row, tower.col = row, col
        self.grid[row][col] = tower
        self.towers.append(tower)
        return True, "OK"

    def place_wall(self, wall: Wall, row: int, col: int) -> tuple[bool, str]:
        """Coloca un muro en (row, col)."""
        if not self.in_bounds(row, col):
            return False, "Posición fuera del mapa."
        if not self.is_empty(row, col):
            return False, "La celda ya está ocupada."
        if row == self.BASE_ROW and col == self.BASE_COL:
            return False, "No puedes colocar un muro sobre la base."

        wall.row, wall.col = row, col
        self.grid[row][col] = wall
        self.walls.append(wall)
        return True, "OK"

    def place_unit(self, unit: Unit, row: int, col: int) -> tuple[bool, str]:
        """
        Coloca una unidad en (row, col).
        Las unidades sólo pueden entrar por las 2 primeras filas.
        """
        if not self.in_bounds(row, col):
            return False, "Posición fuera del mapa."
        if row > 1:
            return False, "Las unidades deben colocarse en las filas 0 o 1."
        if not self.is_empty(row, col):
            return False, "La celda ya está ocupada."

        unit.row, unit.col = row, col
        self.grid[row][col] = unit
        self.units.append(unit)
        return True, "OK"

    # ── Eliminación de objetos ────────────────────────────────────────────────

    def remove_object(self, row: int, col: int) -> None:
        """Elimina el objeto en (row, col) del mapa y de las listas."""
        obj = self.grid[row][col]
        if obj is None:
            return

        self.grid[row][col] = None

        if isinstance(obj, Tower) and obj in self.towers:
            self.towers.remove(obj)
        elif isinstance(obj, Wall) and obj in self.walls:
            self.walls.remove(obj)
        elif isinstance(obj, Unit) and obj in self.units:
            self.units.remove(obj)

    def clean_dead(self) -> dict:
        """
        Elimina del mapa todos los objetos muertos (hp <= 0).
        Retorna un resumen: {"towers": n, "walls": n, "units": n}
        """
        removed = {"towers": 0, "walls": 0, "units": 0}

        for obj_list, key in [(self.towers, "towers"),
                               (self.walls,  "walls"),
                               (self.units,  "units")]:
            dead = [o for o in obj_list if not o.is_alive]
            for obj in dead:
                self.grid[obj.row][obj.col] = None
                obj_list.remove(obj)
                removed[key] += 1

        return removed

    # ── Movimiento de unidades ────────────────────────────────────────────────

    def move_unit(self, unit: Unit) -> tuple[bool, str]:
        """
        Mueve la unidad hacia la base un número de pasos igual a unit.speed.
        Si la celda destino está bloqueada, se detiene antes.
        Retorna (True, "reached_base") si llegó a la base, (True, "moved") si se movió,
        o (False, motivo) si no pudo moverse.
        """
        if unit.is_frozen:
            return False, f"{unit.name} está congelada ({unit.frozen_turns} turno/s)."

        target_row, target_col = unit.move_towards_base(self.BASE_ROW, self.BASE_COL)

        # Calcular ruta paso a paso y detenerse ante obstáculos
        new_row, new_col = unit.row, unit.col
        steps = unit.speed

        while steps > 0:
            # Decidir dirección del siguiente paso
            dr = self.BASE_ROW - new_row
            dc = self.BASE_COL - new_col

            if dr == 0 and dc == 0:
                # Llegó a la base
                return True, "reached_base"

            next_row, next_col = new_row, new_col
            if dc != 0:
                next_col += 1 if dc > 0 else -1
            elif dr != 0:
                next_row += 1 if dr > 0 else -1

            cell = self.grid[next_row][next_col]

            if cell is None:
                # Celda libre: avanzar
                self.grid[new_row][new_col] = None
                new_row, new_col = next_row, next_col
                self.grid[new_row][new_col] = unit
            elif isinstance(cell, Base):
                # Llegó a la base
                self.grid[new_row][new_col] = None
                unit.row, unit.col = new_row, new_col
                return True, "reached_base"
            else:
                # Obstáculo (torre, muro u otra unidad): se detiene
                break

            steps -= 1

        unit.row, unit.col = new_row, new_col
        return True, "moved"

    # ── Consultas de rango ────────────────────────────────────────────────────

    def units_in_range(self, row: int, col: int, attack_range: int) -> list[Unit]:
        """Retorna las unidades vivas dentro del rango de una torre."""
        result = []
        for unit in self.units:
            if not unit.is_alive:
                continue
            dist = abs(unit.row - row) + abs(unit.col - col)  # distancia Manhattan
            if dist <= attack_range:
                result.append(unit)
        return result

    def defenses_in_range(self, row: int, col: int, attack_range: int) -> list:
        """
        Retorna torres, muros y la base dentro del rango de una unidad.
        Útil para decidir a qué atacar.
        """
        result = []
        targets = self.towers + self.walls + ([self.base] if self.base.is_alive else [])
        for obj in targets:
            dist = abs(obj.row - row) + abs(obj.col - col)
            if dist <= attack_range:
                result.append(obj)
        # Prioridad: muros primero, luego torres, luego base
        result.sort(key=lambda o: (
            0 if isinstance(o, Wall) else
            1 if isinstance(o, Tower) else 2
        ))
        return result

    # ── Reset ─────────────────────────────────────────────────────────────────

    def reset(self) -> None:
        """Limpia el mapa para iniciar una nueva ronda (mantiene la base)."""
        self.grid = [[None] * self.COLS for _ in range(self.ROWS)]
        self.towers.clear()
        self.walls.clear()
        self.units.clear()
        self.base.hp = self.base.max_hp
        self.grid[self.BASE_ROW][self.BASE_COL] = self.base

    # ── Representación de texto (debug) ──────────────────────────────────────

    def to_ascii(self) -> str:
        """Imprime el mapa como texto para debug."""
        lines = []
        for r in range(self.ROWS):
            row_str = ""
            for c in range(self.COLS):
                obj = self.grid[r][c]
                if obj is None:
                    row_str += " . "
                elif isinstance(obj, Base):
                    row_str += " B "
                elif isinstance(obj, Tower):
                    row_str += " T "
                elif isinstance(obj, Wall):
                    row_str += " W "
                elif isinstance(obj, Unit):
                    row_str += " U "
                else:
                    row_str += " ? "
            lines.append(row_str)
        return "\n".join(lines)
