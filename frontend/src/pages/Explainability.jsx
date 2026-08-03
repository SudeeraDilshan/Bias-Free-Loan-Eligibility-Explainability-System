import { useNavigate } from 'react-router-dom';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

const Explainability = ({ prediction }) => {
  const navigate = useNavigate();

  if (!prediction || !prediction.top_factors) {
    return (
      <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center' }}>
        <h2 style={{ color: 'var(--text-secondary)' }}>No SHAP Data</h2>
        <p style={{ marginBottom: '2rem' }}>Please submit a loan application to view explainability data.</p>
        <button className="btn btn-primary" onClick={() => navigate('/')}>Go to Application</button>
      </div>
    );
  }

  const chartData = [...prediction.top_factors].reverse().map(f => ({
    name: f.factor,
    value: f.shap_contribution,
    impact: f.impact,
    actualValue: f.value
  }));

  return (
    <div className="animate-fade-in">
      <div className="glass-panel" style={{ padding: '2.5rem', marginBottom: '2rem', background: 'linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%)' }}>
        <h1 style={{ margin: '0 0 0.5rem', fontSize: '2.5rem', color: 'white' }}>🔍 SHAP Explainability Analysis</h1>
        <p style={{ margin: 0, color: 'rgba(255,255,255,0.8)' }}>Understanding why the model made its decision — factor by factor</p>
      </div>

      <div className="glass-panel" style={{ padding: '2rem', marginBottom: '2rem' }}>
        <h3 style={{ borderLeft: '4px solid var(--accent-primary)', paddingLeft: '0.75rem', marginBottom: '2rem' }}>Top Contributing Features (SHAP)</h3>
        <div style={{ height: '400px' }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} layout="vertical" margin={{ top: 5, right: 30, left: 100, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" horizontal={false} />
              <XAxis type="number" stroke="rgba(255,255,255,0.5)" />
              <YAxis dataKey="name" type="category" stroke="rgba(255,255,255,0.8)" width={150} tick={{fill: '#e2e8f0'}} />
              <Tooltip 
                cursor={{fill: 'rgba(255,255,255,0.05)'}}
                contentStyle={{ background: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', color: '#fff' }}
              />
              <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.value > 0 ? '#10b981' : '#ef4444'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="glass-panel" style={{ padding: '2rem' }}>
        <h3 style={{ borderLeft: '4px solid var(--accent-primary)', paddingLeft: '0.75rem', marginBottom: '1.5rem' }}>Factor Details</h3>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                <th style={{ padding: '1rem', color: 'var(--text-secondary)' }}>Rank</th>
                <th style={{ padding: '1rem', color: 'var(--text-secondary)' }}>Feature</th>
                <th style={{ padding: '1rem', color: 'var(--text-secondary)' }}>Impact</th>
                <th style={{ padding: '1rem', color: 'var(--text-secondary)' }}>Feature Value</th>
                <th style={{ padding: '1rem', color: 'var(--text-secondary)' }}>SHAP Contribution</th>
              </tr>
            </thead>
            <tbody>
              {prediction.top_factors.map((f, i) => (
                <tr key={i} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                  <td style={{ padding: '1rem' }}>#{i + 1}</td>
                  <td style={{ padding: '1rem', fontWeight: 500 }}>{f.factor}</td>
                  <td style={{ padding: '1rem', color: f.impact === 'Positive' ? 'var(--success)' : 'var(--danger)' }}>
                    {f.impact === 'Positive' ? '↗️ Positive' : '↘️ Negative'}
                  </td>
                  <td style={{ padding: '1rem' }}>{f.value.toFixed(4)}</td>
                  <td style={{ padding: '1rem' }}>{f.shap_contribution.toFixed(4)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Explainability;
