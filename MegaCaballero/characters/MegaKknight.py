from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math

# --- IMPORTAMOS EL ESTADO PARA LEER LAS EXPRESIONES ---
from MegaCaballero.actions import state 

# Paleta de colores base
COLOR_ARMOR_BASE = (0.2, 0.2, 0.25)
COLOR_BELT_BASE = (0.1, 0.1, 0.1)
COLOR_SKIN_BASE = (1.0, 0.8, 0.6)
COLOR_MACE = (0.4, 0.4, 0.45)
COLOR_BUCKLE = (0.8, 0.7, 0.1)
COLOR_PLUME = (0.0, 0.0, 1.0)

def draw_body():


    # Feliz (3): Armadura amarilla | Enojo (7): Armadura roja
    if state.expression == 3:
        color = (1.0, 1.0, 0.0)
    elif state.expression == 7:
        color = (0.8, 0.1, 0.1)
    else:
        color = COLOR_ARMOR_BASE
        
    glColor3fv(color)
    glPushMatrix()
    glTranslatef(0.0, 0.0, 0.0)
    glScalef(1.2, 1.1, 0.8) 
    glutSolidCube(1.0)
    glPopMatrix()

def draw_belt():
    # El cinturón y la hebilla se mantienen siempre de su color original
    glColor3fv(COLOR_BELT_BASE)
    glPushMatrix()
    glTranslatef(0.0, -0.55, 0.0) 
    glScalef(1.25, 0.2, 0.85) 
    glutSolidCube(1.0)
    glPopMatrix()

    glColor3fv(COLOR_BUCKLE)
    glPushMatrix()
    glTranslatef(0.0, -0.55, 0.45) 
    glScalef(0.35, 0.3, 0.1)
    glutSolidCube(1.0)
    glPopMatrix()

def draw_legs():
    if state.expression == 3:
        armor_color = (1.0, 1.0, 0.0)
    elif state.expression == 7:
        armor_color = (0.8, 0.1, 0.1)
    else:
        armor_color = COLOR_ARMOR_BASE
    
    for i, x in enumerate([-0.35, 0.35]): 
        glColor3fv(armor_color)
        glPushMatrix()
        glTranslatef(x, -0.5, 0.0) 
        
        # --- ANIMACIÓN DE CAMINAR ---
        # Una pierna va hacia adelante y la otra hacia atrás
        angle = state.walk_angle if i == 0 else -state.walk_angle
        glRotatef(angle, 1, 0, 0)
        
        glRotatef(90, 1, 0, 0)     
        glutSolidCylinder(0.2, 0.6, 16, 1) 
        
        glColor3fv(COLOR_BELT_BASE) 
        glPushMatrix()
        glTranslatef(0.0, 0.0, 0.6) # Nos movemos al final del cilindro
        glScalef(0.25, 0.35, 0.15)  # Ajuste de escala por el orden de transformaciones
        glutSolidSphere(1.0, 16, 16)
        glPopMatrix()
        glPopMatrix()

def draw_arms_and_maces():
    if state.expression == 3:
        armor_color = (1.0, 1.0, 0.0)
    elif state.expression == 7:
        armor_color = (0.8, 0.1, 0.1)
    else:
        armor_color = COLOR_ARMOR_BASE
    
    for i, x_dir in enumerate([-1, 1]):
        glPushMatrix()
        glTranslatef(0.85 * x_dir, 0.2, 0.0) 
        
        glColor3fv(armor_color)
        glPushMatrix()
        glScalef(1.2, 1.2, 1.2) 
        glutSolidSphere(0.25, 16, 16)
        glPopMatrix()
        
        rot_z = 90 * x_dir  
        rot_x = 50          

        if state.expression == 3: rot_z, rot_x = 160 * x_dir, 0
        elif state.expression == 6: rot_z, rot_x = 30 * x_dir, 70
        elif state.expression == 7: rot_z, rot_x = 75 * x_dir, -10

        # --- ANIMACIONES FÍSICAS DE LOS BRAZOS ---
        # 3. Saludar (Solo el brazo derecho)
        if i == 1 and state.is_waving:
            rot_z -= 60 # Levanta el brazo
            rot_z += state.wave_angle # Lo mueve de lado a lado
            
        # 4. Festejar (Ambos brazos arriba y abajo)
        rot_x -= state.celebrate_angle
        
        # 7. Mega Smash (Levanta brazos y los azota)
        rot_x -= state.smash_arm_angle

        glRotatef(rot_z, 0, 0, 1) 
        glRotatef(rot_x, 1, 0, 0)         
        
        glutSolidCylinder(0.25, 1.3, 16, 1)
        glTranslatef(0.0, 0.0, 1.3)
        glColor3fv(COLOR_MACE)
        glutSolidSphere(0.6, 24, 24)
        
        glColor3fv(armor_color)
        angles = [(0,0), (90,0), (-90,0), (0,90), (0,-90), (180,0)]
        for rot_ax, rot_ay in angles:
            glPushMatrix()
            glRotatef(rot_ax, 1, 0, 0)
            glRotatef(rot_ay, 0, 1, 0)
            glTranslatef(0.0, 0.0, 0.5) 
            glutSolidCone(0.15, 0.4, 16, 1)
            glPopMatrix()
        glPopMatrix()

