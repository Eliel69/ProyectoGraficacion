
from OpenGL.GL import *

def draw(size=12, step=1.0, color=(0.18,0.18,0.26)):
    glDisable(GL_LIGHTING)
    glColor3f(*color)
    glLineWidth(0.8)
    glBegin(GL_LINES)
    x = -size
    while x <= size:
        glVertex3f(x,0.01,-size); glVertex3f(x,0.01,size)
        x += step
    z = -size
    while z <= size:
        glVertex3f(-size,0.01,z); glVertex3f(size,0.01,z)
        z += step
    glEnd()
    glLineWidth(1.0)
    glEnable(GL_LIGHTING)