import React, { useState } from 'react';
import axios from 'axios';
import './App.css';
import LoanApplicationForm from './components/LoanApplicationForm';
import PredictionResult from './components/PredictionResult';
import SHAPExplanation from './components/SHAPExplanation';
import LoadingSpinner from './components/LoadingSpinner';

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [step, setStep] = useState('form'); // 'form' | 'loading' | 'result'
  const [prediction, setPrediction] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async (formData) => {
    setStep('loading');
    setError(null);
    
    try {
      const response = await axios.post(`${API_BASE_URL}/predict`, formData);
      setPrediction(response.data);
      setStep('result');
    } catch (err) {
      setError(err.response?.data?.detail || 'Error processing prediction');
      setStep('form');
    }
  };

  const handleReset = () => {
    setStep('form');
    setPrediction(null);
    setError(null);
  };

  return (
    <div className="App">
      <header className="header">
        <div className="container">
          <h1>🏦 Bias-Free Loan Eligibility System</h1>
          <p>AI-Powered Prediction with Explainability & Fairness Analysis</p>
        </div>
      </header>

      <main className="main-content">
        <div className="container">
          {error && (
            <div className="error-message">
              <span>⚠️ {error}</span>
              <button onClick={handleReset}>Try Again</button>
            </div>
          )}

          {step === 'form' && (
            <LoanApplicationForm onSubmit={handleSubmit} />
          )}

          {step === 'loading' && <LoadingSpinner />}

          {step === 'result' && prediction && (
            <>
              <PredictionResult prediction={prediction} />
              <SHAPExplanation prediction={prediction} />
              <button className="reset-button" onClick={handleReset}>
                Process Another Application
              </button>
            </>
          )}
        </div>
      </main>

      <footer className="footer">
        <p>© 2026 Bias-Free Loan Eligibility System | Powered by XGBoost & SHAP</p>
      </footer>
    </div>
  );
}

export default App;
