# 3D Gaussian Splatting Demo

Tento projekt slúži ako vzdelávacia implementácia a vizualizátor pre **3D Gaussian Splatting (3DGS)**. 
Je zameraný na pochopenie základných matematických princípov reprezentácie 3D scén pomocou 3D gaussovských elipsoidov, projekcie z 3D do 2D (splattingu), alfa-blendingu a vizualizácie pomocou OpenGL.

## Architektúra projektu

- `main.py` - Hlavný spúšťací skript.
- `ui/` - Grafické užívateľské rozhranie (GUI) postavené na PyQt6.
- `rendering/` - Logika pre vykresľovanie (PyOpenGL) a virtuálna orbitálna kamera.
- `core/` - Jadro obsahujúce matematický model pre Gaussove elipsoidy a operácie s nimi.

## Inštalácia a spustenie

Projekt využíva vlastné Python virtuálne prostredie (`venv`).

### 1. Aktivácia virtuálneho prostredia
Pred inštaláciou balíčkov a spustením je nutné aktivovať virtuálne prostredie. V termináli v zložke projektu spustite:

**Na operačnom systéme Windows (Príkazový riadok / PowerShell):**
```cmd
venv\Scripts\activate
```

**Na Linuxe / macOS:**
```bash
source venv/bin/activate
```

### 2. Inštalácia závislostí
Po aktivácii prostredia nainštalujte požadované knižnice:
```bash
pip install -r requirements.txt
```

### 3. Spustenie aplikácie
```bash
python main.py
```
