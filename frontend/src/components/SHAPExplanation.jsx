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

        <div className="shap-explanation">
          <h3>💡 What is SHAP?</h3>
          <p>
            SHAP (Shapley Additive exPlanations) uses game theory to explain predictions.
            Each feature's importance is calculated based on its contribution to the final 
            decision, considering all possible combinations of features.
          </p>
          <ul>
            <li><strong>Positive Impact:</strong> Increases loan approval chances</li>
            <li><strong>Negative Impact:</strong> Decreases loan approval chances</li>
            <li><strong>SHAP Value:</strong> Quantifies the magnitude of each factor's influence</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default SHAPExplanation;
