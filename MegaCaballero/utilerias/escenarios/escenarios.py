from OpenGL.GL import *
from OpenGL.GLUT import *

# --- LOS 3 OBJETOS INTERACTIVOS (COLISIONES) ---

def dibujar_cofre(x, z):
    glPushMatrix()
    glTranslatef(x, 0.5, z) 
    glColor3f(0.5, 0.25, 0.0) 
    glutSolidCube(1.0)
    glColor3f(1.0, 0.8, 0.0) 
    glPushMatrix()
    glTranslatef(0.0, 0.5, 0.0)
    glScalef(1.05, 0.2, 1.05)
    glutSolidCube(1.0)
    glPopMatrix()
    glPopMatrix()

def dibujar_cristal_elixir(x, z):
    glPushMatrix()
    glTranslatef(x, 1.0, z) 
    glColor3f(0.8, 0.2, 1.0) 
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)
    glutSolidCone(0.5, 1.0, 16, 1)
    glPopMatrix()
    glPushMatrix()
    glRotatef(90, 1, 0, 0)
    glutSolidCone(0.5, 1.0, 16, 1)
    glPopMatrix()
    glPopMatrix()

def dibujar_tronco(x, z):
    glPushMatrix()
    # Centramos el tronco un poco mejor 
    glTranslatef(x - 1.0, 0.4, z) 
    glColor3f(0.4, 0.2, 0.0)
    glPushMatrix()
    glRotatef(90, 0, 1, 0) 
    glutSolidCylinder(0.4, 2.0, 16, 1) # Cilindro acostado en eje X
    glPopMatrix()
    
    # NUEVOS PICOS: Más cantidad, más pequeños y perfectamente pegados
    glColor3f(0.2, 0.1, 0.0)
    # Recorremos el largo del tronco 
    for x_pos in [0.2, 0.6, 1.0, 1.4, 1.8]: 
        # Ponemos picos alrededor 
        for angle in [0, 90, 180, 270]:
            glPushMatrix()
            glTranslatef(x_pos, 0.0, 0.0) # Nos paramos en el largo del tronco
            glRotatef(angle, 1, 0, 0)     # Rotamos alrededor del tronco
            glTranslatef(0.0, 0.4, 0.0)   # Subimos a la "piel" del tronco 
            glRotatef(-90, 1, 0, 0)       # Apuntamos el pico hacia afuera
            glutSolidCone(0.08, 0.25, 8, 1) # Conos chiquitos y filosos
            glPopMatrix()
    glPopMatrix()

# --- DECORACIONES ESPECÍFICAS DE CADA ARENA ---

def dibujar_hueso(x, z, rot_y=0):
    glColor3f(0.9, 0.9, 0.8) 
    glPushMatrix()
    glTranslatef(x, 0.2, z)
    glRotatef(rot_y, 0, 1, 0) 
    glRotatef(90, 0, 1, 0) 
    glutSolidCylinder(0.15, 1.5, 16, 1) 
    for end in [0.0, 1.5]:
        for offset in [-0.15, 0.15]:
            glPushMatrix()
            glTranslatef(offset, 0.0, end)
            glutSolidSphere(0.2, 16, 16)
            glPopMatrix()
    glPopMatrix()

def dibujar_pilar_morado(x, z, height=3.0):
    glColor3f(0.6, 0.1, 0.8)
    glPushMatrix()
    glTranslatef(x, 0.0, z)
    glRotatef(-90, 1, 0, 0)
    glutSolidCylinder(0.6, height, 16, 1) 
    glPopMatrix()

def dibujar_brazo_mecanico(x, z):
    glPushMatrix()
    glTranslatef(x, 0.0, z)
    glScalef(0.7, 0.7, 0.7) 
    glColor3f(0.3, 0.3, 0.3)
    glPushMatrix()
    glTranslatef(0.0, 0.2, 0.0)
    glScalef(1.5, 0.4, 1.5)
    glutSolidCube(1.0)
    glPopMatrix()
    glColor3f(0.5, 0.2, 0.2)
    glPushMatrix()
    glTranslatef(0.0, 1.5, 0.0)
    glScalef(0.6, 2.5, 0.6)
    glutSolidCube(1.0)
    glPopMatrix()
    glColor3f(0.7, 0.7, 0.7)
    glPushMatrix()
    glTranslatef(0.0, 2.5, 0.0)
    glRotatef(45, 0, 1, 0) 
    glutSolidCylinder(0.3, 3.0, 16, 1)
    glTranslatef(0.0, 0.0, 3.0)
    glColor3f(0.2, 0.2, 0.2)
    glutSolidCube(0.8)
    glPopMatrix()
    glPopMatrix()

