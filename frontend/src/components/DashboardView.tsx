import React, { useState, useEffect } from 'react';
import { AlertCircle, TrendingUp, PackageCheck, AlertTriangle, DollarSign, Activity } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import './views.css';

const healthData = [
  { name: 'Banana', safe: 4000, warning: 800, critical: 200 },
  { name: 'Orange', safe: 3500, warning: 400, critical: 50 },
  { name: 'Pineapple', safe: 1200, warning: 600, critical: 300 },
  { name: 'Tomato', safe: 2800, warning: 900, critical: 150 },
];

export const DashboardView: React.FC = () => {
  const [logs, setLogs] = useState([
    { id: 1, type: 'critical', time: '10:42 AM', text: 'Shelf 3 (Pineapple): LSTM detected +4°C heat spike. Projected shelf life reduced by 40%.' },
    { id: 2, type: 'warning', time: '10:15 AM', text: 'Shelf 2 (Banana): LightGBM identified suboptimal moisture (0.87).' },
    { id: 3, type: 'safe', time: '09:00 AM', text: 'Shelf 1 (Orange): Batch stabilized. Hybrid model confidence interval narrowed.' }
  ]);

  // Sped up to 4 seconds so the live update is highly visible during demos
  useEffect(() => {
    const interval = setInterval(() => {
      const now = new Date();
      const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
      const randomEvent = Math.random();
      let newLog;
      if (randomEvent > 0.7) {
        newLog = { id: Date.now(), type: 'critical', time: timeStr, text: `Shelf ${Math.floor(Math.random()*5)+1}: Unscheduled temperature variance (+2.1°C). PyTorch LSTM flagged anomaly.` };
      } else if (randomEvent > 0.4) {
        newLog = { id: Date.now(), type: 'warning', time: timeStr, text: `Shelf ${['A','B','C','D'][Math.floor(Math.random()*4)]}: Micro-climate shift detected. Recalculating shelf life via LightGBM...` };
      } else {
        newLog = { id: Date.now(), type: 'safe', time: timeStr, text: `System nominal. Physics baseline matches DeepBoost tensor output.` };
      }
      setLogs(prev => [newLog, ...prev].slice(0, 5));
    }, 4000); 
    
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="view-container">
      <h1>System Overview</h1>
      <p className="subtitle">Real-time inventory intelligence and financial risk assessment.</p>
      
      <div className="kpi-grid-4">
        <div className="kpi-card safe">
          <div className="kpi-icon"><PackageCheck size={24}/></div>
          <div className="kpi-data">
            <h3>Total Active Stock</h3>
            <p className="kpi-value">14,900</p>
          </div>
        </div>
        <div className="kpi-card warning">
          <div className="kpi-icon"><TrendingUp size={24}/></div>
          <div className="kpi-data">
            <h3>Avg. Shelf Life</h3>
            <p className="kpi-value">14.2 Days</p>
          </div>
        </div>
        <div className="kpi-card critical">
          <div className="kpi-icon"><AlertCircle size={24}/></div>
          <div className="kpi-data">
            <h3>Critical (&lt; 5 Days)</h3>
            <p className="kpi-value">700 Units</p>
          </div>
        </div>
        <div className="kpi-card highlight">
          <div className="kpi-icon"><DollarSign size={24}/></div>
          <div className="kpi-data">
            <h3>Value at Risk</h3>
            <p className="kpi-value">$3,450</p>
          </div>
        </div>
      </div>
      
      <div className="dashboard-grid">
        <div className="panel chart-panel">
          <h2>Inventory Health Distribution</h2>
          <div style={{ width: '100%', height: 280 }}>
            <ResponsiveContainer>
              <BarChart data={healthData} margin={{ top: 20, right: 30, left: 10, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                <XAxis dataKey="name" stroke="#94a3b8" label={{ value: "Fruit Variety", position: "insideBottom", offset: -15, fill: "#94a3b8" }} />
                {/* Positive offset pushes it into the chart so it doesn't get cut off */}
                <YAxis stroke="#94a3b8" label={{ value: "Total Units", angle: -90, position: "insideLeft", offset: 15, fill: "#94a3b8" }} />
                <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: 'none', color: '#fff' }} />
                <Bar dataKey="safe" stackId="a" fill="#22c55e" name="Safe" />
                <Bar dataKey="warning" stackId="a" fill="#f59e0b" name="Warning" />
                <Bar dataKey="critical" stackId="a" fill="#ef4444" name="Critical" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="panel list-panel">
          <h2>Top At-Risk Batches</h2>
          <div className="risk-list">
            <div className="risk-item">
              <div className="risk-info">
                <strong>INV-003 (Pineapple)</strong>
                <span>Shelf C • Moisture Anomaly</span>
              </div>
              <div className="risk-badge critical">2 Days Left</div>
            </div>
            <div className="risk-item">
              <div className="risk-info">
                <strong>INV-112 (Banana)</strong>
                <span>Shelf A • High Temp Exposure</span>
              </div>
              <div className="risk-badge critical">3 Days Left</div>
            </div>
            <div className="risk-item">
              <div className="risk-info">
                <strong>INV-089 (Tomato)</strong>
                <span>Shelf D • pH Degradation</span>
              </div>
              <div className="risk-badge warning">6 Days Left</div>
            </div>
          </div>
        </div>
      </div>

      <div className="panel">
        <h2>Live Network Telemetry Log</h2>
        <ul className="alert-list log-list" style={{ minHeight: '180px' }}>
          {logs.map((log) => (
            <li key={log.id} className={`alert-item ${log.type}`} style={{ animation: 'fadeIn 0.5s ease-in' }}>
              {log.type === 'critical' && <AlertTriangle size={16}/>}
              {log.type === 'warning' && <Activity size={16}/>}
              {log.type === 'safe' && <PackageCheck size={16}/>}
              <span><strong>{log.time} - </strong> {log.text}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};
