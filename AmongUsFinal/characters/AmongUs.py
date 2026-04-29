from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math
from AmongUsFinal.actions import state


#  Among Us  –  modelo 3D en OpenGL/GLUT
COLOR_SUIT      = (0.85, 0.08, 0.08)
COLOR_SUIT_DARK = (0.50, 0.03, 0.03)
COLOR_VISOR     = (0.60, 0.88, 1.00)
COLOR_PACK      = (0.65, 0.05, 0.05)
COLOR_HAT       = (0.55, 0.10, 0.75)
COLOR_HAT_BALL  = (0.20, 0.40, 1.00)

def _c(r, g, b):
    glColor3f(r, g, b)


# ── CUERPO ────────────────────────────────────
def draw_body():
    # Cilindro central del torso
    _c(*COLOR_SUIT)
    glPushMatrix()
    glTranslatef(0.0, -0.45, 0.0)
    glRotatef(-90, 1, 0, 0)
    quad = gluNewQuadric()
    gluCylinder(quad, 0.44, 0.42, 0.85, 32, 32)
    gluDeleteQuadric(quad)
    glPopMatrix()

    # Tapa inferior del cilindro
    glPushMatrix()
    glTranslatef(0.0, -0.45, 0.0)
    glRotatef(90, 1, 0, 0)
    quad = gluNewQuadric()
    gluDisk(quad, 0, 0.44, 32, 1)
    gluDeleteQuadric(quad)
    glPopMatrix()

    # Semiesfera inferior (barriga)
    glPushMatrix()
    glTranslatef(0.0, -0.45, 0.0)
    glScalef(1.05, 0.50, 1.05)
    glutSolidSphere(0.44, 32, 32)
    glPopMatrix()

    # Semiesfera superior (hombros)
    glPushMatrix()
    glTranslatef(0.0, 0.40, 0.0)
    glScalef(1.0, 0.45, 1.0)
    glutSolidSphere(0.43, 32, 32)
    glPopMatrix()




# ── CABEZA ────────────────────────────────────
def draw_head():
    _c(*COLOR_SUIT)
    glPushMatrix()
    glTranslatef(0.0, 0.72, 0.04)
    glScalef(1.02, 1.08, 1.0)
    glutSolidSphere(0.46, 32, 32)
    glPopMatrix()


