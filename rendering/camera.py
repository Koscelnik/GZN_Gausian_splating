from OpenGL.GLU import gluLookAt
import math

class Camera:
    """
    Orbitálna 3D kamera pre interaktívne prehliadanie scény.
    Podporuje:
    - Rotáciu (orbit)
    - Priblíženie / oddialenie (zoom)
    - Posun stredu pohľadu (pan)
    """
    def __init__(self):
        self.radius = 6.0
        self.yaw = 45.0    # Uhol okolo osi Y (v stupňoch)
        self.pitch = 30.0  # Uhol elevácie (v stupňoch)
        self.center = [0.0, 0.0, 0.0]  # Bod, na ktorý sa kamera pozerá

    def apply(self):
        """Aplikuje pohľadovú maticu (gluLookAt) do OpenGL."""
        rad_pitch = math.radians(self.pitch)
        rad_yaw = math.radians(self.yaw)

        # Prevod sférických súradníc na karteziánske
        y = self.radius * math.sin(rad_pitch)
        r = self.radius * math.cos(rad_pitch)
        x = r * math.cos(rad_yaw)
        z = r * math.sin(rad_yaw)

        eye_x = self.center[0] + x
        eye_y = self.center[1] + y
        eye_z = self.center[2] + z

        gluLookAt(
            eye_x, eye_y, eye_z,
            self.center[0], self.center[1], self.center[2],
            0.0, 1.0, 0.0
        )

    def rotate(self, dx, dy):
        """Rotácia kamery okolo sledovaného stredu."""
        self.yaw += dx * 0.4
        self.pitch -= dy * 0.4

        # Ochrana pred pretočením cez pól
        self.pitch = max(-89.0, min(89.0, self.pitch))

    def zoom(self, delta):
        """Priblíženie / oddialenie."""
        self.radius *= (0.9 if delta > 0 else 1.1)
        self.radius = max(0.1, min(100.0, self.radius))

    def pan(self, dx, dy):
        """Posun cieľového bodu kamery v rovine kolmej na pohľad."""
        rad_yaw = math.radians(self.yaw)
        # Smerové vektory doprava a hore
        right_x = -math.sin(rad_yaw)
        right_z = math.cos(rad_yaw)

        scale = self.radius * 0.002
        self.center[0] += -dx * right_x * scale
        self.center[2] += -dx * right_z * scale
        self.center[1] += dy * scale
