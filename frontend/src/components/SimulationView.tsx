import React, { useState } from 'react';
import { Activity, ThermometerSun, Snowflake, Wind } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import './views.css';

const scenarioDataMap: any = {
  ideal: [ { day: '-4 Days', temp: 4 }, { day: '-3 Days', temp: 4.2 }, { day: '-2 Days', temp: 3.9 }, { day: '-1 Day', temp: 4.1 }, { day: 'Today', temp: 4.0 } ],
  moderate: [ { day: '-4 Days', temp: 4 }, { day: '-3 Days', temp: 5.5 }, { day: '-2 Days', temp: 3.0 }, { day: '-1 Day', temp: 6.2 }, { day: 'Today', temp: 4.8 } ],
  severe: [ { day: '-4 Days', temp: 4 }, { day: '-3 Days', temp: 4.5 }, { day: '-2 Days', temp: 5.0 }, { day: '-1 Day', temp: 10.5 }, { day: 'Today', temp: 12.0 } ]
};

const varietyProfiles: any = {
  'Banana': { ph: 4.8, moisture: 0.75, offset: 0 },
  'Orange': { ph: 3.8, moisture: 0.87, offset: -2.5 }, 
  'Pineapple': { ph: 3.6, moisture: 0.86, offset: 1.0 },
  'Tomato': { ph: 4.3, moisture: 0.94, offset: -1.5 }
};

export const SimulationView: React.FC = () => {
  const [scenario, setScenario] = useState('ideal');
  const [variety, setVariety] = useState('Banana');
  const [result, setResult] = useState<any>(null);

  const runSimulation = async () => {
    setResult({ status: 'PROCESSING...', days: '--', msg: 'Sending sequence to DeepBoost FastAPI Server...' });
    
    // Shift the baseline temperature specific to the biological storage needs of the variety
    const profile = varietyProfiles[variety];
    const temps = scenarioDataMap[scenario].map((d: any) => parseFloat((d.temp + profile.offset).toFixed(1)));

    try {
      const response = await fetch("http://localhost:8000/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          variety: variety,
          shelf: 'Simulation',
          ph: profile.ph,
          moisture: profile.moisture,
          temperatures: temps
        })
      });
      const data = await response.json();
      
      const source = data.model_trained ? 'Colab PyTorch Model' : 'Physics Fallback Engine';
      setResult({
        status: data.status,
        days: data.predicted_days,
        msg: `Simulation processed successfully by ${source}. It evaluated the ${variety}'s reaction to this specific 5-day temperature curve.`
      });
    } catch (err) {
      setResult({ status: 'ERROR', days: '0', msg: 'Could not reach FastAPI server on port 8000.' });
    }
  };

  const profile = varietyProfiles[variety];
  const currentData = scenarioDataMap[scenario].map((d: any) => ({
    ...d,
    temp: parseFloat((d.temp + profile.offset).toFixed(1))
  }));

  return (
    <div className="view-container">
      <h1>IoT Environment Simulator</h1>
      <p className="subtitle">Inject synthetic anomaly profiles into the remote LSTM sequence engine.</p>
      
      <div className="dashboard-grid">
        <div className="panel simulation-controls">
          <h2>Configure Anomaly</h2>
          <div className="control-group">
            <label>Target Variety</label>
            <select value={variety} onChange={(e) => setVariety(e.target.value)}>
              <option value="Banana">Banana</option>
              <option value="Orange">Orange</option>
              <option value="Pineapple">Pineapple</option>
              <option value="Tomato">Tomato</option>
            </select>
          </div>
          <div className="control-group" style={{ marginTop: '15px' }}>
            <label>Select Climate Scenario</label>
            <div className="scenario-cards">
              <div className={`scenario-card ${scenario === 'ideal' ? 'active' : ''}`} onClick={() => setScenario('ideal')}>
                <Snowflake size={24} />
                <span>Ideal Cold</span>
              </div>
              <div className={`scenario-card ${scenario === 'moderate' ? 'active' : ''}`} onClick={() => setScenario('moderate')}>
                <Wind size={24} />
                <span>Fluctuations</span>
              </div>
              <div className={`scenario-card ${scenario === 'severe' ? 'active' : ''}`} onClick={() => setScenario('severe')}>
                <ThermometerSun size={24} />
                <span>Heatwave</span>
              </div>
            </div>
          </div>
          
          <button className="btn-primary" style={{ marginTop: '25px', width: '100%' }} onClick={runSimulation}>
            <Activity size={18} /> Execute Remote Simulation
          </button>
        </div>

        <div className="panel chart-panel">
          <h2>Simulated 5-Day Temperature Curve ({variety} Adjusted)</h2>
          <div style={{ width: '100%', height: 280 }}>
            <ResponsiveContainer>
              <LineChart data={currentData} margin={{ top: 20, right: 30, left: 10, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false}/>
                <XAxis dataKey="day" stroke="#94a3b8" label={{ value: "Timeline", position: "insideBottom", offset: -15, fill: "#94a3b8" }} />
                <YAxis stroke="#94a3b8" domain={[0, 16]} label={{ value: "Temp (°C)", angle: -90, position: "insideLeft", offset: 15, fill: "#94a3b8" }} />
                <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: 'none', color: '#fff' }} />
                <Line type="monotone" dataKey="temp" stroke="#ef4444" strokeWidth={3} dot={{ r: 5 }} name="Temp (°C)"/>
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {result && (
        <div className={`result-panel ${result.status.toLowerCase()}`}>
          <h2>AI Trajectory Result: {result.status}</h2>
          <div className="result-huge">{result.days} Days</div>
          <p>{result.msg}</p>
        </div>
      )}
    </div>
  );
};
