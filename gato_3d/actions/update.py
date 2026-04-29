# actions/update.py
import math
from gato_3d.actions import state
from gato_3d.resources import sounds

def update_logic():
    mc = state.motion_cycle

    # ── 1. Lógica de animaciones ─────────────────────────────────────────────
    if state.current_motion != "idle":
        state.motion_cycle += 0.12

    m = state.current_motion

    if m == "caminar":
        state.leg_L_pitch =  math.sin(mc) * 35
        state.leg_R_pitch = -math.sin(mc) * 35
        state.arm_L_pitch = -math.sin(mc) * 25
        state.arm_R_pitch =  math.sin(mc) * 25
        state.char_z -= state.char_speed
        state.guy_z   = state.char_z

    elif m == "saltar":
        state.char_y = abs(math.sin(mc)) * 2.0
        state.leg_L_pitch = -abs(math.sin(mc)) * 20
        state.leg_R_pitch = -abs(math.sin(mc)) * 20
        if mc > math.pi:
            _reset_motion()

    elif m == "saludar":
        # Brazo derecho sube y baja de forma visible (rango 0-90°)
        state.arm_R_pitch = 45 + math.sin(mc * 2) * 45
        state.arm_L_pitch = 0

    elif m == "brazos_arriba":
        # Brazos suben progresivamente hasta 160° (muy visible)
        t = min(mc / 0.5, 1.0)
        state.arm_L_pitch = t * 160
        state.arm_R_pitch = t * 160

    elif m == "girar":
        state.char_rotation = (state.char_rotation + 5) % 360

    elif m == "agacharse":
        t = 0.5 + 0.5 * math.sin(mc - math.pi / 2)
        state.body_scale_y = 1.0 - 0.4 * t
        state.leg_L_pitch  =  45 * t
        state.leg_R_pitch  =  45 * t

    elif m == "bailar":
        state.char_rotation += math.sin(mc) * 4
        state.arm_L_pitch = math.sin(mc * 2) * 70
        state.arm_R_pitch = math.cos(mc * 2) * 70
        state.leg_L_pitch = math.sin(mc * 1.5) * 30
        state.leg_R_pitch = -math.sin(mc * 1.5) * 30

    # ── 2. Timers ─────────────────────────────────────────────────────────────
    if state.motion_timer > 0:
        state.motion_timer -= 1
    elif state.motion_timer == 0 and state.current_motion not in ("idle", "caminar", "saltar"):
        _reset_motion()

    # ── 3. Colisiones ─────────────────────────────────────────────────────────
    for obj in state.collision_objects:
        dx = state.char_x - obj["pos"][0]
        dz = state.char_z - obj["pos"][2]
        dist = math.sqrt(dx*dx + dz*dz)
        if dist < 1.2 and not obj["hit"]:
            obj["hit"] = True
            # Cambio de color del personaje según el objeto
            if obj["type"] == "cubo":
                state.char_color = [1.0, 0.25, 0.10]   # rojo-naranja
            elif obj["type"] == "esfera":
                state.char_color = [0.20, 0.50, 1.0]   # azul brillante
            elif obj["type"] == "cono":
                state.char_color = [0.15, 0.90, 0.35]  # verde brillante
            state.current_expression = obj["effect_expr"]
            state.current_motion     = obj["effect_motion"]
            state.motion_timer       = 80
            state.motion_cycle       = 0.0
            sounds.play(obj["effect_motion"])
        elif dist > 2.0 and obj["hit"]:
            obj["hit"] = False
            state.char_color = [0.4, 0.85, 0.88]   # color original

    # ── 4. Sonido por movimiento (corta el anterior al cambiar) ───────────────
    if state.current_motion != state._last_sound_motion:
        if state.current_motion != "idle":
            sounds.play(state.current_motion)    # corta el anterior
        state._last_sound_motion = state.current_motion

    # ── 5. Sonido de escenario al cambiar (corta el anterior) ─────────────────
    if state.current_scene != state.prev_scene:
        sounds.play_scene(state.current_scene)   
        state.prev_scene = state.current_scene

def _reset_motion():
    state.current_motion = "idle"
    state.char_y    = 0.0
    state.body_scale_y = 1.0
    state.arm_L_pitch = state.arm_R_pitch = 0.0
    state.leg_L_pitch = state.leg_R_pitch = 0.0
    state.motion_cycle = 0.0
