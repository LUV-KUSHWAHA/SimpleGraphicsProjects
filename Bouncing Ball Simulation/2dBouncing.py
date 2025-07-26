import pygame
import sys

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
GRAVITY = 0.5
ELASTICITY = 0.85
FRICTION = 0.99

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# Set up display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bouncing Ball Simulation")
clock = pygame.time.Clock()

# Ball properties
ball_radius = 40
ball_pos = [WIDTH // 4, HEIGHT // 4]
ball_vel = [30, 0]  # Initial velocity (x, y)

def main():
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Physics update
        # Apply gravity
        ball_vel[1] += GRAVITY
        
        # Update position
        ball_pos[0] += ball_vel[0]
        ball_pos[1] += ball_vel[1]
        
        # Collision with walls
        if ball_pos[0] - ball_radius < 0:  # Left wall
            ball_pos[0] = ball_radius
            ball_vel[0] = -ball_vel[0] * ELASTICITY
            ball_vel[1] *= FRICTION
        elif ball_pos[0] + ball_radius > WIDTH:  # Right wall
            ball_pos[0] = WIDTH - ball_radius
            ball_vel[0] = -ball_vel[0] * ELASTICITY
            ball_vel[1] *= FRICTION
            
        # Collision with floor/ceiling
        if ball_pos[1] + ball_radius > HEIGHT:  # Floor
            ball_pos[1] = HEIGHT - ball_radius
            ball_vel[1] = -ball_vel[1] * ELASTICITY
            ball_vel[0] *= FRICTION
        elif ball_pos[1] - ball_radius < 0:  # Ceiling
            ball_pos[1] = ball_radius
            ball_vel[1] = -ball_vel[1] * ELASTICITY
            ball_vel[0] *= FRICTION
        
        # Drawing
        screen.fill(BLACK)
        pygame.draw.circle(screen, RED, (int(ball_pos[0]), int(ball_pos[1])), ball_radius)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()