import { useNavigate } from 'react-router-dom';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

const FEATURE_NAMES_MAP = {
  'ApplicantIncome_LKR': 'Applicant Income',
  'CoapplicantIncome_LKR': 'Co-applicant Income',
  'LoanAmount_LKR': 'Loan Amount',
  'Loan_Amount_Term': 'Loan Term',
  'CRIB_Clearance': 'CRIB Clearance',
  'Property_Region_SL': 'Property Region',
  'Employment_Sector': 'Employment Sector',
  'Dependents': 'Dependents',
  'Gender': 'Gender',
  'Married': 'Marital Status',
  'Education': 'Education',
  'Self_Employed': 'Self Employed',
  'Loan_Type': 'Loan Type'
};

const formatFeatureName = (name) => FEATURE_NAMES_MAP[name] || name;

const Explainability = ({ prediction }) => {
  const navigate = useNavigate();

  if (!prediction || !prediction.top_factors) {
    return (
      <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center' }}>
        <h2 style={{ color: 'var(--text-secondary)' }}>No Analysis Data</h2>
        <p style={{ marginBottom: '2rem' }}>Please submit a loan application to view the decision breakdown.</p>
        <button className="btn btn-primary" onClick={() => navigate('/')}>Go to Application</button>
      </div>
    );
  }

  const chartData = [...prediction.top_factors].reverse().map(f => ({
    name: formatFeatureName(f.factor),
    value: f.shap_contribution,
    impact: f.impact,
    actualValue: f.value
  }));

  return (
    <div className="animate-fade-in">
      <div className="glass-panel" style={{ padding: '2.5rem', marginBottom: '2rem', background: 'linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%)' }}>
        <h1 style={{ margin: '0 0 0.5rem', fontSize: '2.5rem', color: 'white' }}>🔍 Decision Breakdown</h1>
        <p style={{ margin: 0, color: 'rgba(255,255,255,0.9)', fontSize: '1.1rem' }}>Understanding exactly why the system made its decision</p>
      </div>

      <div className="glass-panel" style={{ padding: '2rem', marginBottom: '2rem' }}>
        <h3 style={{ borderLeft: '4px solid var(--accent-primary)', paddingLeft: '0.75rem', marginBottom: '2rem' }}>Most Important Factors</h3>
        <div style={{ height: '400px' }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} layout="vertical" margin={{ top: 5, right: 30, left: 120, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" horizontal={false} />
              <XAxis type="number" stroke="rgba(255,255,255,0.4)" />
              <YAxis dataKey="name" type="category" stroke="rgba(255,255,255,0.9)" width={140} tick={{fill: '#e2e8f0', fontSize: '0.9rem'}} />
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
        <h3 style={{ borderLeft: '4px solid var(--accent-primary)', paddingLeft: '0.75rem', marginBottom: '1.5rem' }}>Detailed Factor Impact</h3>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '1.05rem' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                <th style={{ padding: '1rem', color: 'var(--text-secondary)' }}>Rank</th>
                <th style={{ padding: '1rem', color: 'var(--text-secondary)' }}>Applicant Information</th>
                <th style={{ padding: '1rem', color: 'var(--text-secondary)' }}>Applicant's Value</th>
                <th style={{ padding: '1rem', color: 'var(--text-secondary)' }}>Impact Weight</th>
                <th style={{ padding: '1rem', color: 'var(--text-secondary)' }}>Effect on Decision</th>
              </tr>
            </thead>
            <tbody>
              {prediction.top_factors.map((f, i) => (
                <tr key={i} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                  <td style={{ padding: '1rem', color: 'var(--text-secondary)' }}>#{i + 1}</td>
                  <td style={{ padding: '1rem', fontWeight: 600 }}>{formatFeatureName(f.factor)}</td>
                  <td style={{ padding: '1rem' }}>{f.value}</td>
                  <td style={{ padding: '1rem' }}>{Math.abs(f.shap_contribution).toFixed(2)}</td>
                  <td style={{ padding: '1rem' }}>
                    {f.impact === 'Positive' ? (
                      <span className="badge badge-success" style={{ fontSize: '0.9rem' }}>↗️ Increased Approval</span>
                    ) : (
                      <span className="badge badge-danger" style={{ fontSize: '0.9rem' }}>↘️ Decreased Approval</span>
                    )}
                  </td>
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
