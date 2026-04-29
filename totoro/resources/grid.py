from OpenGL.GL import *
from OpenGL.GLUT import *
from totoro.actions import state


def draw_ground(r, g, b):
    glDisable(GL_LIGHTING)
    glColor3f(r, g, b)
    glBegin(GL_QUADS)
    glVertex3f(-30, 0, -30)
    glVertex3f(30, 0, -30)
    glVertex3f(30, 0, 30)
    glVertex3f(-30, 0, 30)
    glEnd()
    glEnable(GL_LIGHTING)


def draw_grid(size=20, step=1):
    glDisable(GL_LIGHTING)
    glColor3f(0.7, 0.7, 0.7)
    glBegin(GL_LINES)
    for i in range(-size, size + 1, step):
        glVertex3f(i, 0, -size)
        glVertex3f(i, 0, size)

        glVertex3f(-size, 0, i)
        glVertex3f(size, 0, i)
    glEnd()
    glEnable(GL_LIGHTING)


def draw_axes(length=3):
    glDisable(GL_LIGHTING)
    glLineWidth(3)
    glBegin(GL_LINES)

    glColor3f(1, 0, 0)
    glVertex3f(0, 0, 0)
    glVertex3f(length, 0, 0)

    glColor3f(0, 1, 0)
    glVertex3f(0, 0, 0)
    glVertex3f(0, length, 0)

    glColor3f(0, 0, 1)
    glVertex3f(0, 0, 0)
    glVertex3f(0, 0, length)

    glEnd()
    glLineWidth(1)
    glEnable(GL_LIGHTING)


def draw_tree(x, z):
    glPushMatrix()
    glTranslatef(x, 1.5, z)
    glColor3f(0.45, 0.25, 0.1)
    glutSolidCube(1.0)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(x, 3.5, z)
    glColor3f(0.1, 0.6, 0.2)
    glutSolidSphere(2.0, 20, 20)
    glPopMatrix()


def draw_box(x, y, z, sx, sy, sz, r, g, b):
    glPushMatrix()
    glTranslatef(x, y, z)
    glScalef(sx, sy, sz)
    glColor3f(r, g, b)
    glutSolidCube(1.0)
    glPopMatrix()


def draw_current_scene():
    if state.current_scene == 1: 
        draw_ground(0.5, 0.8, 0.5)
        draw_grid(30, 2)
        draw_tree(-10, -10)
        draw_tree(10, -12)
        draw_tree(-12, 8)
        draw_tree(12, 10)

    elif state.current_scene == 2: 
        draw_ground(0.2, 0.2, 0.2)
        draw_box(-8, 4, -10, 4, 8, 8, 0.25, 0.25, 0.3)
        draw_box(8, 4, -10, 4, 8, 8, 0.25, 0.25, 0.3)

    elif state.current_scene == 3: 
        draw_ground(0.6, 0.3, 0.2)
        draw_box(0, 0.5, -5, 15, 1, 10, 0.55, 0.3, 0.2)
        draw_box(-8, 5, -8, 1, 10, 1, 0.8, 0.8, 0.2)
        draw_box(8, 5, -8, 1, 10, 1, 0.8, 0.8, 0.2)

    elif state.current_scene == 4: 
        draw_ground(0.55, 0.45, 0.3)
        draw_box(-6, 0.5, -8, 3, 1, 3, 0.4, 0.4, 0.4)
        draw_box(6, 0.5, -6, 3, 1, 3, 0.4, 0.4, 0.4)
        draw_box(0, 0.5, 8, 4, 1, 2, 0.4, 0.4, 0.4)
 