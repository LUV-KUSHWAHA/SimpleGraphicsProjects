import pygame
import sys
import random
import math
from pygame.locals import *

pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
GRAVITY = 0.5
BOX_SIZE = 300
VIEW_DISTANCE = 800
BACKGROUND_COLOR = (0, 0, 0)
WHITE = (255, 255, 255)

# Display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("3D Ball Simulation with Mouse Interaction")
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 16)

# Global camera angles
angle_x, angle_y = 0, 0

def rotate_point(x, y, z, ax, ay):
    # X-axis rotation
    cosx, sinx = math.cos(ax), math.sin(ax)
    y, z = y * cosx - z * sinx, y * sinx + z * cosx
    # Y-axis rotation
    cosy, siny = math.cos(ay), math.sin(ay)
    x, z = x * cosy - z * siny, x * siny + z * cosy
    return x, y, z

class Ball3D:
    def __init__(self):
        self.radius = random.randint(20, 30)
        self.x = random.randint(-BOX_SIZE//2, BOX_SIZE//2)
        self.y = random.randint(-BOX_SIZE//2, BOX_SIZE//2)
        self.z = random.randint(-BOX_SIZE//2, BOX_SIZE//2)
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)
        self.vz = random.uniform(-3, 3)
        self.color = (random.randint(80, 255), random.randint(80, 255), random.randint(80, 255))
        self.trajectory = []
        self.max_trajectory = 20
        self.dragged = False

    def update(self):
        if not self.dragged:
            self.vy -= GRAVITY
            self.x += self.vx
            self.y += self.vy
            self.z += self.vz

        self.trajectory.append((self.x, self.y, self.z))
        if len(self.trajectory) > self.max_trajectory:
            self.trajectory.pop(0)

        r = self.radius
        for axis, vel_attr in [('x', 'vx'), ('y', 'vy'), ('z', 'vz')]:
            val = getattr(self, axis)
            vel = getattr(self, vel_attr)
            if val - r < -BOX_SIZE//2:
                setattr(self, axis, -BOX_SIZE//2 + r)
                setattr(self, vel_attr, -vel * 0.8)
            elif val + r > BOX_SIZE//2:
                setattr(self, axis, BOX_SIZE//2 - r)
                setattr(self, vel_attr, -vel * 0.8)

    def project_3d_to_2d(self, x, y, z):
        x, y, z = rotate_point(x, y, z, angle_x, angle_y)
        factor = VIEW_DISTANCE / (VIEW_DISTANCE + z)
        x2d = x * factor + WIDTH // 2
        y2d = -y * factor + HEIGHT // 2
        r2d = self.radius * factor
        return x2d, y2d, r2d

    def draw(self, surface):
        if len(self.trajectory) > 1:
            points = [self.project_3d_to_2d(*pt)[:2] for pt in self.trajectory]
            pygame.draw.lines(surface, (*self.color, 100), False, points, 2)

        x2d, y2d, r2d = self.project_3d_to_2d(self.x, self.y, self.z)
        pygame.draw.circle(surface, self.color, (int(x2d), int(y2d)), int(r2d))
        depth_color = tuple(min(255, c + 50) for c in self.color)
        pygame.draw.circle(surface, depth_color, (int(x2d), int(y2d)), int(r2d * 0.3))

    def is_mouse_over(self, mx, my):
        x2d, y2d, r2d = self.project_3d_to_2d(self.x, self.y, self.z)
        dist = math.hypot(mx - x2d, my - y2d)
        return dist < r2d

def draw_3d_box():
    corners = [(-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),
               (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)]
    corners = [(x * BOX_SIZE//2, y * BOX_SIZE//2, z * BOX_SIZE//2) for x, y, z in corners]
    projected = [Ball3D().project_3d_to_2d(*rotate_point(x, y, z, angle_x, angle_y))[:2] for (x, y, z) in corners]

    edges = [(0, 1), (1, 2), (2, 3), (3, 0),
             (4, 5), (5, 6), (6, 7), (7, 4),
             (0, 4), (1, 5), (2, 6), (3, 7)]
    for a, b in edges:
        pygame.draw.line(screen, (100, 100, 100), projected[a], projected[b])

def main():
    global angle_x, angle_y
    balls = [Ball3D() for _ in range(5)]
    rotating, dragging = False, False
    selected_ball = None
    last_mouse_pos = (0, 0)
    rotate_sensitivity = 0.005

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse
                    rotating = True
                    last_mouse_pos = pygame.mouse.get_pos()
                elif event.button == 3:  # Right mouse
                    mx, my = pygame.mouse.get_pos()
                    for ball in reversed(balls):
                        if ball.is_mouse_over(mx, my):
                            selected_ball = ball
                            selected_ball.dragged = True
                            dragging = True
                            last_mouse_pos = pygame.mouse.get_pos()
                            break

            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    rotating = False
                elif event.button == 3:
                    dragging = False
                    if selected_ball:
                        selected_ball.dragged = False
                        selected_ball = None

            elif event.type == MOUSEMOTION:
                mx, my = pygame.mouse.get_pos()
                dx = mx - last_mouse_pos[0]
                dy = my - last_mouse_pos[1]
                if rotating:
                    angle_y -= dx * rotate_sensitivity
                    angle_x -= dy * rotate_sensitivity
                elif dragging and selected_ball:
                    selected_ball.x += dx * 0.5
                    selected_ball.z += dy * 0.5
                    selected_ball.vx = selected_ball.vz = 0
                last_mouse_pos = (mx, my)

            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    balls.append(Ball3D())
                elif event.key == K_c:
                    balls = [Ball3D() for _ in range(5)]

        for ball in balls:
            ball.update()

        screen.fill(BACKGROUND_COLOR)
        draw_3d_box()
        for ball in sorted(balls, key=lambda b: b.z, reverse=True):
            ball.draw(screen)

        for i, text in enumerate(["LMB: Rotate", "RMB: Drag Ball", "SPACE: Add Ball", "C: Reset"]):
            screen.blit(font.render(text, True, WHITE), (10, 10 + i * 20))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
