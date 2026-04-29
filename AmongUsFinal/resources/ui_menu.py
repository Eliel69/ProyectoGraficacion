# resources/ui_menu.py
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
from AmongUsFinal.actions import state

def draw_text(x, y, text, color=(1,1,1)):
    """Dibuja texto en pantalla en coordenadas 2D"""
    glColor3fv(color)
    glRasterPos2f(x, y)
    for char in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

def draw_hud():
    # 1. Guardar la proyección 3D actual
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    
    # 2. Configurar vista 2D (Ortográfica) que coincida con el tamaño de ventana
    window_width = glutGet(GLUT_WINDOW_WIDTH)
    window_height = glutGet(GLUT_WINDOW_HEIGHT)
    gluOrtho2D(0, window_width, window_height, 0) # (0,0) en la esquina superior izquierda
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # Apagar luces y profundidad temporalmente para que el texto brille por encima de todo
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)

    # --- DIBUJAR INSTRUCCIONES (Si la tecla 'I' está activa) ---
    if state.show_instructions:
        draw_text(10, 20, "--- INSTRUCCIONES DEL SISTEMA ---", (1, 1, 0)) # Amarillo
        
        # LOS 7 MOVIMIENTOS DE CÁMARA
        draw_text(10, 40, "CAMARA (7 Movimientos):", (0.5, 1, 1))
        draw_text(10, 60, " 1-4. Arrastrar Mouse(ClickIzquierdo): Mirar Arriba/Abajo y Paneo Izq/Der", (1, 1, 1))
        draw_text(10, 80, " 5-6. Flechas Arriba/Abajo: Hacer grande/pequeno", (1, 1, 1))
        draw_text(10, 100, " 6-7. Flechas Izq/Der: Desplazamiento", (1, 1, 1))
        draw_text(10, 120, " 8. Tecla R: Resetear vista normal", (1, 1, 1))
        
        draw_text(10, 140, "PERSONAJE Y ENTORNO:", (0.5, 1, 1))
        draw_text(10, 160, " - Rueda del Mouse: Girar al personaje 360 grados", (1, 1, 1))
        draw_text(10, 180, " - Caminar: A | Saltar: S | Girar: D | Temblar: F | Agachar: G", (1, 1, 1))
        draw_text(10, 200, " - Expresiones (1-6): Neutral, Enojado, Sospecha, Triste, Sorpresa, Pena", (1, 1, 1))
        draw_text(10, 220, " - Mutear Musica: M", (1, 1, 1))
        draw_text(10, 240, " - Escenarios:", (0.5, 1, 0.5))
        draw_text(10, 260, " - F1-Cafetería" ,(1.0, 1.0, 1.0))
        draw_text(10, 280, " - F2-Electricidad", (1.0, 1.0, 1.0))
        draw_text(10, 300, " - F3-Sala de escudos", (1.0, 1.0, 1.0))
        draw_text(10, 320, " - F4-Espacio", (1.0, 1.0, 1.0))
        draw_text(10, 340, " - F5-Enfermería", (1.0, 1.0, 1.0))

    # --- DIBUJAR ACERCA DE (Si la tecla 'C' está activa) ---
    if state.show_about:
        # Lo dibujamos alineado a la derecha
        x_pos = window_width - 350
        draw_text(x_pos, 25, "--- ACERCA DE ---", (1, 0.5, 0.5))
        draw_text(x_pos, 55, "Personaje: Tripulante Espacial", (1, 1, 1))
        draw_text(x_pos, 80, "Autor: Eliel Izay Figueroa Ortega", (1, 1, 1))
        draw_text(x_pos, 105, "Materia: Graficacion", (1, 1, 1))

    # --- MENSAJE FLOTANTE SIEMPRE VISIBLE ---
    if not state.show_instructions and not state.show_about:
        draw_text(10, 25, "Presiona 'I' para Instrucciones | 'C' para Acerca de", (0.8, 0.8, 0.8))

    # Restaurar luces, profundidad y vista 3D
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()