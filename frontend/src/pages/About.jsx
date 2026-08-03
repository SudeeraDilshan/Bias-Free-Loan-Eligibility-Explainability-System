const About = () => {
  return (
    <div className="animate-fade-in">
      <div className="glass-panel" style={{ padding: '2.5rem', marginBottom: '2rem' }}>
        <h1 style={{ margin: '0 0 1rem', fontSize: '2rem', color: 'var(--text-primary)' }}>ℹ️ About the System</h1>
        <p style={{ lineHeight: 1.6, color: 'var(--text-secondary)' }}>
          This is a full-stack ML application combining predictive modeling with AI explainability.
        </p>
      </div>
      
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
        <div className="glass-panel" style={{ padding: '2rem' }}>
          <h3 style={{ borderLeft: '4px solid var(--accent-primary)', paddingLeft: '0.75rem', marginBottom: '1rem' }}>Technology Stack</h3>
          <ul style={{ listStyle: 'none', padding: 0, color: 'var(--text-secondary)' }}>
            <li style={{ marginBottom: '0.5rem' }}><strong>Frontend:</strong> React.js, Recharts, Vite</li>
            <li style={{ marginBottom: '0.5rem' }}><strong>Backend:</strong> FastAPI, Python</li>
            <li style={{ marginBottom: '0.5rem' }}><strong>ML Model:</strong> XGBoost (Trained on SL data)</li>
            <li style={{ marginBottom: '0.5rem' }}><strong>Explainability:</strong> SHAP (TreeExplainer)</li>
            <li style={{ marginBottom: '0.5rem' }}><strong>Local AI:</strong> Qwen2.5-0.5B-Instruct</li>
          </ul>
        </div>
        
        <div className="glass-panel" style={{ padding: '2rem' }}>
          <h3 style={{ borderLeft: '4px solid var(--accent-primary)', paddingLeft: '0.75rem', marginBottom: '1rem' }}>Key Features</h3>
          <ul style={{ listStyle: 'none', padding: 0, color: 'var(--text-secondary)' }}>
            <li style={{ marginBottom: '0.5rem' }}>✓ Automated OCR for Paysheets</li>
            <li style={{ marginBottom: '0.5rem' }}>✓ PDF Extraction for CRIB Reports</li>
            <li style={{ marginBottom: '0.5rem' }}>✓ Local offline LLM reasoning</li>
            <li style={{ marginBottom: '0.5rem' }}>✓ 60% DTI (Debt-to-Income) rule check</li>
            <li style={{ marginBottom: '0.5rem' }}>✓ Demographic Parity fairness evaluation</li>
          </ul>
        </div>
      </div>
    </div>
  );
};
export default About;
