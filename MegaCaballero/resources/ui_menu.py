from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from MegaCaballero.actions import state
from OpenGL.GLUT import glutBitmapCharacter, GLUT_BITMAP_HELVETICA_18, GLUT_BITMAP_9_BY_15

FONT_TITLE = GLUT_BITMAP_HELVETICA_18
FONT_BODY = GLUT_BITMAP_9_BY_15 

def draw_rect(x, y, width, height, color=(0, 0, 0, 0.6)):
    """Dibuja un rectángulo con transparencia para el fondo del menú"""
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4fv(color)
    glBegin(GL_QUADS)
    glVertex2f(x, y)
    glVertex2f(x + width, y)
    glVertex2f(x + width, y + height)
    glVertex2f(x, y + height)
    glEnd()
    glDisable(GL_BLEND)

def draw_text(x, y, text, color=(1, 1, 1), font=FONT_BODY):
    glColor3fv(color)
    glRasterPos2f(x, y)
    for char in text:
        glutBitmapCharacter(font, ord(char))

def draw_hud():
    window_width = glutGet(GLUT_WINDOW_WIDTH)
    window_height = glutGet(GLUT_WINDOW_HEIGHT)

    # --- Configuración de Matriz 2D ---
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, window_width, window_height, 0)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)

    # --- 1. INSTRUCCIONES (Panel Izquierdo) ---
    if state.show_instructions:
        # Fondo oscuro semi-transparente
        draw_rect(5, 5, 550, 420, (0, 0, 0, 0.7))
        # Borde decorativo
        draw_rect(5, 5, 550, 2, (1, 1, 0, 0.8)) 

        draw_text(20, 30, ">>> CONTROLES DE SISTEMA <<<", (1, 0.8, 0), FONT_TITLE)
        
        y_off = 60
        sections = [
            ("CÁMARA", (0, 1, 1), [
                "• Mouse Click Izq : Rotar (Izq/Der/Arri/Abj)",
                "• Flechas         : Traslación (Der,Izr,Frente/Atras)",
                "• Scroll          : Zoom In/Out",
                "• Tecla [R]       : Resetear Cámara"
            ]),
            ("MEGA CABALLERO", (1, 0.5, 1), [
                "• [A] Caminar | [S] Saltar | [D] Saludar",
                "• [F] Festejo | [G] Girar  | [H] Agachar",
                "• [J] Mega Salto ",
                "1: Triste | 2: Enojado  | 3: Feliz",
                "4: Pena   | 5: Sorpresa | 6: Duda",
                "7: Ira    | 8: Neutral"
            ]),
            ("ESCENARIOS (F1 - F7)", (0.5, 1, 0.5), [
                "F1: Arena | F2: Foso | F3: Valle | F4: Taller",
                "F5: Pico Helado | F6: Fuerte | F7: Legendaria"
            ])
        ]

        for title, color, lines in sections:
            draw_text(20, y_off, title, color)
            y_off += 20
            for line in lines:
                draw_text(35, y_off, line, (0.9, 0.9, 0.9))
                y_off += 20
            y_off += 10

    # --- 2. ACERCA DE (Panel Derecho) ---
    if state.show_about:
        panel_w = 380
        x_start = window_width - panel_w - 10
        draw_rect(x_start, 5, panel_w, 150, (0.1, 0.1, 0.2, 0.8))
        
        draw_text(x_start + 15, 30, "INFORMACIÓN DEL PROYECTO", (1, 0.4, 0.4), FONT_TITLE)
        info = [
            f"Personaje: Mega Caballero",
            f"Autor: {state.author_name if hasattr(state, 'author_name') else 'Eliel Figueroa'}",
            f"Materia: Graficación",
            f"Docente: Rocío E. Pulido Alba",
            f"Periodo E.: Enero-Junio"
        ]
        for i, line in enumerate(info):
            draw_text(x_start + 15, 60 + (i * 22), line, (1, 1, 1))

    
    if not state.show_instructions and not state.show_about:
        draw_rect(0, window_height - 35, window_width, 35, (0, 0, 0, 0.5))
        msg = "[I] Instrucciones | [C] Créditos | [M] Sonido"
        draw_text(window_width/2 - 150, window_height - 12, msg, (1, 1, 1))

   
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()

