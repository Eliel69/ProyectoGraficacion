# resources/scenarios.py
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import random

# Generar estrellas aleatorias para el Espacio
estrellas = [(random.uniform(-30, 30), random.uniform(-10, 30), random.uniform(-30, -10)) for _ in range(200)]

def draw_room(floor_color, wall_color):
    """Dibuja un piso y 4 paredes formando una habitación cerrada"""
    
    # --- 1. PISO ---
    glColor3fv(floor_color)
    glBegin(GL_QUADS)
    glVertex3f(-15.0, -1.0, 15.0)   # Esquina frontal izquierda
    glVertex3f(15.0, -1.0, 15.0)    # Esquina frontal derecha
    glVertex3f(15.0, -1.0, -15.0)   # Esquina trasera derecha
    glVertex3f(-15.0, -1.0, -15.0)  # Esquina trasera izquierda
    glEnd()

    # --- 2. PARED DE FONDO (Atrás) ---
    glColor3fv(wall_color)
    glBegin(GL_QUADS)
    glVertex3f(-15.0, -1.0, -15.0)  
    glVertex3f(15.0, -1.0, -15.0)   
    glVertex3f(15.0, 10.0, -15.0)   
    glVertex3f(-15.0, 10.0, -15.0)  
    glEnd()

    # --- 3. PARED FRONTAL (Adelante - Detrás de la cámara) ---
    glColor3fv(wall_color)
    glBegin(GL_QUADS)
    glVertex3f(-15.0, -1.0, 15.0)  
    glVertex3f(15.0, -1.0, 15.0)   
    glVertex3f(15.0, 10.0, 15.0)   
    glVertex3f(-15.0, 10.0, 15.0)  
    glEnd()

    # --- 4. PARED IZQUIERDA ---
    glColor3fv(wall_color)
    glBegin(GL_QUADS)
    glVertex3f(-15.0, -1.0, 15.0)  
    glVertex3f(-15.0, -1.0, -15.0)   
    glVertex3f(-15.0, 10.0, -15.0)   
    glVertex3f(-15.0, 10.0, 15.0)  
    glEnd()

    # --- 5. PARED DERECHA ---
    glColor3fv(wall_color)
    glBegin(GL_QUADS)
    glVertex3f(15.0, -1.0, 15.0)  
    glVertex3f(15.0, -1.0, -15.0)   
    glVertex3f(15.0, 10.0, -15.0)   
    glVertex3f(15.0, 10.0, 15.0)  
    glEnd()

def set_background(scenario_id):
    """Cambia el color del vacío infinito"""
    if scenario_id == 4: 
        glClearColor(0.0, 0.0, 0.0, 1.0) # Negro para el espacio
    else: 
        glClearColor(0.1, 0.1, 0.1, 1.0) # Gris oscuro para que no deslumbre al salir de la habitación

def draw_cafeteria():
    draw_room((0.3, 0.3, 0.3), (0.7, 0.8, 0.9)) # Piso gris oscuro, pared celeste
    
    # Ventanas al espacio en la pared de fondo
    glColor3f(0.0, 0.1, 0.3) # Azul muy oscuro
    for x in [-6.0, 0.0, 6.0]:
        glBegin(GL_QUADS)
        glVertex3f(x - 2.0, 2.0, -14.9) # Un poquito adelante de la pared para que no parpadee
        glVertex3f(x + 2.0, 2.0, -14.9)
        glVertex3f(x + 2.0, 6.0, -14.9)
        glVertex3f(x - 2.0, 6.0, -14.9)
        glEnd()

    # Mesas (Base delgada + Tapa ancha)
    for x in [-4.0, 4.0]:
        glColor3f(0.4, 0.4, 0.4) # Pata gris
        glPushMatrix()
        glTranslatef(x, -1.0, -5.0)
        glRotatef(-90, 1, 0, 0)
        glutSolidCylinder(0.2, 1.0, 16, 1)
        glPopMatrix()
        
        glColor3f(0.8, 0.8, 0.8) # Tapa blanca/plata
        glPushMatrix()
        glTranslatef(x, 0.0, -5.0)
        glRotatef(-90, 1, 0, 0)
        glutSolidCylinder(2.0, 0.1, 32, 1)
        glPopMatrix()

        # Botón de emergencia al centro
        glColor3f(1.0, 0.0, 0.0)
        glPushMatrix()
        glTranslatef(x, 0.1, -5.0)
        glRotatef(-90, 1, 0, 0)
        glutSolidCylinder(0.3, 0.1, 16, 1)
        glPopMatrix()

