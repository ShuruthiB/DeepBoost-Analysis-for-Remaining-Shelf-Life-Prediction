from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

if __package__:
    from .api.predict import router as predict_router
    from .api.simulate import router as simulate_router
    from .api.evaluate import router as evaluate_router
    from .api.explain import router as explain_router
    app_module = "backend.main:app"
else:
    # Also support `python main.py` when the working directory is backend/.
    from api.predict import router as predict_router
    from api.simulate import router as simulate_router
    from api.evaluate import router as evaluate_router
    from api.explain import router as explain_router
    app_module = "main:app"

app = FastAPI(title="Inventory Intelligence Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all modular routers
app.include_router(predict_router, prefix="/api")
app.include_router(simulate_router, prefix="/api")
app.include_router(evaluate_router, prefix="/api")
app.include_router(explain_router, prefix="/api")

@app.get("/")
def read_root():
    return {"status": "DeepBoost FastAPI is running"}

if __name__ == "__main__":
    uvicorn.run(app_module, host="0.0.0.0", port=8000, reload=True)