def draw_head_and_helmet():
    if state.expression == 3:
        armor_color = (1.0, 1.0, 0.0)
    elif state.expression == 7:
        armor_color = (0.8, 0.1, 0.1)
    else:
        armor_color = COLOR_ARMOR_BASE

    skin_color = (1.0, 0.2, 0.2) if state.expression == 2 else COLOR_SKIN_BASE

    glColor3fv(armor_color)
    glPushMatrix()
    glTranslatef(0.0, 1.0, 0.0)
    glScalef(1.0, 0.9, 0.9)
    glutSolidSphere(0.7, 32, 32)
    glPopMatrix()

    # Rostro (Piel)
    glDisable(GL_LIGHTING) 
    glColor3fv(skin_color)
    glPushMatrix()
    glTranslatef(0.0, 1.0, 0.65) 
    glScalef(0.4, 0.3, 0.1)
    glutSolidSphere(1.0, 16, 16)
    glPopMatrix()

    # --- LÓGICA DE LOS OJOS ---
    if state.expression == 5: # ASOMBRO
        glColor3f(1.0, 1.0, 1.0)
        eye_sx, eye_sy = 2.6, 2.6
    elif state.expression == 6: # DUDA: Ojos planos horizontales
        glColor3f(0.0, 0.0, 0.0)
        eye_sx, eye_sy = 1.5, 0.2
    else: # Normal, Triste, Ira, Feliz, Pena, Enojo (Mantienen ojos redondos)
        glColor3f(0.0, 0.0, 0.0)
        eye_sx, eye_sy = 1.0, 1.0

    for x in [-0.15, 0.15]:
        glPushMatrix()
        glTranslatef(x, 1.05, 0.72)
        glScalef(eye_sx, eye_sy, 1.0)
        glutSolidSphere(0.05, 8, 8)
        glPopMatrix()

    # --- DETALLES ANIME SEGÚN EXPRESIÓN ---
    if state.expression == 1: # TRISTE: Gota de sudor/lágrima azul MÁS GRANDE (Ojitos se mantienen)
        glColor3f(0.0, 0.5, 1.0)
        glPushMatrix()
        glTranslatef(0.2, 0.9, 0.75) 
        glScalef(0.08, 0.12, 0.04) 
        glutSolidSphere(1.0, 8, 8)
        glPopMatrix()

    elif state.expression == 2: # IRA: Cejas en V negras (¡De regreso!)
        glColor3f(0.0, 0.0, 0.0)
        for x_dir in [-1, 1]:
            glPushMatrix()
            glTranslatef(0.15 * x_dir, 1.15, 0.75) 
            glRotatef(30 * x_dir, 0, 0, 1) # Inclinadas hacia el centro
            glScalef(0.1, 0.03, 0.02)
            glutSolidCube(1.0)
            glPopMatrix()

    elif state.expression == 4: # PENA: 2 cruces grandes y 3 líneas arriba
        # 2 Cruces rojas grandes
        glColor3f(1.0, 0.0, 0.0)
        for pos_x in [-0.25, 0.25]: 
            for rot in [0, 90]:
                glPushMatrix()
                glTranslatef(pos_x, 1.1, 0.72) 
                glRotatef(45 + rot, 0, 0, 1)
                glScalef(0.12, 0.04, 0.04) 
                glutSolidCube(1.0)
                glPopMatrix()
                
        # 3 Líneas negras anchas arriba
        glColor3f(0.0, 0.0, 0.0)
        for dx in [-0.08, 0.0, 0.08]:
            glPushMatrix()
            glTranslatef(-0.25 + dx, 1.35, 0.72) 
            glScalef(0.04, 0.15, 0.04) 
            glutSolidCube(1.0)
            glPopMatrix()

    elif state.expression == 7: # ENOJO: Ceja negra central horizontal
        glColor3f(0.0, 0.0, 0.0)
        glPushMatrix()
        glTranslatef(0.0, 1.15, 0.75) # Centro, arriba de los ojos
        
        glScalef(0.4, 0.05, 0.05)     
        glutSolidCube(1.0)
        glPopMatrix()
            
    glEnable(GL_LIGHTING)

    # Rejilla del casco
    glColor3fv(armor_color)
    angles = [-20, -10, 0, 10, 20] 
    for angle in angles:
        glPushMatrix()
        glTranslatef(0.0, 0.75, 0.0) 
        glRotatef(angle, 0, 1, 0)    
        glTranslatef(0.0, 0.0, 0.75) 
        glRotatef(-90, 1, 0, 0)      
        glutSolidCylinder(0.035, 0.22, 8, 1) 
        glPopMatrix()

    # Pluma tipo gota
    glColor3fv(COLOR_PLUME)
    glPushMatrix()
    glTranslatef(0.0, 1.6, -0.2) 
    glutSolidSphere(0.2, 16, 16)
    glRotatef(-90, 1, 0, 0)
    glutSolidCone(0.2, 0.5, 16, 1)
    glPopMatrix()

def draw_megaknight_full():
    glPushMatrix()
    
    # --- ANIMACIONES FÍSICAS DEL CUERPO ENTERO ---
    # Salto, Agache y Mega Smash afectan la altura Y
    total_y_offset = state.jump_y + state.crouch_y + state.smash_y
    
    if state.expression == 1: 
        total_y_offset -= 0.4 
        glScalef(1.0, 0.8, 1.0)      
        
    glTranslatef(0.0, total_y_offset, 0.0)
    
    # Girar afecta la rotación en Y
    glRotatef(state.spin_angle, 0, 1, 0)
        
    draw_legs()
    draw_body()
    draw_belt()
    draw_arms_and_maces()
    draw_head_and_helmet()
    
    glPopMatrix()