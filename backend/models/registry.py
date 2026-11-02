from __future__ import annotations

import json
from pathlib import Path

import joblib
import lightgbm as lgb
import torch

from .hybrid_fusion import HybridFusionModel

MODEL_DIR = Path(__file__).resolve().parent


def load_registry(model_dir: str | Path = MODEL_DIR) -> dict:
    directory = Path(model_dir)
    metadata = json.loads((directory / "metadata.json").read_text())
    model = HybridFusionModel(
        static_features=metadata["static_feature_count"],
        hidden_size=metadata["lstm_hidden_size"],
    )
    model.load_state_dict(
        torch.load(directory / "hybrid_lstm.pt", map_location="cpu", weights_only=True)
    )
    model.eval()
    return {
        "metadata": metadata,
        "scaler_static": joblib.load(directory / "scaler_stat.pkl"),
        "scaler_dynamic": joblib.load(directory / "scaler_dyn.pkl"),
        "lightgbm": lgb.Booster(model_file=str(directory / "lgbm_static.txt")),
        "hybrid": model,
    }