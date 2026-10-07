import sys
import pygame
from pygame.locals import *
from rendering.camera import Camera
from rendering.renderer import Renderer
from core.gaussian_model import GaussianModel

def main():
    pygame.init()
    width, height = 1024, 768

    # Nastavenie OpenGL okna cez Pygame
    pygame.display.set_caption("3D Gaussian Splatting Viewer")
    pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL | RESIZABLE)

    renderer = Renderer()
    renderer.init_gl(width, height)

    camera = Camera()
    model = GaussianModel()

    clock = pygame.time.Clock()
    running = True

    # Stav ovládania myšou
    is_orbiting = False
    is_panning = False
    last_mouse_pos = (0, 0)

    print("=" * 60)
    print("3D Gaussian Splatting Demo úspešne beží!")
    print("Ovládanie:")
    print(" - Ľavé tlačidlo myši: Rotácia kamery (Orbit)")
    print(" - Pravé / Stredné tlačidlo myši: Posun pohľadu (Pan)")
    print(" - Koliesko myši: Zoom")
    print(" - Kláves R: Reset pohľadu kamery")
    print("=" * 60)

    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

            elif event.type == VIDEORESIZE:
                width, height = event.w, event.h
                renderer.resize(width, height)

            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:  # Ľavé tlačidlo
                    is_orbiting = True
                    last_mouse_pos = event.pos
                elif event.button in (2, 3):  # Stredné alebo pravé tlačidlo
                    is_panning = True
                    last_mouse_pos = event.pos
                elif event.button == 4:  # Koliesko hore
                    camera.zoom(1)
                elif event.button == 5:  # Koliesko dole
                    camera.zoom(-1)

            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    is_orbiting = False
                elif event.button in (2, 3):
                    is_panning = False

            elif event.type == MOUSEMOTION:
                if is_orbiting:
                    dx = event.pos[0] - last_mouse_pos[0]
                    dy = event.pos[1] - last_mouse_pos[1]
                    camera.rotate(dx, dy)
                    last_mouse_pos = event.pos
                elif is_panning:
                    dx = event.pos[0] - last_mouse_pos[0]
                    dy = event.pos[1] - last_mouse_pos[1]
                    camera.pan(dx, dy)
                    last_mouse_pos = event.pos

            elif event.type == MOUSEWHEEL:
                camera.zoom(event.y)

            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
                elif event.key == K_r:
                    camera = Camera()

        # Vykreslenie scény
        renderer.clear()
        camera.apply()
        renderer.draw_grid_and_axes()

        pygame.display.flip()

        # Zobrazenie FPS a stavu v titulku okna
        fps = clock.get_fps()
        pygame.display.set_caption(f"3D Gaussian Splatting Demo | FPS: {fps:.1f} | Yaw: {camera.yaw:.0f}° Pitch: {camera.pitch:.0f}°")

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
