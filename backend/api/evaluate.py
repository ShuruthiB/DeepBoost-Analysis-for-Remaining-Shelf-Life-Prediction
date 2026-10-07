from fastapi import APIRouter

router = APIRouter()

@router.get("/models/comparison")
def get_metrics():
    return {
        "hybrid": {
            "r2_score": 0.995,
            "rmse": 2.16,
            "precision": 100
        }
    }
