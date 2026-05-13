# niveles/state.py
# Estado global compartido para todos los niveles.

# -- Personajes seleccionados
personaje_idx    = 0
personaje_idx_p2 = 1

# -- Posicion / movimiento jugadores
p1_x       = -2.0
p1_z       =  0.0
p1_speed   =  0.12
p1_rot     =  0.0
p1_walking = False
p1_anim    =  0.0

p2_x       =  2.0
p2_z       =  0.0
p2_speed   =  0.12
p2_rot     =  180.0
p2_walking = False
p2_anim    =  0.0

# -- Teclas
k_w = False; k_s = False; k_a = False; k_d = False
k_up = False; k_down = False; k_left = False; k_right = False

# -- Puntaje ACUMULADO (persiste entre niveles)
score_p1 = 0
score_p2 = 0

# -- Puntaje del nivel actual (se resetea al iniciar cada nivel)
nivel_score_p1 = 0
nivel_score_p2 = 0

# -- Meta de puntos para completar un nivel
META_PUNTOS = 20

# -- Estado del nivel
nivel_completado  = False   # True cuando alguien llega a META_PUNTOS
nivel_ganador     = 0       # 1 o 2
mostrar_resultado = False   # pantalla de fin de nivel activa
resultado_timer   = 0       # frames hasta pasar al siguiente nivel

# -- HUD por jugador
hud_msg          = ""
hud_msg2         = ""
hud_fb_p1        = ""
hud_fb_p2        = ""
hud_fb_timer_p1  = 0
hud_fb_timer_p2  = 0

WIN_W = 960
WIN_H = 620
