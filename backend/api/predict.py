from __future__ import annotations

import numpy as np
import torch
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..data.schema import TEMPERATURE_COLUMNS
from ..features.sequencing import lightgbm_features
from ..models.registry import load_registry

router = APIRouter()
_registry: dict | None = None


class PredictRequest(BaseModel):
    variety: str
    shelf: str | None = None
    ph: float
    moisture: float
    temperatures: list[float] = Field(min_length=len(TEMPERATURE_COLUMNS), max_length=len(TEMPERATURE_COLUMNS))


def _get_registry() -> dict:
    global _registry
    if _registry is None:
        try:
            _registry = load_registry()
        except (FileNotFoundError, OSError, RuntimeError, ValueError, KeyError) as error:
            raise HTTPException(
                status_code=503,
                detail="Hybrid model artifacts are unavailable. Run backend/trainer.py first.",
            ) from error
    return _registry


@router.post("/predict")
def run_prediction(data: PredictRequest) -> dict:
    registry = _get_registry()
    metadata = registry["metadata"]
    if data.variety not in metadata["varieties"]:
        raise HTTPException(
            status_code=422,
            detail=f"Unknown variety '{data.variety}'. Expected one of {metadata['varieties']}.",
        )
    row = {
        "Variety": data.variety,
        "pH": data.ph,
        "Moisture": data.moisture,
        **{column: temperature for column, temperature in zip(TEMPERATURE_COLUMNS, data.temperatures)},
    }
    import pandas as pd

    frame = pd.DataFrame([row])
    static = registry["scaler_static"].transform(frame[["pH", "Moisture"]].to_numpy())
    dynamic = registry["scaler_dynamic"].transform(
        frame[list(TEMPERATURE_COLUMNS)].to_numpy()
    ).reshape(1, len(TEMPERATURE_COLUMNS), 1)
    lgb_features, _ = lightgbm_features(frame, metadata["varieties"])
    lgb_prediction = registry["lightgbm"].predict(lgb_features).astype(np.float32)
    with torch.no_grad():
        residual_days = float(
            registry["hybrid"](
                torch.from_numpy(dynamic.astype(np.float32)),
                torch.from_numpy(lgb_prediction.reshape(-1, 1)),
                torch.from_numpy(static.astype(np.float32)),
            ).item()
        )
    predicted_days = float(lgb_prediction[0] + residual_days)
    predicted_days = max(0.0, min(predicted_days, 40.0))
    status = "CRITICAL" if predicted_days <= 5 else "WARNING" if predicted_days <= 10 else "SAFE"
    return {
        "variety": data.variety,
        "shelf": data.shelf,
        "predicted_days": round(predicted_days, 1),
        "status": status,
        "model_trained": True,
        "data_source": "DeepBoost Hybrid LightGBM + LSTM",
    }
