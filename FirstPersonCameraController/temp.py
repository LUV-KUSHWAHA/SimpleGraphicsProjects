import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import time
import math

# Initialize Pygame
pygame.init()
width, height = 800, 600
screen = pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL)
pygame.display.set_caption("Enhanced First Person Controller")
pygame.event.set_grab(True)
pygame.mouse.set_visible(False)

# Camera
cam_pos = np.array([0.0, 0.0, 3.0])
cam_yaw = 0.0
cam_pitch = 0.0
move_speed = 5.0
mouse_sensitivity = 0.1
mouse_locked = True

# Lighting setup
def init_lighting():
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_POSITION, [0, 5, 5, 1])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1, 1, 1, 1])
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

# Cube with colors
def draw_colored_cube():
    vertices = [
        [1, -1, -1], [1, 1, -1], [-1, 1, -1], [-1, -1, -1],
        [1, -1, 1], [1, 1, 1], [-1, -1, 1], [-1, 1, 1]
    ]
    faces = [
        (0, 1, 2, 3), (3, 2, 7, 6), (6, 7, 5, 4),
        (4, 5, 1, 0), (1, 5, 7, 2), (4, 0, 3, 6)
    ]
    colors = [
        (1, 0, 0), (0, 1, 0), (0, 0, 1),
        (1, 1, 0), (1, 0, 1), (0, 1, 1)
    ]
    glBegin(GL_QUADS)
    for i, face in enumerate(faces):
        glColor3fv(colors[i])
        for vertex in face:
            glVertex3fv(vertices[vertex])
    glEnd()

# Calculate direction vector from yaw and pitch
def get_camera_direction():
    x = math.cos(math.radians(cam_pitch)) * math.sin(math.radians(cam_yaw))
    y = math.sin(math.radians(cam_pitch))
    z = -math.cos(math.radians(cam_pitch)) * math.cos(math.radians(cam_yaw))
    return np.array([x, y, z])

# Main loop
clock = pygame.time.Clock()
init_lighting()

last_time = time.time()

while True:
    delta_time = time.time() - last_time
    last_time = time.time()
    
    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            pygame.quit()
            quit()
        elif event.type == MOUSEBUTTONDOWN and event.button == 3:  # Right click
            mouse_locked = not mouse_locked
            pygame.event.set_grab(mouse_locked)
            pygame.mouse.set_visible(not mouse_locked)

    # Mouse movement
    if mouse_locked:
        rel = pygame.mouse.get_rel()
        cam_yaw += rel[0] * mouse_sensitivity
        cam_pitch -= rel[1] * mouse_sensitivity
        cam_pitch = max(-89.0, min(89.0, cam_pitch))

    # Movement
    keys = pygame.key.get_pressed()
    direction = get_camera_direction()
    right = np.cross(direction, [0, 1, 0])
    up = np.cross(right, direction)

    if keys[K_w]:
        cam_pos += direction * move_speed * delta_time
    if keys[K_s]:
        cam_pos -= direction * move_speed * delta_time
    if keys[K_a]:
        cam_pos -= right * move_speed * delta_time
    if keys[K_d]:
        cam_pos += right * move_speed * delta_time
    if keys[K_SPACE]:
        cam_pos += up * move_speed * delta_time
    if keys[K_LSHIFT]:
        cam_pos -= up * move_speed * delta_time

    # OpenGL rendering
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(70, width / height, 0.1, 100.0)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    center = cam_pos + get_camera_direction()
    gluLookAt(*cam_pos, *center, 0, 1, 0)

    # Draw scene
    draw_colored_cube()
    pygame.display.flip()
    clock.tick(60)
