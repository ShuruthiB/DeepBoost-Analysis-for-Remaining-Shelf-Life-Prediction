import React, { useState } from 'react';
import { Search, Filter, Plus, X, BarChart2 } from 'lucide-react';
import './views.css';

const initialInventory = [
  { id: 'INV-001', batch: 'BN-882', supplier: 'AgriCorp', variety: 'Banana', shelf: 'A', ph: 4.8, moisture: 0.75, temp: 15, status: 'Pending', days: '--' },
  { id: 'INV-002', batch: 'OR-110', supplier: 'SunFarms', variety: 'Orange', shelf: 'B', ph: 3.8, moisture: 0.87, temp: 4, status: 'Pending', days: '--' },
  { id: 'INV-003', batch: 'PN-405', supplier: 'TropiGrow', variety: 'Pineapple', shelf: 'C', ph: 3.6, moisture: 0.86, temp: 18, status: 'Pending', days: '--' },
  { id: 'INV-004', batch: 'TM-992', supplier: 'RedVine', variety: 'Tomato', shelf: 'D', ph: 4.3, moisture: 0.94, temp: 16, status: 'Pending', days: '--' },
  { id: 'INV-005', batch: 'BN-883', supplier: 'AgriCorp', variety: 'Banana', shelf: 'A', ph: 4.7, moisture: 0.76, temp: 21, status: 'Pending', days: '--' }
];

const optimalRanges: any = {
  'Banana': { ph: '4.5 - 5.2', moisture: '75% - 80%', temp: '13.0°C - 15.0°C' },
  'Orange': { ph: '3.3 - 4.2', moisture: '85% - 90%', temp: '3.0°C - 8.0°C' },
  'Pineapple': { ph: '3.4 - 4.0', moisture: '80% - 88%', temp: '10.0°C - 13.0°C' },
  'Tomato': { ph: '4.2 - 4.9', moisture: '90% - 95%', temp: '12.0°C - 16.0°C' }
};

