# actions/state.py
# ── Posición y estado del personaje ─────────────────────────────────────────
char_x, char_y, char_z = 0.0, 0.0, 0.0
char_speed  = 0.15
char_color  = [0.4, 0.85, 0.88]
char_rotation = 0.0

# Alias usados en main.py
guy_x = char_x
guy_z = char_z

# ── Animación y movimiento ───────────────────────────────────────────────────
current_motion = "idle"
motion_timer  = 0
motion_cycle  = 0.0

arm_L_pitch, arm_R_pitch = 0.0, 0.0
arm_L_roll,  arm_R_roll  = 0.0, 0.0
leg_L_pitch, leg_R_pitch = 0.0, 0.0
body_scale_y = 1.0

# ── Expresiones ─────────────────────────────────────────────────────────────
current_expression = "neutral"
current_scene = "arcoiris"
current_motion = "idle"

show_instructions = False
show_about = False
char_color = [0.4, 0.85, 0.88]

char_rotation = 0
body_scale_y = 1.0

arm_L_pitch = 0
arm_R_pitch = 0
leg_L_pitch = 0
leg_R_pitch = 0
# ── Cámara ───────────────────────────────────────────────────────────────────
cam_radius   = 8.0
cam_yaw      = 0.0
cam_pitch    = 20.0
cam_target_y = 1.0

# ── Interfaz ─────────────────────────────────────────────────────────────────
show_info         = False
show_instructions = False
sound_enabled     = True
current_scene     = 1
prev_scene        = 1

# ── Objetos de colisión ──────────────────────────────────────────────────────
# Posiciones x,z — la y se ignora, los objetos se colocan sobre el plano en scenes.py
collision_objects = [
    {"id": 1, "pos": ( 3.5, 0.0,  2.5), "hit": False,
     "type": "cubo",   "color": (0.9, 0.30, 0.10),
     "effect_motion": "saltar",  "effect_expr": "miedo"},
    {"id": 2, "pos": (-3.5, 0.0, -2.5), "hit": False,
     "type": "esfera", "color": (0.20, 0.55, 0.95),
     "effect_motion": "bailar",  "effect_expr": "felicidad"},
    {"id": 3, "pos": ( 0.0, 0.0, -4.5), "hit": False,
     "type": "cono",   "color": (0.10, 0.85, 0.30),
     "effect_motion": "saludar", "effect_expr": "admiracion"},
]

_last_sound_motion = ""
