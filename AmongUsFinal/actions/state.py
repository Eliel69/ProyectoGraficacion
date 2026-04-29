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
expression = "neutral" 

# None, "jump", "spin", "shake", "vent"
reaction_type = None   
reaction_timer = 0
reaction_duration = 45 # Duración de la animación (aprox 45 frames)