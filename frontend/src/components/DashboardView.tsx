import React, { useEffect, useState } from 'react';
import { AlertCircle, TrendingUp, PackageCheck, AlertTriangle, Activity } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import './views.css';
import { apiRequest } from '../lib/api';

export const DashboardView: React.FC = () => {
  const [inventory, setInventory] = useState<any[]>([]);
  useEffect(() => {
    apiRequest<any[]>('/inventory')
      .then(setInventory)
      .catch(error => console.error(error));
  }, []);
  const healthData = Array.from(new Set(inventory.map(item => item.variety))).map(name => ({
    name,
    safe: inventory.filter(item => item.variety === name && item.status === 'SAFE').length,
    warning: inventory.filter(item => item.variety === name && item.status === 'WARNING').length,
    critical: inventory.filter(item => item.variety === name && item.status === 'CRITICAL').length,
  }));
  const analyzed = inventory.filter(item => item.days != null);
  const criticalCount = inventory.filter(item => item.status === 'CRITICAL').length;
  const atRisk = inventory
    .filter(item => item.days != null && Number(item.days) <= 10)
    .sort((left, right) => Number(left.days) - Number(right.days))
    .slice(0, 3);
  const averageDays = analyzed.length
    ? analyzed.reduce((sum, item) => sum + Number(item.days), 0) / analyzed.length
    : 0;

  return (
    <div className="view-container">
      <h1>System Overview</h1>
      
      <div className="kpi-grid-4">
        <div className="kpi-card safe">
          <div className="kpi-icon"><PackageCheck size={24}/></div>
          <div className="kpi-data">
            <h3>Total Active Stock</h3>
            <p className="kpi-value">{inventory.length}</p>
          </div>
        </div>
        <div className="kpi-card warning">
          <div className="kpi-icon"><TrendingUp size={24}/></div>
          <div className="kpi-data">
            <h3>Avg. Shelf Life</h3>
            <p className="kpi-value">{averageDays.toFixed(1)} Days</p>
          </div>
        </div>
        <div className="kpi-card critical">
          <div className="kpi-icon"><AlertCircle size={24}/></div>
          <div className="kpi-data">
            <h3>Critical (&lt; 5 Days)</h3>
            <p className="kpi-value">{criticalCount}</p>
          </div>
        </div>
        <div className="kpi-card highlight">
        <div className="kpi-icon"><TrendingUp size={24}/></div>
          <div className="kpi-data">
              <h3>At-Risk Batches</h3>
              <p className="kpi-value">{atRisk.length}</p>
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
            {atRisk.map(item => (
              <div className="risk-item" key={item.id}>
                <div className="risk-info">
                  <strong>{item.id} ({item.variety})</strong>
                  <span>Shelf {item.shelf} • {item.status} priority</span>
                </div>
                <div className={`risk-badge ${item.status.toLowerCase()}`}>
                  {item.days} Days Left
                </div>
              </div>
            ))}
            {atRisk.length === 0 && <p className="subtitle">No batches require immediate attention.</p>}
          </div>
        </div>
      </div>

      <div className="panel">
        <h2>Live Network Telemetry Log</h2>
        <ul className="alert-list log-list" style={{ minHeight: '180px' }}>
          {inventory.filter(item => item.status !== 'Pending').slice(0, 5).map((item) => {
            const log = {
              id: item.id,
              type: item.status.toLowerCase(),
              time: 'Database',
              text: `${item.id} (${item.variety}) analyzed by the hybrid model: ${item.days ?? '--'} days remaining.`
            };
            return (
            <li key={log.id} className={`alert-item ${log.type}`} style={{ animation: 'fadeIn 0.5s ease-in' }}>
              {log.type === 'critical' && <AlertTriangle size={16}/>}
              {log.type === 'warning' && <Activity size={16}/>}
              {log.type === 'safe' && <PackageCheck size={16}/>}
              <span><strong>{log.time} - </strong> {log.text}</span>
            </li>
            );
          })}
        </ul>
      </div>
    </div>
  );
};
