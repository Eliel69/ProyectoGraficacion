# resources/input_handlers.py
from OpenGL.GLUT import *
from gato_3d.actions import state, camera
from gato_3d.resources import sounds

def keyboard(key, x, y):
    b = key.lower()

    # ── Control de sonido e interfaz ─────────────────────────────────────────
    if b == b'm':
        sounds.toggle_all()
    if b == b'i':
        state.show_info         = not state.show_info
    if b == b'h':
        state.show_instructions = not state.show_instructions

    # ── Escenarios 1-7 ───────────────────────────────────────────────────────
    if b in (b'1', b'2', b'3', b'4', b'5', b'6', b'7'):
        sc = int(b)
        if sc != state.current_scene:
            state.current_scene = sc
            state.char_color    = [0.4, 0.85, 0.88]   # reset color

    # ── Movimientos ──────────────────────────────────────────────────────────
    if b == b'q':
        _set_motion("caminar")
    elif b == b'w':
        _set_motion("saltar", timer=0, reset_cycle=True)
    elif b == b'e':
        _set_motion("saludar", timer=100, reset_cycle=True)
    elif b == b'r':
        _set_motion("brazos_arriba", timer=70)
    elif b == b't':
        _set_motion("girar", timer=60)
    elif b == b'y':
        _set_motion("agacharse", timer=70)
    elif b == b'u':
        _set_motion("bailar", timer=140)

    # Detener movimiento
    if b == b's':
        state.current_motion = "idle"
        state.motion_timer   = 0

    # Reset cámara
    if b == b'c':
        camera.reset_camera()

def special_keys(key, x, y):
    # ── Cámara ───────────────────────────────────────────────────────────────
    if key == GLUT_KEY_LEFT:   state.cam_yaw   -= 5.0
    if key == GLUT_KEY_RIGHT:  state.cam_yaw   += 5.0
    if key == GLUT_KEY_UP:     state.cam_pitch  += 5.0
    if key == GLUT_KEY_DOWN:   state.cam_pitch  -= 5.0
    if key == GLUT_KEY_PAGE_UP:   state.cam_radius -= 0.5
    if key == GLUT_KEY_PAGE_DOWN: state.cam_radius += 0.5

    # ── Expresiones F1-F7, F8=neutral ────────────────────────────────────────
    _expr_map = {
        GLUT_KEY_F1: "guiño",
        GLUT_KEY_F2: "felicidad",
        GLUT_KEY_F3: "tristeza",
        GLUT_KEY_F4: "miedo",
        GLUT_KEY_F5: "enojo",
        GLUT_KEY_F6: "duda",
        GLUT_KEY_F7: "admiracion",
        GLUT_KEY_F8: "neutral",
    }
    if key in _expr_map:
        state.current_expression = _expr_map[key]

def mouse_wheel(wheel, direction, x, y):
    state.cam_radius -= direction * 0.5

# ── Helper ────────────────────────────────────────────────────────────────────
def _set_motion(name, timer=0, reset_cycle=False):
    state.current_motion = name
    if timer:
        state.motion_timer = timer
    if reset_cycle:
        state.motion_cycle = 0.0
