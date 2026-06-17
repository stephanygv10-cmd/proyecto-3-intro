"""
units.py
Define la clase base Unit y sus tres subtipos con habilidades especiales.
"""


class Unit:
    """
    Clase base para todas las unidades atacantes.

    Atributos:
        name (str): Nombre de la unidad.
        cost (int): Costo en dinero para comprarla.
        hp (int): Puntos de vida actuales.
        max_hp (int): Puntos de vida máximos.
        damage (int): Daño por ataque normal.
        speed (int): Casillas que avanza por turno.
        special_cooldown (int): Turnos entre activaciones de habilidad especial.
        special_timer (int): Contador interno de turnos.
        frozen_turns (int): Turnos de parálisis restantes (por magia, etc.).
        row / col (int): Posición actual en el mapa.
    """

    def __init__(self, name: str, cost: int, hp: int,
                 damage: int, speed: int, special_cooldown: int):
        self.name = name
        self.cost = cost
        self.hp = hp
        self.max_hp = hp
        self.damage = damage
        self.speed = speed
        self.special_cooldown = special_cooldown
        self.special_timer = 0
        self.frozen_turns = 0   # turnos congelada por torre mágica
        self.row = -1
        self.col = -1

    # ── Propiedades ──────────────────────────────────────────────────────────

    @property
    def is_alive(self) -> bool:
        return self.hp > 0

    @property
    def is_frozen(self) -> bool:
        return self.frozen_turns > 0

    @property
    def special_ready(self) -> bool:
        return self.special_timer >= self.special_cooldown

    # ── Métodos generales ────────────────────────────────────────────────────

    def take_damage(self, amount: int) -> int:
        """Aplica daño. Retorna daño real recibido."""
        real = min(amount, self.hp)
        self.hp -= real
        return real

    def heal(self, amount: int) -> int:
        """Cura la unidad sin superar max_hp. Retorna cantidad curada."""
        real = min(amount, self.max_hp - self.hp)
        self.hp += real
        return real

    def attack(self, target) -> int:
        """Ataca a un objetivo (torre, muro o base). Retorna daño infligido."""
        return target.take_damage(self.damage)

    def tick(self):
        """
        Avanza el temporizador de habilidad especial.
        Descuenta un turno de parálisis si está congelada.
        """
        if self.frozen_turns > 0:
            self.frozen_turns -= 1
            return  # no acumula especial mientras está congelada

        if self.special_timer < self.special_cooldown:
            self.special_timer += 1

    def move_towards_base(self, base_row: int, base_col: int) -> tuple[int, int]:
        """
        Calcula la nueva posición moviéndose hacia la base enemy.
        Avanza 'speed' casillas en dirección a (base_row, base_col).
        Retorna (new_row, new_col) sin modificar el estado interno.
        El MapGrid es quien valida y aplica el movimiento.
        """
        dr = base_row - self.row
        dc = base_col - self.col

        steps = self.speed
        new_row, new_col = self.row, self.col

        # Moverse primero horizontalmente, luego verticalmente (pathfinding simple)
        while steps > 0:
            if dc != 0:
                new_col += 1 if dc > 0 else -1
                dc = base_col - new_col
            elif dr != 0:
                new_row += 1 if dr > 0 else -1
                dr = base_row - new_row
            else:
                break
            steps -= 1

        return new_row, new_col

    def use_special(self, targets: list, allies: list = None) -> str:
        """
        Activa la habilidad especial. Debe sobreescribirse en cada subclase.

        Args:
            targets: Torres/muros/base en rango de ataque.
            allies: Otras unidades aliadas en el mapa.
        """
        raise NotImplementedError("Cada subclase debe implementar use_special().")

    def info(self) -> dict:
        return {
            "name": self.name,
            "cost": self.cost,
            "hp": f"{self.hp}/{self.max_hp}",
            "damage": self.damage,
            "speed": self.speed,
            "special_cooldown": self.special_cooldown,
            "special_ready": self.special_ready,
            "frozen": self.frozen_turns,
        }

    def __repr__(self):
        return (f"{self.__class__.__name__}(hp={self.hp}/{self.max_hp}, "
                f"dmg={self.damage}, spd={self.speed})")


