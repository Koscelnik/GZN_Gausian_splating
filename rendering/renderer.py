import os
import math
import numpy as np
from OpenGL.GL import *
from OpenGL.GL import shaders
from OpenGL.GLU import gluPerspective

class Renderer:
    """
    OpenGL vykresľovacie jadro s podporou hĺbkového radenia (Back-to-Front Depth Sorting).
    Podporuje:
    1. GLSL 3D Gaussian Splatting (EWA Splatting, kovariancia 3D->2D, adaptívne elipsy, exponenciálny útlm).
    2. Jednoduché body (Fixed-function GL_POINTS - rýchly referenčný point cloud).
    """
    def __init__(self):
        self.splat_program = None
        self.use_shader = True  # True = GLSL Splatting (Elipsy), False = Jednoduché body
        self.width = 1024
        self.height = 768
        self.fov = 45.0

        # Uniform lokácie pre splat program
        self.u_view_loc = -1
        self.u_proj_loc = -1
        self.u_viewport_loc = -1
        self.u_focal_loc = -1
        self.u_opacity_mult_loc = -1

        # Cache pre hĺbkové radenie (Depth sorting)
        self.sorted_indices = None
        self.last_view_dir = None

    def init_gl(self, width, height):
        """Inicializácia OpenGL stavov a shaderu."""
        glClearColor(0.08, 0.08, 0.10, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Povolenie point sprites pre GLSL shader (gl_PointCoord)
        glEnable(GL_PROGRAM_POINT_SIZE)
        glEnable(GL_POINT_SPRITE)
        glTexEnvi(GL_POINT_SPRITE, GL_COORD_REPLACE, GL_TRUE)

        # Vyhladzovanie bodov pre fixed-function mód
        glEnable(GL_POINT_SMOOTH)
        glHint(GL_POINT_SMOOTH_HINT, GL_NICEST)

        self.compile_shaders()
        self.resize(width, height)

    def compile_shaders(self):
        """Kompilácia GLSL EWA Splatting shaderu."""
        shader_dir = os.path.join(os.path.dirname(__file__), "shaders")
        vert_path = os.path.join(shader_dir, "splat.vert")
        frag_path = os.path.join(shader_dir, "splat.frag")

        try:
            with open(vert_path, "r", encoding="utf-8") as f:
                vert_src = f.read()
            with open(frag_path, "r", encoding="utf-8") as f:
                frag_src = f.read()

            v_shader = shaders.compileShader(vert_src, GL_VERTEX_SHADER)
            f_shader = shaders.compileShader(frag_src, GL_FRAGMENT_SHADER)
            self.splat_program = shaders.compileProgram(v_shader, f_shader)

            self.u_view_loc = glGetUniformLocation(self.splat_program, "u_view")
            self.u_proj_loc = glGetUniformLocation(self.splat_program, "u_projection")
            self.u_viewport_loc = glGetUniformLocation(self.splat_program, "u_viewport")
            self.u_focal_loc = glGetUniformLocation(self.splat_program, "u_focal")
            self.u_opacity_mult_loc = glGetUniformLocation(self.splat_program, "u_opacity_mult")
            print("[Renderer] GLSL EWA Splatting shader úspešne skompilovaný!")
        except Exception as e:
            print(f"[Renderer] Chyba pri kompilácii splat shaderu: {e}")
            self.splat_program = None
            self.use_shader = False

    def resize(self, width, height):
        """Aktualizácia rozmerov a perspektívy."""
        if height == 0:
            height = 1
        self.width = width
        self.height = height
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.fov, width / float(height), 0.1, 200.0)
        glMatrixMode(GL_MODELVIEW)

    def clear(self):
        """Vyčistenie farebného a hĺbkového bufferu."""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    def draw_grid_and_axes(self, grid_size=4, step=1.0):
        """Vykreslenie orientačnej 3D mriežky a osí."""
        glUseProgram(0)
        glLineWidth(1.0)
        glColor4f(0.20, 0.20, 0.24, 0.5)
        glBegin(GL_LINES)
        for i in np.arange(-grid_size, grid_size + 0.1, step):
            glVertex3f(-grid_size, 0.0, i)
            glVertex3f(grid_size, 0.0, i)
            glVertex3f(i, 0.0, -grid_size)
            glVertex3f(i, 0.0, grid_size)
        glEnd()

        # Osi: X (červená), Y (zelená), Z (modrá)
        glLineWidth(2.5)
        glBegin(GL_LINES)
        glColor3f(0.9, 0.2, 0.2)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(1.5, 0.0, 0.0)

        glColor3f(0.2, 0.85, 0.2)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, 1.5, 0.0)

        glColor3f(0.2, 0.45, 0.95)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, 0.0, 1.5)
        glEnd()
        glLineWidth(1.0)

    def reset_sorting(self):
        """Reset vyrovnávacej pamäte radenia pri zmene modelu."""
        self.sorted_indices = None
        self.last_view_dir = None

    def draw_gaussians(self, model, point_size=10.0, opacity_mult=1.0):
        """Vykreslenie Gaussov s hĺbkovým radením zozadu dopredu (Back-to-Front)."""
        if model.positions is None or model.num_gaussians == 0:
            return

        view_mat = glGetFloatv(GL_MODELVIEW_MATRIX)
        proj_mat = glGetFloatv(GL_PROJECTION_MATRIX)

        # 1. Hĺbkové radenie (Back-to-Front Depth Sort)
        # Smer pohľadu kamery (tretí riadok view matice v column-major pamäti)
        view_dir = np.array([view_mat[0, 2], view_mat[1, 2], view_mat[2, 2]], dtype=np.float32)

        need_sort = (
            self.sorted_indices is None
            or len(self.sorted_indices) != model.num_gaussians
            or self.last_view_dir is None
            or np.dot(view_dir, self.last_view_dir) < 0.999
        )

        if need_sort:
            # cam_z je záporná hĺbka v priestore kamery (najvzdialenejšie body majú najmenšie/najzápornejšie z)
            cam_z = (model.positions[:, 0] * view_dir[0] +
                     model.positions[:, 1] * view_dir[1] +
                     model.positions[:, 2] * view_dir[2])
            # argsort zoradí indexy vzostupne (najvzdialenejšie prvé -> zozadu dopredu)
            self.sorted_indices = np.argsort(cam_z).astype(np.uint32)
            self.last_view_dir = view_dir.copy()

        rgba = np.hstack([model.colors, model.opacities]).astype(np.float32)

        if self.use_shader and self.splat_program:
            # === 1. REŽIM: GLSL EWA SPLATTING (SKUTOČNÉ ELIPSY) ===
            glUseProgram(self.splat_program)

            glUniformMatrix4fv(self.u_view_loc, 1, GL_FALSE, view_mat)
            glUniformMatrix4fv(self.u_proj_loc, 1, GL_FALSE, proj_mat)
            glUniform2f(self.u_viewport_loc, float(self.width), float(self.height))

            focal = self.height / (2.0 * math.tan(math.radians(self.fov * 0.5)))
            glUniform1f(self.u_focal_loc, focal)
            glUniform1f(self.u_opacity_mult_loc, float(opacity_mult))

            # Vypneme zápis do depth buffera pri prelínaní transparentných splatov
            glDepthMask(GL_FALSE)

            glEnableVertexAttribArray(0)
            glEnableVertexAttribArray(1)
            glEnableVertexAttribArray(2)
            glEnableVertexAttribArray(3)

            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, model.positions)
            glVertexAttribPointer(1, 4, GL_FLOAT, GL_FALSE, 0, rgba)
            glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 0, model.scales)
            glVertexAttribPointer(3, 4, GL_FLOAT, GL_FALSE, 0, model.rotations)

            glDrawElements(GL_POINTS, model.num_gaussians, GL_UNSIGNED_INT, self.sorted_indices)

            glDisableVertexAttribArray(3)
            glDisableVertexAttribArray(2)
            glDisableVertexAttribArray(1)
            glDisableVertexAttribArray(0)

            glDepthMask(GL_TRUE)
            glUseProgram(0)

        else:
            # === 2. REŽIM: JEDNODUCHÉ BODY (FIXED-FUNCTION GL_POINTS) ===
            glUseProgram(0)
            glPointSize(float(point_size))

            glEnableClientState(GL_VERTEX_ARRAY)
            glEnableClientState(GL_COLOR_ARRAY)

            glVertexPointer(3, GL_FLOAT, 0, model.positions)
            glColorPointer(4, GL_FLOAT, 0, rgba)

            glDrawElements(GL_POINTS, model.num_gaussians, GL_UNSIGNED_INT, self.sorted_indices)

            glDisableClientState(GL_COLOR_ARRAY)
            glDisableClientState(GL_VERTEX_ARRAY)
