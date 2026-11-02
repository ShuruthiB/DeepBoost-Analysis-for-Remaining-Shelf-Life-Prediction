import React, { useEffect, useMemo, useState } from 'react';
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { AlertTriangle, CalendarDays, Package, TrendingDown } from 'lucide-react';
import { apiRequest } from '../lib/api';
import './views.css';

type InventoryItem = {
  id: string;
  batch: string;
  variety: string;
  shelf: string;
  status: string;
  days: number | null;
};

type DecayPoint = {
  inventory_id: string;
  recorded_at: string;
  days_remaining: number;
  status: string;
};

const colors = ['#3b82f6', '#22c55e', '#f59e0b', '#ef4444', '#a855f7', '#06b6d4'];

export const AnalyticsView: React.FC = () => {
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
  const selectedHistory = decayHistory.filter(point => point.inventory_id === selectedId);
  const chartData = selectedHistory.map(point => ({
    date: point.recorded_at,
    days: point.days_remaining,
    status: point.status,
  }));
  const averageRemainingDays = inventory.length
    ? inventory.reduce((sum, item) => sum + (item.days ?? 0), 0) / inventory.length
    : 0;
  const atRiskCount = inventory.filter(item => item.days != null && item.days <= 10).length;
  const latestDate = decayHistory.at(-1)?.recorded_at ?? 'No records';
  const statusColor = selectedBatch?.status === 'CRITICAL'
    ? '#ef4444'
    : selectedBatch?.status === 'WARNING'
      ? '#f59e0b'
      : '#22c55e';

  const varietyLines = useMemo(
    () => Array.from(new Set(inventory.map(item => item.variety))).map((variety, index) => (
      <Line
        key={variety}
        type="monotone"
        data={Array.from(new Set(decayHistory.map(point => point.recorded_at))).map(date => {
          const batchIds = inventory.filter(item => item.variety === variety).map(item => item.id);
          const values = decayHistory
            .filter(point => batchIds.includes(point.inventory_id) && point.recorded_at === date)
            .map(point => point.days_remaining);
          return {
            date,
            days: values.length
              ? values.reduce((sum, value) => sum + value, 0) / values.length
              : null,
          };
        })}
        dataKey="days"
        name={variety}
        stroke={colors[index % colors.length]}
        strokeWidth={2}
        dot={{ r: 3 }}
      />
    )),
    [decayHistory, inventory],
  );

  return (
    <div className="view-container">
      <header className="view-header">
        <div>
          <h1>Batch Decay Analytics</h1>
        </div>
      </header>

      {error && <div className="panel"><p>{error}</p></div>}

      <section className="panel metrics-overview">
        <div className="metrics-grid">
          <div className="metric-card">
            <Package size={24} />
            <div><div className="metric-value">{inventory.length}</div><div className="metric-label">Tracked Batches</div></div>
          </div>
          <div className="metric-card">
            <TrendingDown size={24} />
            <div><div className="metric-value">{averageRemainingDays.toFixed(1)}</div><div className="metric-label">Average Days Remaining</div></div>
          </div>
          <div className="metric-card">
            <AlertTriangle size={24} />
            <div><div className="metric-value">{atRiskCount}</div><div className="metric-label">Batches at Risk</div></div>
          </div>
          <div className="metric-card">
            <CalendarDays size={24} />
            <div><div className="metric-value">{latestDate}</div><div className="metric-label">Latest Recorded Date</div></div>
          </div>
        </div>
      </section>

      <section className="panel">
        <div className="panel-header">
          <div>
            <h2>Batch Decay History</h2>
          </div>
          <select value={selectedId} onChange={event => setSelectedId(event.target.value)}>
            {inventory.map(item => (
              <option key={item.id} value={item.id}>{item.batch} - {item.variety}</option>
            ))}
          </select>
        </div>
        <div style={{ width: '100%', height: 330 }}>
          <ResponsiveContainer>
            <LineChart data={chartData} margin={{ top: 20, right: 30, left: 10, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
              <XAxis dataKey="date" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" label={{ value: 'Days Remaining', angle: -90, position: 'insideLeft', fill: '#94a3b8' }} />
              <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', color: '#fff' }} />
              <Line type="monotone" dataKey="days" stroke={statusColor} strokeWidth={3} name="Days remaining" dot={{ r: 5 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
        {selectedBatch && (
          <div className="result-panel" style={{ borderColor: statusColor }}>
            <strong>{selectedBatch.batch} ({selectedBatch.variety})</strong>
            <span> Shelf {selectedBatch.shelf} · {selectedBatch.status} · {selectedBatch.days ?? '--'} days remaining</span>
          </div>
        )}
      </section>

      <section className="panel">
        <h2>All Variety Decay Trends</h2>
        <div style={{ width: '100%', height: 330 }}>
          <ResponsiveContainer>
            <LineChart margin={{ top: 20, right: 30, left: 10, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
              <XAxis dataKey="date" type="category" allowDuplicatedCategory={false} stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', color: '#fff' }} />
              <Legend />
              {varietyLines}
            </LineChart>
          </ResponsiveContainer>
        </div>
      </section>
    </div>
  );
};
