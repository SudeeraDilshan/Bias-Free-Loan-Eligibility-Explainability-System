import { useNavigate } from 'react-router-dom';

const PredictionResults = ({ prediction, setPrediction }) => {
  const navigate = useNavigate();

  if (!prediction) {
    return (
      <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center' }}>
        <h2 style={{ color: 'var(--text-secondary)' }}>No Prediction Data</h2>
        <p style={{ marginBottom: '2rem' }}>Please submit a loan application first.</p>
        <button className="btn btn-primary" onClick={() => navigate('/')}>Go to Application</button>
      </div>
    );
  }

  const isApproved = prediction.prediction === "Approved";
  const approvalPct = prediction.approval_probability * 100;
  const rejectionPct = prediction.rejection_probability * 100;
  
  return (
    <div className="animate-fade-in">
      <div className="glass-panel" style={{ 
        padding: '2.5rem', 
        marginBottom: '2rem', 
        textAlign: 'center',
        background: isApproved ? 'linear-gradient(135deg, #0f9b58 0%, #11c26d 100%)' : 'linear-gradient(135deg, #c0392b 0%, #e74c3c 100%)' 
      }}>
        <h1 style={{ margin: '0 0 0.5rem', fontSize: '2.5rem', color: 'white' }}>
          {isApproved ? '✅ LOAN APPROVED' : '❌ LOAN REJECTED'}
        </h1>
        <p style={{ margin: 0, color: 'rgba(255,255,255,0.9)' }}>
          Application ID: <strong>{prediction.loan_id}</strong> | {new Date(prediction.timestamp).toLocaleString()}
        </p>
      </div>

      {prediction.llm_explanation && (
        <div className="glass-panel" style={{ padding: '2.5rem', marginBottom: '2rem', border: '1px solid rgba(59, 130, 246, 0.4)' }}>
          <h2 style={{ color: 'var(--accent-primary)', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            🤖 AI Explanation
          </h2>
          <div style={{ fontSize: '1.25rem', color: 'var(--text-primary)', lineHeight: 1.7 }}>
            {prediction.llm_explanation}
          </div>
        </div>
      )}

      {!prediction.llm_explanation && (
        <div className="glass-panel" style={{ padding: '2.5rem', marginBottom: '2rem' }}>
          <h2 style={{ color: 'var(--accent-primary)', marginBottom: '1.5rem' }}>📋 Decision Reasoning</h2>
          <div style={{ fontSize: '1.25rem', color: 'var(--text-primary)', lineHeight: 1.7 }}>
            {prediction.reasoning_summary}
          </div>
        </div>
      )}

      <h3 style={{ marginBottom: '1.5rem', color: 'var(--text-secondary)' }}>Technical Details</h3>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1.5rem', marginBottom: '2rem' }}>
        <div className="glass-panel" style={{ padding: '1.5rem', textAlign: 'center' }}>
          <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Model Confidence</div>
          <div style={{ fontSize: '2rem', fontWeight: 700, margin: '0.5rem 0', color: 'var(--text-primary)' }}>{(prediction.confidence_score * 100).toFixed(1)}%</div>
        </div>
        <div className="glass-panel" style={{ padding: '1.5rem', textAlign: 'center' }}>
          <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Risk Level</div>
          <div style={{ fontSize: '2rem', fontWeight: 700, margin: '0.5rem 0', color: prediction.risk_level === 'Low' ? 'var(--success)' : (prediction.risk_level === 'Medium' ? 'var(--warning)' : 'var(--danger)') }}>
            {prediction.risk_level}
          </div>
        </div>
        <div className="glass-panel" style={{ padding: '1.5rem', textAlign: 'center' }}>
          <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Probability Split</div>
          <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem', marginTop: '0.75rem', fontSize: '1.1rem' }}>
            <span style={{ color: '#10b981', fontWeight: 'bold' }}>{approvalPct.toFixed(0)}% App</span>
            <span style={{ color: 'var(--text-secondary)' }}>|</span>
            <span style={{ color: '#ef4444', fontWeight: 'bold' }}>{rejectionPct.toFixed(0)}% Rej</span>
          </div>
        </div>
      </div>
      
      <div style={{ textAlign: 'center', marginTop: '3rem' }}>
        <button className="btn btn-primary" onClick={() => { setPrediction(null); navigate('/'); }} style={{ padding: '1rem 2.5rem', fontSize: '1.1rem' }}>
          🔄 Start New Application
        </button>
      </div>
    </div>
  );
};

export default PredictionResults;
