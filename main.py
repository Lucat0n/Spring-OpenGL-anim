import math
import numpy as np
from PIL import Image
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *

EDGES = 12

SCREEN_FRAMES = 60
SCREEN_HEIGHT = 800
SCREEN_WIDTH = 800

SPRING_BASE_HEIGHT = 0.15
SPRING_DIAMETER_DIV = 20
SPRING_OFFSET_Y = -0.2
SPRING_SCALE = 0.06

COMPRESSION_OFFSET = 0.06
COMPRESSION_SCALING = 0.4

k = 1

BALL_MASS = 0.2
g = 9.81

velocity = 0.0

textures = {}

SPRING_LENGTH = 10
current_spring_length = 18
SPR_LEN = 0.6 * 8 * math.pi

base_vertices = (
    (-7,-7, 18),
    (-7,7,18),
    (7,7,18),
    (7,-7,18),
    (-7, -7, 20),
    (-7, 7, 20),
    (7, 7, 20),
    (7, -7, 20),
)

base_surfaces = (
    (0,1,2,3), #bottom
    (1,2,6,5),
    (4,5,1,0),
    (0,3,7,4),
    (2,3,7,6),
    (4,5,6,7)
)

def load_texture(file):
    img = Image.open(file)
    img_data = np.array(list(img.getdata()), np.int8)
    textID = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, textID)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    #glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img.size[0], img.size[1], 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
    return textID

def draw():
    glClearColor(0, 0, 0, 1)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glPushMatrix()
    glTranslatef(0.0,SPRING_OFFSET_Y,0)
    glRotatef(-90, 1, 0, 0)
    draw_base()
    draw_spring_ends()
    draw_spring()
    glPushMatrix()
    glTranslatef(0, 0, SPR_LEN - current_spring_length * COMPRESSION_SCALING + (SPR_LEN - current_spring_length) * 0.01)
    draw_sphere()
    glPopMatrix()
    glPopMatrix()
    glFlush()
    glutSwapBuffers()

def draw_base():
    glBindTexture(GL_TEXTURE_2D, textures["wood"])
    glEnable(GL_TEXTURE_2D)
    for surface in base_surfaces:
        glBegin(GL_QUADS)
        n = 0
        for vertex in surface:
            if n == 0:
                xv = 0.0
                yv = 0.0
            elif n == 1:
                xv = 1.0
                yv = 0.0
            elif n == 2:
                xv = 1.0
                yv = 1.0
            else:
                xv = 0.0
                yv = 1.0
            glTexCoord2f(xv, yv)
            glVertex3fv(base_vertices[vertex])
            n+=1
        glEnd()

def draw_sphere():
    glPushMatrix()
    glTranslatef(0,0,-4.5)
    glTranslatef(0, 0, (SPR_LEN - current_spring_length * COMPRESSION_SCALING) * 0.1)
    quadric = gluNewQuadric()
    gluQuadricDrawStyle(quadric, GLU_FILL)
    gluQuadricTexture(quadric, True)
    gluQuadricNormals(quadric, GLU_SMOOTH)
    gluSphere(quadric,3,25,25)
    glPopMatrix()

def draw_spring():
    t = np.linspace(0, 8 * math.pi, 80)
    u_arr = np.linspace(0, 2*math.pi, EDGES)
    u = 0.5
    glPushMatrix()

    glTranslatef(0, 0, SPR_LEN - current_spring_length * 0.4)
    glTranslatef(0, 0, (SPR_LEN - current_spring_length * 0.4) * COMPRESSION_OFFSET)
    glScalef(1, 1, current_spring_length / SPR_LEN * 0.4)

    points_cache = []
    for ti in t:
        cache = []

        for u_val in u_arr:
            point = (math.cos(ti)*(3.0+math.cos(u_val)), math.sin(ti) * (3.0+math.cos(u_val)), 0.6*ti+math.sin(u_val))
            cache.append(point)

        cache.append(cache[0])
        if points_cache:
            draw_quads([cache, points_cache])

        points_cache = cache
    glPopMatrix()

