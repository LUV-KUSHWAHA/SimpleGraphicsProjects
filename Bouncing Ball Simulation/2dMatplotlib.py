import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Circle

# Constants
WIDTH, HEIGHT = 10, 10
GRAVITY = 0.1
ELASTICITY = 0.8
FRICTION = 0.99

# Initial conditions
ball_pos = np.array([2.0, 8.0])
ball_vel = np.array([0.5, 0.0])
ball_radius = 0.5

# Set up figure
fig, ax = plt.subplots(figsize=(8, 8))
ax.set_xlim(0, WIDTH)
ax.set_ylim(0, HEIGHT)
ax.set_aspect('equal')
ax.grid(True)

# Create ball
ball = Circle((ball_pos[0], ball_pos[1]), ball_radius, fc='r')
ax.add_patch(ball)

def update(frame):
    global ball_pos, ball_vel
    
    # Apply gravity
    ball_vel[1] -= GRAVITY
    
    # Update position
    ball_pos += ball_vel
    
    # Collision detection
    if ball_pos[0] - ball_radius < 0:
        ball_pos[0] = ball_radius
        ball_vel[0] = -ball_vel[0] * ELASTICITY
        ball_vel[1] *= FRICTION
    elif ball_pos[0] + ball_radius > WIDTH:
        ball_pos[0] = WIDTH - ball_radius
        ball_vel[0] = -ball_vel[0] * ELASTICITY
        ball_vel[1] *= FRICTION
        
    if ball_pos[1] - ball_radius < 0:
        ball_pos[1] = ball_radius
        ball_vel[1] = -ball_vel[1] * ELASTICITY
        ball_vel[0] *= FRICTION
    elif ball_pos[1] + ball_radius > HEIGHT:
        ball_pos[1] = HEIGHT - ball_radius
        ball_vel[1] = -ball_vel[1] * ELASTICITY
        ball_vel[0] *= FRICTION
    
    # Update ball position
    ball.center = (ball_pos[0], ball_pos[1])
    
    return ball,

ani = animation.FuncAnimation(fig, update, frames=range(1000), 
                              interval=20, blit=True)
plt.show()