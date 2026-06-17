"""
factions.py
Define las facciones disponibles en el juego.
Cada facción determina la apariencia visual de torres, muros, unidades y base.
"""


class Faction:
    """
    Representa una facción del juego.

    Atributos:
        name (str): Nombre de la facción.
        colors (dict): Paleta de colores para cada elemento del juego.
        symbols (dict): Símbolos/emojis para representar cada elemento en el mapa.
        description (str): Descripción temática de la facción.
    """

    def __init__(self, name: str, colors: dict, symbols: dict, description: str):
        self.name = name
        self.colors = colors      # {"base", "tower", "wall", "unit", "bg", "accent"}
        self.symbols = symbols    # {"base", "tower_basic", "tower_heavy", "tower_magic",
                                  #  "wall", "soldier", "tank", "fast"}
        self.description = description

    def __repr__(self):
        return f"Faction({self.name!r})"


# ── Definición de las 3 facciones ────────────────────────────────────────────

FACTIONS: dict[str, Faction] = {

    "Medieval": Faction(
        name="Medieval",
        colors={
            "base":    "#8B4513",   # marrón castillo
            "tower":   "#A0522D",   # marrón claro
            "wall":    "#696969",   # gris piedra
            "unit":    "#B8860B",   # dorado oscuro
            "bg":      "#2F1B0E",   # fondo tierra oscura
            "accent":  "#DAA520",   # dorado
            "text":    "#F5DEB3",   # trigo
        },
        symbols={
            "base":          "🏰",
            "tower_basic":   "🗼",
            "tower_heavy":   "⛩",
            "tower_magic":   "🔮",
            "wall":          "🧱",
            "soldier":       "⚔",
            "tank":          "🛡",
            "fast":          "🏹",
        },
        description="Castillos de piedra, caballeros y magia arcana."
    ),

    "Futurista": Faction(
        name="Futurista",
        colors={
            "base":    "#00BFFF",   # cian eléctrico
            "tower":   "#1E90FF",   # azul neón
            "wall":    "#4169E1",   # azul royal
            "unit":    "#00CED1",   # turquesa
            "bg":      "#0A0A1A",   # fondo espacio
            "accent":  "#00FFFF",   # cian brillante
            "text":    "#E0F7FF",   # blanco azulado
        },
        symbols={
            "base":          "🛸",
            "tower_basic":   "🤖",
            "tower_heavy":   "🔧",
            "tower_magic":   "⚡",
            "wall":          "🔷",
            "soldier":       "👾",
            "tank":          "🚀",
            "fast":          "⚡",
        },
        description="Tecnología avanzada, láseres y drones de combate."
    ),

    "Naturaleza": Faction(
        name="Naturaleza",
        colors={
            "base":    "#228B22",   # verde bosque
            "tower":   "#32CD32",   # verde lima
            "wall":    "#6B8E23",   # verde oliva
            "unit":    "#9ACD32",   # verde amarillo
            "bg":      "#0B1A0B",   # fondo selva oscura
            "accent":  "#7CFC00",   # verde césped brillante
            "text":    "#F0FFF0",   # blanco verdoso
        },
        symbols={
            "base":          "🌳",
            "tower_basic":   "🌿",
            "tower_heavy":   "🪨",
            "tower_magic":   "🍄",
            "wall":          "🌵",
            "soldier":       "🐺",
            "tank":          "🐻",
            "fast":          "🦅",
        },
        description="Criaturas del bosque, espinas y magia natural."
    ),
}


def get_faction(name: str) -> Faction:
    """Retorna la facción por nombre. Lanza KeyError si no existe."""
    if name not in FACTIONS:
        raise KeyError(f"Facción '{name}' no encontrada. Opciones: {list(FACTIONS.keys())}")
    return FACTIONS[name]


def faction_names() -> list[str]:
    """Retorna los nombres de todas las facciones disponibles."""
    return list(FACTIONS.keys())