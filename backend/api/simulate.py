from fastapi import APIRouter
from pydantic import BaseModel
from kinetics.q10 import calculate_q10_decay
import random

router = APIRouter()

class ScenarioRequest(BaseModel):
    scenario: str # ideal, moderate, severe

@router.post("/simulate/scenario")
def run_simulation(data: ScenarioRequest):
    temps = []
    base_temp = 4.0
    
    # Generate anomalous temporal sequence based on scenario
    for i in range(5):
        if data.scenario == 'severe' and i >= 3:
            temps.append(base_temp + 6.0 + random.uniform(0, 2))
        elif data.scenario == 'moderate':
            temps.append(base_temp + random.uniform(-2, 3))
        else:
            temps.append(base_temp + random.uniform(-0.5, 0.5))
            
    days = calculate_q10_decay(temps, base_life=15.0, ph=4.8, moisture=0.75)
    
    status = "SAFE"
    if days <= 5.0:
        status = "CRITICAL"
        
    return {
        "scenario": data.scenario,
        "days": round(days, 1),
        "status": status,
        "history": [round(t, 1) for t in temps]
    }
