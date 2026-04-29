pos_x = 0.0
pos_y = 0.0
pos_z = 0.0
rotation_y = 0.0
scale = 1.0

expression = 'neutral'
expression_timer = 0

movement = 'idle'
move_timer = 0
walk_cycle = 0.0
jump_phase = 0.0
greet_phase = 0.0
spin_angle = 0.0
arm_angle = 0.0

move_forward = False
move_backward = False
move_left = False
move_right = False

collision_objects = [
    {"id": 0, "x":  2.5, "y": 0.0, "z":  0.0, "radius": 0.6, "color": (1.0, 0.5, 0.0), "hit": False, "hit_timer": 0},
    {"id": 1, "x": -2.5, "y": 0.0, "z":  0.0, "radius": 0.6, "color": (0.2, 0.8, 0.2), "hit": False, "hit_timer": 0},
    {"id": 2, "x":  0.0, "y": 0.0, "z": -3.0, "radius": 0.7, "color": (0.7, 0.1, 0.9), "hit": False, "hit_timer": 0},
]

current_scenario = 0
scenario_names = [
    "Dungeon de Jesoo",
    "Cueva de las Hormigas",
    "Santuario de las Sombras",
    "Portal de la Monarquia",
    "Dimension del Caos",
    "Castillo del Rey Sombra",
    "Puerta del Infierno",
]

cam_yaw = 0.0
cam_pitch = 15.0
cam_distance = 8.0
cam_pan_x = 0.0
cam_pan_y = 0.8
cam_mode = 'normal'
 
music_enabled = True      
fx_enabled = True         

show_help = False
show_about = False
hud_msg = ""
hud_timer = 0

mouse_last_x = 0
mouse_last_y = 0
mouse_dragging = False