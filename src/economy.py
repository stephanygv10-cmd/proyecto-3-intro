"""
economy.py
Gestiona el dinero de cada jugador durante la partida.
"""

# Dinero inicial por ronda
# El atacante recibe más dinero base porque atacar (romper muros + avanzar)
# es más caro por unidad que defender (un muro barato bloquea mucho HP).
INITIAL_MONEY_DEFENDER = 180
INITIAL_MONEY_ATTACKER = 200

# Dinero extra por ronda acumulada (se suma a partir de ronda 2)
ROUND_BONUS = 30

# Recompensas para el defensor al eliminar unidades
KILL_REWARD = {
    "Soldado":       15,
    "Tanque":        40,
    "Unidad Rápida": 20,
}

# Recompensas para el atacante por daño
DAMAGE_REWARD_PER_HIT  = 8    # por dañar una torre o muro
TOWER_DESTROY_REWARD   = 35   # por destruir una torre
WALL_DESTROY_REWARD    = 20   # por destruir un muro
BASE_DAMAGE_REWARD     = 1    # por cada punto de daño a la base
                               # (antes 3: con torres pesadas de 30 dmg eso
                               # daba $90 por golpe, más que el costo de la
                               # torre que lo causó. Con 1, el bono queda
                               # proporcional sin ser la fuente principal
                               # de ingresos del atacante)


class Economy:
    """
    Maneja el presupuesto de un jugador durante la partida.

    Atributos:
        money (int): Dinero disponible actualmente.
        role (str): 'defender' o 'attacker'.
    """

    def __init__(self, role: str, starting_money: int = None):
        self.role = role
        if starting_money is not None:
            self.money = starting_money
        else:
            self.money = (INITIAL_MONEY_DEFENDER if role == "defender"
                          else INITIAL_MONEY_ATTACKER)

    # ── Operaciones básicas ───────────────────────────────────────────────────

    def can_afford(self, cost: int) -> bool:
        return self.money >= cost

    def spend(self, cost: int) -> bool:
        """Descuenta dinero si hay suficiente. Retorna True si tuvo éxito."""
        if not self.can_afford(cost):
            return False
        self.money -= cost
        return True

    def earn(self, amount: int) -> None:
        """Añade dinero."""
        self.money += amount

    # ── Bonificaciones de inicio de ronda ─────────────────────────────────────

    def add_round_bonus(self, round_number: int) -> int:
        """
        Suma el dinero de inicio de ronda.
        A partir de la ronda 2 se añade un bono extra acumulativo.
        Retorna la cantidad añadida.
        """
        base = (INITIAL_MONEY_DEFENDER if self.role == "defender"
                else INITIAL_MONEY_ATTACKER)
        bonus = ROUND_BONUS * max(0, round_number - 1)
        total = base + bonus
        self.earn(total)
        return total

    # ── Recompensas del defensor ──────────────────────────────────────────────

    def reward_kill(self, unit_name: str) -> int:
        """Suma recompensa al defensor por eliminar una unidad. Retorna cantidad."""
        amount = KILL_REWARD.get(unit_name, 10)
        self.earn(amount)
        return amount

    # ── Recompensas del atacante ──────────────────────────────────────────────

    def reward_damage_tower(self) -> int:
        """Suma recompensa al atacante por dañar una torre/muro."""
        self.earn(DAMAGE_REWARD_PER_HIT)
        return DAMAGE_REWARD_PER_HIT

    def reward_destroy_tower(self) -> int:
        """Suma recompensa al atacante por destruir una torre."""
        self.earn(TOWER_DESTROY_REWARD)
        return TOWER_DESTROY_REWARD

    def reward_destroy_wall(self) -> int:
        """Suma recompensa al atacante por destruir un muro."""
        self.earn(WALL_DESTROY_REWARD)
        return WALL_DESTROY_REWARD

    def reward_base_damage(self, damage: int) -> int:
        """Suma recompensa proporcional al daño infligido a la base."""
        amount = damage * BASE_DAMAGE_REWARD
        self.earn(amount)
        return amount

    def __repr__(self):
        return f"Economy(role={self.role!r}, money={self.money})"