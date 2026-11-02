from __future__ import annotations

from pathlib import Path

import lightgbm as lgb
import numpy as np


def train_lightgbm(
    features: np.ndarray,
    target: np.ndarray,
    *,
    validation_features: np.ndarray,
    validation_target: np.ndarray,
) -> lgb.LGBMRegressor:
    model = lgb.LGBMRegressor(
        objective="regression",
        n_estimators=400,
        learning_rate=0.05,
        num_leaves=63,
        min_child_samples=40,
        subsample=0.9,
        colsample_bytree=0.9,
        reg_lambda=0.1,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(
        features,
        target,
        eval_set=[(validation_features, validation_target)],
        callbacks=[lgb.early_stopping(30, verbose=False)],
    )
    return model


def save_lightgbm(model: lgb.LGBMRegressor, path: str | Path) -> None:
    model.booster_.save_model(str(path))