export const InventoryView: React.FC = () => {
  const [inventory, setInventory] = useState(initialInventory);
  const [search, setSearch] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedBatch, setSelectedBatch] = useState<any>(null);
  const [newBatch, setNewBatch] = useState({ variety: 'Banana', batch: '', supplier: '', shelf: '', ph: 4.5, moisture: 0.8, temp: 10 });

  const handlePredict = async (item: any) => {
    try {
      const response = await fetch("http://localhost:8000/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          variety: item.variety,
          shelf: item.shelf,
          ph: item.ph,
          moisture: item.moisture,
          temperatures: [item.temp - 1, item.temp, item.temp, item.temp, item.temp]
        })
      });
      const data = await response.json();
      
      const updatedItem = { ...item, status: data.status, days: data.predicted_days };
      
      // Update global table state
      setInventory(prev => prev.map(invItem => invItem.id === item.id ? updatedItem : invItem));
      
      // FORCIBLY open the selected batch panel immediately upon clicking analyze so details are never hidden
      setSelectedBatch(updatedItem);
      
      return updatedItem;
    } catch (err) {
      console.error(err);
      return item;
    }
  };

  const handleAddBatch = async () => {
    const newId = `INV-00${inventory.length + 1}`;
    const tempItem = { ...newBatch, id: newId, status: 'Scanning...', days: 0 };
    setInventory([...inventory, tempItem]);
    setShowAddModal(false);
    
    await handlePredict(tempItem);
  };

  const filteredInventory = inventory.filter(item => 
    item.batch.toLowerCase().includes(search.toLowerCase()) || 
    item.variety.toLowerCase().includes(search.toLowerCase()) ||
    item.supplier.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="view-container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1>Inventory Database</h1>
          <p className="subtitle">Manage batches and trigger live DeepBoost API inferences.</p>
        </div>
        <div className="inventory-controls">
          <div className="search-bar">
            <Search size={16} />
            <input 
              type="text" 
              placeholder="Search batch, variety, supplier..." 
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <button className="btn-secondary" onClick={() => setShowAddModal(true)}><Plus size={16}/> Add Batch</button>
        </div>
      </div>

      <div className="panel table-container">
        <table className="inventory-table hoverable-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Batch</th>
              <th>Supplier</th>
              <th>Variety</th>
              <th>Shelf</th>
              <th>pH Profile</th>
              <th>Moisture</th>
              <th>Temp</th>
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {filteredInventory.map(item => (
              <tr key={item.id} onClick={() => setSelectedBatch(item)}>
                <td><strong>{item.id}</strong></td>
                <td>{item.batch}</td>
                <td>{item.supplier}</td>
                <td>{item.variety}</td>
                <td>{item.shelf}</td>
                <td>{item.ph}</td>
                <td>{(item.moisture * 100).toFixed(0)}%</td>
                <td>{item.temp}°C</td>
                <td>
                  <span className={`status-badge ${item.status.toLowerCase()}`}>{item.status}</span>
                </td>
                <td>
                  <button className="btn-predict" onClick={(e) => { e.stopPropagation(); handlePredict(item); }}>
                    <BarChart2 size={14} style={{ marginRight: '5px', verticalAlign: 'middle' }}/>
                    Analyze
                  </button>
                </td>
              </tr>
            ))}
            {filteredInventory.length === 0 && (
              <tr><td colSpan={10} style={{textAlign: 'center', padding: '20px'}}>No inventory matches your search.</td></tr>
            )}
          </tbody>
        </table>
      </div>

      {selectedBatch && (
        <div className="panel detail-panel" style={{ marginTop: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '15px' }}>
            <h2 style={{ margin: 0, color: 'var(--accent)' }}>Live Batch Telemetry: {selectedBatch.id} ({selectedBatch.variety})</h2>
            <X size={24} style={{ cursor: 'pointer', color: 'var(--text-muted)' }} onClick={() => setSelectedBatch(null)} />
          </div>
          <div className="dashboard-grid">
            <div>
              <table className="inventory-table detailed-table">
                <thead>
                  <tr>
                    <th>Feature Stream</th>
                    <th>Live Sensor Value</th>
                    <th>Optimal Range</th>
                    <th>AI Routing Weight</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td><strong>pH Profile</strong></td>
                    <td>{selectedBatch.ph}</td>
                    <td>{optimalRanges[selectedBatch.variety]?.ph || '4.0 - 5.0'}</td>
                    <td>High (LightGBM)</td>
                  </tr>
                  <tr>
                    <td><strong>Moisture Level</strong></td>
                    <td>{(selectedBatch.moisture * 100).toFixed(0)}%</td>
                    <td>{optimalRanges[selectedBatch.variety]?.moisture || '75% - 85%'}</td>
                    <td>Medium (LightGBM)</td>
                  </tr>
                  <tr>
                    <td><strong>Avg Temperature</strong></td>
                    <td>{selectedBatch.temp}°C</td>
                    <td>{optimalRanges[selectedBatch.variety]?.temp || '10.0°C - 15.0°C'}</td>
                    <td style={{ color: '#ef4444' }}>Critical (LSTM)</td>
                  </tr>
                  <tr>
                    <td><strong>Ambient CO2</strong></td>
                    <td>420 ppm (Simulated)</td>
                    <td>&lt; 500 ppm</td>
                    <td>Low (Ignored)</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div className={`result-panel ${selectedBatch.status.toLowerCase()}`} style={{ marginTop: 0 }}>
              <h3 style={{ marginTop: 0 }}>AI Shelf Life Prediction</h3>
              <div className="result-huge" style={{ fontSize: '48px' }}>{selectedBatch.days} Days</div>
              <p style={{ margin: 0 }}>Model Output Status: <strong>{selectedBatch.status}</strong></p>
              <button className="btn-primary" style={{ marginTop: '15px', width: '100%' }} onClick={() => handlePredict(selectedBatch)}>
                Force Network Recalculation
              </button>
            </div>
          </div>
        </div>
      )}

      {showAddModal && (
        <div className="modal-overlay">
          <div className="modal-content panel">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <h2 style={{margin: 0}}>Add New Batch</h2>
              <X size={20} style={{cursor: 'pointer'}} onClick={() => setShowAddModal(false)} />
            </div>
            
            <div className="control-group" style={{marginBottom: '15px'}}>
              <label>Variety</label>
              <select value={newBatch.variety} onChange={e => setNewBatch({...newBatch, variety: e.target.value})}>
                <option>Banana</option>
                <option>Orange</option>
                <option>Pineapple</option>
                <option>Tomato</option>
              </select>
            </div>
            <div className="modal-grid">
              <div className="control-group">
                <label>Batch Code</label>
                <input type="text" value={newBatch.batch} onChange={e => setNewBatch({...newBatch, batch: e.target.value})} placeholder="e.g. BN-999" />
              </div>
              <div className="control-group">
                <label>Supplier</label>
                <input type="text" value={newBatch.supplier} onChange={e => setNewBatch({...newBatch, supplier: e.target.value})} placeholder="Supplier Name" />
              </div>
              <div className="control-group">
                <label>Shelf Location</label>
                <input type="text" value={newBatch.shelf} onChange={e => setNewBatch({...newBatch, shelf: e.target.value})} placeholder="e.g. E" />
              </div>
              <div className="control-group">
                <label>Current Temp (°C)</label>
                <input type="number" value={newBatch.temp} onChange={e => setNewBatch({...newBatch, temp: parseFloat(e.target.value)})} />
              </div>
              <div className="control-group">
                <label>pH Level</label>
                <input type="number" step="0.1" value={newBatch.ph} onChange={e => setNewBatch({...newBatch, ph: parseFloat(e.target.value)})} />
              </div>
              <div className="control-group">
                <label>Moisture %</label>
                <input type="number" step="0.01" value={newBatch.moisture} onChange={e => setNewBatch({...newBatch, moisture: parseFloat(e.target.value)})} />
              </div>
            </div>
            <button className="btn-primary" style={{marginTop: '20px', width: '100%'}} onClick={handleAddBatch}>Save Batch & Run AI Inference</button>
          </div>
        </div>
      )}
    </div>
  );
};
