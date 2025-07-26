import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

# Initialize Pygame
pygame.init()
width, height = 800, 600
pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL)
pygame.mouse.set_visible(False)
pygame.event.set_grab(True)  # Locks mouse to window

# Camera settings
cam_pos = [0, 0, -5]  # x, y, z
cam_yaw, cam_pitch = 0, 0  # Rotation angles
move_speed = 0.1
mouse_sensitivity = 0.2

# Simple 3D Cube (for testing)
def draw_cube():
    vertices = [
        [1, -1, -1], [1, 1, -1], [-1, 1, -1], [-1, -1, -1],
        [1, -1, 1], [1, 1, 1], [-1, -1, 1], [-1, 1, 1]
    ]
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),
        (4, 5), (5, 7), (7, 6), (6, 4),
        (0, 4), (1, 5), (2, 7), (3, 6)
    ]
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()

# Handle keyboard input (WASD movement)
def handle_keyboard():
    keys = pygame.key.get_pressed()
    forward = np.array([np.sin(np.radians(cam_yaw)), 0, np.cos(np.radians(cam_yaw))])
    right = np.array([np.sin(np.radians(cam_yaw + 90)), 0, np.cos(np.radians(cam_yaw + 90))])

    if keys[K_w]:  # Forward
        cam_pos[0] += forward[0] * move_speed
        cam_pos[2] += forward[2] * move_speed
    if keys[K_s]:  # Backward
        cam_pos[0] -= forward[0] * move_speed
        cam_pos[2] -= forward[2] * move_speed
    if keys[K_a]:  # Left
        cam_pos[0] -= right[0] * move_speed
        cam_pos[2] -= right[2] * move_speed
    if keys[K_d]:  # Right
        cam_pos[0] += right[0] * move_speed
        cam_pos[2] += right[2] * move_speed

# Handle mouse look
def handle_mouse():
    global cam_yaw, cam_pitch
    rel_x, rel_y = pygame.mouse.get_rel()
    cam_yaw += rel_x * mouse_sensitivity
    cam_pitch -= rel_y * mouse_sensitivity
    cam_pitch = max(-89, min(89, cam_pitch))  # Clamp pitch

# Main loop
clock = pygame.time.Clock()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            pygame.quit()
            quit()

    handle_keyboard()
    handle_mouse()

    # Clear screen and set perspective
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    gluPerspective(45, (width / height), 0.1, 50.0)

    # Apply camera rotation & position
    glRotatef(cam_pitch, 1, 0, 0)  # Look up/down
    glRotatef(cam_yaw, 0, 1, 0)    # Look left/right
    glTranslatef(-cam_pos[0], -cam_pos[1], -cam_pos[2])  # Move camera

    # Draw a simple 3D cube (for testing)
    draw_cube()

    pygame.display.flip()
    clock.tick(60)  # 60 FPS