# actions/state.py

zoom = 45.0
show_instructions = False
show_about = False

camera_follow = True

fox_x = 0.0  # Usaremos las variables originales del zorro para no romper dependencias
fox_z = 0.0
fox_speed = 0.1 # Velocidad de desplazamiento

rotate_x = 0.0
rotate_y = 0.0

#escenarios
current_escenario=1

# Teclas
key_up = False
key_down = False
key_left = False
key_right = False

mouse_down = False
last_mouse_x = 0
last_mouse_y = 0

# --- NUEVAS VARIABLES PARA EXPRESIONES Y MOVIMIENTOS ---
walking = False
animation_angle = 0.0

shaking = False
shake_timer = 0.0

# "neutral", "angry", "suspicious", "sad", "surprised"
expression = 0 

# None, "jump", "spin", "shake", "vent"
reaction_type = None   
reaction_timer = 0
reaction_duration = 45 # Duración de la animación (aprox 45 frames)

# --- VARIABLES DE ANIMACIÓN (7 MOVIMIENTOS) ---
# Banderas de activación
is_walking = False
is_jumping = False
is_waving = False
is_celebrating = False
is_spinning = False
is_crouching = False
is_smashing = False

# Variables de cálculo
walk_angle = 0.0
walk_dir = 1.0

jump_y = 0.0
jump_velocity = 0.0

wave_angle = 0.0
wave_dir = 1.0

celebrate_angle = 0.0
celebrate_dir = 1.0
celebrate_cycles=0

spin_angle = 0.0

crouch_y = 0.0
crouch_dir = -1.0

smash_y = 0.0
smash_arm_angle = 0.0
smash_phase = 0

last_collision = None