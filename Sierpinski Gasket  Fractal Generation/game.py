import pygame
import sys
import random
import math

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1200, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fractal Generator: Sierpinski Gasket")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

def draw_triangle(points, color, depth):
    """Draw a triangle given 3 points"""
    pygame.draw.polygon(screen, color, points, 1)

def get_midpoint(p1, p2):
    """Return midpoint between two points"""
    return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)

def sierpinski_recursive(points, depth, max_depth):
    """Recursively draw Sierpinski triangle"""
    draw_triangle(points, BLUE, depth)
    
    if depth < max_depth:
        # Get midpoints
        a = get_midpoint(points[0], points[1])
        b = get_midpoint(points[1], points[2])
        c = get_midpoint(points[2], points[0])
        
        # Recursively draw smaller triangles
        sierpinski_recursive([points[0], a, c], depth + 1, max_depth)
        sierpinski_recursive([a, points[1], b], depth + 1, max_depth)
        sierpinski_recursive([c, b, points[2]], depth + 1, max_depth)

def sierpinski_chaos(vertices, iterations):
    """Generate Sierpinski using chaos game method"""
    # Start with a random point inside the triangle
    x, y = random.uniform(0, WIDTH), random.uniform(0, HEIGHT)
    
    for _ in range(iterations):
        # Randomly select one vertex
        vertex = random.choice(vertices)
        
        # Move halfway to the vertex
        x = (x + vertex[0]) / 2
        y = (y + vertex[1]) / 2
        
        # Draw the point
        screen.set_at((int(x), int(y)), RED)

def main():
    # Initial triangle vertices
    vertices = [
        (WIDTH // 2, 50),
        (50, HEIGHT - 50),
        (WIDTH - 50, HEIGHT - 50)
    ]
    
    # Initial parameters
    max_depth = 5
    chaos_iterations = 50000
    method = 'recursive'  # or 'chaos'
    
    clock = pygame.time.Clock()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    method = 'recursive'
                elif event.key == pygame.K_2:
                    method = 'chaos'
                elif event.key == pygame.K_UP and max_depth < 10:
                    max_depth += 1
                elif event.key == pygame.K_DOWN and max_depth > 1:
                    max_depth -= 1
                elif event.key == pygame.K_RIGHT:
                    chaos_iterations = min(chaos_iterations + 10000, 100000)
                elif event.key == pygame.K_LEFT:
                    chaos_iterations = max(chaos_iterations - 10000, 1000)
        
        screen.fill(WHITE)
        
        if method == 'recursive':
            sierpinski_recursive(vertices, 0, max_depth)
        else:
            sierpinski_chaos(vertices, chaos_iterations)
        
        # Display info
        font = pygame.font.SysFont('Arial', 20)
        info = f"Method: {method} | Depth: {max_depth} | Iterations: {chaos_iterations}"
        text = font.render(info, True, BLACK)
        screen.blit(text, (10, 10))
        
        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main()