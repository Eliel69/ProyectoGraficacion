
# ----------------------------
# Cámara / entrada
# ----------------------------
zoom = 18.0
rotate_x = 0.0
rotate_y = 0.0
mouse_down = False
last_mouse_x = 0
last_mouse_y = 0

# ----------------------------
# Personaje
# ----------------------------
char_x = 0.0
char_z = -18.5
char_speed = 0.8

walking = False
show_instructions = True
show_about = False
sound_enabled = True

# ----------------------------
# Expresiones 
# ----------------------------
expression = "neutral"

# ----------------------------
# Animaciones
# ----------------------------
animation_angle = 0.0
blink_timer = 0.0
arm_angle = 0.0
leg_angle = 0.0
jump_offset = 0.0
spin_angle = 0.0
shake_offset = 0.0

# ----------------------------
# Reacciones / movimientos 
# ----------------------------
reaction_type = None
reaction_timer = 0
reaction_duration = 30

# ----------------------------
# Escenarios 
# ----------------------------
current_scene = 1

# ----------------------------
# Límites de escena
# ----------------------------
scene_bounds = {
    "x": (-20.0, 20.0),
    "z": (-30.0, 30.0)
}