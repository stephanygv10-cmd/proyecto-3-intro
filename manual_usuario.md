# Manual de Usuario — Defensa y Asalto de Base

## 1. Inicio del programa

Ejecutá `python main.py` desde la carpeta raíz del proyecto.

---

## 2. Pantalla de Login / Registro

Al abrir el juego verás la pantalla de autenticación.

**Registrarse (primera vez):**
1. Escribí un nombre de usuario (mínimo 3 caracteres).
2. Escribí una contraseña (mínimo 4 caracteres).
3. Presioná **Registrarse**.

**Iniciar sesión:**
1. Escribí tu usuario y contraseña.
2. Presioná **Iniciar sesión** o la tecla Enter.

El juego pedirá primero al **Jugador 1** y luego al **Jugador 2**.
Ambos jugadores deben ser cuentas distintas.

> Desde esta pantalla también podés consultar el **Ranking** con el botón 🏆.

---

## 3. Selección de Facción

Cada jugador elige una de las **3 facciones disponibles**:

| Facción    | Estilo              | Base | Unidades         |
|------------|---------------------|------|------------------|
| Medieval   | Castillos y magia   | 🏰   | ⚔ 🛡 🏹         |
| Futurista  | Tecnología y lásers | 🛸   | 👾 🚀 ⚡         |
| Naturaleza | Bosque y criaturas  | 🌳   | 🐺 🐻 🦅         |

- El **Jugador 1 elige primero**.
- El **Jugador 2 no puede elegir la misma** facción que el Jugador 1.
- La facción solo afecta la apariencia visual.

---

## 4. Pantalla de Juego

### Mapa
- Cuadrícula de **10×10 casillas**.
- La **Base Central (B)** está fija en el centro del mapa.
- Las unidades atacantes entran por las **filas 0 y 1** (parte superior).

### Panel lateral
- Muestra el dinero de cada jugador.
- Muestra los HP de la base central.
- Contiene la **tienda** y el **log de eventos**.

---

## 5. Fase de Construcción (Defensor)

Es el turno del **Jugador 1 (Defensor)**.

1. Seleccioná un ítem de la tienda (torre o muro).
2. Hacé clic en una casilla vacía del mapa para colocarlo.
3. Cuando termines, presioná **"Defensor listo → Fase de Ataque"**.

### Torres disponibles

| Torre        | Costo | HP  | Daño | Alcance | Habilidad especial            |
|--------------|-------|-----|------|---------|-------------------------------|
| Torre Básica | $50   | 80  | 15   | 3       | Disparo doble (cada 3 turnos) |
| Torre Pesada | $120  | 200 | 30   | 2       | Daño en área (cada 5 turnos)  |
| Torre Mágica | $90   | 100 | 10   | 4       | Congelar unidad (cada 4 turnos)|
| Muro         | $20   | 60  | —    | —       | Bloquea el paso               |

---

## 6. Fase de Ataque (Atacante)

Es el turno del **Jugador 2 (Atacante)**.

1. Seleccioná una unidad de la tienda.
2. Hacé clic en las **filas 0 o 1** del mapa para colocarla.
3. Cuando termines, presioná **"Atacante listo → ¡COMBATE!"**.

### Unidades disponibles

| Unidad        | Costo | HP  | Daño | Velocidad | Habilidad especial              |
|---------------|-------|-----|------|-----------|---------------------------------|
| Soldado       | $40   | 60  | 12   | 2         | Ataque doble (cada 3 turnos)    |
| Tanque        | $100  | 200 | 25   | 1         | Escudo temporal (cada 5 turnos) |
| Unidad Rápida | $60   | 40  | 8    | 3         | Ráfaga de velocidad (cada 3 t.) |

---

## 7. Fase de Combate

Presioná **"▶ Siguiente turno"** para avanzar turno a turno.

En cada turno:
1. Las **torres atacan** a las unidades más cercanas dentro de su alcance.
2. Las **unidades se mueven** hacia la base (según su velocidad).
3. Si una unidad llega a la base, la **ataca directamente**.
4. Los objetos con HP = 0 son eliminados del mapa.

El log de eventos a la derecha muestra cada acción en detalle.

---

## 8. Condiciones de victoria por ronda

**El Defensor gana la ronda si:**
- Todas las unidades atacantes son eliminadas.
- El atacante se queda sin dinero para comprar más unidades.

**El Atacante gana la ronda si:**
- Logra destruir la base central (HP = 0).

**El primero en ganar 3 rondas gana la partida.**

---

## 9. Sistema de dinero

| Evento                          | Quién cobra  | Cantidad     |
|---------------------------------|--------------|--------------|
| Inicio de cada ronda            | Ambos        | $200 / $180  |
| Bono por ronda adicional        | Ambos        | +$30/ronda   |
| Eliminar una unidad             | Defensor     | $15–$40      |
| Dañar una torre/muro            | Atacante     | $5           |
| Destruir una torre              | Atacante     | $25          |
| Destruir un muro                | Atacante     | $10          |
| Daño a la base                  | Atacante     | $2 por punto |

---

## 10. Ranking

Desde la pantalla de login podés ver el **Top 5** de jugadores con más victorias como defensor y como atacante.

Las victorias se actualizan automáticamente al terminar cada partida.

---

## 11. Solución de problemas

| Problema                        | Solución                                      |
|---------------------------------|-----------------------------------------------|
| La ventana no abre              | Verificá que Python 3.10+ esté instalado      |
| Error de importación            | Ejecutá desde la carpeta raíz (`python main.py`) |
| No recuerdo mi contraseña       | No hay recuperación; creá una cuenta nueva    |
| El mapa no responde al clic     | Primero seleccioná un ítem de la tienda       |
