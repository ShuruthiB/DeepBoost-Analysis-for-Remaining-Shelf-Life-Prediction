import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from './contexts/ThemeContext';
import { Layout } from './Layout';
import { DashboardView } from './components/DashboardView';
import { InventoryView } from './components/InventoryView';
import { ProjectionView } from './components/ProjectionView';
import { AnalyticsView } from './components/AnalyticsView';
import { MonitorShelvesView } from './components/MonitorShelvesView';
import './index.css';

function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<DashboardView />} />
            <Route path="inventory" element={<InventoryView />} />
            <Route path="projection" element={<ProjectionView />} />
            <Route path="analytics" element={<AnalyticsView />} />
            <Route path="monitor-shelves" element={<MonitorShelvesView />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;
