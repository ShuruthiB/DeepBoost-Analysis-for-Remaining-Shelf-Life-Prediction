from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from api.predict import router as predict_router
from api.simulate import router as simulate_router
from api.evaluate import router as evaluate_router
from api.explain import router as explain_router

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
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
