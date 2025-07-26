import pygame
import numpy as np
import math
import random

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Enhanced 2D Ray Casting with Soft Shadows")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 100, 100)
GREEN = (100, 255, 100)
BLUE = (100, 100, 255)
GRAY = (80, 80, 80)
LIGHT_COLOR = (255, 255, 200)
AMBIENT = 0.2  # Ambient light level

# Light Source
class Light:
    def __init__(self, pos):
        self.pos = list(pos)
        self.radius = 10
        self.rays = 360  # Number of rays to cast
        self.penumbra_rays = 4  # Rays per main ray for soft shadows
        self.strength = 1.5  # Light intensity
        
    def move(self, pos):
        self.pos = list(pos)

# Objects (Circles)
class CircleObject:
    def __init__(self, pos, radius, color):
        self.pos = list(pos)
        self.radius = radius
        self.color = color
        self.original_color = list(color)
        
    def update_lighting(self, light_factor):
        # Apply lighting to object color
        self.color = (
            min(255, int(self.original_color[0] * light_factor)),
            min(255, int(self.original_color[1] * light_factor)),
            min(255, int(self.original_color[2] * light_factor))
        )

# Walls (Lines)
class Wall:
    def __init__(self, start, end, color=GRAY):
        self.start = list(start)
        self.end = list(end)
        self.color = color
        self.thickness = 3

