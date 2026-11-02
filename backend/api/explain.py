from fastapi import APIRouter
from ..models.registry import load_registry

router = APIRouter()

@router.get("/explain/latest")
def get_feature_importances():
    registry = load_registry()
    model = registry["lightgbm"]
    names = registry["metadata"]["feature_names"]
    values = model.feature_importance(importance_type="gain")
    total = float(values.sum()) or 1.0
    return [
        {"name": name, "importance": round(float(value) / total, 4)}
        for name, value in sorted(
            zip(names, values),
            key=lambda item: item[1],
            reverse=True,
        )
    ]
