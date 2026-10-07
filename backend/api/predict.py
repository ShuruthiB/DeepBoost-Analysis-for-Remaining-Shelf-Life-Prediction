from fastapi import APIRouter
from pydantic import BaseModel
import torch
import torch.nn as nn
import lightgbm as lgb
import joblib
import os
import numpy as np
from kinetics.q10 import calculate_q10_decay

router = APIRouter()

class PredictRequest(BaseModel):
    variety: str
    shelf: str
    ph: float
    moisture: float
    temperatures: list[float]

# 1. Define the identical PyTorch architecture used in Colab
class HybridShelfLifeModel(nn.Module):
    def __init__(self, dyn_features, stat_features, hidden_size=128):
        super(HybridShelfLifeModel, self).__init__()
        self.lstm = nn.LSTM(input_size=dyn_features, hidden_size=hidden_size, batch_first=True, num_layers=2)
        self.fc1 = nn.Linear(hidden_size + 1 + stat_features, 256)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(256, 128) 
        self.fc3 = nn.Linear(128, 1)

    def forward(self, x_dynamic, x_lgb_static, x_raw_static):
        _, (hn, _) = self.lstm(x_dynamic)
        temporal_features = hn[-1] 
        fusion_features = torch.cat((temporal_features, x_lgb_static, x_raw_static), dim=1)
        
        out = self.relu(self.fc1(fusion_features))
        out = self.relu(self.fc2(out))
        return self.fc3(out).squeeze(dim=-1)

# 2. Pre-load Models and Scalers on server startup
MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
MODELS_LOADED = False

try:
    # Load Scalers
    scaler_stat = joblib.load(os.path.join(MODELS_DIR, 'scaler_stat.pkl'))
    scaler_dyn = joblib.load(os.path.join(MODELS_DIR, 'scaler_dyn.pkl'))
    
    # Load LightGBM
    lgbm_model = lgb.Booster(model_file=os.path.join(MODELS_DIR, 'lgbm_static.txt'))
    
    # Load PyTorch LSTM (dyn_features=1 for temperature, stat_features=2 for pH/moisture)
    device = torch.device("cpu")
    hybrid_lstm = HybridShelfLifeModel(dyn_features=1, stat_features=2).to(device)
    hybrid_lstm.load_state_dict(torch.load(os.path.join(MODELS_DIR, 'hybrid_lstm.pt'), map_location=device, weights_only=True))
    hybrid_lstm.eval()
    
    MODELS_LOADED = True
    print("Successfully loaded Colab models from disk.")
except Exception as e:
    print(f"Warning: Models not found in /models folder. Using Physics Engine fallback. Error: {e}")


@router.post("/predict")
def predict_shelf_life(data: PredictRequest):
    if MODELS_LOADED:
        # 3. AI Inference Flow (Matches Colab Data Formatting)
        
        # Prepare Static Data [pH, moisture]
        static_raw = np.array([[data.ph, data.moisture]])
        static_scaled = scaler_stat.transform(static_raw)
        
        # Prepare Dynamic Data [5 days of temperatures]
        # Reshape to (5, 1) for scaling, then (1, 5, 1) for PyTorch batching
        dyn_raw = np.array(data.temperatures).reshape(5, 1)
        dyn_scaled = scaler_dyn.transform(dyn_raw).reshape(1, 5, 1)

        # LightGBM Prediction (Output must be reshaped to (1, 1) for PyTorch cat)
        lgb_out = lgbm_model.predict(static_scaled).reshape(-1, 1)
        
        # PyTorch Hybrid Prediction
        with torch.no_grad():
            t_dyn = torch.FloatTensor(dyn_scaled)
            t_lgb = torch.FloatTensor(lgb_out)
            t_stat = torch.FloatTensor(static_scaled)
            
            hybrid_out = hybrid_lstm(t_dyn, t_lgb, t_stat)
            
            # Extract scalar float
            raw_predicted_days = hybrid_out.item()
            
            # Apply biological baseline scaling so different fruits react uniquely
            bases = {'Banana': 15.0, 'Orange': 28.0, 'Pineapple': 10.0, 'Tomato': 18.0}
            base = bases.get(data.variety, 15.0)
            
            # Scale the raw normalized model output by the biological baseline
            predicted_days = raw_predicted_days * (base / 15.0)
            
        data_source = "DeepBoost Hybrid Model (Live Inference)"
    else:
        # Fallback if files aren't dropped into the /models/ folder yet
        bases = {'Banana': 15.0, 'Orange': 28.0, 'Pineapple': 10.0, 'Tomato': 18.0}
        base = bases.get(data.variety, 15.0)
        predicted_days = calculate_q10_decay(data.temperatures, base, data.ph, data.moisture)
        data_source = "Physics Engine (Fallback Mode)"
    
    # Boundary constraints
    predicted_days = max(0.0, min(float(predicted_days), 40.0))

    status = "SAFE"
    if predicted_days <= 5.0:
        status = "CRITICAL"
    elif predicted_days <= 10.0:
        status = "WARNING"
        
    return {
        "variety": data.variety,
        "shelf": data.shelf,
        "predicted_days": round(predicted_days, 1),
        "status": status,
        "model_trained": MODELS_LOADED,
        "data_source": data_source
    }
