# Build:  pyinstaller packaging/spoilsense.spec --noconfirm   (run from project root)
import os
from PyInstaller.utils.hooks import collect_all

ROOT = os.path.abspath(os.path.join(SPECPATH, ".."))   # project root
R = lambda p: os.path.join(ROOT, p)

datas, binaries, hiddenimports = [], [], []
for pkg in ("lightgbm", "uvicorn"):
    d, b, h = collect_all(pkg)
    datas += d; binaries += b; hiddenimports += h

datas += [
    (R("backend/models/runtime_weights.npz"), "backend/models"),
    (R("backend/models/runtime_scalers.json"), "backend/models"),
    (R("backend/models/*.txt"), "backend/models"),
    (R("backend/models/metadata.json"), "backend/models"),   # metrics.json is not needed at runtime
    (R("backend/data/schema.sql"), "backend/data"),
    (R("frontend/dist"), "frontend_dist"),
]
hiddenimports += ["backend.main"]

a = Analysis(
    [R("launcher.py")],
    pathex=[ROOT],
    datas=datas, binaries=binaries, hiddenimports=hiddenimports,
    excludes=["torch", "sklearn", "joblib", "tkinter", "matplotlib", "IPython", "pytest",
              "PIL", "pyarrow", "numba", "jupyter", "notebook", "setuptools"],
)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True,
          name="SpoilSenseAI", console=True)   # console=True shows logs; set False once stable
coll = COLLECT(exe, a.binaries, a.datas, name="SpoilSenseAI")
