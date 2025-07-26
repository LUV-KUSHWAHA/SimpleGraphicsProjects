import pygame
import sys
import random
import math
from pygame.locals import *

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
GRAVITY = 0.5
BACKGROUND_COLOR = (0, 0, 0)

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# Set up display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("3D Bouncing Ball Simulation (Pseudo-3D)")
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 16)

# 3D simulation parameters
BOX_SIZE = 300  # Size of the 3D space
VIEW_DISTANCE = 800  # Distance from viewer to projection plane

class Ball3D:
    def __init__(self):
        self.radius = random.randint(15, 30)
        self.x = random.randint(-BOX_SIZE//2, BOX_SIZE//2)
        self.y = random.randint(-BOX_SIZE//2, BOX_SIZE//2)
        self.z = random.randint(-BOX_SIZE//2, BOX_SIZE//2)
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)
        self.vz = random.uniform(-3, 3)
        self.color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
        self.trajectory = []
        self.max_trajectory = 20

    def update(self):
        # Apply gravity in Y axis (up is positive Y in our 3D space)
        self.vy -= GRAVITY
        
        # Update position
        self.x += self.vx
        self.y += self.vy
        self.z += self.vz
        
        # Record trajectory
        self.trajectory.append((self.x, self.y, self.z))
        if len(self.trajectory) > self.max_trajectory:
            self.trajectory.pop(0)
        
        # Collision with walls
        if self.x - self.radius < -BOX_SIZE//2:
            self.x = -BOX_SIZE//2 + self.radius
            self.vx = -self.vx * 0.8
        elif self.x + self.radius > BOX_SIZE//2:
            self.x = BOX_SIZE//2 - self.radius
            self.vx = -self.vx * 0.8
            
        if self.y - self.radius < -BOX_SIZE//2:
            self.y = -BOX_SIZE//2 + self.radius
            self.vy = -self.vy * 0.8
            self.vx *= 0.99
            self.vz *= 0.99
        elif self.y + self.radius > BOX_SIZE//2:
            self.y = BOX_SIZE//2 - self.radius
            self.vy = -self.vy * 0.8
            
        if self.z - self.radius < -BOX_SIZE//2:
            self.z = -BOX_SIZE//2 + self.radius
            self.vz = -self.vz * 0.8
        elif self.z + self.radius > BOX_SIZE//2:
            self.z = BOX_SIZE//2 - self.radius
            self.vz = -self.vz * 0.8
    
    def project_3d_to_2d(self, x, y, z):
        """Convert 3D coordinates to 2D screen coordinates using perspective projection"""
        factor = VIEW_DISTANCE / (VIEW_DISTANCE + z)
        x2d = x * factor + WIDTH // 2
        y2d = -y * factor + HEIGHT // 2  # Negative because pygame Y increases downward
        radius2d = self.radius * factor
        return x2d, y2d, radius2d
    
    def draw(self, surface):
        # Draw trajectory
        if len(self.trajectory) > 1:
            points = []
            for point in self.trajectory:
                x2d, y2d, _ = self.project_3d_to_2d(*point)
                points.append((x2d, y2d))
            if len(points) > 1:
                pygame.draw.lines(surface, (*self.color, 100), False, points, 2)
        
        # Draw ball
        x2d, y2d, radius2d = self.project_3d_to_2d(self.x, self.y, self.z)
        pygame.draw.circle(surface, self.color, (int(x2d), int(y2d)), int(radius2d))
        
        # Draw depth indicator
        depth_color = (min(255, self.color[0] + 100), min(255, self.color[1] + 100), min(255, self.color[2] + 100))
        pygame.draw.circle(surface, depth_color, (int(x2d), int(y2d)), int(radius2d * 0.3))

def draw_3d_box(surface):
    """Draw a wireframe cube representing the 3D space"""
    corners = [
        (-BOX_SIZE//2, -BOX_SIZE//2, -BOX_SIZE//2),
        (BOX_SIZE//2, -BOX_SIZE//2, -BOX_SIZE//2),
        (BOX_SIZE//2, BOX_SIZE//2, -BOX_SIZE//2),
        (-BOX_SIZE//2, BOX_SIZE//2, -BOX_SIZE//2),
        (-BOX_SIZE//2, -BOX_SIZE//2, BOX_SIZE//2),
        (BOX_SIZE//2, -BOX_SIZE//2, BOX_SIZE//2),
        (BOX_SIZE//2, BOX_SIZE//2, BOX_SIZE//2),
        (-BOX_SIZE//2, BOX_SIZE//2, BOX_SIZE//2)
    ]
    
    # Project all corners to 2D
    projected = []
    for corner in corners:
        x, y, _ = Ball3D().project_3d_to_2d(*corner)
        projected.append((x, y))
    
    # Draw edges
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),  # Back face
        (4, 5), (5, 6), (6, 7), (7, 4),  # Front face
        (0, 4), (1, 5), (2, 6), (3, 7)   # Connecting edges
    ]
    
    for edge in edges:
        pygame.draw.line(surface, (100, 100, 100), projected[edge[0]], projected[edge[1]])

def main():
    running = True
    balls = [Ball3D() for _ in range(5)]
    
    # Camera rotation
    angle_x = 0
    angle_y = 0
    rotate_speed = 0.01
    
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    balls.append(Ball3D())
                elif event.key == K_c:
                    balls = [Ball3D() for _ in range(5)]
        
        # Get keyboard state for rotation control
        keys = pygame.key.get_pressed()
        if keys[K_LEFT]:
            angle_y -= rotate_speed
        if keys[K_RIGHT]:
            angle_y += rotate_speed
        if keys[K_UP]:
            angle_x -= rotate_speed
        if keys[K_DOWN]:
            angle_x += rotate_speed
        
        # Physics update
        for ball in balls:
            ball.update()
        
        # Drawing
        screen.fill(BACKGROUND_COLOR)
        
        # Draw 3D box
        draw_3d_box(screen)
        
        # Draw balls
        for ball in sorted(balls, key=lambda b: b.z, reverse=True):  # Painter's algorithm
            ball.draw(screen)
        
        # Draw instructions
        instructions = [
            "SPACE: Add new ball",
            "C: Reset simulation",
            "Arrow keys: Rotate view",
            f"Balls: {len(balls)}"
        ]
        for i, text in enumerate(instructions):
            text_surface = font.render(text, True, WHITE)
            screen.blit(text_surface, (10, 10 + i * 20))
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()