import React, { useEffect, useMemo, useState } from 'react';
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { AlertTriangle, CalendarDays, CheckCircle, Package, TrendingDown } from 'lucide-react';
import { apiRequest } from '../lib/api';
import './views.css';

type InventoryItem = {
  id: string;
  batch: string;
  supplier: string;
  variety: string;
  shelf: string;
  ph: number;
  moisture: number;
  temp: number;
  status: string;
  days: number | null;
};

type DecayPoint = {
  inventory_id: string;
  recorded_at: string;
  days_remaining: number;
  status: string;
};

const statusColors: Record<string, string> = {
  SAFE: '#22c55e',
  WARNING: '#f59e0b',
  CRITICAL: '#ef4444',
  Pending: '#94a3b8',
};

export const ProjectionView: React.FC = () => {
  const [inventory, setInventory] = useState<InventoryItem[]>([]);
  const [decayHistory, setDecayHistory] = useState<DecayPoint[]>([]);
  const [selectedId, setSelectedId] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    Promise.all([
      apiRequest<InventoryItem[]>('/inventory'),
      apiRequest<DecayPoint[]>('/inventory/decay'),
    ])
      .then(([inventoryRows, decayRows]) => {
        setInventory(inventoryRows);
        setDecayHistory(decayRows);
        setSelectedId(inventoryRows[0]?.id ?? '');
      })
      .catch((requestError: Error) => setError(requestError.message));
  }, []);

  const selectedBatch = inventory.find(item => item.id === selectedId);
  const history = useMemo(
    () => decayHistory
      .filter(point => point.inventory_id === selectedId)
      .map(point => ({
        date: point.recorded_at,
        days: point.days_remaining,
        status: point.status,
      })),
    [decayHistory, selectedId],
  );
  const firstDays = history[0]?.days ?? selectedBatch?.days ?? 0;
  const currentDays = history.at(-1)?.days ?? selectedBatch?.days ?? 0;
  const degradation = firstDays > 0
    ? Math.max(0, ((firstDays - currentDays) / firstDays) * 100)
    : 0;
  const color = statusColors[selectedBatch?.status ?? 'Pending'];

  return (
    <div className="view-container">
      <header className="view-header">
        <div>
          <h1>Shelf Life Projection</h1>
        </div>
      </header>

      {error && <div className="panel"><p>{error}</p></div>}

      <section className="panel">
        <div className="panel-header">
          <div>
            <h2>Inventory Batch</h2>
          </div>
          <select value={selectedId} onChange={event => setSelectedId(event.target.value)}>
            {inventory.map(item => (
              <option key={item.id} value={item.id}>
                {item.batch} - {item.variety} - {item.status}
              </option>
            ))}
          </select>
        </div>
        {selectedBatch && (
          <div className="dashboard-grid">
            <div className="metric-card">
              <Package size={24} />
              <div><div className="metric-value">{selectedBatch.batch}</div><div className="metric-label">{selectedBatch.variety} · Shelf {selectedBatch.shelf}</div></div>
            </div>
            <div className="metric-card">
              {selectedBatch.status === 'SAFE' ? <CheckCircle size={24} /> : <AlertTriangle size={24} />}
              <div><div className="metric-value">{selectedBatch.status}</div><div className="metric-label">Saved inventory status</div></div>
            </div>
            <div className="metric-card">
              <TrendingDown size={24} />
              <div><div className="metric-value">{currentDays.toFixed(1)} Days</div><div className="metric-label">Remaining shelf life</div></div>
            </div>
            <div className="metric-card">
              <CalendarDays size={24} />
              <div><div className="metric-value">{degradation.toFixed(1)}%</div><div className="metric-label">Recorded decay</div></div>
            </div>
          </div>
        )}
      </section>

      <section className="panel">
        <h2>Persisted Daily Decay</h2>
        <div style={{ width: '100%', height: 330 }}>
          <ResponsiveContainer>
            <LineChart data={history} margin={{ top: 20, right: 30, left: 10, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
              <XAxis dataKey="date" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" label={{ value: 'Days Remaining', angle: -90, position: 'insideLeft', fill: '#94a3b8' }} />
              <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', color: '#fff' }} />
              <Line type="monotone" dataKey="days" stroke={color} strokeWidth={3} dot={{ r: 5 }} name="Days remaining" />
            </LineChart>
          </ResponsiveContainer>
        </div>
        {!history.length && <p className="subtitle">No decay history is available for this batch.</p>}
      </section>
    </div>
  );
};