def draw_spring_ends():
    upper_vertices_list = [[] for x in range(5)]
    bottom_vertices_list = [[] for x in range(5)]

    for i in range(EDGES):
        rot = i/EDGES*2*math.pi
        upper_vertices_list[0].append((math.sin(rot), math.cos(rot),18))
        upper_vertices_list[1].append((math.sin(rot), math.cos(rot), 16))
        upper_vertices_list[2].append((1, math.cos(rot), math.sin(rot)+15))
        upper_vertices_list[3].append((2, math.cos(rot), math.sin(rot)+15))
        upper_vertices_list[4].append((math.cos(0)*(3.0+math.cos(rot)), math.sin(0) * (3.0+math.cos(rot)), 0.6*8*math.pi+math.sin(rot)))
        bottom_vertices_list[0].append((math.cos(0)*(3.0+math.cos(rot)), math.sin(0) * (3.0+math.cos(rot)), math.sin(rot)))
        bottom_vertices_list[1].append((3, math.cos(-rot), math.sin(-rot)))
        bottom_vertices_list[2].append((1, math.cos(-rot), math.sin(-rot)))
        bottom_vertices_list[3].append((math.sin(rot), math.cos(rot), -1))
        bottom_vertices_list[4].append((math.sin(rot), math.cos(rot), -4))

    for i in range(6):
        bottom_vertices_list[0].append(bottom_vertices_list[0].pop(0))

    for l1, l2 in zip(upper_vertices_list, bottom_vertices_list):
        l1.append(l1[0])
        l2.append(l2[0])

    glBindTexture(GL_TEXTURE_2D, textures["metal"])
    glEnable(GL_TEXTURE_2D)
    draw_quads(upper_vertices_list[:2])
    glPushMatrix()
    glTranslatef(0, 0, SPR_LEN - current_spring_length * COMPRESSION_SCALING)
    glTranslatef(0, 0, (SPR_LEN - current_spring_length * COMPRESSION_SCALING) * COMPRESSION_OFFSET)
    glScalef(1, 1, current_spring_length / SPR_LEN * COMPRESSION_SCALING)
    draw_quads(upper_vertices_list[1:])
    glPopMatrix()
    glPushMatrix()
    glTranslatef(0, 0, SPR_LEN - current_spring_length * COMPRESSION_SCALING)
    glTranslatef(0, 0, (SPR_LEN - current_spring_length * COMPRESSION_SCALING) * COMPRESSION_OFFSET)
    glScalef(1, 1, current_spring_length / SPR_LEN * COMPRESSION_SCALING)
    draw_quads(bottom_vertices_list)
    glPopMatrix()

def draw_quads(vertices_list):
    for l1, l2 in zip(vertices_list[:-1], vertices_list[1:]):
        for u,b in zip(zip(l1[:-1],l1[1:]),zip(l2[:-1],l2[1:])):
            glBegin(GL_QUADS)
            glTexCoord2f(0, 0)
            glVertex3fv(b[0])
            glTexCoord2f(1, 0)
            glVertex3fv(u[0])
            glTexCoord2f(1, 1)
            glVertex3fv(u[1])
            glTexCoord2f(0, 1)
            glVertex3fv(b[1])
            glEnd()

def keyboard(key, x, y):
    ch = key.decode("utf-8")
    if ch not in ['w', 'a', 's', 'd', 'z', 'x', 'q', 'e', 'r', 'f', 'c', 'v']:
        return
    glMatrixMode(GL_PROJECTION)
    if ch == 'w':
        glTranslatef(0,0,1)
    elif ch == 's':
        glTranslatef(0,0,-1)
    elif ch == 'a':
        glTranslatef(-1,0,0)
    elif ch == 'd':
        glTranslatef(1,0,0)
    elif ch == 'r':
        glTranslatef(0,1,0)
    elif ch == 'f':
        glTranslatef(0,-1,0)
    elif ch == 'z':
        glRotatef(5, 0, 1, 0)
    elif ch == 'x':
        glRotatef(-5, 0, 1, 0)
    elif ch == 'q':
        glRotatef(-5, 0, 0, 1)
    elif ch == 'e':
        glRotatef(5, 0, 0, 1)
    elif ch == 'c':
        glRotatef(-5, 1, 0, 0)
    elif ch == 'v':
        glRotatef(5, 1, 0, 0)
    glMatrixMode(GL_MODELVIEW)

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(SCREEN_WIDTH, SCREEN_HEIGHT)
    glutCreateWindow('Lab 2')
    textures["metal"] = load_texture("metal.jpg")
    textures["wood"] = load_texture("wood.jpg")
    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    gluPerspective(60, SCREEN_WIDTH/SCREEN_HEIGHT, 1, 55)
    glTranslatef(0,0,-40) #front
    glMatrixMode(GL_MODELVIEW)
    glutKeyboardFunc(keyboard)
    glutDisplayFunc(draw)
    glutTimerFunc(16, timer, 1)
    glutMainLoop()

def timer(value):
    global current_spring_length
    global velocity
    delta_X = current_spring_length/SPR_LEN
    Q = -k * delta_X
    F = g * BALL_MASS
    velocity += Q + F
    current_spring_length += velocity
    glutTimerFunc(16, timer, 1)
    glutPostRedisplay()

if __name__ == '__main__':
    main()