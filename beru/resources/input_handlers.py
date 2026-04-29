# beru/resources/input_handlers.py
# CORRECCIONES: Todos los imports locales corregidos a rutas de paquete completo.
# - 'import actions.state as state'    → from beru.actions import state
# - 'import actions.camara as camara'  → from beru.actions import camara
# - 'import actions.update as update'  → from beru.actions import update
# - 'from Utilerias import scenarios'  → from beru.Utilerias import scenarios
# - 'from resources import sound_manager' → from beru.resources import sound_manager

from OpenGL.GLUT import *
from beru.actions import state                       # CORREGIDO
from beru.actions import camara                      # CORREGIDO
from beru.actions import update                      # CORREGIDO
from beru.Utilerias import scenarios                 # CORREGIDO
from beru.resources import sound_manager             # CORREGIDO

def keyboard(key, x, y):
    k = key.decode('utf-8').lower() if isinstance(key, bytes) else key.lower()

    if k == 'w':
        state.move_forward = True
    elif k == 's':
        state.move_backward = True
    elif k == 'a':
        state.move_left = True
    elif k == 'd':
        state.move_right = True

    elif k == '1':
        update.set_expression('smile')
        update.set_hud("Expresion: Sonrisa")
    elif k == '2':
        update.set_expression('sad')
        update.set_hud("Expresion: Tristeza")
    elif k == '3':
        update.set_expression('angry')
        update.set_hud("Expresion: Enojo")
    elif k == '4':
        update.set_expression('fear')
        update.set_hud("Expresion: Miedo")
    elif k == '5':
        update.set_expression('doubt')
        update.set_hud("Expresion: Duda")
    elif k == '6':
        update.set_expression('admire')
        update.set_hud("Expresion: Admiracion")
    elif k == '7':
        update.set_expression('wink')
        update.set_hud("Expresion: Guino")

    elif k == ' ':
        update.set_movement('jump', 60)
        update.set_hud("Movimiento: Saltar")
    elif k == 'g':
        update.set_movement('greet', 80)
        update.set_hud("Movimiento: Saludar")
    elif k == 'r':
        update.set_movement('spin', 40)
        update.set_hud("Movimiento: Girar")
    elif k == 'u':
        update.set_movement('arms_up', 30)
        update.set_hud("Movimiento: Subir garras")
    elif k == 'j':
        update.set_movement('arms_down', 30)
        update.set_hud("Movimiento: Bajar garras")

    elif k == '\t':
        scenarios.next_scenario()
        update.set_hud(f"Escenario: {state.scenario_names[state.current_scenario]}")
    elif k in '0123456':
        scenarios.set_scenario(int(k))
        update.set_hud(f"Escenario: {state.scenario_names[int(k)]}")

    elif k == '+':
        camara.zoom_in()
    elif k == '-':
        camara.zoom_out()
    elif k == 'f':
        active = camara.toggle_follow()
        update.set_hud("Camara: Seguimiento" if active else "Camara: Normal")

    elif k == 'h':
        state.show_help = not state.show_help
    elif k == 'p':
        state.show_about = not state.show_about

    elif k == 'm':
        enabled = sound_manager.toggle_music()
        update.set_hud("Musica de fondo: ON" if enabled else "Musica de fondo: OFF")
    elif k == 'n':
        enabled = sound_manager.toggle_fx()
        update.set_hud("Sonidos de acciones: ON" if enabled else "Sonidos de acciones: OFF")

    elif k == '\x1b':
        try:
            sound_manager.stop_all()
            glutLeaveMainLoop()
        except Exception:
            import os; os._exit(0)

    glutPostRedisplay()


def keyboard_up(key, x, y):
    k = key.decode('utf-8').lower() if isinstance(key, bytes) else key.lower()
    if k == 'w': state.move_forward  = False
    elif k == 's': state.move_backward = False
    elif k == 'a': state.move_left   = False
    elif k == 'd': state.move_right  = False


def special_keys(key, x, y):
    if key == GLUT_KEY_UP:        state.move_forward  = True
    elif key == GLUT_KEY_DOWN:    state.move_backward = True
    elif key == GLUT_KEY_LEFT:    state.move_left     = True
    elif key == GLUT_KEY_RIGHT:   state.move_right    = True
    elif key == GLUT_KEY_PAGE_UP: camara.pan_up()
    elif key == GLUT_KEY_PAGE_DOWN: camara.pan_down()
    elif key == GLUT_KEY_HOME:
        camara.reset()
        update.set_hud("Camara: Reset")


def special_keys_up(key, x, y):
    if key == GLUT_KEY_UP:      state.move_forward  = False
    elif key == GLUT_KEY_DOWN:  state.move_backward = False
    elif key == GLUT_KEY_LEFT:  state.move_left     = False
    elif key == GLUT_KEY_RIGHT: state.move_right    = False


def mouse_button(button, btn_state, x, y):
    if button == GLUT_LEFT_BUTTON:
        state.mouse_dragging = (btn_state == GLUT_DOWN)
        state.mouse_last_x   = x
        state.mouse_last_y   = y
    elif button == 3:
        camara.zoom_in(0.3)
    elif button == 4:
        camara.zoom_out(0.3)


def mouse_motion(x, y):
    if state.mouse_dragging:
        dx = x - state.mouse_last_x
        dy = y - state.mouse_last_y
        camara.move_right(dx * 0.4)
        camara.move_down(dy * 0.4)
        state.mouse_last_x = x
        state.mouse_last_y = y
    glutPostRedisplay()
