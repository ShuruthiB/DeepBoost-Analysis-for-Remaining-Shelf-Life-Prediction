import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './views.css';

const featureImportanceData = [
  { name: 'Temperature Sequence (LSTM)', importance: 0.85 },
  { name: 'pH Profile (LightGBM)', importance: 0.65 },
  { name: 'Moisture (LightGBM)', importance: 0.55 },
  { name: 'CO2 Exposure', importance: 0.20 }
];

const modelComparisonData = [
  { name: 'Standalone LSTM', r2: 0.56 },
  { name: 'Random Forest', r2: 0.83 },
  { name: 'XGBoost', r2: 0.84 },
  { name: 'Hybrid DeepBoost', r2: 0.99 }
];

export const AnalyticsView: React.FC = () => {
  return (
    <div className="view-container">
      <h1>DeepBoost Analytics & XAI</h1>
      <p className="subtitle">Model architecture performance and explainability metrics.</p>

      <div className="dashboard-grid">
        <div className="panel chart-panel">
          <h2>Architecture Comparison (Test Set)</h2>
          <div style={{ width: '100%', height: 320 }}>
            <ResponsiveContainer>
              <BarChart data={modelComparisonData} margin={{ top: 20, right: 30, left: 10, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false}/>
                <XAxis dataKey="name" stroke="#94a3b8" label={{ value: "Architecture", position: "insideBottom", offset: -15, fill: "#94a3b8" }} />
                <YAxis stroke="#94a3b8" domain={[0, 1]} label={{ value: "R² Score (Higher is Better)", angle: -90, position: "insideLeft", offset: 15, fill: "#94a3b8" }} />
                <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: 'none', color: '#fff' }} />
                <Legend verticalAlign="top" height={36}/>
                <Bar dataKey="r2" fill="#3b82f6" name="R² Score" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="panel chart-panel">
          <h2>Explainable AI (XAI) - Feature Importance</h2>
          <div style={{ width: '100%', height: 320 }}>
            <ResponsiveContainer>
              <BarChart data={featureImportanceData} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" horizontal={false} />
                <XAxis type="number" stroke="#94a3b8" label={{ value: "Relative Importance Weight", position: "insideBottom", offset: -15, fill: "#94a3b8" }} />
                <YAxis dataKey="name" type="category" width={170} stroke="#94a3b8" />
                <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: 'none', color: '#fff' }} />
                <Bar dataKey="importance" fill="#8b5cf6" name="Importance Score" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};
