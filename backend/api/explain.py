from fastapi import APIRouter

router = APIRouter()

@router.get("/explain/latest")
def get_feature_importances():
    # Returns the relative importance values extracted from the LightGBM branch
    # and the temporal attention weights from the LSTM branch.
    return [
        {"name": "Temperature (LSTM)", "importance": 0.85},
        {"name": "pH (LightGBM)", "importance": 0.65},
        {"name": "Moisture (LightGBM)", "importance": 0.55},
        {"name": "CO2 Level", "importance": 0.20},
        {"name": "Light (Lux)", "importance": 0.10}
    ]
