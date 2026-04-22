import React from 'react';
import './LoadingSpinner.css';

const LoadingSpinner = () => {
  return (
    <div className="loading-container">
      <div className="spinner"></div>
      <h2>Processing Application...</h2>
      <p>Analyzing application with AI and generating SHAP explanations</p>
    </div>
  );
};

export default LoadingSpinner;