# ── VISERA ────────────────────────────────────
def draw_visor():
    visor_color = COLOR_VISOR
    scale_x = 0.68
    scale_y = 0.45
    brillo_scale_x = 0.22
    brillo_scale_y = 0.15

    # Variables de control para detalles anime
    draw_tear = False
    draw_anime_embarrassed = False
    draw_angry_brows = False

    # 🎭 LÓGICA DE LAS EXPRESIONES
    if state.expression == "angry":      
        visor_color = (0.9, 0.1, 0.1)    
        draw_angry_brows = True          
        
    elif state.expression == "sad":      
        visor_color = (0.2, 0.3, 0.5)    
        draw_tear = True                 
        
    elif state.expression == "suspicious": 
        scale_y = 0.15                   
        
    elif state.expression == "surprised":  
        scale_x = 0.85 
        scale_y = 0.70 
        brillo_scale_x = 0.45
        brillo_scale_y = 0.40
        
    elif state.expression == "embarrassed":
        visor_color = (1.0, 1.0, 1.0)    # Visor Blanco puro
        draw_anime_embarrassed = True    
        scale_y = 0.20                   # Visor apachurrado

    # --- 1. DIBUJO DEL CRISTAL BASE DEL VISOR (CON LUZ) ---
    _c(*visor_color)
    glPushMatrix()
    glTranslatef(0.0, 0.76, 0.50)
    glScalef(scale_x, scale_y, 0.10)
    glutSolidSphere(0.46, 32, 32)
    glPopMatrix()

    # --- 2. DETALLES ESTILO ANIME ---
    # APAGAMOS LA LUZ TEMPORALMENTE para obtener colores puros sin brillo blanco
    glDisable(GL_LIGHTING) 

    if draw_anime_embarrassed:
        
        # Ojos cerrados tipo anime: > < 
        _c(1.0, 0.2, 0.6) 
        
        # Ojo izquierdo (>)
        glPushMatrix()
        glTranslatef(-0.25, 0.76, 0.55) 
        glRotatef(45, 0, 0, 1)          
        glScalef(0.03, 0.10, 0.05)      
        glutSolidSphere(1.0, 16, 16)
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(-0.25, 0.76, 0.55)
        glRotatef(-45, 0, 0, 1)
        glScalef(0.03, 0.10, 0.05)
        glutSolidSphere(1.0, 16, 16)
        glPopMatrix()
        
        # Ojo derecho (<)
        glPushMatrix()
        glTranslatef(0.25, 0.76, 0.55)
        glRotatef(45, 0, 0, 1)
        glScalef(0.03, 0.10, 0.05)
        glutSolidSphere(1.0, 16, 16)
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(0.25, 0.76, 0.55)
        glRotatef(-45, 0, 0, 1)
        glScalef(0.03, 0.10, 0.05)
        glutSolidSphere(1.0, 16, 16)
        glPopMatrix()

        # Líneas de pena (\\\) arriba del visor
        _c(0.1, 0.1, 0.1) # Negro puro
        for dx in [-0.15, 0.0, 0.15]:
            glPushMatrix()
            glTranslatef(dx, 1.02, 0.42)  
            glRotatef(-30, 0, 0, 1)       
            glScalef(0.02, 0.12, 0.03)    
            glutSolidSphere(1.0, 16, 16)
            glPopMatrix()
            
    elif draw_tear:
        _c(0.2, 0.6, 1.0) # Azul puro para la lágrima
        glPushMatrix()
        glTranslatef(0.35, 0.65, 0.54) 
        glRotatef(-15, 0, 0, 1)        
        glScalef(0.08, 0.16, 0.05)     
        glutSolidSphere(1.0, 16, 16)
        glPopMatrix()
        
    elif draw_angry_brows:
        _c(0.1, 0.1, 0.1) # Cejas negras puras
        glPushMatrix()
        glTranslatef(-0.2, 0.95, 0.52)
        glRotatef(-30, 0, 0, 1)
        glScalef(0.15, 0.04, 0.05)
        glutSolidSphere(1.0, 16, 16)
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(0.2, 0.95, 0.52)
        glRotatef(30, 0, 0, 1)
        glScalef(0.15, 0.04, 0.05)
        glutSolidSphere(1.0, 16, 16)
        glPopMatrix()

    # VOLVEMOS A PRENDER LA LUZ PARA EL RESTO DEL CUERPO
    glEnable(GL_LIGHTING)

    # --- 3. BRILLO DEL VISOR NORMAL ---
    if not draw_anime_embarrassed:
        _c(0.88, 0.97, 1.0)
        glPushMatrix()
        glTranslatef(-0.10, 0.86, 0.54)
        glScalef(brillo_scale_x, brillo_scale_y, 0.05)
        glutSolidSphere(0.30, 16, 16)
        glPopMatrix()

# ── MOCHILA ───────────────────────────────────
def draw_backpack():
    _c(*COLOR_PACK)

    glPushMatrix()
    glTranslatef(0.0, 0.10, -0.52)
    glScalef(0.65, 0.90, 0.42)
    glutSolidSphere(0.46, 28, 28)
    glPopMatrix()

    _c(*COLOR_SUIT_DARK)
    glPushMatrix()
    glTranslatef(0.0, 0.10, -0.46)
    glRotatef(90, 1, 0, 0)
    quad = gluNewQuadric()
    gluCylinder(quad, 0.16, 0.16, 0.10, 16, 4)
    gluDeleteQuadric(quad)
    glPopMatrix()