def dibujar_caja(x, z, scale=1.0):
    """Cajas de suministros para el taller"""
    glPushMatrix()
    glTranslatef(x, 0.5 * scale, z)
    glScalef(scale, scale, scale)
    glColor3f(0.6, 0.4, 0.2) # Café madera
    glutSolidCube(1.0)
    glColor3f(0.3, 0.15, 0.0) # Borde oscuro para resaltar
    glutWireCube(1.02)
    glPopMatrix()

def dibujar_arbol_nieve(x, z, scale=1.0):
    glPushMatrix()
    glTranslatef(x, 0.0, z)
    glScalef(scale, scale, scale) 
    glColor3f(0.4, 0.2, 0.1)
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)
    glutSolidCylinder(0.3, 1.5, 16, 1)
    glPopMatrix()
    glColor3f(0.9, 0.95, 1.0)
    glPushMatrix()
    glTranslatef(0.0, 1.0, 0.0)
    glRotatef(-90, 1, 0, 0)
    glutSolidCone(1.2, 3.0, 4, 1) 
    glPopMatrix()
    glPopMatrix()

def dibujar_camino_lava():
    glColor3f(0.9, 0.2, 0.0) 
    glBegin(GL_QUADS)
    glNormal3f(0.0, 1.0, 0.0)
    glVertex3f(-2.0, 0.01, -15.0)
    glVertex3f(-2.0, 0.01,  15.0)
    glVertex3f( 2.0, 0.01,  15.0)
    glVertex3f( 2.0, 0.01, -15.0)
    glEnd()

def dibujar_roca_volcanica(x, z, scale_x, scale_y, scale_z):
    glColor3f(0.15, 0.15, 0.15) 
    glPushMatrix()
    glTranslatef(x, 0.3, z) 
    glScalef(scale_x, scale_y, scale_z) 
    glutSolidSphere(0.8, 16, 16)
    glPopMatrix()

def dibujar_trofeo_gigante(x, z):
    glPushMatrix()
    glTranslatef(x, 0.0, z)
    glScalef(0.8, 0.8, 0.8) 
    glColor3f(1.0, 0.8, 0.0) 
    glPushMatrix()
    glTranslatef(0.0, 1.0, 0.0)
    glRotatef(90, 1, 0, 0)
    glutSolidCone(1.5, 1.0, 16, 1)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(0.0, 1.0, 0.0)
    glRotatef(-90, 1, 0, 0)
    glutSolidCylinder(0.4, 1.5, 16, 1)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(0.0, 3.0, 0.0)
    glutSolidSphere(1.2, 32, 32)
    glPopMatrix()
    glPopMatrix()

def dibujar_torre_princesa(x, z, is_blue=True):
    """Torres del fondo con banderas (Azul o Roja)"""
    glPushMatrix()
    glTranslatef(x, 0.0, z)
    
    # 1. Base cuadrada alta
    glColor3f(0.7, 0.7, 0.7) # Piedra gris
    glPushMatrix()
    glTranslatef(0.0, 1.5, 0.0)
    glScalef(1.5, 3.0, 1.5)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # 2. Techo apachurrado
    glColor3f(0.3, 0.3, 0.3) # Gris oscuro
    glPushMatrix()
    glTranslatef(0.0, 3.1, 0.0)
    glScalef(1.8, 0.4, 1.8)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # 3. Poste de la bandera
    glColor3f(0.6, 0.4, 0.2) # Madera
    glPushMatrix()
    glTranslatef(0.0, 3.3, 0.0)
    glRotatef(-90, 1, 0, 0)
    glutSolidCylinder(0.05, 1.5, 8, 1)
    glPopMatrix()
    
    # 4. Bandera (Triángulo)
    if is_blue: glColor3f(0.1, 0.3, 1.0)
    else:       glColor3f(1.0, 0.2, 0.2)
    
    glBegin(GL_TRIANGLES)
    # Poste 
    glVertex3f(0.0, 4.6, 0.0) # Punta superior pegada al poste
    glVertex3f(1.0, 4.2, 0.0) # Punta de la bandera ondeando
    glVertex3f(0.0, 3.8, 0.0) # Punta inferior pegada al poste
    glEnd()
    
    glPopMatrix()


# --- MANEJO CENTRAL DE ESCENARIOS ---

