import sys
import os
import pygame
from pygame.locals import *
from rendering.camera import Camera
from rendering.renderer import Renderer
from core.gaussian_model import GaussianModel

def main():
    pygame.init()
    width, height = 1024, 768

    pygame.display.set_caption("3D Gaussian Splatting Viewer")
    pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL | RESIZABLE)

    renderer = Renderer()
    renderer.init_gl(width, height)

    camera = Camera()
    model = GaussianModel()

    clock = pygame.time.Clock()
    running = True

    # Nastavenia zobrazenia
    point_size = 10.0
    opacity_mult = 1.0
    show_grid = True
    sphere_path = os.path.join("examples", "pretrained", "sample_sphere.ply")
    flowers_path = os.path.join("examples", "pretrained", "flowers_1", "flowers_1.ply")

    # Stav ovládania myšou
    is_orbiting = False
    is_panning = False
    last_mouse_pos = (0, 0)

    print("=" * 75)
    print("3D Gaussian Splatting Viewer")
    print("=" * 75)
    print("KLÁVESY:")
    print("  [2]       -> Načítať syntetickú guľu (sample_sphere.ply - 1 000 Gaussov)")
    print("  [3] / [F] -> Načítať reálny model kvetov (flowers_1.ply - 562 000 Gaussov)")
    print("  [S]       -> PREPNÚŤ: GLSL Splatting (Elipsy) vs Jednoduché body")
    print("  [U]       -> Otočiť model o 180° okolo osi X (Upside down flip)")
    print("  [O] / [P] -> Znížiť / zvýšiť krytie (Opacity Multiplier)")
    print("  [1]       -> Vyčistiť scénu")
    print("  [G]       -> Zapnúť / vypnúť mriežku a osi")
    print("  [+] / [-] -> Zväčšiť / zmenšiť veľkosť bodov")
    print("  [R]       -> Resetovať kameru")
    print("  [ESC]     -> Ukončiť")
    print("\nOVLÁDANIE MYŠOU:")
    print("  - Ľavé tlačidlo: Orbit rotácia okolo stredu")
    print("  - Pravé / Stredné tlačidlo: Posun (Pan)")
    print("  - Koliesko myši: Zoom")
    print("=" * 75)

    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

            elif event.type == VIDEORESIZE:
                width, height = event.w, event.h
                renderer.resize(width, height)

            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
                elif event.key == K_r:
                    camera = Camera()
                elif event.key in (K_2, K_KP2):
                    # Kláves 2: Guľa
                    print(f"\n-> Načítavam guľu: {sphere_path}...")
                    if not os.path.exists(sphere_path):
                        import subprocess
                        subprocess.run([sys.executable, os.path.join("examples", "generate_sample_ply.py")])
                    model.load_from_ply(sphere_path)
                    renderer.reset_sorting()
                    camera.radius = 5.0
                    camera.center = [0.0, 0.0, 0.0]

                elif event.key in (K_3, K_KP3, K_f):
                    # Kláves 3 alebo F: Kvety (flowers_1.ply)
                    print(f"\n-> Načítavam kvety: {flowers_path}...")
                    if os.path.exists(flowers_path):
                        model.load_from_ply(flowers_path)
                        # Prevod z COLMAP (Y smeruje nadol) na OpenGL (Y smeruje nahor)
                        model.rotate_180_x()
                        renderer.reset_sorting()
                        camera.radius = 2.4
                        camera.center = [0.1, -0.05, -0.2]
                        camera.yaw = 25.0
                        camera.pitch = 15.0
                    else:
                        print(f"[Upozornenie] Súbor {flowers_path} nebol nájdený.")

                elif event.key == K_u:
                    # Kláves U: Manuálne otočenie o 180° okolo osi X
                    model.rotate_180_x()
                    renderer.reset_sorting()

                elif event.key == K_o:
                    # Kláves O: Znížiť krytie
                    opacity_mult = max(0.2, opacity_mult - 0.2)
                    print(f"\n-> Krytie znížené: {opacity_mult:.1f}x")

                elif event.key == K_p:
                    # Kláves P: Zvýšiť krytie
                    opacity_mult = min(5.0, opacity_mult + 0.2)
                    print(f"\n-> Krytie zvýšené: {opacity_mult:.1f}x")

                elif event.key == K_s:
                    # Prepnutie režimu GLSL Splatting vs Jednoduché body
                    renderer.use_shader = not renderer.use_shader
                    mode_name = "GLSL 3D Gaussian Splatting (Elipsy)" if renderer.use_shader else "Jednoduché body (Point Cloud)"
                    print(f"\n-> Režim zobrazenia zmenený na: {mode_name}")

                elif event.key in (K_1, K_KP1):
                    model = GaussianModel()
                    renderer.reset_sorting()
                    print("\n-> Scéna vyčistená.")

                elif event.key == K_g:
                    show_grid = not show_grid

                elif event.key in (K_PLUS, K_KP_PLUS, K_EQUALS):
                    point_size = min(50.0, point_size + 2.0)

                elif event.key in (K_MINUS, K_KP_MINUS):
                    point_size = max(2.0, point_size - 2.0)

            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    is_orbiting = True
                    last_mouse_pos = event.pos
                elif event.button in (2, 3):
                    is_panning = True
                    last_mouse_pos = event.pos
                elif event.button == 4:
                    camera.zoom(1)
                elif event.button == 5:
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

        # Vykreslenie scény
        renderer.clear()
        camera.apply()

        if show_grid:
            renderer.draw_grid_and_axes()

        # Vykreslenie modelu (GLSL elipsy alebo jednoduché body)
        renderer.draw_gaussians(model, point_size=point_size, opacity_mult=opacity_mult)

        pygame.display.flip()

        # Stav v záhlaví okna
        fps = clock.get_fps()
        count = model.num_gaussians
        mode_str = "GLSL Splatting" if renderer.use_shader else "Jednoduché body"
        pygame.display.set_caption(f"3D Gaussian Splatting | Režim: [{mode_str}] | Krytie: {opacity_mult:.1f}x | Gaussov: {count:,} | FPS: {fps:.1f}")

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
