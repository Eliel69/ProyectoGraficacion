# resources/input_handlers.py
from OpenGL.GLUT import *
from fallguy.actions    import state, camera
from fallguy.resources  import sounds
import sys

def mouse(button, state_btn, x, y):
    if button==3 and state_btn==GLUT_DOWN: camera.zoom_in();  glutPostRedisplay(); return
    if button==4 and state_btn==GLUT_DOWN: camera.zoom_out(); glutPostRedisplay(); return
    if button==GLUT_LEFT_BUTTON:
        state.mouse_down = (state_btn==GLUT_DOWN)
    state.last_mouse_x=x; state.last_mouse_y=y
    camera.mouse(button,state_btn,x,y)
    glutPostRedisplay()

def motion(x, y):
    if not state.mouse_down: return
    camera.motion(x,y)
    state.last_mouse_x=x; state.last_mouse_y=y
    glutPostRedisplay()

def special_keys(key, x, y):
    # Flechas mueven la CAMARA
    camera.handle_special_keys(key,x,y)
    # Flechas tambien mueven personaje cuando camina
    if   key==GLUT_KEY_UP:    state.key_up    = True
    elif key==GLUT_KEY_DOWN:  state.key_down  = True
    elif key==GLUT_KEY_LEFT:  state.key_left  = True
    elif key==GLUT_KEY_RIGHT: state.key_right = True
    glutPostRedisplay()

def special_keys_up(key, x, y):
    if   key==GLUT_KEY_UP:    state.key_up    = False
    elif key==GLUT_KEY_DOWN:  state.key_down  = False
    elif key==GLUT_KEY_LEFT:  state.key_left  = False
    elif key==GLUT_KEY_RIGHT: state.key_right = False

def keyboard(key, x, y):
    b = key

    # ── MOVIMIENTO ──────────────────────────────────────────────────────────
    if   b == b'w': state.walking = not state.walking

    # ── 5 MOVIMIENTOS ESPECIALES ─────────────────────────────────────────────
    elif b == b'j':   # Salto
        state.reaction_type="jump"; state.reaction_timer=0; sounds.play("jump")
    elif b == b'u':   # Brazos arriba (toggle)
        state.reaction_type = None if state.reaction_type=="arms" else "arms"
    elif b == b'k':   # Giro 360
        state.reaction_type="spin"; state.reaction_timer=0
    elif b == b'p':   # Reposo idle (toggle)
        state.reaction_type = None if state.reaction_type=="idle" else "idle"

    # ── 5 EXPRESIONES ────────────────────────────────────────────────────────
    elif b == b'1': state.expression="neutral"
    elif b == b'2': state.expression="wink";  sounds.play("expr+")
    elif b == b'3': state.expression="angry"; sounds.play("expr-")
    elif b == b'4': state.expression="fear";  sounds.play("expr-")
    elif b == b'5': state.expression="sad";   sounds.play("expr-")

    # ── 5 ESCENAS  (acepta minuscula Y mayuscula) ────────────────────────────
    elif b in (b'f', b'F'): _change_scene(1)
    elif b in (b'g', b'G'): _change_scene(2)
    elif b in (b'h', b'H'): _change_scene(3)
    elif b in (b'l', b'L'): _change_scene(4)   # L de fútboL (J choca con salto)
    elif b in (b'n', b'N'): _change_scene(5)   # N de diversioNes

    # ── CAMARA ───────────────────────────────────────────────────────────────
    elif b == b'r': camera.reset_camera()   # Reset
    elif b == b'q': camera.zoom_in()        # Zoom in
    elif b == b'e': camera.zoom_out()       # Zoom out
    elif b == b'z': camera.move_up()        # Arriba
    elif b == b'x': camera.move_down()      # Abajo

    # ── SONIDO ────────────────────────────────────────────────────────────────
    elif b == b'm': state.sound_enabled = not state.sound_enabled

    # ── UI ────────────────────────────────────────────────────────────────────
    elif b == b'i': state.show_instructions = not state.show_instructions
    elif b == b'a': state.show_about        = not state.show_about

    elif b == b'\x1b': sys.exit(0)

    glutPostRedisplay()

def _change_scene(n):
    state.current_scene=n; state.guy_x=0.0; state.guy_z=0.0; sounds.play("scene")