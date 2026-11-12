from __future__ import annotations

import argparse
import json
import random
from dataclasses import dataclass
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import torch
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from torch.utils.data import DataLoader, TensorDataset

from ..data.cleaning import clean_inventory_frame
from ..data.loader import DEFAULT_DATASET_PATH, load_inventory_dataset
from ..data.schema import TARGET_COLUMN
from ..features.sequencing import dynamic_array, lightgbm_features, static_array
from ..models.hybrid_fusion import HybridFusionModel
from ..models.lightgbm_branch import save_lightgbm, train_lightgbm


@dataclass(frozen=True)
class TrainingConfig:
    dataset_path: Path = DEFAULT_DATASET_PATH
    model_dir: Path = Path(__file__).resolve().parents[1] / "models"
    max_rows: int | None = None
    epochs: int = 3
    batch_size: int = 4096
    learning_rate: float = 1e-3
    seed: int = 42


def _set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def _metrics(actual: np.ndarray, predicted: np.ndarray) -> dict[str, float]:
    return {
        "mae": float(mean_absolute_error(actual, predicted)),
        "rmse": float(np.sqrt(mean_squared_error(actual, predicted))),
        "r2": float(r2_score(actual, predicted)),
    }


def train(config: TrainingConfig = TrainingConfig()) -> dict:
    _set_seed(config.seed)
    frame = clean_inventory_frame(
        load_inventory_dataset(config.dataset_path, max_rows=config.max_rows)
    )
    train_frame, holdout_frame = train_test_split(
        frame, test_size=0.2, random_state=config.seed, stratify=frame["Variety"]
    )
    validation_frame, test_frame = train_test_split(
        holdout_frame, test_size=0.5, random_state=config.seed, stratify=holdout_frame["Variety"]
    )
    varieties = sorted(frame["Variety"].unique().tolist())

    static_scaler = StandardScaler().fit(static_array(train_frame))
    dynamic_scaler = StandardScaler().fit(dynamic_array(train_frame))
    lgb_train, feature_names = lightgbm_features(train_frame, varieties)
    lgb_validation, _ = lightgbm_features(validation_frame, varieties)
    lgb_test, _ = lightgbm_features(test_frame, varieties)
    target_train = train_frame[TARGET_COLUMN].to_numpy(dtype=np.float32)
    target_validation = validation_frame[TARGET_COLUMN].to_numpy(dtype=np.float32)
    target_test = test_frame[TARGET_COLUMN].to_numpy(dtype=np.float32)

    lgb_model = train_lightgbm(
        lgb_train,
        target_train,
        validation_features=lgb_validation,
        validation_target=target_validation,
    )
    lgb_train_prediction = lgb_model.predict(lgb_train).astype(np.float32)
    lgb_validation_prediction = lgb_model.predict(lgb_validation).astype(np.float32)
    lgb_test_prediction = lgb_model.predict(lgb_test).astype(np.float32)

    def tensors(data: pd.DataFrame, lgb_prediction: np.ndarray):
        dynamic = dynamic_scaler.transform(dynamic_array(data)).reshape(-1, 5, 1)
        static = static_scaler.transform(static_array(data))
        target = data[TARGET_COLUMN].to_numpy(dtype=np.float32) - lgb_prediction
        return (
            torch.from_numpy(dynamic.astype(np.float32)),
            torch.from_numpy(lgb_prediction.reshape(-1, 1)),
            torch.from_numpy(static.astype(np.float32)),
            torch.from_numpy(target),
        )

    train_tensors = tensors(train_frame, lgb_train_prediction)
    validation_tensors = tensors(validation_frame, lgb_validation_prediction)
    test_tensors = tensors(test_frame, lgb_test_prediction)
    loader = DataLoader(
        TensorDataset(*train_tensors), batch_size=config.batch_size, shuffle=True, num_workers=0
    )
    hybrid = HybridFusionModel(static_features=static_array(train_frame).shape[1])
    optimizer = torch.optim.AdamW(hybrid.parameters(), lr=config.learning_rate)
    loss_fn = torch.nn.MSELoss()
    best_state = None
    best_validation_loss = float("inf")

    for _ in range(config.epochs):
        hybrid.train()
        for dynamic, lgb_prediction, static, target in loader:
            optimizer.zero_grad()
            loss = loss_fn(hybrid(dynamic, lgb_prediction, static), target)
            loss.backward()
            optimizer.step()
        hybrid.eval()
        with torch.no_grad():
            validation_prediction = hybrid(
                validation_tensors[0], validation_tensors[1], validation_tensors[2]
            )
            validation_loss = loss_fn(validation_prediction, validation_tensors[3]).item()
        if validation_loss < best_validation_loss:
            best_validation_loss = validation_loss
            best_state = {
                key: value.cpu().clone() for key, value in hybrid.state_dict().items()
            }

    if best_state is None:
        raise RuntimeError("Hybrid training did not produce a model state.")
    hybrid.load_state_dict(best_state)
    hybrid.eval()
    with torch.no_grad():
        residual_prediction = hybrid(
            test_tensors[0], test_tensors[1], test_tensors[2]
        ).numpy()
        test_prediction = lgb_test_prediction + residual_prediction

    config.model_dir.mkdir(parents=True, exist_ok=True)
    save_lightgbm(lgb_model, config.model_dir / "lgbm_static.txt")
    joblib.dump(static_scaler, config.model_dir / "scaler_stat.pkl")
    joblib.dump(dynamic_scaler, config.model_dir / "scaler_dyn.pkl")
    torch.save(hybrid.state_dict(), config.model_dir / "hybrid_lstm.pt")
    from ..models.runtime import export_runtime_files  # torch-free copy for the packaged app

    export_runtime_files(config.model_dir)
    metrics = {
        "rows": int(len(frame)),
        "train_rows": int(len(train_frame)),
        "validation_rows": int(len(validation_frame)),
        "test_rows": int(len(test_frame)),
        "lightgbm_test": _metrics(target_test, lgb_test_prediction),
        "hybrid_test": _metrics(target_test, test_prediction),
    }
    metadata = {
        "dataset": str(config.dataset_path),
        "feature_names": feature_names,
        "varieties": varieties,
        "static_feature_count": 2,
        "lstm_hidden_size": 64,
        "sequence_length": 5,
        "fusion_target": "target_residual_over_lightgbm",
        "metrics": metrics,
    }
    (config.model_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))
    (config.model_dir / "metrics.json").write_text(json.dumps(metrics, indent=2))
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description="Train DeepBoost LightGBM + LSTM.")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET_PATH)
    parser.add_argument("--model-dir", type=Path, default=TrainingConfig.model_dir)
    parser.add_argument("--max-rows", type=int, default=None)
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=4096)
    args = parser.parse_args()
    print(json.dumps(train(TrainingConfig(
        dataset_path=args.dataset, model_dir=args.model_dir, max_rows=args.max_rows,
        epochs=args.epochs, batch_size=args.batch_size
    )), indent=2))


if __name__ == "__main__":
    main()
