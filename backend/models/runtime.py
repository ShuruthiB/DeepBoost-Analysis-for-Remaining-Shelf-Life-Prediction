"""Torch-free inference: runs the trained hybrid LSTM with NumPy only.

`export_runtime_files()` converts hybrid_lstm.pt + the sklearn scalers into
runtime_weights.npz / runtime_scalers.json (needs torch+joblib, run at training time).
`load_runtime()` + `hybrid_residual()` use only NumPy, so the packaged app needs no torch.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

MODEL_DIR = Path(__file__).resolve().parent
WEIGHTS = "runtime_weights.npz"
SCALERS = "runtime_scalers.json"


def export_runtime_files(model_dir: str | Path = MODEL_DIR) -> None:
    import joblib
    import torch

    directory = Path(model_dir)
    state = torch.load(directory / "hybrid_lstm.pt", map_location="cpu", weights_only=True)
    np.savez(directory / WEIGHTS, **{k: v.numpy().astype(np.float32) for k, v in state.items()})
    scalers = {}
    for key, name in (("static", "scaler_stat.pkl"), ("dynamic", "scaler_dyn.pkl")):
        scaler = joblib.load(directory / name)
        scalers[key] = {"mean": scaler.mean_.tolist(), "scale": scaler.scale_.tolist()}
    (directory / SCALERS).write_text(json.dumps(scalers))


def runtime_files_exist(model_dir: str | Path = MODEL_DIR) -> bool:
    directory = Path(model_dir)
    return (directory / WEIGHTS).is_file() and (directory / SCALERS).is_file()


def load_runtime(model_dir: str | Path = MODEL_DIR) -> dict:
    directory = Path(model_dir)
    weights = {k: v for k, v in np.load(directory / WEIGHTS).items()}
    scalers = json.loads((directory / SCALERS).read_text())
    return {
        "weights": weights,
        "scalers": {
            k: {"mean": np.asarray(v["mean"], np.float32), "scale": np.asarray(v["scale"], np.float32)}
            for k, v in scalers.items()
        },
    }


def _sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-x))


def _lstm_last_hidden(w: dict, seq: np.ndarray) -> np.ndarray:
    """2-layer LSTM (PyTorch gate order i,f,g,o); seq: (batch, steps, features)."""
    batch, steps, _ = seq.shape
    layer_input = seq
    for layer in (0, 1):
        w_ih, w_hh = w[f"lstm.weight_ih_l{layer}"], w[f"lstm.weight_hh_l{layer}"]
        bias = w[f"lstm.bias_ih_l{layer}"] + w[f"lstm.bias_hh_l{layer}"]
        hidden_size = w_hh.shape[1]
        h = np.zeros((batch, hidden_size), np.float32)
        c = np.zeros((batch, hidden_size), np.float32)
        outputs = []
        for t in range(steps):
            gates = layer_input[:, t, :] @ w_ih.T + h @ w_hh.T + bias
            i, f, g, o = np.split(gates, 4, axis=1)
            c = _sigmoid(f) * c + _sigmoid(i) * np.tanh(g)
            h = _sigmoid(o) * np.tanh(c)
            outputs.append(h)
        layer_input = np.stack(outputs, axis=1)
    return h


def hybrid_residual(runtime: dict, dynamic_raw: np.ndarray, static_raw: np.ndarray,
                    lgb_prediction: np.ndarray) -> np.ndarray:
    """dynamic_raw: (batch, 5) temps; static_raw: (batch, 2) pH, moisture; lgb_prediction: (batch,)."""
    s, d, w = runtime["scalers"], runtime["scalers"]["dynamic"], runtime["weights"]
    static = (static_raw - s["static"]["mean"]) / s["static"]["scale"]
    dynamic = ((dynamic_raw - d["mean"]) / d["scale"]).astype(np.float32)[..., None]
    hidden = _lstm_last_hidden(w, dynamic)
    fused = np.concatenate([hidden, lgb_prediction.reshape(-1, 1), static], axis=1).astype(np.float32)
    x = np.maximum(fused @ w["head.0.weight"].T + w["head.0.bias"], 0.0)
    return (x @ w["head.2.weight"].T + w["head.2.bias"]).reshape(-1)
