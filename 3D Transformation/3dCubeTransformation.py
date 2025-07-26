import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import time

class CubeVisualizer:
    def __init__(self):
        pygame.init()
        self.display = (1200, 700)
        pygame.display.set_caption("Advanced 3D Transformation Explorer")
        pygame.display.set_mode(self.display, DOUBLEBUF | OPENGL | RESIZABLE)
        self.clock = pygame.time.Clock()

        # Camera state
        self.camera_distance = 10.0
        self.camera_angle = [30, 30]
        self.last_mouse_pos = None

        # Cube transformation state
        self.translate = np.zeros(3)
        self.scale = np.ones(3)
        self.rotation = np.zeros(3)
        self.auto_rotate = False

        # Toggles
        self.wireframe = False
        self.lighting = False
        self.culling = False
        self.grid = False
        self.texture_enabled = False

        # Projection state
        self.perspective = True

        self.rotation_speed = 1.0
        self.move_speed = 0.1
        self.scale_speed = 0.05

        self.init_geometry()
        self.init_opengl()
        self.init_texture()

    def init_geometry(self):
        self.vertices = np.array([
            [1, 1, -1],
            [1, -1, -1],
            [-1, -1, -1],
            [-1, 1, -1],
            [1, 1, 1],
            [1, -1, 1],
            [-1, -1, 1],
            [-1, 1, 1]
        ], dtype=np.float32)

        self.edges = (
            (0,1), (1,2), (2,3), (3,0),
            (4,5), (5,6), (6,7), (7,4),
            (0,4), (1,5), (2,6), (3,7)
        )

        self.faces = (
            (0,1,2,3),
            (4,5,6,7),
            (0,1,5,4),
            (2,3,7,6),
            (0,3,7,4),
            (1,2,6,5)
        )

        self.face_colors = [
            (1,0,0,0.6),
            (0,1,0,0.6),
            (0,0,1,0.6),
            (1,1,0,0.6),
            (1,0,1,0.6),
            (0,1,1,0.6)
        ]

    def init_opengl(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glClearColor(0.1, 0.1, 0.1, 1.0)
        self.set_projection()

    def init_texture(self):
        self.texture_id = glGenTextures(1)
        checkerboard = np.zeros((64, 64, 3), dtype=np.uint8)
        checkerboard[::2, ::2] = 255
        checkerboard[1::2, 1::2] = 255

        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, 64, 64, 0, GL_RGB, GL_UNSIGNED_BYTE, checkerboard)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    def set_projection(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspect = self.display[0] / self.display[1]
        if self.perspective:
            gluPerspective(45, aspect, 0.1, 100.0)
        else:
            glOrtho(-5*aspect, 5*aspect, -5, 5, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                return False
            if event.type == VIDEORESIZE:
                self.display = (event.w, event.h)
                pygame.display.set_mode(self.display, DOUBLEBUF | OPENGL | RESIZABLE)
                glViewport(0, 0, event.w, event.h)
                self.set_projection()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return False
                elif event.key == K_TAB:
                    self.wireframe = not self.wireframe
                    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE if self.wireframe else GL_FILL)
                elif event.key == K_l:
                    self.toggle_lighting()
                elif event.key == K_c:
                    self.toggle_culling()
                elif event.key == K_SPACE:
                    self.auto_rotate = not self.auto_rotate
                elif event.key == K_g:
                    self.grid = not self.grid
                elif event.key == K_t:
                    self.texture_enabled = not self.texture_enabled
                elif event.key == K_p:
                    self.perspective = True
                    self.set_projection()
                elif event.key == K_o:
                    self.perspective = False
                    self.set_projection()
                elif event.key == K_s:
                    self.save_screenshot()
                elif event.key == K_m:
                    self.print_matrix()
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 4:
                    self.camera_distance = max(2, self.camera_distance - 0.5)
                elif event.button == 5:
                    self.camera_distance += 0.5
                elif event.button == 1:
                    self.last_mouse_pos = pygame.mouse.get_pos()
            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    self.last_mouse_pos = None
            if event.type == MOUSEMOTION:
                if self.last_mouse_pos:
                    x, y = pygame.mouse.get_pos()
                    dx = x - self.last_mouse_pos[0]
                    dy = y - self.last_mouse_pos[1]
                    self.camera_angle[0] += dx * 0.3
                    self.camera_angle[1] += dy * 0.3
                    self.camera_angle[1] = max(-89, min(89, self.camera_angle[1]))
                    self.last_mouse_pos = (x, y)

        keys = pygame.key.get_pressed()
        if keys[K_LEFT]: self.translate[0] -= self.move_speed
        if keys[K_RIGHT]: self.translate[0] += self.move_speed
        if keys[K_UP]: self.translate[1] += self.move_speed
        if keys[K_DOWN]: self.translate[1] -= self.move_speed
        if keys[K_PAGEUP]: self.translate[2] += self.move_speed
        if keys[K_PAGEDOWN]: self.translate[2] -= self.move_speed

        if keys[K_w]: self.rotation[0] += self.rotation_speed
        if keys[K_s]: self.rotation[0] -= self.rotation_speed
        if keys[K_a]: self.rotation[1] += self.rotation_speed
        if keys[K_d]: self.rotation[1] -= self.rotation_speed
        if keys[K_q]: self.rotation[2] += self.rotation_speed
        if keys[K_e]: self.rotation[2] -= self.rotation_speed

        if keys[K_EQUALS]: self.scale += self.scale_speed
        if keys[K_MINUS]: self.scale = np.maximum(0.1, self.scale - self.scale_speed)

        return True

    def toggle_lighting(self):
        self.lighting = not self.lighting
        if self.lighting:
            glEnable(GL_LIGHTING)
            glEnable(GL_LIGHT0)
            glLightfv(GL_LIGHT0, GL_POSITION, [1, 1, 1, 0])
            glLightfv(GL_LIGHT0, GL_DIFFUSE, [1, 1, 1, 1])
            glEnable(GL_COLOR_MATERIAL)
            glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        else:
            glDisable(GL_LIGHTING)
            glDisable(GL_LIGHT0)
            glDisable(GL_COLOR_MATERIAL)

    def toggle_culling(self):
        self.culling = not self.culling
        if self.culling:
            glEnable(GL_CULL_FACE)
            glCullFace(GL_BACK)
        else:
            glDisable(GL_CULL_FACE)

    def save_screenshot(self):
        width, height = self.display
        glPixelStorei(GL_PACK_ALIGNMENT, 1)
        data = glReadPixels(0, 0, width, height, GL_RGB, GL_UNSIGNED_BYTE)
        image = pygame.image.fromstring(data, (width, height), "RGB")
        image = pygame.transform.flip(image, False, True)
        pygame.image.save(image, "screenshot.png")
        print("\nScreenshot saved as screenshot.png")

    def print_matrix(self):
        matrix = glGetFloatv(GL_MODELVIEW_MATRIX)
        print("\nCurrent ModelView Matrix:")
        for row in matrix:
            print(row)

    def draw_grid(self):
        glColor3f(0.5, 0.5, 0.5)
        glBegin(GL_LINES)
        for i in range(-10, 11):
            glVertex3f(i, 0, -10)
            glVertex3f(i, 0, 10)
            glVertex3f(-10, 0, i)
            glVertex3f(10, 0, i)
        glEnd()

    def draw_cube(self):
        if self.texture_enabled:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.texture_id)

        if not self.wireframe:
            glBegin(GL_QUADS)
            for i, face in enumerate(self.faces):
                glColor4fv(self.face_colors[i])
                for vertex in face:
                    if self.texture_enabled:
                        glTexCoord2f((vertex % 2), ((vertex//2) % 2))
                    glVertex3fv(self.vertices[vertex])
            glEnd()

        if self.texture_enabled:
            glDisable(GL_TEXTURE_2D)

        glColor3f(1, 1, 1)
        glBegin(GL_LINES)
        for edge in self.edges:
            for vertex in edge:
                glVertex3fv(self.vertices[vertex])
        glEnd()

    def update(self, dt):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        azimuth = np.radians(self.camera_angle[0])
        elevation = np.radians(self.camera_angle[1])
        x = self.camera_distance * np.cos(elevation) * np.sin(azimuth)
        y = self.camera_distance * np.sin(elevation)
        z = self.camera_distance * np.cos(elevation) * np.cos(azimuth)
        gluLookAt(x, y, z, 0, 0, 0, 0, 1, 0)

        if self.grid:
            self.draw_grid()

        glPushMatrix()
        glTranslatef(*self.translate)
        glScalef(*self.scale)
        glRotatef(self.rotation[0], 1, 0, 0)
        glRotatef(self.rotation[1], 0, 1, 0)
        glRotatef(self.rotation[2], 0, 0, 1)
        self.draw_cube()
        glPopMatrix()

        if self.auto_rotate:
            self.rotation[1] += self.rotation_speed * dt * 60

        pygame.display.flip()

    def run(self):
        running = True
        last_time = time.time()
        while running:
            dt = time.time() - last_time
            last_time = time.time()
            running = self.handle_events()
            self.update(dt)
            fps = self.clock.get_fps()
            print(f"\rFPS: {fps:.1f} | AutoRotate: {self.auto_rotate} | Lighting: {self.lighting} | Culling: {self.culling} | Wireframe: {self.wireframe} | Grid: {self.grid} | Texture: {self.texture_enabled} | Projection: {'Perspective' if self.perspective else 'Orthographic'}", end="")
            self.clock.tick(60)
        pygame.quit()

if __name__ == "__main__":
    CubeVisualizer().run()
