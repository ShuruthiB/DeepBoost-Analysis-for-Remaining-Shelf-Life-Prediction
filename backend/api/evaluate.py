from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..data.loader import DEFAULT_DATASET_PATH

router = APIRouter()


class EvaluationRequest(BaseModel):
    dataset: str | None = None
    max_rows: int | None = None


@router.get("/models/comparison")
def get_metrics():
    try:
        from ..evaluation.evaluate_hybrid import evaluate
        return evaluate()
    except (FileNotFoundError, OSError, RuntimeError, ValueError, KeyError) as error:
        raise HTTPException(status_code=503, detail=str(error)) from error


@router.post("/models/evaluate")
def evaluate_model(request: EvaluationRequest):
    try:
        from ..evaluation.evaluate_hybrid import evaluate
        return evaluate(
            request.dataset or DEFAULT_DATASET_PATH,
            max_rows=request.max_rows,
        )
    except (FileNotFoundError, OSError, RuntimeError, ValueError, KeyError) as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
