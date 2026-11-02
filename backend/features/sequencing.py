from __future__ import annotations

import numpy as np
import pandas as pd

from ..data.schema import STATIC_COLUMNS, TEMPERATURE_COLUMNS


def dynamic_array(frame: pd.DataFrame) -> np.ndarray:
    return frame.loc[:, list(TEMPERATURE_COLUMNS)].to_numpy(dtype=np.float32)


def static_array(frame: pd.DataFrame) -> np.ndarray:
    return frame.loc[:, list(STATIC_COLUMNS)].to_numpy(dtype=np.float32)


def lightgbm_features(
    frame: pd.DataFrame,
    varieties: list[str] | tuple[str, ...] | None = None,
) -> tuple[np.ndarray, list[str]]:
    temperatures = frame.loc[:, list(TEMPERATURE_COLUMNS)]
    features = pd.DataFrame(
        {
            "pH": frame["pH"].to_numpy(),
            "Moisture": frame["Moisture"].to_numpy(),
            "temp_mean": temperatures.mean(axis=1),
            "temp_min": temperatures.min(axis=1),
            "temp_max": temperatures.max(axis=1),
            "temp_std": temperatures.std(axis=1).fillna(0),
            "temp_slope": temperatures.iloc[:, -1].to_numpy()
            - temperatures.iloc[:, 0].to_numpy(),
        },
        index=frame.index,
    )
    for variety in list(varieties or sorted(frame["Variety"].unique())):
        features[f"variety_{variety}"] = (frame["Variety"] == variety).astype(float)
    return features.to_numpy(dtype=np.float32), list(features.columns)