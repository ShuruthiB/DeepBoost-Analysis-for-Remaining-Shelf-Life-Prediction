import React, { useEffect, useState } from 'react';
import { ChevronLeft, ChevronRight, Search, Plus, X, BarChart2 } from 'lucide-react';
import './views.css';
import { apiRequest } from '../lib/api';

const optimalRanges: any = {
  'Banana': { ph: '4.5 - 5.2', moisture: '75% - 80%', temp: '13.0°C - 15.0°C' },
  'Orange': { ph: '3.3 - 4.2', moisture: '85% - 90%', temp: '3.0°C - 8.0°C' },
  'Pineapple': { ph: '3.4 - 4.0', moisture: '80% - 88%', temp: '10.0°C - 13.0°C' },
  'Tomato': { ph: '4.2 - 4.9', moisture: '90% - 95%', temp: '12.0°C - 16.0°C' }
};

export const InventoryView: React.FC = () => {
  const [inventory, setInventory] = useState<any[]>([]);
  const [search, setSearch] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedBatch, setSelectedBatch] = useState<any>(null);
  const [page, setPage] = useState(1);
  const [newBatch, setNewBatch] = useState({ variety: 'Banana', batch: '', supplier: '', shelf: '', ph: 4.5, moisture: 0.8, temp: 10 });

  useEffect(() => {
    apiRequest<any[]>('/inventory')
      .then(setInventory)
      .catch(error => {
        console.error(error);
        setInventory([]);
      });
  }, []);

  const handleAddBatch = async () => {
    const newId = `INV-${String(inventory.length + 1).padStart(3, '0')}`;
    try {
      const savedItem = await apiRequest<any>('/inventory', {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...newBatch, id: newId })
      });
      setInventory(prev => [...prev, savedItem]);
      setShowAddModal(false);
      setSelectedBatch(savedItem);
    } catch (error) {
      console.error(error);
    }
  };

  const filteredInventory = inventory.filter(item => 
    item.batch.toLowerCase().includes(search.toLowerCase()) || 
    item.variety.toLowerCase().includes(search.toLowerCase()) ||
    item.supplier.toLowerCase().includes(search.toLowerCase())
  );
  const pageSize = 8;
  const pageCount = Math.max(1, Math.ceil(filteredInventory.length / pageSize));
  const currentPage = Math.min(page, pageCount);
  const pagedInventory = filteredInventory.slice(
    (currentPage - 1) * pageSize,
    currentPage * pageSize,
  );

  return (
    <div className="view-container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1>Inventory Database</h1>
        </div>
        <div className="inventory-controls">
          <div className="search-bar">
            <Search size={16} />
            <input 
              type="text" 
              placeholder="Search batch, variety, supplier..." 
              value={search}
              onChange={(e) => { setSearch(e.target.value); setPage(1); }}
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
            {pagedInventory.map(item => (
              <tr key={item.id} onClick={() => setSelectedBatch(item)}>
                <td><strong>{item.id}</strong></td>
                <td>{item.batch}</td>
                <td>{item.supplier || 'Unassigned'}</td>
                <td>{item.variety}</td>
                <td>{item.shelf || 'Unassigned'}</td>
                <td>{item.ph}</td>
                <td>{(item.moisture * 100).toFixed(0)}%</td>
                <td>{item.temp}°C</td>
                <td>
                  <span className={`status-badge ${item.status.toLowerCase()}`}>{item.status}</span>
                </td>
                <td>
                  <button className="btn-predict" onClick={(e) => { e.stopPropagation(); setSelectedBatch(item); }}>
                    <BarChart2 size={14} style={{ marginRight: '5px', verticalAlign: 'middle' }}/>
                    View
                  </button>
                </td>
              </tr>
            ))}
            {filteredInventory.length === 0 && (
              <tr><td colSpan={10} style={{textAlign: 'center', padding: '20px'}}>No inventory matches your search.</td></tr>
            )}
          </tbody>
        </table>
        {filteredInventory.length > 0 && (
          <div className="pagination-controls">
            <span>Showing {(currentPage - 1) * pageSize + 1}-{Math.min(currentPage * pageSize, filteredInventory.length)} of {filteredInventory.length} batches</span>
            <div>
              <button
                className="btn-secondary"
                type="button"
                disabled={currentPage === 1}
                onClick={() => setPage(currentPage - 1)}
              >
                <ChevronLeft size={16} /> Previous
              </button>
              <span style={{ margin: '0 12px' }}>Page {currentPage} of {pageCount}</span>
              <button
                className="btn-secondary"
                type="button"
                disabled={currentPage === pageCount}
                onClick={() => setPage(currentPage + 1)}
              >
                Next <ChevronRight size={16} />
              </button>
            </div>
          </div>
        )}
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
                </tbody>
              </table>
            </div>
            <div className={`result-panel ${selectedBatch.status.toLowerCase()}`} style={{ marginTop: 0 }}>
              <h3 style={{ marginTop: 0 }}>AI Shelf Life Prediction</h3>
              <div className="result-huge">{selectedBatch.days ?? '--'} Days</div>
              <p style={{ margin: 0 }}>Model Output Status: <strong>{selectedBatch.status}</strong></p>
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
