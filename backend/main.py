from fastapi import FastAPI
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

@app.get("/")
def read_root():
    return {"status": "SpoilSense AI API is running"}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
