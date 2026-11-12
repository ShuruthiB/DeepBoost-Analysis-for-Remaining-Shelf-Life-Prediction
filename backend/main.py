import os
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

if __package__:
    from .api.evaluate import router as evaluation_router
    from .api.explain import router as explain_router
    from .api.inventory import router as inventory_router
    from .api.predict import router as predict_router
    from .api.train import router as train_router
else:
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from backend.api.evaluate import router as evaluation_router
    from backend.api.explain import router as explain_router
    from backend.api.inventory import router as inventory_router
    from backend.api.predict import router as predict_router
    from backend.api.train import router as train_router

app = FastAPI(title="SpoilSense AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all modular routers
app.include_router(predict_router, prefix="/api")
app.include_router(evaluation_router, prefix="/api")
app.include_router(explain_router, prefix="/api")
app.include_router(train_router, prefix="/api")
app.include_router(inventory_router, prefix="/api")

def _frontend_dir() -> Path | None:
    """Built React app: bundled by PyInstaller, or frontend/dist in a normal checkout."""
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
    for candidate in (base / "frontend_dist", base / "frontend" / "dist"):
        if (candidate / "index.html").is_file():
            return candidate
    return None


_FRONTEND = _frontend_dir()

if _FRONTEND:
    app.mount("/assets", StaticFiles(directory=_FRONTEND / "assets"), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def serve_spa(full_path: str):
        if full_path.startswith("api/"):
            return {"detail": "Not Found"}
        target = (_FRONTEND / full_path).resolve()
        if full_path and target.is_file() and _FRONTEND.resolve() in target.parents:
            return FileResponse(target)
        return FileResponse(_FRONTEND / "index.html")
else:
    @app.get("/")
    def read_root():
        return {"status": "SpoilSense AI API is running"}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
