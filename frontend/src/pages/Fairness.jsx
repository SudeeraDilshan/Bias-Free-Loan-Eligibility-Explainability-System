import { useState, useEffect } from 'react';

const Fairness = () => {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('http://localhost:8000/extract/fairness')
      .then(res => {
         if (!res.ok) throw new Error("Fairness endpoint not ready yet");
         return res.json();
      })
      .then(data => {
        setReport(data);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) return <div style={{ padding: '3rem', textAlign: 'center' }}>Loading Fairness Report...</div>;
  if (error) return <div className="glass-panel" style={{ padding: '2rem', color: 'var(--warning)' }}>⚠️ {error}.</div>;

  return (
    <div className="animate-fade-in">
       <div className="glass-panel" style={{ padding: '2.5rem', marginBottom: '2rem', background: 'linear-gradient(135deg, #4c1d95 0%, #7c3aed 100%)' }}>
        <h1 style={{ margin: '0 0 0.5rem', fontSize: '2.5rem', color: 'white' }}>⚖️ Fairness & Bias Analysis</h1>
        <p style={{ margin: 0, color: 'rgba(255,255,255,0.8)' }}>Model-level fairness evaluation across sensitive demographic attributes</p>
      </div>
      
      {report && Object.entries(report).map(([attr, metrics]) => (
        <div key={attr} className="glass-panel" style={{ padding: '2rem', marginBottom: '2rem' }}>
           <h3 style={{ borderLeft: '4px solid var(--accent-primary)', paddingLeft: '0.75rem', marginBottom: '1.5rem', textTransform: 'capitalize' }}>👤 Sensitive Attribute: {attr}</h3>
           
           <div style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
             <strong>Overall Bias Level:</strong> 
             <span className={`badge ${metrics.overall_bias_level === 'Low' ? 'badge-success' : 'badge-danger'}`}>
               {metrics.overall_bias_level}
             </span>
           </div>

           <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1.5rem' }}>
             <div style={{ padding: '1.5rem', background: 'rgba(255,255,255,0.02)', borderRadius: '12px' }}>
                <h4 style={{ marginBottom: '1rem', color: 'var(--text-secondary)' }}>Demographic Parity</h4>
                <div style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '0.5rem' }}>
                  {metrics.demographic_parity.dp_difference.toFixed(4)}
                </div>
                <div style={{ marginBottom: '1rem' }}>
                  <span className={`badge ${metrics.demographic_parity.is_fair ? 'badge-success' : 'badge-danger'}`}>
                    {metrics.demographic_parity.is_fair ? '✓ FAIR' : '✗ UNFAIR'}
                  </span>
                </div>
                <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                  {Object.entries(metrics.demographic_parity.approval_rates).map(([grp, rate]) => (
                     <div key={grp}>• {grp}: {(rate * 100).toFixed(1)}%</div>
                  ))}
                </div>
             </div>

             <div style={{ padding: '1.5rem', background: 'rgba(255,255,255,0.02)', borderRadius: '12px' }}>
                <h4 style={{ marginBottom: '1rem', color: 'var(--text-secondary)' }}>Equal Opportunity</h4>
                <div style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '0.5rem' }}>
                  {metrics.equal_opportunity.eod_difference.toFixed(4)}
                </div>
                <div style={{ marginBottom: '1rem' }}>
                  <span className={`badge ${metrics.equal_opportunity.is_fair ? 'badge-success' : 'badge-danger'}`}>
                    {metrics.equal_opportunity.is_fair ? '✓ FAIR' : '✗ UNFAIR'}
                  </span>
                </div>
             </div>

             <div style={{ padding: '1.5rem', background: 'rgba(255,255,255,0.02)', borderRadius: '12px' }}>
                <h4 style={{ marginBottom: '1rem', color: 'var(--text-secondary)' }}>Disparate Impact</h4>
                <div style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '0.5rem' }}>
                  {metrics.disparate_impact.di_ratio.toFixed(4)}
                </div>
                <div style={{ marginBottom: '1rem' }}>
                  <span className={`badge ${metrics.disparate_impact.is_fair ? 'badge-success' : 'badge-danger'}`}>
                    {metrics.disparate_impact.is_fair ? '✓ FAIR' : '✗ UNFAIR'}
                  </span>
                </div>
             </div>
           </div>
        </div>
      ))}
    </div>
  );
};
export default Fairness;
