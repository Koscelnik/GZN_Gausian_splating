from OpenGL.GLU import gluLookAt
import math

class Camera:
    def __init__(self):
        self.radius = 5.0
        self.yaw = 45.0   # rotácia okolo osi Y
        self.pitch = 30.0 # rotácia hore/dole
        self.center = [0.0, 0.0, 0.0]

    def apply(self):
        # Prevod sférických súradníc (yaw, pitch, radius) na karteziánske (x, y, z)
        y = self.radius * math.sin(math.radians(self.pitch))
        r = self.radius * math.cos(math.radians(self.pitch))
        x = r * math.cos(math.radians(self.yaw))
        z = r * math.sin(math.radians(self.yaw))

        eye_x = self.center[0] + x
        eye_y = self.center[1] + y
        eye_z = self.center[2] + z

        gluLookAt(
            eye_x, eye_y, eye_z,                 # Pozícia kamery
            self.center[0], self.center[1], self.center[2], # Bod na ktorý sa pozeráme
            0.0, 1.0, 0.0                        # Vektor "hore"
        )

    def rotate(self, dx, dy):
        self.yaw += dx * 0.5
        self.pitch += dy * 0.5
        
        # Obmedzíme rotáciu hore/dole aby kamera nepreskočila pól
        if self.pitch > 89.0:
            self.pitch = 89.0
        if self.pitch < -89.0:
            self.pitch = -89.0
