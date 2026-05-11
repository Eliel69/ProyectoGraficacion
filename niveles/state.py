# niveles/state.py
# ─────────────────────────────────────────────────────────────
# Estado global compartido para los tres niveles del juego.
# NO depende de ningún personaje específico.
# El main_arcade importa este módulo para saber en qué nivel
# está y delegarle display/keyboard/update.
# ─────────────────────────────────────────────────────────────

# ── Navegación entre niveles ──────────────────────────────────
# None   → no hay nivel activo (control en el arcade)
# 1,2,3  → nivel activo
nivel_activo = None

# Índice del personaje seleccionado en el lobby (0-5)
# El nivel lo usa para saber qué función de dibujo llamar
personaje_idx = 0

# ── Jugador 1 (WASD) ─────────────────────────────────────────
p1_x        = -2.0
p1_z        =  0.0
p1_speed    =  0.12
p1_rot      =  0.0       # rotación en Y (grados)
p1_walking  =  False
p1_anim     =  0.0       # ángulo de animación de pasos

# ── Jugador 2 (Flechas) ───────────────────────────────────────
p2_x        =  2.0
p2_z        =  0.0
p2_speed    =  0.12
p2_rot      =  180.0
p2_walking  =  False
p2_anim     =  0.0

# ── Teclas activas ────────────────────────────────────────────
# Jugador 1
k_w = False; k_s = False; k_a = False; k_d = False

# Jugador 2
k_up = False; k_down = False; k_left = False; k_right = False

# ── Cámara compartida (cenital/seguimiento) ───────────────────
cam_height   = 12.0      # altura del ojo sobre el escenario
cam_tilt     = 55.0      # ángulo de inclinación (grados desde arriba)
cam_zoom     = 45.0      # FOV

# ── Puntuaje ─────────────────────────────────────────────────
score_p1 = 0
score_p2 = 0

# ── Estado del nivel activo ───────────────────────────────────
# Se resetea cada vez que se entra a un nivel
nivel_completado = False
turno            = 1        # 1 o 2 → quién tiene la instrucción activa

# ── HUD compartido ───────────────────────────────────────────
hud_msg       = ""          # instrucción visible ("¡Toca la caja Azul!")
hud_timer     = 0           # frames restantes del mensaje
hud_feedback  = ""          # "¡Correcto!" / "¡Incorrecto!" / ""
hud_fb_timer  = 0           # frames del feedback

WIN_W = 960
WIN_H = 620
