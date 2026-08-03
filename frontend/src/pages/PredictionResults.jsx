import { AlertCircle, CheckCircle2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';

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
  
  const pieData = [
    { name: 'Approval', value: approvalPct },
    { name: 'Rejection', value: rejectionPct }
  ];
  const COLORS = ['#10b981', '#ef4444'];

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

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1.5rem', marginBottom: '2rem' }}>
        <div className="glass-panel" style={{ padding: '1.5rem', textAlign: 'center' }}>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Approval Probability</div>
          <div style={{ fontSize: '2.5rem', fontWeight: 700, margin: '0.5rem 0', color: 'var(--text-primary)' }}>{approvalPct.toFixed(1)}%</div>
        </div>
        <div className="glass-panel" style={{ padding: '1.5rem', textAlign: 'center' }}>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Confidence Score</div>
          <div style={{ fontSize: '2.5rem', fontWeight: 700, margin: '0.5rem 0', color: 'var(--text-primary)' }}>{(prediction.confidence_score * 100).toFixed(1)}%</div>
        </div>
        <div className="glass-panel" style={{ padding: '1.5rem', textAlign: 'center' }}>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Risk Level</div>
          <div style={{ fontSize: '2.5rem', fontWeight: 700, margin: '0.5rem 0', color: prediction.risk_level === 'Low' ? 'var(--success)' : (prediction.risk_level === 'Medium' ? 'var(--warning)' : 'var(--danger)') }}>
            {prediction.risk_level}
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', marginBottom: '2rem' }}>
        <div className="glass-panel" style={{ padding: '2rem' }}>
          <h3 style={{ borderLeft: '4px solid var(--accent-primary)', paddingLeft: '0.75rem', marginBottom: '1.5rem' }}>Probability Split</h3>
          <div style={{ height: '250px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={pieData} cx="50%" cy="50%" innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value">
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div style={{ display: 'flex', justifyContent: 'center', gap: '2rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}><span style={{ width: 12, height: 12, borderRadius: '50%', background: COLORS[0] }}></span> Approval</div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}><span style={{ width: 12, height: 12, borderRadius: '50%', background: COLORS[1] }}></span> Rejection</div>
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          <div className="glass-panel" style={{ padding: '2rem' }}>
            <h3 style={{ borderLeft: '4px solid var(--accent-primary)', paddingLeft: '0.75rem', marginBottom: '1rem' }}>📋 Decision Reasoning</h3>
            <div style={{ background: 'rgba(0,0,0,0.2)', padding: '1.5rem', borderRadius: '12px', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
              {prediction.reasoning_summary}
            </div>
          </div>

          {prediction.llm_explanation && (
            <div className="glass-panel" style={{ padding: '2rem', border: '1px solid rgba(59, 130, 246, 0.3)' }}>
              <h3 style={{ borderLeft: '4px solid var(--accent-primary)', paddingLeft: '0.75rem', marginBottom: '1rem' }}>🤖 Local AI Explanation</h3>
              <div style={{ background: 'linear-gradient(135deg, rgba(30, 58, 138, 0.2) 0%, rgba(17, 24, 39, 0.4) 100%)', padding: '1.5rem', borderRadius: '12px', color: 'var(--text-primary)', lineHeight: 1.6 }}>
                {prediction.llm_explanation}
              </div>
            </div>
          )}
        </div>
      </div>
      
      <div style={{ textAlign: 'center' }}>
        <button className="btn btn-primary" onClick={() => { setPrediction(null); navigate('/'); }}>
          🔄 New Application
        </button>
      </div>
    </div>
  );
};

export default PredictionResults;
