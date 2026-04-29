# resources/input_handlers.py
from OpenGL.GLUT import *
from AmongUsFinal.actions import state
from AmongUsFinal.actions import camera
from AmongUsFinal.utilerias.sonidos import audio_manager
import sys
from AmongUsFinal.utilerias.escenarios import escenarios

def mouse(button, state_btn, x, y): 

   # --- SCROLL: GIRAR AL PERSONAJE SOBRE SU EJE ---
    if button == 3 and state_btn == GLUT_DOWN: # Scroll Arriba
        state.rotate_y += 15.0
        glutPostRedisplay()
    elif button == 4 and state_btn == GLUT_DOWN: # Scroll Abajo
        state.rotate_y -= 15.0
        glutPostRedisplay()

    # CLICK NORMAL
    if button == GLUT_LEFT_BUTTON:
        state.mouse_down = (state_btn == GLUT_DOWN)
        state.last_mouse_x = x
        state.last_mouse_y = y
        camera.mouse(button, state_btn, x, y)
        glutPostRedisplay()



def motion(x, y):

    if not state.mouse_down:
        return

    dx = x - state.last_mouse_x
    dy = y - state.last_mouse_y

    '''sensitivity = 0.01

    state.fox_x += dx * sensitivity
    state.fox_z += dy * sensitivity'''

    state.rotate_y += dx * 0.3
    state.rotate_x += dy * 0.3

    state.last_mouse_x = x
    state.last_mouse_y = y

    #camera.motion(x, y)

    glutPostRedisplay()



# Teclas especiales como flechas
   
def special_keys(key, x, y):
    # 1. Zoom In (Flecha Arriba = Se hace más grande)
    if key == GLUT_KEY_UP:
        state.zoom -= 2.0
        if state.zoom < 10.0: state.zoom = 10.0  # Límite máximo de acercamiento
        
    # 2. Zoom Out (Flecha Abajo = Se hace más pequeño)
    elif key == GLUT_KEY_DOWN:
        state.zoom += 2.0
        if state.zoom > 90.0: state.zoom = 90.0  # Límite máximo de alejamiento
        
    # 3. Paneo Lateral (Flechas Izquierda/Derecha mueven la cámara)
    elif key == GLUT_KEY_LEFT or key == GLUT_KEY_RIGHT:
        camera.handle_special_keys(key, x, y)

    # --- CAMBIO DE ESCENARIOS (F1 a F5) ---
    elif key == GLUT_KEY_F1: state.current_escenario = 1 # Cafetería
    elif key == GLUT_KEY_F2: state.current_escenario = 2 # Electricidad
    elif key == GLUT_KEY_F3: state.current_escenario = 3 # Escudos
    elif key == GLUT_KEY_F4: state.current_escenario = 4 # Espacio
    elif key == GLUT_KEY_F5: state.current_escenario = 5 # Enfermería  
    glutPostRedisplay()





def keyboard(key, x, y):
    b = key.lower() # Convertimos a minúscula 
    
    if b == b'i': state.show_instructions = not state.show_instructions
    elif b == b'c': state.show_about = not state.show_about
    elif b == b'r':  # RESET DE CÁMARA
        camera.reset_camera()
        state.fox_x=0.0
        state.fox_z = 0.0
        state.rotate_y = 0.0
        state.rotate_x = 0.0
    # CONTROL MAESTRO DE SONIDO (Tecla M)
    if b == b'm':
        if audio_manager.sonido_activado:
            audio_manager.sonidoOff()
        else:
            audio_manager.sonidoOn()
            
    # EXPRESIONES
    elif b == b'1': state.expression = "neutral"
    elif b == b'2': 
        state.expression = "angry"
        audio_manager.play_sound(audio_manager.exp_angry)
    elif b == b'3': 
        state.expression = "suspicious"
        audio_manager.play_sound(audio_manager.exp_suspicious)
    elif b == b'4': 
        state.expression = "sad"
        audio_manager.play_sound(audio_manager.exp_sad)
    elif b == b'5': 
        state.expression = "surprised"
        audio_manager.play_sound(audio_manager.exp_surprised)
    elif b == b'6': 
        state.expression = "embarrassed"
        audio_manager.play_sound(audio_manager.exp_embarrassed)

    # MOVIMIENTOS Y REACCIONES
    elif b == b'a': 
        state.walking = not state.walking
        if state.walking:
            audio_manager.play_sound(audio_manager.sound_walk, loop=True) # Activa loop
        else:
            audio_manager.stop_sound(audio_manager.sound_walk) # Apaga loop

    elif b == b's': 
        state.reaction_type = "jump"; state.reaction_timer = 0
        audio_manager.play_sound(audio_manager.sound_jump)
        
    elif b == b'd': 
        state.reaction_type = "spin"; state.reaction_timer = 0
        audio_manager.play_sound(audio_manager.sound_spin)
        
    elif b == b'f': 
        state.shaking = not state.shaking
        if state.shaking:
            audio_manager.play_sound(audio_manager.sound_shake, loop=True)
        else:
            audio_manager.stop_sound(audio_manager.sound_shake)
        
    elif b == b'g': 
        state.reaction_type = "vent"; state.reaction_timer = 0
        audio_manager.play_sound(audio_manager.sound_vent)

    elif key == b'\x1b': # ESC
        glutLeaveMainLoop()
        
    glutPostRedisplay()
    