# ── PIERNAS ───────────────────────────────────
def draw_legs():
    # ANIMACIÓN 1: CAMINAR
    leg_angle = 0
    if state.walking:
        # math.sin genera oscilación suave (adelante y atrás)
        leg_angle = math.sin(state.animation_angle) * 35 

    for i, dx in enumerate([-0.20, 0.20]):
        # Una pierna va hacia adelante, la otra hacia atrás
        current_angle = leg_angle if i == 0 else -leg_angle
        
        glPushMatrix()
        glTranslatef(dx, -0.50, 0.0)      # Pivote en la cadera
        glRotatef(current_angle, 1, 0, 0) # Rotación de la zancada
        glTranslatef(0.0, -0.38, 0.0)     # Bajar resto de la pierna
        
        # Muslo
        _c(*COLOR_SUIT_DARK)
        glPushMatrix()
        glRotatef(-90, 1, 0, 0)
        quad = gluNewQuadric()
        gluCylinder(quad, 0.17, 0.15, 0.38, 20, 8)
        gluDeleteQuadric(quad)
        glPopMatrix()

        # Pie
        _c(*COLOR_SUIT)
        glPushMatrix()
        glTranslatef(0.0, -0.02, 0.10)
        glScalef(1.0, 0.40, 1.35)
        glutSolidSphere(0.18, 20, 10)
        glPopMatrix()
        
        glPopMatrix()

# ── GORRITO ───────────────────────────────────
# Cono encima de la cabeza + esfera en la punta
def draw_hat():
    # Base del gorro (cono)
    _c(*COLOR_HAT)
    glPushMatrix()
    glTranslatef(0.0, 1.18, 0.04)
    glRotatef(-90, 1, 0, 0)            
    glutSolidCone(0.28, 0.42, 24, 16)
    glPopMatrix()

    # Esfera en la punta del cono
    _c(*COLOR_HAT_BALL)
    glPushMatrix()
    glTranslatef(0.0, 1.62, 0.04)
    glutSolidSphere(0.08, 16, 16)
    glPopMatrix()


# ── FUNCIÓN PRINCIPAL ─────────────────────────
def draw_amongus_full():
    glPushMatrix()
    
    # --- ANIMACIONES GLOBALES (REACCIONES) ---
    if state.reaction_type == "jump":
        # ANIMACIÓN 2: SALTAR 
        progress = (state.reaction_timer / state.reaction_duration) * math.pi
        y_offset = math.sin(progress) * 1.5
        glTranslatef(0.0, y_offset, 0.0)
        
    elif state.reaction_type == "spin":
        # ANIMACIÓN 3: GIRO (360 grados)
        progress = state.reaction_timer / state.reaction_duration
        glRotatef(progress * 360, 0, 1, 0)
        
    elif state.reaction_type == "shake":
        # ANIMACIÓN 4: TEMBLAR (Vibración lateral rápida)
        x_offset = math.sin(state.reaction_timer * 1.5) * 0.1
        glTranslatef(x_offset, 0.0, 0.0)
        
    elif state.reaction_type == "vent":
        # ANIMACIÓN 5: ALCANTARILLA / AGACHARSE
        progress = state.reaction_timer / state.reaction_duration
        # Se aplasta hasta un 50% de su altura y vuelve a subir
        squat = 1.0 - (math.sin(progress * math.pi) * 0.5) 
        glTranslatef(0.0, -0.45 * (1.0 - squat), 0.0) # Pegado al suelo
        glScalef(1.0, squat, 1.0)

   
    if state.shaking:
        x_offset = math.sin(state.shake_timer * 1.5) * 0.1
        glTranslatef(x_offset, 0.0, 0.0)    

    # Inclinación adicional si está triste (Expresión corporal)
    if state.expression == "sad":
        glRotatef(15, 1, 0, 0) 
        glTranslatef(0.0, -0.1, 0.1)

    # Renderizado base
    glTranslatef(0.0, 0.45, 0.0) 
    
    draw_backpack()
    draw_body()
    draw_legs()
    draw_head()
    draw_hat()
    draw_visor()

    glPopMatrix()