def draw_electrical():
    draw_room((0.4, 0.4, 0.4), (0.8, 0.7, 0.2)) # Piso gris, pared amarilla mostaza
    
    # Cajas de luz grandes y variadas
    posiciones = [(-5.0, 1.5, -8.0), (0.0, 2.0, -10.0), (4.0, 1.0, -6.0)]
    escalas = [(2.0, 4.0, 1.0), (3.0, 5.0, 1.5), (1.5, 3.0, 1.0)]
    
    for i in range(3):
        # Cuerpo de la caja
        glColor3f(0.5, 0.5, 0.5)
        glPushMatrix()
        glTranslatef(*posiciones[i])
        glScalef(*escalas[i])
        glutSolidCube(1.0)
        glPopMatrix()
        
        # Botones de colores brillantes en cada caja
        glDisable(GL_LIGHTING)
        glPushMatrix()
        # Moverse a la cara frontal de la caja
        glTranslatef(posiciones[i][0], posiciones[i][1], posiciones[i][2] + (escalas[i][2]/2) + 0.05)
        
        glColor3f(1.0, 0.0, 0.0) # Rojo
        glPushMatrix()
        glTranslatef(-0.3, 0.5, 0.0)
        glutSolidCube(0.2)
        glPopMatrix()
        
        glColor3f(0.0, 1.0, 0.0) # Verde
        glPushMatrix()
        glTranslatef(0.4, 0.0, 0.0)
        glutSolidCube(0.2)
        glPopMatrix()
        
        glColor3f(0.0, 0.5, 1.0) # Azul
        glPushMatrix()
        glTranslatef(-0.3, -0.5, 0.0)
        glutSolidCube(0.2)
        glPopMatrix()
        glPopMatrix()
        glEnable(GL_LIGHTING)

def draw_shields():
    draw_room((0.1, 0.2, 0.3), (0.2, 0.3, 0.5)) # Cuarto azul oscuro tecnológico
    
    # Generador de escudo central (Esfera brillante gigante)
    glColor3f(0.5, 0.5, 0.5) # Base
    glPushMatrix()
    glTranslatef(0.0, -1.0, -6.0)
    glRotatef(-90, 1, 0, 0)
    glutSolidCylinder(2.0, 0.5, 32, 1)
    glPopMatrix()

    glDisable(GL_LIGHTING)
    glColor3f(0.0, 0.8, 1.0) # Esfera de energía cyan
    glPushMatrix()
    glTranslatef(0.0, 0.5, -6.0)
    glutSolidSphere(1.5, 32, 32) 
    glPopMatrix()
    glEnable(GL_LIGHTING)

    # Pilares emisores de escudo a los lados
    for x in [-4.0, 4.0]:
        glColor3f(0.3, 0.3, 0.3)
        glPushMatrix()
        glTranslatef(x, -1.0, -6.0)
        glRotatef(-90, 1, 0, 0)
        glutSolidCylinder(0.5, 3.0, 16, 1)
        glPopMatrix()
        
        # Luz arriba del pilar
        glDisable(GL_LIGHTING)
        glColor3f(0.0, 0.5, 1.0)
        glPushMatrix()
        glTranslatef(x, 2.2, -6.0)
        glutSolidSphere(0.4, 16, 16)
        glPopMatrix()
        glEnable(GL_LIGHTING)

def draw_space():
    # No dibujamos cuarto, solo el vacío negro con estrellas
    glDisable(GL_LIGHTING)
    glColor3f(1.0, 1.0, 1.0)
    glPointSize(2.0)
    glBegin(GL_POINTS)
    for x, y, z in estrellas:
        glVertex3f(x, y, z)
    glEnd()
    glEnable(GL_LIGHTING)

    # Agregamos un planeta
    glPushMatrix()
    glTranslatef(5.0, 4.0, -15.0)
    glutSolidSphere(2.0, 16, 16)
    glPopMatrix()

def draw_medbay():
    draw_room((0.8, 0.9, 0.9), (0.9, 0.95, 1.0)) # Blanco/Celeste súper limpio
    
    # Camilla Base
    glColor3f(0.7, 0.7, 0.7)
    glPushMatrix()
    glTranslatef(-3.0, -0.5, -4.0)
    glScalef(1.5, 0.5, 3.0)
    glutSolidCube(1.0)
    glPopMatrix()

    # Colchón azulito
    glColor3f(0.4, 0.6, 0.9)
    glPushMatrix()
    glTranslatef(-3.0, -0.2, -4.0)
    glScalef(1.4, 0.2, 2.9)
    glutSolidCube(1.0)
    glPopMatrix()

    # Cruz Roja en la pared
    glDisable(GL_LIGHTING)
    glColor3f(1.0, 0.0, 0.0)
    glPushMatrix()
    glTranslatef(0.0, 3.0, -14.9)
    glScalef(0.5, 2.0, 0.1)
    glutSolidCube(1.0)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(0.0, 3.0, -14.9)
    glScalef(2.0, 0.5, 0.1)
    glutSolidCube(1.0)
    glPopMatrix()
    glEnable(GL_LIGHTING)

    # Anaquel de medicinas
    glColor3f(0.6, 0.6, 0.6)
    glPushMatrix()
    glTranslatef(4.0, 1.5, -8.0)
    glScalef(2.0, 5.0, 1.0) # Mueble alto
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Repisas y frascos de medicina
    for y in [-0.5, 1.0, 2.5]:
        glColor3f(0.8, 0.8, 0.8) # Repisa
        glPushMatrix()
        glTranslatef(4.0, y, -7.5)
        glScalef(1.8, 0.1, 0.8)
        glutSolidCube(1.0)
        glPopMatrix()
        
        glColor3f(0.0, 1.0, 0.5) # Frasco verde fosforescente
        glPushMatrix()
        glTranslatef(3.5, y + 0.3, -7.5)
        glRotatef(-90, 1, 0, 0)
        glutSolidCylinder(0.2, 0.5, 16, 1)
        glPopMatrix()

def draw_current_scenario(scenario_id):
    if scenario_id == 1: draw_cafeteria()
    elif scenario_id == 2: draw_electrical()
    elif scenario_id == 3: draw_shields()
    elif scenario_id == 4: draw_space()
    elif scenario_id == 5: draw_medbay()