# Scene Setup
light = Light([WIDTH // 2, HEIGHT // 2])
objects = [
    CircleObject([300, 200], 50, RED),
    CircleObject([500, 400], 70, GREEN),
    CircleObject([200, 450], 40, BLUE),
    CircleObject([400, 300], 60, (200, 200, 0))
]

walls = [
    Wall([100, 100], [700, 100]),
    Wall([700, 100], [700, 500]),
    Wall([700, 500], [100, 500]),
    Wall([100, 500], [100, 100]),
    Wall([250, 150], [350, 250]),  # Additional diagonal wall
]

# Helper Functions
def distance(p1, p2):
    return math.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)

def point_on_line_segment(p, line_start, line_end):
    # Check if point p is on the line segment between start and end
    cross = (line_end[0] - line_start[0]) * (p[1] - line_start[1]) - (line_end[1] - line_start[1]) * (p[0] - line_start[0])
    if abs(cross) > 1e-12:
        return False
    
    min_x = min(line_start[0], line_end[0])
    max_x = max(line_start[0], line_end[0])
    min_y = min(line_start[1], line_end[1])
    max_y = max(line_start[1], line_end[1])
    
    return (min_x <= p[0] <= max_x) and (min_y <= p[1] <= max_y)

def ray_intersects_circle(ray_origin, ray_dir, circle_pos, circle_radius):
    # Vector from ray origin to circle center
    oc = (circle_pos[0] - ray_origin[0], circle_pos[1] - ray_origin[1])
    
    # Projection of oc onto ray direction
    proj = oc[0] * ray_dir[0] + oc[1] * ray_dir[1]
    
    # Closest point on ray to circle center
    closest = (
        ray_origin[0] + ray_dir[0] * proj,
        ray_origin[1] + ray_dir[1] * proj
    )
    
    # Distance from closest point to circle center
    dist = distance(closest, circle_pos)
    
    if dist < circle_radius:
        # Calculate intersection points
        d = math.sqrt(circle_radius**2 - dist**2)
        t1 = proj - d
        t2 = proj + d
        
        # Return the closest intersection point
        t = min(t1, t2) if t1 > 0 and t2 > 0 else max(t1, t2)
        if t > 0:
            return (
                ray_origin[0] + ray_dir[0] * t,
                ray_origin[1] + ray_dir[1] * t
            )
    return None

def ray_intersects_line(ray_origin, ray_dir, line_start, line_end):
    # Line segment vector
    line_vec = (line_end[0] - line_start[0], line_end[1] - line_start[1])
    
    # Ray-Line intersection math
    denominator = ray_dir[0] * line_vec[1] - ray_dir[1] * line_vec[0]
    
    if abs(denominator) < 1e-6:
        return None  # Parallel lines
    
    t = ((line_start[0] - ray_origin[0]) * line_vec[1] - (line_start[1] - ray_origin[1]) * line_vec[0]) / denominator
    u = -((ray_origin[0] - line_start[0]) * ray_dir[1] - (ray_origin[1] - line_start[1]) * ray_dir[0]) / denominator
    
    if 0 <= u <= 1 and t > 0:
        return (
            ray_origin[0] + ray_dir[0] * t,
            ray_origin[1] + ray_dir[1] * t
        )
    return None

def get_normal(point, obj):
    if isinstance(obj, CircleObject):
        # For circles, normal points from center to surface
        dx = point[0] - obj.pos[0]
        dy = point[1] - obj.pos[1]
        length = math.sqrt(dx*dx + dy*dy)
        return (dx/length, dy/length) if length > 0 else (0, 1)
    else:
        # For walls, normal is perpendicular to the wall
        dx = obj.end[0] - obj.start[0]
        dy = obj.end[1] - obj.start[1]
        length = math.sqrt(dx*dx + dy*dy)
        # Rotate 90 degrees clockwise and normalize
        return (dy/length, -dx/length) if length > 0 else (0, 1)

def calculate_lighting():
    # Reset object colors
    for obj in objects:
        obj.color = obj.original_color
    
    # Calculate lighting for each object
    for obj in objects:
        # Vector from light to object center
        light_dir = (obj.pos[0] - light.pos[0], obj.pos[1] - light.pos[1])
        dist = math.sqrt(light_dir[0]**2 + light_dir[1]**2)
        if dist == 0:
            continue
            
        light_dir = (light_dir[0]/dist, light_dir[1]/dist)
        
        # Get normal at closest point (approximation)
        normal = get_normal(obj.pos, obj)
        
        # Lambertian diffuse term (dot product)
        diffuse = max(0, light_dir[0] * normal[0] + light_dir[1] * normal[1])
        
        # Shadow calculation (soft shadows)
        visible = 0
        total_samples = light.penumbra_rays
        
        # Jittered sampling for penumbra
        for i in range(total_samples):
            # Add small random offset to ray direction
            angle = math.atan2(light_dir[1], light_dir[0])
            angle += random.uniform(-0.1, 0.1)  # Small jitter
            jittered_dir = (math.cos(angle), math.sin(angle))
            
            # Cast shadow ray
            in_shadow = False
            
            # Check against other objects
            for other in objects:
                if other == obj:
                    continue
                if ray_intersects_circle(light.pos, jittered_dir, other.pos, other.radius):
                    in_shadow = True
                    break
            
            # Check against walls
            if not in_shadow:
                for wall in walls:
                    if ray_intersects_line(light.pos, jittered_dir, wall.start, wall.end):
                        in_shadow = True
                        break
            
            if not in_shadow:
                visible += 1
        
        shadow_factor = visible / total_samples
        
        # Distance attenuation (light falls off with distance)
        attenuation = min(1, 100 / (dist**0.5))
        
        # Final light calculation
        light_factor = AMBIENT + (diffuse * shadow_factor * attenuation * light.strength)
        obj.update_lighting(light_factor)

# Main Game Loop
running = True
clock = pygame.time.Clock()
dragging_obj = None

while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEMOTION:
            if pygame.mouse.get_pressed()[0]:  # Left mouse button
                mouse_pos = pygame.mouse.get_pos()
                if dragging_obj:
                    dragging_obj.pos = list(mouse_pos)
                else:
                    light.move(mouse_pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if event.button == 1:  # Left click
                # Check if clicking on an object to drag it
                for obj in objects:
                    if distance(mouse_pos, obj.pos) < obj.radius:
                        dragging_obj = obj
                        break
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left click release
                dragging_obj = None
    
    # Clear screen
    screen.fill(BLACK)
    
    # Calculate lighting
    calculate_lighting()
    
    # Draw walls
    for wall in walls:
        pygame.draw.line(screen, wall.color, wall.start, wall.end, wall.thickness)
    
    # Draw objects with lighting
    for obj in objects:
        pygame.draw.circle(screen, obj.color, (int(obj.pos[0]), int(obj.pos[1])), obj.radius)
        # Draw outline
        pygame.draw.circle(screen, (50, 50, 50), (int(obj.pos[0]), int(obj.pos[1])), obj.radius, 1)
    
    # Draw light source
    pygame.draw.circle(screen, LIGHT_COLOR, (int(light.pos[0]), int(light.pos[1])), light.radius)
    pygame.draw.circle(screen, (200, 200, 100), (int(light.pos[0]), int(light.pos[1])), light.radius + 5, 1)
    
    # Display instructions
    font = pygame.font.SysFont('Arial', 16)
    text = font.render("Click and drag to move light. Click objects to move them.", True, WHITE)
    screen.blit(text, (10, 10))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()