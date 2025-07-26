import pygame
import sys
import random
import math

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
GRAVITY = 0.5
BACKGROUND_COLOR = (0, 0, 0)

# Ball materials with different properties
MATERIALS = {
    "rubber": {"elasticity": 0.8, "friction": 0.99, "color": (255, 0, 0)},
    "glass": {"elasticity": 0.95, "friction": 0.998, "color": (0, 100, 255)},
    "steel": {"elasticity": 0.7, "friction": 0.95, "color": (200, 200, 200)},
    "wood": {"elasticity": 0.6, "friction": 0.9, "color": (139, 69, 19)}
}

# Set up display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Advanced Bouncing Ball Simulation")
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 16)

class Ball:
    def __init__(self, x, y, material="rubber"):
        self.radius = random.randint(15, 30)
        self.x = x
        self.y = y
        self.vx = random.uniform(-5, 5)
        self.vy = random.uniform(-5, 0)
        self.material = material
        self.trajectory = []
        self.max_trajectory = 50
        
    @property
    def elasticity(self):
        return MATERIALS[self.material]["elasticity"]
    
    @property
    def friction(self):
        return MATERIALS[self.material]["friction"]
    
    @property
    def color(self):
        return MATERIALS[self.material]["color"]
    
    def update(self):
        # Apply gravity
        self.vy += GRAVITY
        
        # Update position
        self.x += self.vx
        self.y += self.vy
        
        # Record trajectory (for drawing)
        self.trajectory.append((self.x, self.y))
        if len(self.trajectory) > self.max_trajectory:
            self.trajectory.pop(0)
        
        # Collision with walls
        if self.x - self.radius < 0:  # Left wall
            self.x = self.radius
            self.vx = -self.vx * self.elasticity
            self.vy *= self.friction
        elif self.x + self.radius > WIDTH:  # Right wall
            self.x = WIDTH - self.radius
            self.vx = -self.vx * self.elasticity
            self.vy *= self.friction
            
        # Collision with floor/ceiling
        if self.y + self.radius > HEIGHT:  # Floor
            self.y = HEIGHT - self.radius
            self.vy = -self.vy * self.elasticity
            self.vx *= self.friction
        elif self.y - self.radius < 0:  # Ceiling
            self.y = self.radius
            self.vy = -self.vy * self.elasticity
            self.vx *= self.friction
    
    def draw(self, surface):
        # Draw trajectory
        if len(self.trajectory) > 1:
            pygame.draw.lines(surface, (*self.color, 50), False, self.trajectory, 2)
        
        # Draw ball
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        
        # Draw material label
        text = font.render(self.material, True, (255, 255, 255))
        surface.blit(text, (int(self.x) - text.get_width() // 2, int(self.y) - self.radius - 20))

def check_collision(ball1, ball2):
    dx = ball1.x - ball2.x
    dy = ball1.y - ball2.y
    distance = math.sqrt(dx*dx + dy*dy)
    
    if distance < ball1.radius + ball2.radius:
        # Calculate collision response (simplified)
        angle = math.atan2(dy, dx)
        
        # Move balls apart
        overlap = (ball1.radius + ball2.radius - distance) / 2
        ball1.x += overlap * math.cos(angle)
        ball1.y += overlap * math.sin(angle)
        ball2.x -= overlap * math.cos(angle)
        ball2.y -= overlap * math.sin(angle)
        
        # Calculate velocities
        total_elasticity = (ball1.elasticity + ball2.elasticity) / 2
        total_friction = (ball1.friction + ball2.friction) / 2
        
        # Exchange velocities (simplified physics)
        ball1.vx, ball2.vx = ball2.vx * total_elasticity, ball1.vx * total_elasticity
        ball1.vy, ball2.vy = ball2.vy * total_elasticity, ball1.vy * total_elasticity
        
        # Apply friction
        ball1.vx *= total_friction
        ball1.vy *= total_friction
        ball2.vx *= total_friction
        ball2.vy *= total_friction

def main():
    running = True
    balls = []
    dragging = False
    drag_start = (0, 0)
    selected_material = "rubber"
    
    # Create some initial balls
    for _ in range(3):
        material = random.choice(list(MATERIALS.keys()))
        balls.append(Ball(
            random.randint(100, WIDTH-100),
            random.randint(100, HEIGHT-100),
            material
        ))
    
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    dragging = True
                    drag_start = event.pos
                elif event.button == 3:  # Right click
                    # Change material on right click
                    materials = list(MATERIALS.keys())
                    current_idx = materials.index(selected_material)
                    selected_material = materials[(current_idx + 1) % len(materials)]
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and dragging:
                    dragging = False
                    end_pos = event.pos
                    # Create new ball with velocity based on drag
                    vx = (drag_start[0] - end_pos[0]) / 10
                    vy = (drag_start[1] - end_pos[1]) / 10
                    new_ball = Ball(drag_start[0], drag_start[1], selected_material)
                    new_ball.vx = vx
                    new_ball.vy = vy
                    balls.append(new_ball)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Add a random ball on space
                    material = random.choice(list(MATERIALS.keys()))
                    balls.append(Ball(
                        random.randint(50, WIDTH-50),
                        random.randint(50, HEIGHT-50),
                        material
                    ))
                elif event.key == pygame.K_c:
                    # Clear all balls
                    balls = []
        
        # Physics update
        for ball in balls:
            ball.update()
        
        # Ball-ball collisions
        for i in range(len(balls)):
            for j in range(i+1, len(balls)):
                check_collision(balls[i], balls[j])
        
        # Drawing
        screen.fill(BACKGROUND_COLOR)
        
        # Draw instructions
        instructions = [
            "Left click and drag to throw a ball",
            "Right click to change material",
            "Space to add random ball",
            "C to clear all balls",
            f"Current material: {selected_material}"
        ]
        for i, text in enumerate(instructions):
            text_surface = font.render(text, True, (255, 255, 255))
            screen.blit(text_surface, (10, 10 + i * 20))
        
        # Draw drag line if dragging
        if dragging:
            pygame.draw.line(screen, (255, 255, 255), drag_start, pygame.mouse.get_pos(), 2)
        
        # Draw balls
        for ball in balls:
            ball.draw(screen)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()