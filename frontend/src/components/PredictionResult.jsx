import React from 'react';
import './PredictionResult.css';

const PredictionResult = ({ prediction }) => {
  const isApproved = prediction.prediction === 'Approved';
  const riskColors = {
    'Low': '#27ae60',
    'Medium': '#f39c12',
    'High': '#e74c3c'
  };

  return (
    <div className="result-container">
      <div className={`result-card ${isApproved ? 'approved' : 'rejected'}`}>
        <div className="result-header">
          <h2>
            {isApproved ? '✅ LOAN APPROVED' : '❌ LOAN REJECTED'}
          </h2>
          <p className="application-id">Application ID: {prediction.loan_id}</p>
        </div>

        <div className="metrics-grid">
          <div className="metric">
            <label>Approval Probability</label>
            <div className="probability-bar">
              <div 
                className="probability-fill"
                style={{ width: `${prediction.approval_probability * 100}%` }}
              ></div>
            </div>
            <span className="probability-text">
              {(prediction.approval_probability * 100).toFixed(1)}%
            </span>
          </div>

          <div className="metric">
            <label>Confidence Score</label>
            <div className="confidence">
              {(prediction.confidence_score * 100).toFixed(1)}%
            </div>
          </div>

          <div className="metric">
            <label>Risk Level</label>
            <div 
              className="risk-badge"
              style={{ backgroundColor: riskColors[prediction.risk_level] }}
            >
              {prediction.risk_level}
            </div>
          </div>
        </div>

        <div className="reasoning-section">
          <h3>📋 Decision Reasoning</h3>
          <p className="reasoning-text">
            {prediction.reasoning_summary}
          </p>
        </div>

        <div className="decision-timestamp">
          <small>Decision made: {new Date(prediction.timestamp).toLocaleString()}</small>
        </div>
      </div>
    </div>
  );
};

export default PredictionResult;