def establecer_fondo(scenario_id):
    if scenario_id == 1:   glClearColor(0.5, 0.8, 1.0, 1.0) 
    elif scenario_id == 2: glClearColor(0.9, 0.6, 0.2, 1.0) 
    elif scenario_id == 3: glClearColor(0.2, 0.1, 0.4, 1.0) 
    elif scenario_id == 4: glClearColor(0.4, 0.4, 0.4, 1.0) 
    elif scenario_id == 5: glClearColor(0.7, 0.9, 1.0, 1.0) 
    elif scenario_id == 6: glClearColor(0.4, 0.0, 0.0, 1.0) 
    elif scenario_id == 7: glClearColor(0.0, 0.0, 0.1, 1.0) 

def dibujar_escenario_actual(scenario_id):
    if scenario_id == 1:   glColor3f(0.3, 0.8, 0.3) 
    elif scenario_id == 2: glColor3f(0.9, 0.8, 0.4) 
    elif scenario_id == 3: glColor3f(0.5, 0.2, 0.6) 
    elif scenario_id == 4: glColor3f(0.3, 0.15, 0.0) 
    elif scenario_id == 5: glColor3f(0.9, 0.9, 1.0) 
    elif scenario_id == 6: glColor3f(0.2, 0.2, 0.2) 
    elif scenario_id == 7: glColor3f(0.8, 0.7, 0.1) 

    glBegin(GL_QUADS)
    glNormal3f(0.0, 1.0, 0.0)
    glVertex3f(-15.0, 0.0, -15.0)
    glVertex3f(-15.0, 0.0,  15.0)
    glVertex3f( 15.0, 0.0,  15.0)
    glVertex3f( 15.0, 0.0, -15.0)
    glEnd()

    
    dibujar_cofre(2.0, -1.5)          
    dibujar_cristal_elixir(-2.5, -2.0) 
    dibujar_tronco(-2.5, 2.0)             

  
    if scenario_id == 2: 
        dibujar_hueso(-4.0, -3.0, rot_y=45)
        dibujar_hueso(5.0, -1.0, rot_y=-30)
        dibujar_hueso(-3.5, 4.0, rot_y=15)
        dibujar_hueso(4.5, -4.0, rot_y=80)
        
    elif scenario_id == 3: 
        # Pilar frontal derecho 
        dibujar_pilar_morado(5.0, 4.0, height=3.0) 
        dibujar_pilar_morado(4.5, -4.0, height=4.0)
        dibujar_pilar_morado(-5.5, -3.0, height=2.5)
        dibujar_pilar_morado(-4.5, 4.5, height=1.5)
        
    elif scenario_id == 4: 
        # Brazo original movido más atrás, y añadimos un segundo brazo a la izquierda
        dibujar_brazo_mecanico(4.5, -5.0)
        dibujar_brazo_mecanico(-5.5, -4.0)
        # Agregamos las cajas
        dibujar_caja(-4.0, 1.0, scale=1.5)
        dibujar_caja(-4.5, -1.0)
        dibujar_caja(3.5, 2.0, scale=1.2)
        
    elif scenario_id == 5: 
        # Árboles empujados hacia los bordes 
        dibujar_arbol_nieve(-5.0, -3.5, scale=1.2)
        dibujar_arbol_nieve(5.5, -2.0, scale=0.8)
        dibujar_arbol_nieve(-4.5, 4.5, scale=1.0)
        dibujar_arbol_nieve(4.5, 4.5, scale=1.5)
        dibujar_arbol_nieve(0.0, -6.0, scale=0.9)
        
    elif scenario_id == 6: 
        dibujar_camino_lava()
        # Rocas 
        dibujar_roca_volcanica(5.5, -2.0, scale_x=1.5, scale_y=0.8, scale_z=1.0)
        dibujar_roca_volcanica(-5.0, 3.0, scale_x=1.0, scale_y=0.5, scale_z=1.5)
        dibujar_roca_volcanica(4.8, 4.5, scale_x=1.2, scale_y=1.0, scale_z=0.8)
        dibujar_roca_volcanica(-5.5, -3.5, scale_x=1.8, scale_y=0.6, scale_z=1.2)
        
    elif scenario_id == 7: 
        dibujar_trofeo_gigante(0.0, -2.0)
        # Torres de las princesas 
        dibujar_torre_princesa(-4.0, -7.0, is_blue=True)   # Torre Azul
        dibujar_torre_princesa(4.0, -7.0, is_blue=False)   # Torre Roja