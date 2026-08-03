import { NavLink } from 'react-router-dom';
import { Home, BarChart2, Search, Scale, Info } from 'lucide-react';
import { useState, useEffect } from 'react';
import logo from '../assets/logo.png';

const Sidebar = () => {
  const [backendStatus, setBackendStatus] = useState('Checking...');

  useEffect(() => {
    fetch('http://localhost:8000/health')
      .then(res => {
        if (res.ok) setBackendStatus('Online');
        else setBackendStatus('Offline');
      })
      .catch(() => setBackendStatus('Offline'));
  }, []);

  return (
    <aside className="sidebar">
      <div style={{ marginBottom: '2rem', display: 'flex', justifyContent: 'center', width: '100%' }}>
        <img src={logo} alt="Bank Logo" style={{ maxWidth: '100%', maxHeight: '90px', objectFit: 'contain' }} />
      </div>

      <nav style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', flex: 1 }}>
        <NavLink to="/" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
          <Home size={20} />
          <span>Loan Application</span>
        </NavLink>
        <NavLink to="/results" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
          <BarChart2 size={20} />
          <span>Prediction Results</span>
        </NavLink>
        <NavLink to="/explainability" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
          <Search size={20} />
          <span>Explainability</span>
        </NavLink>
        <NavLink to="/fairness" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
          <Scale size={20} />
          <span>Fairness Report</span>
        </NavLink>
        <NavLink to="/about" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
          <Info size={20} />
          <span>About</span>
        </NavLink>
      </nav>

      <div className="glass-panel" style={{ padding: '1rem', marginTop: 'auto' }}>
        <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
          Backend Status:
        </div>
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          gap: '0.5rem', 
          marginTop: '0.25rem',
          color: backendStatus === 'Online' ? 'var(--success)' : 'var(--danger)',
          fontWeight: 600
        }}>
          <span style={{ 
            width: '8px', 
            height: '8px', 
            borderRadius: '50%', 
            background: backendStatus === 'Online' ? 'var(--success)' : 'var(--danger)' 
          }}></span>
          {backendStatus}
        </div>
        <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
          Port 8000
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
