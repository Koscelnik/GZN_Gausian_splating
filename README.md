# 3D Gaussian Splatting Demo

Tento projekt slúži ako vzdelávacia implementácia a interaktívny prehliadač (viewer) pre **3D Gaussian Splatting (3DGS)**.
Cieľom je pochopiť a od základov implementovať matematické princípy reprezentácie 3D scén, 3D kovariančných matíc, projekcie do 2D (splatting), alfa-blendingu a vykresľovania v reálnom čase pomocou OpenGL.

## Architektúra projektu

- `main.py` - Hlavná aplikačná slučka (event loop, spracovanie vstupu a okna).
- `rendering/`
  - `renderer.py` - OpenGL renderovacie jadro (projekcia, stavy OpenGL, 3D mriežka a osi).
  - `camera.py` - Orbitálna 3D kamera (rotácia, posun, približovanie).
- `core/`
  - `gaussian_model.py` - Matematická reprezentácia 3D Gaussov (načítanie dát, transformácie, 2D splatting).

## Ovládanie
- **Ľavé tlačidlo myši (ťahanie):** Rotácia kamery (Orbit okolo stredu)
- **Pravé / Stredné tlačidlo myši (ťahanie):** Posun cieľového bodu (Pan)
- **Koliesko myši:** Priblíženie / oddialenie (Zoom)
- **Kláves R:** Reset pohľadu kamery
- **Kláves ESC:** Ukončenie

## Spustenie

1. Aktivácia prostredia:
   ```cmd
   venv\Scripts\activate
   ```

2. Inštalácia závislostí:
   ```bash
   pip install -r requirements.txt
   ```

3. Spustenie aplikácie:
   ```bash
   python main.py
   ```