# ── Subclases de Unidad ───────────────────────────────────────────────────────

class Soldier(Unit):
    """
    Soldado: bajo costo, estadísticas normales.
    Habilidad especial: Ataque doble — ataca dos veces al mismo objetivo.
    Cooldown: cada 3 turnos.
    """

    UNIT_TYPE = "soldier"

    def __init__(self):
        super().__init__(
            name="Soldado",
            cost=40,
            hp=60,
            damage=12,
            speed=2,
            special_cooldown=3,
        )

    def use_special(self, targets: list, allies: list = None) -> str:
        """Ataque doble: golpea al primer objetivo dos veces."""
        if not targets:
            self.special_timer = 0
            return f"{self.name}: ataque doble sin objetivo."

        target = targets[0]
        dmg1 = target.take_damage(self.damage)
        dmg2 = target.take_damage(self.damage)
        self.special_timer = 0
        return (f"{self.name} ¡ATAQUE DOBLE! "
                f"→ {target.name} recibe {dmg1 + dmg2} dmg total.")


class Tank(Unit):
    """
    Tanque: mucha vida, movimiento lento.
    Habilidad especial: Escudo temporal — reduce daño recibido a la mitad por 2 turnos.
    Cooldown: cada 5 turnos.
    """

    UNIT_TYPE = "tank"

    def __init__(self):
        super().__init__(
            name="Tanque",
            cost=100,
            hp=200,
            damage=25,
            speed=1,
            special_cooldown=5,
        )
        self.shield_turns = 0   # turnos con escudo activo

    def take_damage(self, amount: int) -> int:
        """Aplica escudo si está activo (reduce daño a la mitad)."""
        if self.shield_turns > 0:
            amount = amount // 2
        return super().take_damage(amount)

    def tick(self):
        """Descuenta turnos de escudo además del tick normal."""
        if self.shield_turns > 0:
            self.shield_turns -= 1
        super().tick()

    def use_special(self, targets: list, allies: list = None) -> str:
        """Escudo temporal: activa protección por 2 turnos."""
        self.shield_turns = 2
        self.special_timer = 0
        return f"{self.name} ¡ESCUDO ACTIVADO! → daño reducido 2 turnos."


class FastUnit(Unit):
    """
    Unidad rápida: poco daño, pero se mueve más rápido.
    Habilidad especial: Ráfaga de velocidad — duplica speed por 1 turno.
    Cooldown: cada 3 turnos.
    """

    UNIT_TYPE = "fast"

    def __init__(self):
        super().__init__(
            name="Unidad Rápida",
            cost=60,
            hp=40,
            damage=8,
            speed=3,
            special_cooldown=3,
        )
        self.speed_boost_turns = 0

    def tick(self):
        """Decrementa el boost de velocidad y llama al tick base."""
        if self.speed_boost_turns > 0:
            self.speed_boost_turns -= 1
            if self.speed_boost_turns == 0:
                self.speed = 3   # restaura velocidad normal
        super().tick()

    def use_special(self, targets: list, allies: list = None) -> str:
        """Ráfaga de velocidad: duplica la velocidad de movimiento por 1 turno."""
        self.speed = 6
        self.speed_boost_turns = 1
        self.special_timer = 0
        return f"{self.name} ¡RÁFAGA! → velocidad x2 este turno."


# ── Catálogo y fábrica ────────────────────────────────────────────────────────

UNIT_CATALOG: dict[str, type] = {
    "Soldado":        Soldier,
    "Tanque":         Tank,
    "Unidad Rápida":  FastUnit,
}

UNIT_COSTS: dict[str, int] = {
    "Soldado":        Soldier().cost,
    "Tanque":         Tank().cost,
    "Unidad Rápida":  FastUnit().cost,
}


def create_unit(unit_type: str) -> Unit:
    """Crea una nueva instancia de unidad por nombre."""
    if unit_type not in UNIT_CATALOG:
        raise ValueError(f"Tipo de unidad inválido: {unit_type!r}. "
                         f"Opciones: {list(UNIT_CATALOG.keys())}")
    return UNIT_CATALOG[unit_type]()