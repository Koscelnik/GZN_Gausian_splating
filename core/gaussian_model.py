import os
import numpy as np

class GaussianModel:
    """
    Trieda reprezentujúca 3D Gaussian Splatting model.
    Ukladá všetky atribúty N gaussov:
    - positions: (N, 3) - 3D stredy (x, y, z)
    - colors:    (N, 3) - RGB farby v rozsahu [0, 1]
    - opacities: (N, 1) - alfa priehľadnosť v rozsahu [0, 1]
    - scales:    (N, 3) - skutočné veľkosti poloosí v 3D (po exp)
    - rotations: (N, 4) - normalizované kvaternióny rotácie [w, x, y, z]
    """
    def __init__(self):
        self.positions = None
        self.colors = None
        self.opacities = None
        self.scales = None
        self.rotations = None
        self.num_gaussians = 0

    def load_from_ply(self, filepath):
        """
        Načíta binárny .ply súbor formátu 3D Gaussian Splatting (Inria štandard).
        Vysvetlenie:
        1. Prečíta textovú hlavičku a zistí počet bodov (element vertex N).
        2. Zistí zoznam vlastností (properties) a ich poradie.
        3. Načíta binárne dáta a prepočíta matematické reprezentácie na fyzikálne:
           - f_dc -> RGB: RGB = clip(0.28209479 * f_dc + 0.5, 0, 1)
           - opacity_raw -> opacity: sigmoid(raw)
           - scale_raw -> scale: exp(raw)
        """
        if not os.path.exists(filepath):
            print(f"[Chyba] Súbor neexistuje: {filepath}")
            return False

        with open(filepath, "rb") as f:
            header_lines = []
            num_points = 0
            properties = []

            while True:
                line = f.readline().decode("latin1").strip()
                header_lines.append(line)
                if line.startswith("element vertex"):
                    num_points = int(line.split()[-1])
                elif line.startswith("property float"):
                    prop_name = line.split()[-1]
                    properties.append(prop_name)
                elif line == "end_header":
                    break

            if num_points == 0:
                print(f"[Chyba] V PLY súbore sa nenašli žiadne body: {filepath}")
                return False

            # Vytvorenie NumPy štruktúrovaného dátového typu (všetky atribúty sú float32)
            dtype = np.dtype([(name, "<f4") for name in properties])
            data = np.frombuffer(f.read(num_points * dtype.itemsize), dtype=dtype)

        self.num_gaussians = num_points

        # 1. Pozície (x, y, z)
        self.positions = np.stack([data["x"], data["y"], data["z"]], axis=-1).astype(np.float32)

        # 2. Farby zo sférických harmonických (SH nultého rádu f_dc_0, f_dc_1, f_dc_2)
        # Vzorec: SH0 = 0.5 + C0 * f_dc, kde C0 = 0.28209479177387814 (1 / (2 * sqrt(pi)))
        C0 = 0.28209479177387814
        if "f_dc_0" in properties:
            r = 0.5 + C0 * data["f_dc_0"]
            g = 0.5 + C0 * data["f_dc_1"]
            b = 0.5 + C0 * data["f_dc_2"]
            self.colors = np.clip(np.stack([r, g, b], axis=-1), 0.0, 1.0).astype(np.float32)
        else:
            self.colors = np.ones((num_points, 3), dtype=np.float32)

        # 3. Opacity (v PLY je uložená pred sigmoidom: opacity = 1 / (1 + exp(-raw)))
        if "opacity" in properties:
            raw_op = data["opacity"]
            self.opacities = (1.0 / (1.0 + np.exp(-raw_op))).reshape(-1, 1).astype(np.float32)
        else:
            self.opacities = np.ones((num_points, 1), dtype=np.float32)

        # 4. Mierka (v PLY uložená v logaritme: scale = exp(raw))
        if "scale_0" in properties:
            sx = np.exp(data["scale_0"])
            sy = np.exp(data["scale_1"])
            sz = np.exp(data["scale_2"])
            self.scales = np.stack([sx, sy, sz], axis=-1).astype(np.float32)
        else:
            self.scales = np.full((num_points, 3), 0.05, dtype=np.float32)

        # 5. Rotácia (jednotkový kvaternión [rot_0, rot_1, rot_2, rot_3])
        if "rot_0" in properties:
            q = np.stack([data["rot_0"], data["rot_1"], data["rot_2"], data["rot_3"]], axis=-1)
            # Normalizácia kvaterniónu q / ||q||
            norm = np.linalg.norm(q, axis=-1, keepdims=True)
            norm[norm == 0] = 1.0
            self.rotations = (q / norm).astype(np.float32)
        else:
            self.rotations = np.zeros((num_points, 4), dtype=np.float32)
            self.rotations[:, 0] = 1.0  # identita [1, 0, 0, 0]

        print(f"[GaussianModel] Uspesne nacitanych {self.num_gaussians} Gaussov zo suboru: {filepath}")
        return True

    def rotate_180_x(self):
        """
        Otočí model o 180 stupňov okolo osi X.
        Používa sa na prevod modelov zo SfM/COLMAP (kde os Y smeruje nadol)
        do OpenGL súradníc (kde os Y smeruje nahor).
        """
        if self.positions is None or self.num_gaussians == 0:
            return

        # 1. Pozície: y -> -y, z -> -z
        self.positions[:, 1] = -self.positions[:, 1]
        self.positions[:, 2] = -self.positions[:, 2]

        # 2. Rotácie (kvaternióny [w, x, y, z]):
        # Násobenie kvaterniónom rotácie q_rot = [0, 1, 0, 0] (180° okolo X)
        w = self.rotations[:, 0].copy()
        x = self.rotations[:, 1].copy()
        y = self.rotations[:, 2].copy()
        z = self.rotations[:, 3].copy()
        self.rotations[:, 0] = -x
        self.rotations[:, 1] = w
        self.rotations[:, 2] = z
        self.rotations[:, 3] = -y
        print("[GaussianModel] Model otoceny o 180 stupnov okolo osi X (spravna orientacia).")
