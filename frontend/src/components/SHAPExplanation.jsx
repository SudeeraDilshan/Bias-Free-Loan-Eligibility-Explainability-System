import React from 'react';
import './SHAPExplanation.css';

const SHAPExplanation = ({ prediction }) => {
  const topFactors = prediction.top_factors || [];

  return (
    <div className="shap-container">
      <div className="shap-card">
        <h2>🔍 SHAP Explainability Analysis</h2>
        <p>Understanding which factors most influenced this decision</p>

        <div className="factors-list">
          <h3>Top Contributing Factors</h3>
          
          {topFactors.map((factor, index) => (
            <div key={index} className="factor-item">
              <div className="factor-header">
                <span className="factor-rank">#{index + 1}</span>
                <h4 className="factor-name">{factor.factor}</h4>
                <span className={`factor-impact ${factor.impact.toLowerCase()}`}>
                  {factor.impact === 'Positive' ? '↗️' : '↘️'} {factor.impact}
                </span>
              </div>

              <div className="factor-details">
                <div className="detail">
                  <label>Value:</label>
                  <span className="detail-value">{factor.value.toFixed(4)}</span>
                </div>
                <div className="detail">
                  <label>SHAP Contribution:</label>
                  <span className="detail-value">{factor.shap_contribution.toFixed(4)}</span>
                </div>
              </div>

              <div className="contribution-bar">
                <div 
                  className={`contribution-fill ${factor.impact.toLowerCase()}`}
                  style={{
                    width: `${Math.min(Math.abs(factor.shap_contribution) * 100, 100)}%`
                  }}
                ></div>
              </div>
            </div>
          ))}
        </div>

      </div>
    </div>
  );
};

export default SHAPExplanation;
