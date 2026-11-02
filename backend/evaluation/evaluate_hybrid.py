from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

from ..data.cleaning import clean_inventory_frame
from ..data.loader import DEFAULT_DATASET_PATH, load_inventory_dataset
from ..data.schema import TARGET_COLUMN
from ..features.sequencing import dynamic_array, lightgbm_features, static_array
from ..models.registry import MODEL_DIR, load_registry


def evaluate(
    dataset_path: str | Path = DEFAULT_DATASET_PATH,
    *,
    model_dir: str | Path = MODEL_DIR,
    max_rows: int | None = None,
) -> dict:
    frame = clean_inventory_frame(load_inventory_dataset(dataset_path, max_rows=max_rows))
    registry = load_registry(model_dir)
    _, test_frame = train_test_split(
        frame, test_size=0.2, random_state=42, stratify=frame["Variety"]
    )
    features, _ = lightgbm_features(test_frame, registry["metadata"]["varieties"])
    lgb_prediction = registry["lightgbm"].predict(features).astype(np.float32)
    dynamic = registry["scaler_dynamic"].transform(dynamic_array(test_frame)).reshape(-1, 5, 1)
    static = registry["scaler_static"].transform(static_array(test_frame))
    with torch.no_grad():
        residual_prediction = registry["hybrid"](
            torch.from_numpy(dynamic.astype(np.float32)),
            torch.from_numpy(lgb_prediction.reshape(-1, 1)),
            torch.from_numpy(static.astype(np.float32)),
        ).numpy()
    hybrid_prediction = lgb_prediction + residual_prediction
    actual = test_frame[TARGET_COLUMN].to_numpy(dtype=np.float32)

    def metrics(prediction: np.ndarray) -> dict[str, float]:
        return {
            "mae": float(mean_absolute_error(actual, prediction)),
            "rmse": float(np.sqrt(mean_squared_error(actual, prediction))),
            "r2": float(r2_score(actual, prediction)),
        }

    return {
        "rows_evaluated": int(len(test_frame)),
        "lightgbm": metrics(lgb_prediction),
        "hybrid": metrics(hybrid_prediction),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate the trained hybrid model.")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET_PATH)
    parser.add_argument("--model-dir", type=Path, default=MODEL_DIR)
    parser.add_argument("--max-rows", type=int, default=None)
    args = parser.parse_args()
    print(json.dumps(evaluate(args.dataset, model_dir=args.model_dir, max_rows=args.max_rows), indent=2))


if __name__ == "__main__":
    main()
