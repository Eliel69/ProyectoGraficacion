# resources/grid.py
from OpenGL.GL import *

def draw_grid(size=20, step=2):
    glDisable(GL_LIGHTING)
    glColor3f(0.6, 0.6, 0.6)
    glBegin(GL_LINES)
    for i in range(-size, size + 1, step):
        glVertex3f(i, 0, -size);  glVertex3f(i, 0,  size)
        glVertex3f(-size, 0, i);  glVertex3f( size, 0, i)
    glEnd()
    glEnable(GL_LIGHTING)

def draw_axes(length=3):
    glDisable(GL_LIGHTING)
    glLineWidth(3)
    glBegin(GL_LINES)
    glColor3f(1,0,0); glVertex3f(0,0,0); glVertex3f(length,0,0)
    glColor3f(0,1,0); glVertex3f(0,0,0); glVertex3f(0,length,0)
    glColor3f(0,0,1); glVertex3f(0,0,0); glVertex3f(0,0,length)
    glEnd()
    glLineWidth(1)
    glEnable(GL_LIGHTING)