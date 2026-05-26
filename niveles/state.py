# ============================================================
# niveles/state.py
# ------------------------------------------------------------
# PATRON BLACKBOARD: Este modulo NO contiene logica ni funciones.
# Solo almacena variables globales compartidas (el "pizarron").
# Cualquier nivel puede leer y escribir aqui sin importar
# a los otros niveles. Esto es "bajo acoplamiento":
# nivel1.py no necesita saber que existe nivel2.py.
# ============================================================

# -- Indices del personaje seleccionado en el lobby (0-5)
# main_arcade los escribe al confirmar seleccion.
# players.py los lee para saber que escala aplicar al dibujar.
personaje_idx    = 0   # Jugador 1
personaje_idx_p2 = 1   # Jugador 2

# -- Posicion y movimiento de los avatares en el escenario
# Coordenadas X/Z en el plano horizontal (Y = altura = siempre 0).
# p1_rot es el angulo de rotacion sobre Y para que el personaje
# mire hacia donde se mueve (calculado con atan2 en players.py).
p1_x       = -2.0
p1_z       =  0.0
p1_speed   =  0.12   # unidades de mundo por frame (~60fps)
p1_rot     =  0.0
p1_walking = False   # True mientras hay tecla activa -> anima la caminata
p1_anim    =  0.0    # angulo oscilante para animacion de pasos

p2_x       =  2.0
p2_z       =  0.0
p2_speed   =  0.12
p2_rot     =  180.0
p2_walking = False
p2_anim    =  0.0

# -- Banderas de teclado (True = tecla presionada ahora mismo)
# Se activan en keyboard/special_keys y se apagan en keyboard_up.
# Usar booleanos en vez de leer el teclado en cada frame evita
# perder pulsaciones rapidas (eventos asincronos de GLUT).
k_w = False; k_s = False; k_a = False; k_d = False       # J1: WASD
k_up = False; k_down = False; k_left = False; k_right = False  # J2: Flechas

# -- Puntaje ACUMULADO entre los 3 niveles
# No se resetea al cambiar de nivel, solo al volver al lobby.
# Permite mostrar el progreso total al final del nivel 3.
score_p1 = 0
score_p2 = 0

# -- Puntaje del nivel actual (se resetea en cada _reset_nivel)
# Separar puntaje parcial del global permite mostrar ambos en el HUD.
nivel_score_p1 = 0
nivel_score_p2 = 0

# -- Meta de puntos para completar un nivel
# Al llegar a META_PUNTOS se activa nivel_completado = True.
META_PUNTOS = 20

# -- Flags de control del flujo del nivel
nivel_completado  = False   # True -> congela el juego, activa pantalla de resultado
nivel_ganador     = 0       # 1 o 2: quien llego primero a META_PUNTOS
mostrar_resultado = False   # True -> muestra pantalla de resultado en el HUD
resultado_timer   = 0       # Cuenta regresiva en frames antes de avanzar al sig nivel
                            # Se decrementa en update() de cada nivel

# -- Mensajes del HUD (actualizados por cada nivel segun la instruccion activa)
hud_msg   = ""   # Instruccion visible para J1 (ej. "J1: Toca el cubo Rojo!")
hud_msg2  = ""   # Instruccion independiente para J2
hud_fb_p1 = ""   # Feedback inmediato J1 (ej. "Correcto! +2" o "Ups! -1")
hud_fb_p2 = ""   # Feedback inmediato J2
hud_fb_timer_p1 = 0   # Frames que permanece visible el feedback de J1
hud_fb_timer_p2 = 0   # Frames que permanece visible el feedback de J2

# -- Dimensiones de la ventana (se actualiza en reshape_maestro)
WIN_W = 960
WIN_H = 620
