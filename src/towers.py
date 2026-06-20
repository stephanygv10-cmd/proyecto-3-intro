"""
towers.py
Define la clase base Tower y sus tres subtipos con habilidades especiales.
"""


class Tower:
    """
    Clase base para todas las torres defensivas.

    Atributos:
        name (str): Nombre de la torre.
        cost (int): Costo en dinero para construirla.
        hp (int): Puntos de vida actuales.
        max_hp (int): Puntos de vida máximos.
        damage (int): Daño por ataque normal.
        attack_range (int): Alcance en casillas.
        special_cooldown (int): Turnos necesarios para activar habilidad especial.
        special_timer (int): Contador interno de turnos desde el último especial.
        row (int): Fila en el mapa (asignada al colocarla).
        col (int): Columna en el mapa (asignada al colocarla).
    """

    def __init__(self, name: str, cost: int, hp: int,
                 damage: int, attack_range: int, special_cooldown: int):
        self.name = name
        self.cost = cost
        self.hp = hp
        self.max_hp = hp
        self.damage = damage
        self.attack_range = attack_range
        self.special_cooldown = special_cooldown
        self.special_timer = 0      # aumenta cada turno; al llegar al cooldown activa especial
        self.row = -1
        self.col = -1

    # ── Propiedades ──────────────────────────────────────────────────────────

    @property
    def is_alive(self) -> bool:
        return self.hp > 0

    @property
    def special_ready(self) -> bool:
        """True si la habilidad especial está disponible este turno."""
        return self.special_timer >= self.special_cooldown

    # ── Métodos generales ────────────────────────────────────────────────────

    def take_damage(self, amount: int) -> int:
        """
        Aplica daño a la torre.
        Retorna el daño real recibido (no puede ser negativo).
        """
        real = min(amount, self.hp)
        self.hp -= real
        return real

    def repair(self, amount: int) -> int:
        """
        Repara la torre (no supera max_hp).
        Retorna la cantidad real curada.
        """
        real = min(amount, self.max_hp - self.hp)
        self.hp += real
        return real

    def attack(self, target) -> int:
        """
        Ataca a un objetivo (unidad o base).
        Retorna el daño infligido.
        """
        return target.take_damage(self.damage)

    def tick(self):
        """Avanza el temporizador de habilidad especial un turno."""
        if self.special_timer < self.special_cooldown:
            self.special_timer += 1

    def use_special(self, targets: list, all_towers: list = None) -> str:
        """
        Activa la habilidad especial de la torre.
        Debe ser sobreescrito en cada subclase.

        Args:
            targets: Lista de unidades en rango (para efectos de daño/debuff).
            all_towers: Lista de torres aliadas (para efectos de soporte).

        Retorna:
            Descripción del efecto activado (para mostrar en la UI).
        """
        raise NotImplementedError("Cada subclase debe implementar use_special().")

    def info(self) -> dict:
        """Retorna un dict con los atributos principales de la torre."""
        return {
            "name": self.name,
            "cost": self.cost,
            "hp": f"{self.hp}/{self.max_hp}",
            "damage": self.damage,
            "range": self.attack_range,
            "special_cooldown": self.special_cooldown,
            "special_ready": self.special_ready,
        }

    def __repr__(self):
        return (f"{self.__class__.__name__}(hp={self.hp}/{self.max_hp}, "
                f"dmg={self.damage}, range={self.attack_range})")


# ── Subclases de Torre ────────────────────────────────────────────────────────

class BasicTower(Tower):
    """
    Torre básica: bajo costo, estadísticas normales.
    Habilidad especial: Disparo doble — ataca dos veces en el mismo turno.
    Cooldown: cada 3 turnos.
    """

    TOWER_TYPE = "tower_basic"

    def __init__(self):
        super().__init__(
            name="Torre Básica",
            cost=50,
            hp=80,
            damage=15,
            attack_range=3,
            special_cooldown=3,
        )

    def use_special(self, targets: list, all_towers: list = None) -> str:
        """Disparo doble: ataca al primer objetivo dos veces."""
        if not targets:
            self.special_timer = 0
            return f"{self.name}: disparo doble, pero no hay objetivos."

        target = targets[0]
        dmg1 = target.take_damage(self.damage)
        dmg2 = target.take_damage(self.damage)
        self.special_timer = 0
        return (f"{self.name} ¡DISPARO DOBLE! "
                f"→ {target.name} recibe {dmg1 + dmg2} dmg total.")


