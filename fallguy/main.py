# main.py  –  Fall Guy 3D
from OpenGL.GL   import *
from OpenGL.GLU  import *
from OpenGL.GLUT import *
import sys

# --- IMPORTS LOCALES CON PREFIJO ---
from fallguy.characters import FullGuys as FallGuy
from fallguy.actions    import camera, state
from fallguy.actions    import update as update_module
from fallguy.resources  import grid, input_handlers, scenes, sounds
def stop_audio():
    """Para todo el audio al salir al lobby."""
    try:
        import pygame
        pygame.mixer.stop()
    except Exception:
        pass


WIN_W, WIN_H = 900, 650

def init():
    glEnable(GL_DEPTH_TEST); glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0);     glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT,GL_AMBIENT_AND_DIFFUSE); glShadeModel(GL_SMOOTH)
    glLightfv(GL_LIGHT0,GL_POSITION,[4.0,8.0,5.0,1.0])
    glLightfv(GL_LIGHT0,GL_AMBIENT, [0.25,0.25,0.25,1.0])
    glLightfv(GL_LIGHT0,GL_DIFFUSE, [0.90,0.90,0.90,1.0])
    glLightfv(GL_LIGHT0,GL_SPECULAR,[1.0,1.0,1.0,1.0])
    sounds.init()

def draw_str(x, y, text, c=(1,1,1)):
    glColor3f(*c); glRasterPos2f(x,y)
    for ch in text: glutBitmapCharacter(GLUT_BITMAP_8_BY_13,ord(ch))

def draw_hud():
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity()
    gluOrtho2D(0,WIN_W,0,WIN_H)
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
    glDisable(GL_LIGHTING); glDisable(GL_DEPTH_TEST)

    sc={1:"Parque",2:"Pista",3:"Bosque",4:"Futbol",5:"Diversiones"}
    mv={None:"Reposo","jump":"Salto","spin":"Giro","arms":"Brazos","idle":"Idle"}
    draw_str(8,8,
        f"Escena:{sc.get(state.current_scene,'?')}  "
        f"Expr:{state.expression}  "
        f"Mov:{mv.get(state.reaction_type,'Reposo')}  "
        f"{'CAMINANDO' if state.walking else 'QUIETO'}  "
        f"Son:{'ON' if state.sound_enabled else 'OFF'}  "
        f"[I]=Instrucciones  [A]=AcercaDe",
        (1,1,0.3))

    if state.show_instructions:
        rows=[
            "========  INSTRUCCIONES  ========",
            "",
            "CAMARA  (7 movimientos):",
            " Flechas Arr/Abj Zoom In / Zoom Out",
            " Flechas Izq/Der Mover lateral",
            " AvPag / RePag Subir / Bajar camara",
            " Q / E Zoom In / Zoom Out",
            " Arrastrar mouse Rotar camara",
            " Scroll mouse Zoom In / Zoom Out",
            " R  Reset camara"
            "PERSONAJE:",
            " W          Caminar ON/OFF",
            " Flechas    Mover personaje (mientras camina)",
            " J          Salto",
            " U          Brazos arriba/abajo",
            " K          Giro 360",
            " P          Reposo ",
            "",
            "EXPRESIONES:",
            " 1  Neutral   2  Guiño",
            " 3  Triste      4  Miedo   5  Feliz",
            "",
            "ESCENAS:",
            " F  Parque    G  Pista    H  Bosque",
            " L  Futbol    N  Diversiones",
            "",
            " M   Sonido ON/OFF",
            " A   Acerca de",
            " ESC Salir",
            "",
            " [I] cerrar",
        ]
        glColor4f(0,0,0,0.82)
        glBegin(GL_QUADS)
        glVertex2f(8,25);glVertex2f(380,25);glVertex2f(380,WIN_H-8);glVertex2f(8,WIN_H-8)
        glEnd()
        for idx,row in enumerate(rows):
            draw_str(16, WIN_H-34-idx*15, row, (0.85,0.95,1.0))

    if state.show_about:
        rows=[
            "========  ACERCA DE  ========",
            "",
            "  Fall Guy 3D, Elaborado por:Brenda Luz Ramirez Garcia",
            "  Diseño de Personajes 3D",
            "  Materia:  Graficacion",
            "  Personaje inspirado en:",
            "  Fall Guys: Ultimate Knockout",
            "  Coordenadas originales de GeoGebra",
            "  - 5 expresiones  - 5 movimientos",
            "  - 5 sonidos      - 5 escenarios",
            "  - 7 movimientos de camara",
            "",
            "  [A] cerrar",
        ]
        glColor4f(0,0,0,0.84)
        glBegin(GL_QUADS)
        glVertex2f(WIN_W-360,25);glVertex2f(WIN_W-8,25)
        glVertex2f(WIN_W-8,WIN_H-8);glVertex2f(WIN_W-360,WIN_H-8)
        glEnd()
        for idx,row in enumerate(rows):
            draw_str(WIN_W-350, WIN_H-34-idx*17, row, (0.35,1.0,0.55))

    glEnable(GL_LIGHTING); glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION); glPopMatrix()
    glMatrixMode(GL_MODELVIEW);  glPopMatrix()

