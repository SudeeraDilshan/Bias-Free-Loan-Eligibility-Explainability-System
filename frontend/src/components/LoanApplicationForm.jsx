import React, { useState } from 'react';
import './LoanApplicationForm.css';

const LoanApplicationForm = ({ onSubmit }) => {
  const [formData, setFormData] = useState({
    Loan_ID: `LP${Date.now()}`,
    Gender: 'Male',
    Married: 'Yes',
    Dependents: 0,
    Education: 'Graduate',
    Self_Employed: 'No',
    ApplicantIncome: 5000,
    CoapplicantIncome: 0,
    LoanAmount: 128,
    Loan_Amount_Term: 360,
    Credit_History: 1,
    Property_Area: 'Urban'
  });

  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: isNaN(value) ? value : parseFloat(value)
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    try {
      await onSubmit(formData);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="form-container">
      <div className="form-card">
        <h2>📝 Loan Application Form</h2>
        <p>Enter applicant details for loan eligibility prediction</p>

        <form onSubmit={handleSubmit} className="form">
          <div className="form-grid">
            {/* Personal Information */}
            <section className="form-section">
              <h3>Personal Information</h3>
              
              <div className="form-group">
                <label>Gender *</label>
                <select name="Gender" value={formData.Gender} onChange={handleChange}>
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                </select>
              </div>

              <div className="form-group">
                <label>Marital Status *</label>
                <select name="Married" value={formData.Married} onChange={handleChange}>
                  <option value="Yes">Married</option>
                  <option value="No">Single</option>
                </select>
              </div>

              <div className="form-group">
                <label>Dependents *</label>
                <select name="Dependents" value={formData.Dependents} onChange={handleChange}>
                  <option value={0}>0</option>
                  <option value={1}>1</option>
                  <option value={2}>2</option>
                  <option value={3}>3+</option>
                </select>
              </div>

              <div className="form-group">
                <label>Education *</label>
                <select name="Education" value={formData.Education} onChange={handleChange}>
                  <option value="Graduate">Graduate</option>
                  <option value="Undergraduate">Undergraduate</option>
                </select>
              </div>
            </section>

            {/* Employment & Income */}
            <section className="form-section">
              <h3>Employment & Income</h3>
              
              <div className="form-group">
                <label>Self Employed *</label>
                <select name="Self_Employed" value={formData.Self_Employed} onChange={handleChange}>
                  <option value="No">No</option>
                  <option value="Yes">Yes</option>
                </select>
              </div>

              <div className="form-group">
                <label>Applicant Income (Monthly in ₹) *</label>
                <input 
                  type="number" 
                  name="ApplicantIncome" 
                  value={formData.ApplicantIncome}
                  onChange={handleChange}
                  min="0"
                  step="100"
                  required
                />
              </div>

              <div className="form-group">
                <label>Co-applicant Income (Monthly in ₹) *</label>
                <input 
                  type="number" 
                  name="CoapplicantIncome" 
                  value={formData.CoapplicantIncome}
                  onChange={handleChange}
                  min="0"
                  step="100"
                />
              </div>

              <div className="form-group">
                <label>Credit History *</label>
                <select name="Credit_History" value={formData.Credit_History} onChange={handleChange}>
                  <option value={1}>Good</option>
                  <option value={0}>Bad</option>
                </select>
              </div>
            </section>

            {/* Loan Details */}
            <section className="form-section">
              <h3>Loan Details</h3>
              
              <div className="form-group">
                <label>Loan Amount (in 000s ₹) *</label>
                <input 
                  type="number" 
                  name="LoanAmount" 
                  value={formData.LoanAmount}
                  onChange={handleChange}
                  min="0"
                  step="10"
                  required
                />
              </div>

              <div className="form-group">
                <label>Loan Amount Term (Months) *</label>
                <input 
                  type="number" 
                  name="Loan_Amount_Term" 
                  value={formData.Loan_Amount_Term}
                  onChange={handleChange}
                  min="0"
                  step="12"
                  required
                />
              </div>

              <div className="form-group">
                <label>Property Area *</label>
                <select name="Property_Area" value={formData.Property_Area} onChange={handleChange}>
                  <option value="Urban">Urban</option>
                  <option value="Semiurban">Semi-urban</option>
                  <option value="Rural">Rural</option>
                </select>
              </div>
            </section>
          </div>

          <button type="submit" className="submit-button" disabled={isSubmitting}>
            {isSubmitting ? 'Processing...' : 'Get Prediction & Explanation'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default LoanApplicationForm;
