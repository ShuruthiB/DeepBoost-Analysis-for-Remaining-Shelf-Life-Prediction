import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Package, BarChart2, TrendingUp, RadioTower, Moon, Sun } from 'lucide-react';
import { useTheme } from './contexts/useTheme';

export const Sidebar: React.FC = () => {
  const { theme, toggleTheme } = useTheme();

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h2>SpoilSense AI</h2>
      </div>
      
      <nav className="sidebar-nav">
        <NavLink to="/" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
          <LayoutDashboard size={20} />
          <span>Dashboard</span>
        </NavLink>
        
        <NavLink to="/inventory" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
          <Package size={20} />
          <span>Inventory</span>
        </NavLink>
        
        <NavLink to="/projection" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
          <TrendingUp size={20} />
          <span>Shelf Life Projection</span>
        </NavLink>
        
        <NavLink to="/analytics" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
          <BarChart2 size={20} />
          <span>Analytics</span>
        </NavLink>

        <NavLink to="/monitor-shelves" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
          <RadioTower size={20} />
          <span>Monitor Shelves</span>
        </NavLink>
      </nav>

      <div className="sidebar-footer">
        <button onClick={toggleTheme} className="theme-toggle-btn">
          {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
          <span>Toggle Theme</span>
        </button>
      </div>
    </aside>
  );
};