def display():
    bgs={1:(0.55,0.82,0.99,1),2:(0.78,0.88,0.96,1),
         3:(0.10,0.20,0.12,1),4:(0.38,0.72,0.28,1),5:(0.05,0.00,0.18,1)}
    glClearColor(*bgs.get(state.current_scene,(0.55,0.82,0.99,1)))
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    camera.apply_camera()
    scenes.draw_current_scene()
    grid.draw_grid()
    glPushMatrix()
    glTranslatef(state.guy_x,0,state.guy_z)
    glRotatef(state.rotate_y,0,1,0)
    glRotatef(state.rotate_x,1,0,0)
    FallGuy.draw_fallguy_full()
    glPopMatrix()
    draw_hud()
    glutSwapBuffers()

def reshape(w,h):
    global WIN_W,WIN_H; WIN_W,WIN_H=w,max(h,1)
    glViewport(0,0,WIN_W,WIN_H)
    glMatrixMode(GL_PROJECTION); glLoadIdentity()
    gluPerspective(45,WIN_W/WIN_H,0.1,300.0)
    glMatrixMode(GL_MODELVIEW)
# ==========================================================
# PUENTES DE CONEXIÓN PARA EL ARCADE
# (Reciben las teclas del menú y las mandan a input_handlers)
# ==========================================================

def keyboard(key, x, y):
    if hasattr(input_handlers, 'keyboard'):
        input_handlers.keyboard(key, x, y)

def special_keys(key, x, y):
    if hasattr(input_handlers, 'special_keys'):
        input_handlers.special_keys(key, x, y)

def mouse(button, state_btn, x, y):
    # Soporte estándar (Para MegaCaballero, AmongUs, Totoro, FallGuy)
    if hasattr(input_handlers, 'mouse'):
        input_handlers.mouse(button, state_btn, x, y)
    # Soporte especial para Beru (Que lo llamó 'mouse_button')
    elif hasattr(input_handlers, 'mouse_button'):
        input_handlers.mouse_button(button, state_btn, x, y)

def motion(x, y):
    # Soporte estándar 
    if hasattr(input_handlers, 'motion'):
        input_handlers.motion(x, y)
    # Soporte especial para Beru (Que lo llamó 'mouse_motion')
    elif hasattr(input_handlers, 'mouse_motion'):
        input_handlers.mouse_motion(x, y)
def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE|GLUT_RGB|GLUT_DEPTH)
    glutInitWindowSize(WIN_W,WIN_H)
    glutCreateWindow(b"Fall Guy 3D - OpenGL")
    init()
    glutDisplayFunc(display); glutReshapeFunc(reshape)
    glutKeyboardFunc(input_handlers.keyboard)
    glutMouseFunc(input_handlers.mouse)
    glutMotionFunc(input_handlers.motion)
    glutSpecialFunc(input_handlers.special_keys)
    glutSpecialUpFunc(input_handlers.special_keys_up)
    glutTimerFunc(16,update.update,0)
    glutMainLoop()

if __name__=="__main__":
    main()