class HeavyTower(Tower):
    """
    Torre pesada: mucha vida y daño alto, pero costo elevado.
    Habilidad especial: Daño en área — daña a todas las unidades en rango.
    Cooldown: cada 5 turnos.
    """

    TOWER_TYPE = "tower_heavy"

    def __init__(self):
        super().__init__(
            name="Torre Pesada",
            cost=120,
            hp=200,
            damage=30,
            attack_range=2,
            special_cooldown=5,
        )

    def use_special(self, targets: list, all_towers: list = None) -> str:
        """Daño en área: inflige daño a todas las unidades en rango."""
        if not targets:
            self.special_timer = 0
            return f"{self.name}: área sin objetivos."

        total = 0
        names = []
        for unit in targets:
            total += unit.take_damage(self.damage)
            names.append(unit.name)
        self.special_timer = 0
        return (f"{self.name} ¡DAÑO EN ÁREA! "
                f"→ golpea a {', '.join(names)} por {self.damage} c/u. "
                f"Total: {total} dmg.")


class MagicTower(Tower):
    """
    Torre mágica: daño bajo, pero habilidad especial fuerte.
    Habilidad especial: Congelar — paraliza a la primera unidad 1 turno extra.
    Cooldown: cada 4 turnos.
    """

    TOWER_TYPE = "tower_magic"

    def __init__(self):
        super().__init__(
            name="Torre Mágica",
            cost=90,
            hp=100,
            damage=10,
            attack_range=4,
            special_cooldown=4,
        )

    def use_special(self, targets: list, all_towers: list = None) -> str:
        """Congelar: aplica el estado 'frozen' al primer objetivo en rango."""
        if not targets:
            self.special_timer = 0
            return f"{self.name}: congelación sin objetivos."

        target = targets[0]
        target.frozen_turns = getattr(target, "frozen_turns", 0) + 1
        self.special_timer = 0
        return (f"{self.name} ¡CONGELACIÓN! "
                f"→ {target.name} queda paralizado 1 turno.")


# ── Muro ──────────────────────────────────────────────────────────────────────

class Wall:
    """
    Muro defensivo: bloquea el paso de unidades enemigas.
    No ataca, solo absorbe daño.
    """

    def __init__(self):
        self.name = "Muro"
        self.cost = 30
        self.hp = 50
        self.max_hp = 50
        self.row = -1
        self.col = -1

    @property
    def is_alive(self) -> bool:
        return self.hp > 0

    def take_damage(self, amount: int) -> int:
        real = min(amount, self.hp)
        self.hp -= real
        return real

    def __repr__(self):
        return f"Wall(hp={self.hp}/{self.max_hp})"


# ── Fábrica ───────────────────────────────────────────────────────────────────

TOWER_CATALOG: dict[str, type] = {
    "Básica":  BasicTower,
    "Pesada":  HeavyTower,
    "Mágica":  MagicTower,
}

TOWER_COSTS: dict[str, int] = {
    "Básica":  BasicTower().cost,
    "Pesada":  HeavyTower().cost,
    "Mágica":  MagicTower().cost,
    "Muro":    Wall().cost,
}

# Descripción corta de la habilidad especial de cada torre, usada en la UI
# para mostrarle al jugador qué hace antes de comprarla.
TOWER_SPECIAL_DESC: dict[str, str] = {
    "Básica": "Disparo doble: ataca 2 veces al mismo objetivo.",
    "Pesada": "Daño en área: golpea a todas las unidades en rango.",
    "Mágica": "Congelar: paraliza a una unidad 1 turno extra.",
    "Muro":   "Sin habilidad. Solo bloquea el paso y absorbe daño.",
}


def create_tower(tower_type: str) -> Tower:
    """Crea una nueva instancia de torre por nombre ('Básica', 'Pesada', 'Mágica')."""
    if tower_type not in TOWER_CATALOG:
        raise ValueError(f"Tipo de torre inválido: {tower_type!r}. "
                         f"Opciones: {list(TOWER_CATALOG.keys())}")
    return TOWER_CATALOG[tower_type]()
