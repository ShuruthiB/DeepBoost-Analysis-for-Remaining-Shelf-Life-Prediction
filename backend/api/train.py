from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..data.loader import DEFAULT_DATASET_PATH

router = APIRouter()


class TrainRequest(BaseModel):
    dataset: str | None = None
    max_rows: int | None = None
    epochs: int = 3
    batch_size: int = 4096


@router.post("/models/train")
def train_model(request: TrainRequest):
    if request.epochs < 1 or request.batch_size < 1:
        raise HTTPException(status_code=422, detail="epochs and batch_size must be positive.")
    from ..training.train_hybrid import TrainingConfig, train  # needs torch: not in packaged app

    return train(TrainingConfig(
        dataset_path=request.dataset or DEFAULT_DATASET_PATH,
        max_rows=request.max_rows,
        epochs=request.epochs,
        batch_size=request.batch_size,
    ))