from __future__ import annotations

from pathlib import Path

import pandas as pd

from .schema import REQUIRED_COLUMNS, validate_columns

DEFAULT_DATASET_PATH = Path(__file__).resolve().parents[2] / "inventory_dataset_1M.csv"


def load_inventory_dataset(
    path: str | Path = DEFAULT_DATASET_PATH,
    *,
    max_rows: int | None = None,
) -> pd.DataFrame:
    dataset_path = Path(path)
    if not dataset_path.is_file():
        raise FileNotFoundError(f"Inventory dataset not found: {dataset_path}")
    frame = pd.read_csv(dataset_path, nrows=max_rows)
    validate_columns(list(frame.columns))
    frame = frame.loc[:, list(REQUIRED_COLUMNS)].copy()
    frame["Variety"] = frame["Variety"].astype(str)
    numeric_columns = [column for column in REQUIRED_COLUMNS if column != "Variety"]
    frame[numeric_columns] = frame[numeric_columns].apply(pd.to_numeric, errors="coerce")
    frame = frame.dropna(subset=list(REQUIRED_COLUMNS)).reset_index(drop=True)
    if frame.empty:
        raise ValueError("The inventory dataset contains no valid training rows.")
    return frame