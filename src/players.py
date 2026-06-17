"""
players.py
Modelo de jugador y gestor de datos (lectura/escritura de players.json).
"""

import json
import os

PLAYERS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "players.json")


class Player:
    """
    Representa a un jugador registrado en el sistema.

    Atributos:
        username (str): Nombre de usuario único.
        password (str): Contraseña del jugador.
        wins_defender (int): Victorias obtenidas como defensor.
        wins_attacker (int): Victorias obtenidas como atacante.
    """

    def __init__(self, username: str, password: str,
                 wins_defender: int = 0, wins_attacker: int = 0):
        self.username = username
        self.password = password
        self.wins_defender = wins_defender
        self.wins_attacker = wins_attacker

    def to_dict(self) -> dict:
        """Convierte el jugador a diccionario para guardarlo en JSON."""
        return {
            "username": self.username,
            "password": self.password,
            "wins_defender": self.wins_defender,
            "wins_attacker": self.wins_attacker,
        }

    @staticmethod
    def from_dict(data: dict) -> "Player":
        """Crea un Player a partir de un diccionario leído del JSON."""
        return Player(
            username=data["username"],
            password=data["password"],
            wins_defender=data.get("wins_defender", 0),
            wins_attacker=data.get("wins_attacker", 0),
        )

    def __repr__(self):
        return (f"Player(username={self.username!r}, "
                f"def_wins={self.wins_defender}, att_wins={self.wins_attacker})")


# ── Funciones de acceso a datos ──────────────────────────────────────────────

def _load_all() -> dict[str, dict]:
    """
    Carga el archivo players.json y devuelve un dict {username: datos}.
    Si el archivo no existe, retorna un dict vacío.
    """
    if not os.path.exists(PLAYERS_FILE):
        return {}
    with open(PLAYERS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def _save_all(data: dict[str, dict]) -> None:
    """Guarda el dict completo de jugadores en players.json."""
    os.makedirs(os.path.dirname(PLAYERS_FILE), exist_ok=True)
    with open(PLAYERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def register_player(username: str, password: str) -> tuple[bool, str]:
    """
    Registra un nuevo jugador.

    Retorna:
        (True, "OK")               si el registro fue exitoso.
        (False, mensaje de error)  si el usuario ya existe o los datos son inválidos.
    """
    username = username.strip()
    password = password.strip()

    if not username or not password:
        return False, "El usuario y la contraseña no pueden estar vacíos."

    if len(username) < 3:
        return False, "El nombre de usuario debe tener al menos 3 caracteres."

    if len(password) < 4:
        return False, "La contraseña debe tener al menos 4 caracteres."

    data = _load_all()

    if username in data:
        return False, f"El usuario '{username}' ya existe."

    player = Player(username, password)
    data[username] = player.to_dict()
    _save_all(data)
    return True, "OK"


def login_player(username: str, password: str) -> tuple[bool, str | Player]:
    """
    Valida las credenciales de un jugador.

    Retorna:
        (True, Player)             si las credenciales son correctas.
        (False, mensaje de error)  si el usuario no existe o la contraseña es incorrecta.
    """
    username = username.strip()
    password = password.strip()

    data = _load_all()

    if username not in data:
        return False, f"El usuario '{username}' no existe."

    stored = data[username]
    if stored["password"] != password:
        return False, "Contraseña incorrecta."

    return True, Player.from_dict(stored)


def update_wins(username: str, role: str) -> None:
    """
    Incrementa en 1 las victorias del jugador según el rol ('defender' o 'attacker').

    Args:
        username (str): Nombre del jugador a actualizar.
        role (str): 'defender' o 'attacker'.
    """
    data = _load_all()
    if username not in data:
        return

    if role == "defender":
        data[username]["wins_defender"] += 1
    elif role == "attacker":
        data[username]["wins_attacker"] += 1

    _save_all(data)


def get_top_players(role: str, top_n: int = 5) -> list[Player]:
    """
    Retorna los top N jugadores ordenados por victorias en el rol indicado.

    Args:
        role (str): 'defender' o 'attacker'.
        top_n (int): Cantidad de jugadores a retornar (por defecto 5).
    """
    data = _load_all()
    players = [Player.from_dict(v) for v in data.values()]

    key = "wins_defender" if role == "defender" else "wins_attacker"
    players.sort(key=lambda p: getattr(p, key), reverse=True)

    return players[:top_n]