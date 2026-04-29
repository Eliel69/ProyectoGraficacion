# actions/state.py

# --- Posicion del personaje ---
guy_x = 0.0
guy_z = 0.0
guy_speed = 0.15

# --- Rotacion manual (mouse drag) ---
rotate_x = 0.0
rotate_y = 0.0

# --- Animacion ---
animation_angle = 0.0
blink_timer     = 0.0
idle_bob        = 0.0
walking         = False

# --- Expresion: "neutral" | "Guiño" | "Triste" | "Nervioso" | "Feliz" ---
expression = "neutral"

# --- Movimiento especial: None | "Saltar" | "Brazos" | "Girar" | "inactivo" ---
reaction_type     = None
reaction_timer    = 0
reaction_duration = 50

# --- Camara libre ---
zoom         = 9.0
camera_follow = False
mouse_down    = False
last_mouse_x  = 0
last_mouse_y  = 0

# --- Teclas de movimiento continuo ---
key_up    = False
key_down  = False
key_left  = False
key_right = False

# --- Escena activa: 1=Parque 2=Pista 3=Bosque 4=Futbol 5=Diversiones ---
current_scene  = 1
scene_bounds   = {"x": (-18, 18), "z": (-18, 18)}

# --- Sonido ---
sound_enabled = True

# --- Pasos (contador interno) ---
step_timer = 0

# --- UI ---
show_instructions = False
show_about        = False