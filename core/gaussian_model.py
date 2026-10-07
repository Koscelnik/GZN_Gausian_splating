import numpy as np

class GaussianModel:
    """
    Trieda reprezentujúca 3D Gaussian Splatting scénu.
    Zatiaľ len základná štruktúra bez konkrétnej implementácie.
    """
    def __init__(self):
        # Parametre gaussov, ktoré budeme neskôr načítať
        self.positions = None      # 3D stredy gaussov (x, y, z)
        self.scales = None         # Mierka pozdĺž 3 osí
        self.rotations = None      # Rotácie (kvaternióny)
        self.opacities = None      # Alfa hodnoty (hustota)
        self.colors = None         # RGB alebo sferické harmonické funkcie
        
    def load_from_ply(self, filepath):
        """
        Neskôr sem pridáme načítavanie dát z .ply súborov.
        """
        pass
        
    def splat_to_2d(self, view_matrix, projection_matrix):
        """
        Tu sa bude diať hlavná mágia projekcie (splatting):
        1. Prevod 3D kovariančnej matice na 2D.
        2. Zoradenie gaussov podľa hĺbky (sorting) pre alfa-blending.
        """
        pass
