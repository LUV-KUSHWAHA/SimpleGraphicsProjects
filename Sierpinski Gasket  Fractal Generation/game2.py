import pygame
import sys
import random
import math
import numpy as np
from pygame import gfxdraw

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1200, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Advanced Fractal Generator")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# Fractal types
SIERPINSKI = 0
MANDELBROT = 1
JULIA = 2

class FractalGenerator:
    def __init__(self):
        self.fractal_type = SIERPINSKI
        self.max_depth = 5
        self.iterations = 100
        self.color_scheme = 0
        self.animate = False
        self.animation_speed = 1
        self.zoom = 1.0
        self.pan_x, self.pan_y = 0, 0
        self.julia_c = complex(-0.7, 0.27015)
        self.mandelbrot_rect = [-2, -1.5, 3, 3]  # x, y, width, height
        
        # Sierpinski vertices
        self.sierpinski_vertices = [
            (WIDTH // 2, 50),
            (50, HEIGHT - 50),
            (WIDTH - 50, HEIGHT - 50)
        ]
        
        # Color palettes
        self.palettes = [
            [(x, x, 255) for x in range(256)],  # Blue gradient
            [(255, x, x) for x in range(256)],  # Red gradient
            [(x, 255, x) for x in range(256)],  # Green gradient
            [(x, x, x) for x in range(256)],    # Grayscale
            [(x, 255-x, 255) for x in range(256)]  # Cyan-purple
        ]
        
        # Animation state
        self.animation_frame = 0
    
    def get_color(self, value, max_value):
        """Get color from palette based on normalized value"""
        palette = self.palettes[self.color_scheme]
        idx = min(int(value / max_value * 255), 255)
        return palette[idx]
    
    def draw_sierpinski_recursive(self, points, depth):
        """Recursive Sierpinski triangle"""
        if depth >= self.max_depth:
            return
            
        # Draw current triangle
        pygame.draw.polygon(screen, self.get_color(depth, self.max_depth), points, 1)
        
        # Get midpoints
        a = ((points[0][0] + points[1][0]) / 2, (points[0][1] + points[1][1]) / 2)
        b = ((points[1][0] + points[2][0]) / 2, (points[1][1] + points[2][1]) / 2)
        c = ((points[2][0] + points[0][0]) / 2, (points[2][1] + points[0][1]) / 2)
        
        # Recursively draw smaller triangles
        self.draw_sierpinski_recursive([points[0], a, c], depth + 1)
        self.draw_sierpinski_recursive([a, points[1], b], depth + 1)
        self.draw_sierpinski_recursive([c, b, points[2]], depth + 1)
    
    def draw_sierpinski_chaos(self):
        """Chaos game method for Sierpinski"""
        # Start with random point
        x, y = random.uniform(0, WIDTH), random.uniform(0, HEIGHT)
        
        for _ in range(self.iterations):
            vertex = random.choice(self.sierpinski_vertices)
            x = (x + vertex[0]) / 2
            y = (y + vertex[1]) / 2
            
            # Apply zoom and pan
            px = (x - self.pan_x) * self.zoom + WIDTH/2
            py = (y - self.pan_y) * self.zoom + HEIGHT/2
            
            if 0 <= px < WIDTH and 0 <= py < HEIGHT:
                screen.set_at((int(px), int(py)), self.get_color(_, self.iterations))
    
    def mandelbrot(self, c, max_iter):
        """Mandelbrot set calculation"""
        z = 0
        for n in range(max_iter):
            if abs(z) > 2:
                return n
            z = z*z + c
        return max_iter
    
    def julia(self, z, max_iter):
        """Julia set calculation"""
        c = self.julia_c
        for n in range(max_iter):
            if abs(z) > 2:
                return n
            z = z*z + c
        return max_iter
    
    def draw_mandelbrot(self):
        """Render Mandelbrot set with zoom/pan"""
        xmin, ymin, w, h = self.mandelbrot_rect
        xmax = xmin + w
        ymax = ymin + h
        
        # Apply zoom
        center_x, center_y = xmin + w/2, ymin + h/2
        w, h = w/self.zoom, h/self.zoom
        xmin, ymin = center_x - w/2, center_y - h/2
        xmax, ymax = center_x + w/2, center_y + h/2
        
        # Apply pan
        xmin += self.pan_x / WIDTH * w
        xmax += self.pan_x / WIDTH * w
        ymin += self.pan_y / HEIGHT * h
        ymax += self.pan_y / HEIGHT * h
        
        for px in range(WIDTH):
            for py in range(HEIGHT):
                # Convert pixel to complex number
                x = xmin + (xmax - xmin) * px / WIDTH
                y = ymin + (ymax - ymin) * py / HEIGHT
                c = complex(x, y)
                
                # Compute
                if self.fractal_type == MANDELBROT:
                    m = self.mandelbrot(c, self.iterations)
                else:  # Julia
                    m = self.julia(c, self.iterations)
                
                # Color based on iterations
                color = self.get_color(m, self.iterations)
                screen.set_at((px, py), color)
    
    def update_animation(self):
        """Update animation parameters"""
        if not self.animate:
            return
            
        self.animation_frame += self.animation_speed
        
        if self.fractal_type == SIERPINSKI:
            # Animate the chaos game
            self.iterations = min(self.iterations + 100, 100000)
        elif self.fractal_type == JULIA:
            # Animate Julia parameter
            angle = self.animation_frame * 0.01
            r = 0.7885
            self.julia_c = complex(r * math.cos(angle), r * math.sin(angle))
        elif self.fractal_type == MANDELBROT:
            # Slowly zoom in
            self.zoom = min(self.zoom * 1.01, 1000)
    
    def draw(self):
        """Draw the current fractal"""
        screen.fill(BLACK)
        
        if self.fractal_type == SIERPINSKI:
            if self.animate or random.random() < 0.1:  # Occasionally use chaos for variety
                self.draw_sierpinski_chaos()
            else:
                self.draw_sierpinski_recursive(self.sierpinski_vertices, 0)
        else:
            self.draw_mandelbrot()
        
        self.draw_ui()
    
    def draw_ui(self):
        """Draw user interface"""
        font = pygame.font.SysFont('Arial', 20)
        
        # Fractal type
        types = ["Sierpinski", "Mandelbrot", "Julia"]
        text = font.render(f"Fractal: {types[self.fractal_type]}", True, WHITE)
        screen.blit(text, (10, 10))
        
        # Parameters
        params = f"Iterations: {self.iterations} | Zoom: {self.zoom:.2f}x"
        text = font.render(params, True, WHITE)
        screen.blit(text, (10, 40))
        
        # Animation
        anim_text = "ANIMATION: ON" if self.animate else "ANIMATION: OFF"
        text = font.render(anim_text, True, WHITE)
        screen.blit(text, (10, 70))
        
        # Instructions
        instr = "1-3: Fractal Type | Up/Down: Depth/Iter | +/-: Zoom | WASD: Pan | C: Colors | Space: Toggle Anim"
        text = font.render(instr, True, WHITE)
        screen.blit(text, (10, HEIGHT - 30))

def main():
    generator = FractalGenerator()
    clock = pygame.time.Clock()
    
    dragging = False
    last_pos = (0, 0)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    generator.fractal_type = SIERPINSKI
                elif event.key == pygame.K_2:
                    generator.fractal_type = MANDELBROT
                elif event.key == pygame.K_3:
                    generator.fractal_type = JULIA
                elif event.key == pygame.K_UP:
                    if generator.fractal_type == SIERPINSKI:
                        generator.max_depth = min(generator.max_depth + 1, 10)
                    else:
                        generator.iterations = min(generator.iterations + 10, 1000)
                elif event.key == pygame.K_DOWN:
                    if generator.fractal_type == SIERPINSKI:
                        generator.max_depth = max(generator.max_depth - 1, 1)
                    else:
                        generator.iterations = max(generator.iterations - 10, 10)
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    generator.zoom *= 1.1
                elif event.key == pygame.K_MINUS:
                    generator.zoom /= 1.1
                elif event.key == pygame.K_c:
                    generator.color_scheme = (generator.color_scheme + 1) % len(generator.palettes)
                elif event.key == pygame.K_SPACE:
                    generator.animate = not generator.animate
                elif event.key == pygame.K_w:
                    generator.pan_y -= 10 / generator.zoom
                elif event.key == pygame.K_s:
                    generator.pan_y += 10 / generator.zoom
                elif event.key == pygame.K_a:
                    generator.pan_x -= 10 / generator.zoom
                elif event.key == pygame.K_d:
                    generator.pan_x += 10 / generator.zoom
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    dragging = True
                    last_pos = event.pos
                elif event.button == 4:  # Mouse wheel up
                    generator.zoom *= 1.1
                elif event.button == 5:  # Mouse wheel down
                    generator.zoom /= 1.1
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    dragging = False
            
            elif event.type == pygame.MOUSEMOTION:
                if dragging:
                    dx = event.pos[0] - last_pos[0]
                    dy = event.pos[1] - last_pos[1]
                    generator.pan_x += dx / generator.zoom
                    generator.pan_y += dy / generator.zoom
                    last_pos = event.pos
        
        generator.update_animation()
        generator.draw()
        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main()