⚔ Defensa y Asalto de Base

Juego de estrategia por turnos para dos jugadores, desarrollado en Python con Tkinter.

Curso: Introducción a la Programación (Modalidad Live Learning)
Repositorio: https://github.com/stephanygv10-cmd/proyecto-3-intro

Descripción

Un jugador asume el rol de defensor y construye una base con muros y torres, mientras el otro asume el rol de atacante y debe destruirla usando distintas unidades. El juego se desarrolla por rondas; el primero en ganar 3 rondas gana la partida.

Requisitos

- Python 3.10 o superior
- Tkinter (incluido en la instalación estándar de Python)
- No requiere instalar librerías externas para ejecutarse

Instalación:

1.Descargar o clonar el repositorio:
  bash
  git clone https://github.com/stephanygv10-cmd/proyecto-3-intro.git
   
2.Abrí una terminal dentro de la carpeta del proyecto.

Ejecución:

bash
python main.py


Importante: ejecutar siempre desde la carpeta raíz del proyecto (donde está `main.py`), o las importaciones de src y ui van a fallar.

Estructura del proyecto


Proyecto-3-intro/
├── main.py                       # Punto de entrada del juego
├── README.md
├── manual_usuario.md
├── data/
│   └── players.json              # Base de datos de jugadores (se crea sola)
├── src/
│   ├── __init__.py
│   ├── players.py                # Clase Player + registro/login/ranking
│   ├── towers.py                 # Clases de torres (Básica, Pesada, Mágica) y Muro
│   ├── units.py                  # Clases de unidades (Soldado, Tanque, Unidad Rápida)
│   ├── map_grid.py                # Cuadrícula 10x10, base central y movimiento
│   ├── factions.py               # Facciones: Medieval, Futurista, Naturaleza
│   └── economy.py                # Dinero inicial, bonos por ronda y recompensas
└── ui/
    ├── __init__.py
    ├── login_window.py           # Pantalla de inicio de sesión y registro
    ├── faction_window.py         # Selección de facción de cada jugador
    ├── game_window.py            # Mapa, tienda, combate y fases de la ronda
    └── ranking_window.py         # Top 5 defensores y top 5 atacantes


Flujo del juego

1. Ambos jugadores inician sesión o se registran.
2. Cada jugador elige una facción distinta (Medieval, Futurista o Naturaleza).
3. El Jugador 1 es el defensor y el Jugador 2 es el atacante.
4. Por ronda: fase de construcción → fase de despliegue → fase de combate.
5. El primero en ganar 3 rondas gana la partida, y sus victorias quedan registradas para el ranking.

Documentación adicional

- [manual_usuario.md](manual_usuario.md): instrucciones detalladas de uso, costos de torres/unidades y condiciones de victoria.
