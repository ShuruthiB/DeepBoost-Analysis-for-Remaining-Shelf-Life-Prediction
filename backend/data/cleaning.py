from __future__ import annotations

import pandas as pd

from .schema import TARGET_COLUMN, TEMPERATURE_COLUMNS


def clean_inventory_frame(frame: pd.DataFrame) -> pd.DataFrame:
    cleaned = frame[
        frame[TARGET_COLUMN].between(0, 40)
        & frame["pH"].between(0, 14)
        & frame["Moisture"].between(0, 1.5)
    ].copy()
    for column in TEMPERATURE_COLUMNS:
        cleaned = cleaned[cleaned[column].between(-50, 80)]
    return cleaned.reset_index(drop=True)