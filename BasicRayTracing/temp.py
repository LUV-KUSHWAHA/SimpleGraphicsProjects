import numpy as np
import matplotlib.pyplot as plt

def ray_sphere_intersect(ray_origin, ray_dir, sphere_center, radius):
    oc = ray_origin - sphere_center
    a = np.dot(ray_dir, ray_dir)
    b = 2.0 * np.dot(oc, ray_dir)
    c = np.dot(oc, oc) - radius * radius
    discriminant = b * b - 4 * a * c
    return discriminant > 0  # True if ray hits sphere

# Camera & Scene Setup
width, height = 200, 200
img = np.zeros((height, width, 3))
sphere_pos = np.array([0, 0, -5])
sphere_radius = 1.0
light_dir = np.array([1, 1, -1]).astype(np.float32)
light_dir /= np.linalg.norm(light_dir)

# Ray Casting Loop
for y in range(height):
    for x in range(width):
        ray_dir = np.array([x - width / 2, y - height / 2, -height]).astype(np.float32)
        ray_dir /= np.linalg.norm(ray_dir)
        if ray_sphere_intersect(np.array([0, 0, 0]), ray_dir, sphere_pos, sphere_radius):
            normal = np.array([x - width / 2, y - height / 2, -height]) - sphere_pos
            normal /= np.linalg.norm(normal)
            diffuse = max(0, np.dot(normal, light_dir))
            img[y, x] = [diffuse, diffuse, diffuse]  # Grayscale shading

plt.imshow(img)
plt.show()