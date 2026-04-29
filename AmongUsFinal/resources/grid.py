from OpenGL.GL import *

def draw_grid(size=20, step=1):
    
    glDisable(GL_LIGHTING)   # para que el grid tenga color uniforme
    glColor3f(0.7, 0.7, 0.7)

    glBegin(GL_LINES)

    for i in range(-size, size + 1, step):

        # líneas paralelas al eje Z
        glVertex3f(i, 0, -size)
        glVertex3f(i, 0, size)

        # líneas paralelas al eje X
        glVertex3f(-size, 0, i)
        glVertex3f(size, 0, i)

    glEnd()

    glEnable(GL_LIGHTING)


def draw_axes(length=3):

    glDisable(GL_LIGHTING)

    glLineWidth(3)

    glBegin(GL_LINES)

    # eje X (rojo)
    glColor3f(1,0,0)
    glVertex3f(0,0,0)
    glVertex3f(length,0,0)

    # eje Y (verde)
    glColor3f(0,1,0)
    glVertex3f(0,0,0)
    glVertex3f(0,length,0)

    # eje Z (azul)
    glColor3f(0,0,1)
    glVertex3f(0,0,0)
    glVertex3f(0,0,length)

    glEnd()

    glLineWidth(1)

    glEnable(GL_LIGHTING)