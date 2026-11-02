import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { AlertTriangle, CheckCircle2, Radio, Thermometer, Droplets, Wind } from 'lucide-react';
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { apiRequest } from '../lib/api';
import './views.css';

type InventoryBatch = {
  id: string;
  batch: string;
  variety: string;
  shelf: string;
  temp: number;
};

type SensorReading = {
  time: string;
  temperature: number;
  humidity: number;
  ethylene: number;
  status: 'STABLE' | 'WATCH' | 'ALERT';
  explanation: string;
  advisory: string;
};

const ranges: Record<string, { temperature: [number, number]; humidity: [number, number] }> = {
  Banana: { temperature: [13, 15], humidity: [75, 80] },
  Orange: { temperature: [3, 8], humidity: [85, 90] },
  Pineapple: { temperature: [10, 13], humidity: [80, 88] },
  Tomato: { temperature: [12, 16], humidity: [90, 95] },
};

const simulatedStepMs = 30 * 60 * 1000;
const updateIntervalMs = 60 * 1000;
const maxReadings = 24;

function formatTime(date: Date) {
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function createReading(batch: InventoryBatch, timestamp: number, sequence: number): SensorReading {
  const range = ranges[batch.variety] || ranges.Banana;
  const midpoint = (range.temperature[0] + range.temperature[1]) / 2;
  const temperature = midpoint + Math.sin(sequence * 0.9) * 1.1 + Math.cos(sequence * 0.35) * 0.4;
  const humidityMidpoint = (range.humidity[0] + range.humidity[1]) / 2;
  const humidity = humidityMidpoint + Math.cos(sequence * 0.7) * 2.4 + Math.sin(sequence * 0.2) * 1.2;
  const ethylene = Math.max(0.1, 0.8 + sequence * 0.04 + Math.sin(sequence * 0.6) * 0.2);
  const temperatureOutside = temperature < range.temperature[0] - 1 || temperature > range.temperature[1] + 1;
  const humidityOutside = humidity < range.humidity[0] - 3 || humidity > range.humidity[1] + 3;
  const temperatureWatch = temperature < range.temperature[0] || temperature > range.temperature[1];
  const humidityWatch = humidity < range.humidity[0] || humidity > range.humidity[1];
  const status = temperatureOutside || humidityOutside ? 'ALERT' : temperatureWatch || humidityWatch ? 'WATCH' : 'STABLE';
  const factor = temperatureOutside || temperatureWatch
    ? `Temperature ${temperature.toFixed(1)}°C vs ${range.temperature[0]}-${range.temperature[1]}°C target`
    : `Humidity ${humidity.toFixed(1)}% vs ${range.humidity[0]}-${range.humidity[1]}% target`;
  const advisory = status === 'ALERT'
    ? 'Inspect the shelf and adjust ambient conditions now.'
    : status === 'WATCH'
      ? 'Check ventilation and confirm the sensor reading.'
      : 'Conditions are within the recommended range.';

  return {
    time: formatTime(new Date(timestamp)),
    temperature: Number(temperature.toFixed(1)),
    humidity: Number(humidity.toFixed(1)),
    ethylene: Number(ethylene.toFixed(2)),
    status,
    explanation: factor,
    advisory,
  };
}

export const MonitorShelvesView: React.FC = () => {
  const [inventory, setInventory] = useState<InventoryBatch[]>([]);
  const [selectedId, setSelectedId] = useState('');
  const [readings, setReadings] = useState<SensorReading[]>([]);
  const [error, setError] = useState('');

  const resetReadings = useCallback((batch: InventoryBatch) => {
    const now = Date.now();
    setReadings(Array.from({ length: 12 }, (_, index) =>
      createReading(batch, now - (11 - index) * simulatedStepMs, index),
    ));
  }, []);

  useEffect(() => {
    apiRequest<InventoryBatch[]>('/inventory')
      .then(items => {
        setInventory(items);
        const firstBatch = items[0];
        if (firstBatch) {
          setSelectedId(current => current || firstBatch.id);
          resetReadings(firstBatch);
        }
      })
      .catch(() => setError('Unable to load inventory batches.'));
  }, [resetReadings]);

  const selectedBatch = inventory.find(item => item.id === selectedId);

  useEffect(() => {
    if (!selectedBatch) return;
    let nextSequence = 12;
    const simulationStart = Date.now();
    const timer = window.setInterval(() => {
      setReadings(current => {
        const next = createReading(
          selectedBatch,
          simulationStart + nextSequence * simulatedStepMs,
          nextSequence,
        );
        nextSequence += 1;
        return [...current, next].slice(-maxReadings);
      });
    }, updateIntervalMs);
    return () => window.clearInterval(timer);
  }, [selectedBatch]);

  const latest = readings[readings.length - 1];
  const statusClass = latest?.status.toLowerCase() || 'stable';
  const statusIcon = latest?.status === 'ALERT'
    ? <AlertTriangle size={18} />
    : latest?.status === 'WATCH'
      ? <AlertTriangle size={18} />
      : <CheckCircle2 size={18} />;

  const chartData = useMemo(() => readings.map(reading => ({
    ...reading,
    label: reading.time,
  })), [readings]);

  return (
    <div className="view-container">
      <div className="page-heading-row">
        <div>
          <h1>Monitor Shelves</h1>
        </div>
        <div className="monitor-selector">
          <label htmlFor="monitor-batch">Batch</label>
          <select
            id="monitor-batch"
            className="styled-select"
            value={selectedId}
            onChange={event => {
              const nextBatch = inventory.find(item => item.id === event.target.value);
              setSelectedId(event.target.value);
              if (nextBatch) resetReadings(nextBatch);
            }}
            disabled={!inventory.length}
          >
            {!inventory.length && <option value="">No batches available</option>}
            {inventory.map(item => (
              <option key={item.id} value={item.id}>
                {item.id} · {item.variety} · Shelf {item.shelf}
              </option>
            ))}
          </select>
        </div>
      </div>

      {error && <div className="inline-error">{error}</div>}
      {selectedBatch && latest && (
        <>
          <div className="monitor-summary-grid">
            <div className={`panel monitor-status-card ${statusClass}`}>
              <div className="monitor-status-title"><Radio size={18} /> Ambient status</div>
              <strong>{latest.status}</strong>
              <span>{latest.time} · updates every 30 min</span>
            </div>
            <div className="panel sensor-metric">
              <Thermometer size={18} />
              <span>Temperature</span>
              <strong>{latest.temperature}°C</strong>
            </div>
            <div className="panel sensor-metric">
              <Droplets size={18} />
              <span>Humidity</span>
              <strong>{latest.humidity}%</strong>
            </div>
            <div className="panel sensor-metric">
              <Wind size={18} />
              <span>Ethylene</span>
              <strong>{latest.ethylene} ppm</strong>
            </div>
          </div>

          <div className="dashboard-grid monitor-grid">
            <div className="panel chart-panel">
              <div className="panel-header">
                <h2>Live environment trend</h2>
                <span className="live-indicator"><i /> Live</span>
              </div>
              <div className="monitor-chart">
                <ResponsiveContainer>
                  <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                    <XAxis dataKey="label" stroke="#94a3b8" />
                    <YAxis yAxisId="temperature" stroke="#f97316" />
                    <YAxis yAxisId="humidity" orientation="right" stroke="#38bdf8" domain={['auto', 'auto']} />
                    <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: 'none', color: '#fff' }} />
                    <Line yAxisId="temperature" type="monotone" dataKey="temperature" stroke="#f97316" strokeWidth={2} dot={false} name="Temperature °C" />
                    <Line yAxisId="humidity" type="monotone" dataKey="humidity" stroke="#38bdf8" strokeWidth={2} dot={false} name="Humidity %" />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="panel explainability-panel">
              <div className="panel-header"><h2>Explainable status</h2></div>
              <div className={`explainability-status ${statusClass}`}>{statusIcon}<strong>{latest.status}</strong></div>
              <p>{latest.explanation}</p>
              <div className="advisory">
                <strong>Advisory</strong>
                <span>{latest.advisory}</span>
              </div>
              <div className="monitor-factors">
                <span>Batch: {selectedBatch.id}</span>
                <span>Variety: {selectedBatch.variety}</span>
                <span>Shelf: {selectedBatch.shelf}</span>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};
