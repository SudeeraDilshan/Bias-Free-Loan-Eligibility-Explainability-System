import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { UploadCloud, FileText, CheckCircle, AlertTriangle } from 'lucide-react';

const SL_REGIONS = [
  "Ampara", "Anuradhapura", "Badulla", "Batticaloa", "Colombo", "Galle",
  "Gampaha", "Hambantota", "Jaffna", "Kalutara", "Kandy", "Kegalle",
  "Kilinochchi", "Kurunegala", "Mannar", "Matale", "Matara", "Monaragala",
  "Mullaitivu", "Nuwara Eliya", "Polonnaruwa", "Puttalam", "Ratnapura",
  "Trincomalee", "Vavuniya"
];

const LOAN_TYPES = ["Personal Loan", "Business/SME Loan", "Housing Loan", "Vehicle Lease"];
const MIN_LOAN_AMOUNTS = {
  "Personal Loan": 50000,
  "Business/SME Loan": 500000,
  "Housing Loan": 1000000,
  "Vehicle Lease": 300000
};
const EMPLOYMENT_SECTORS = ["Private Sector", "Government", "Informal/Self-Employed"];

const LoanApplication = ({ setPrediction }) => {
  const navigate = useNavigate();
  const [loadingPaysheets, setLoadingPaysheets] = useState(false);
  const [loadingCrib, setLoadingCrib] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  
  const [error, setError] = useState(null);
  const [paysheetFiles, setPaysheetFiles] = useState([]);
  const [paysheetData, setPaysheetData] = useState(null);
  const [cribFile, setCribFile] = useState(null);
  const [cribData, setCribData] = useState(null);
  
  const [formData, setFormData] = useState({
    Gender: "Male",
    Married: "Yes",
    Dependents: "0",
    Education: "Graduate",
    Self_Employed: "No",
    Employment_Sector: "Private Sector",
    ApplicantIncome_LKR: 184500,
    CoapplicantIncome_LKR: 61940,
    Loan_Type: "Personal Loan",
    LoanAmount_LKR: 1180000,
    Loan_Amount_Term: 48,
    Property_Region_SL: "Kandy"
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handlePaysheetSelect = async (e) => {
    const files = Array.from(e.target.files);
    if (!files.length) return;

    const newFiles = [...paysheetFiles, ...files].slice(0, 3);
    setPaysheetFiles(newFiles);
    
    if (newFiles.length === 3 && !paysheetData) {
      await processPaysheets(newFiles);
    }
  };

  const processPaysheets = async (filesToProcess) => {
    const formData = new FormData();
    for (let i = 0; i < filesToProcess.length; i++) {
      formData.append('files', filesToProcess[i]);
    }

    try {
      setLoadingPaysheets(true);
      const res = await fetch('http://localhost:8000/extract/paysheets', {
        method: 'POST',
        body: formData,
      });
      if (!res.ok) throw new Error('Failed to process paysheets');
      const data = await res.json();
      setPaysheetData(data);
      setFormData(prev => ({ ...prev, ApplicantIncome_LKR: data.calculated_avg_salary }));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoadingPaysheets(false);
    }
  };

  const handleCribUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setCribFile(file);

    const formData = new FormData();
    formData.append('file', file);

    try {
      setLoadingCrib(true);
      const res = await fetch('http://localhost:8000/extract/crib', {
        method: 'POST',
        body: formData,
      });
      if (!res.ok) throw new Error('Failed to process CRIB report');
      const data = await res.json();
      setCribData(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoadingCrib(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!paysheetData || !cribData) {
      setError("Please upload both paysheets and CRIB report to proceed.");
      return;
    }

    const payload = {
      Loan_ID: `LP${Math.floor(Date.now() / 1000)}`,
      ...formData,
      ApplicantIncome_LKR: Number(formData.ApplicantIncome_LKR),
      CoapplicantIncome_LKR: Number(formData.CoapplicantIncome_LKR),
      LoanAmount_LKR: Number(formData.LoanAmount_LKR),
      Loan_Amount_Term: Number(formData.Loan_Amount_Term),
      CRIB_Clearance: cribData.risk_grade
    };

    try {
      setSubmitting(true);
      const res = await fetch('http://localhost:8000/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (!res.ok) throw new Error('Prediction failed');
      const data = await res.json();
      setPrediction(data);
      navigate('/results');
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  // Calculate EMI
  const annualRate = 15;
  const monthlyRate = (annualRate / 100) / 12;
  const emi = formData.LoanAmount_LKR * monthlyRate * Math.pow(1 + monthlyRate, formData.Loan_Amount_Term) / (Math.pow(1 + monthlyRate, formData.Loan_Amount_Term) - 1);
  const maxEMI = paysheetData ? paysheetData.calculated_avg_salary * 0.6 : formData.ApplicantIncome_LKR * 0.6;
  const isEmiValid = emi <= maxEMI;
  
  const minAmount = MIN_LOAN_AMOUNTS[formData.Loan_Type];
  const isMinAmountValid = formData.LoanAmount_LKR >= minAmount;

  return (
    <div className="animate-fade-in">
      <div className="glass-panel" style={{ padding: '2rem', marginBottom: '2rem', background: 'linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%)' }}>
        <h1 style={{ margin: 0, fontSize: '2rem', color: 'white' }}>🏦 Bias-Free Loan Eligibility System</h1>
        <p style={{ margin: '0.5rem 0 0', opacity: 0.8, color: 'white' }}>AI-powered prediction with full explainability & fairness analysis</p>
      </div>

      {error && (
        <div style={{ padding: '1rem', background: 'rgba(239, 68, 68, 0.2)', color: 'var(--danger)', borderRadius: '8px', marginBottom: '1.5rem', border: '1px solid var(--danger)' }}>
          <AlertTriangle size={20} style={{ display: 'inline', marginRight: '0.5rem', verticalAlign: 'middle' }} />
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="glass-panel" style={{ padding: '2rem' }}>
        <h3 style={{ borderLeft: '4px solid var(--accent-primary)', paddingLeft: '0.75rem', marginBottom: '1.5rem' }}>Personal Information</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>Gender</label>
            <select name="Gender" value={formData.Gender} onChange={handleInputChange} className="input-field">
              <option>Male</option><option>Female</option>
            </select>
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>Marital Status</label>
            <select name="Married" value={formData.Married} onChange={handleInputChange} className="input-field">
              <option>Yes</option><option>No</option>
            </select>
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>Dependents</label>
            <select name="Dependents" value={formData.Dependents} onChange={handleInputChange} className="input-field">
              <option>0</option><option>1</option><option>2</option><option>3+</option>
            </select>
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>Education</label>
            <select name="Education" value={formData.Education} onChange={handleInputChange} className="input-field">
              <option>Graduate</option><option>Not Graduate</option>
            </select>
          </div>
        </div>

        <h3 style={{ borderLeft: '4px solid var(--accent-primary)', paddingLeft: '0.75rem', marginBottom: '1.5rem' }}>Documents & Verification</h3>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginBottom: '2rem' }}>
          <div style={{ padding: '1.5rem', background: 'rgba(255,255,255,0.02)', border: '1px dashed var(--glass-border)', borderRadius: '12px' }}>
            <h4 style={{ marginBottom: '1rem' }}><FileText size={18} style={{ display: 'inline', marginRight: '0.5rem', verticalAlign: 'middle' }}/> 3-Month Paysheets</h4>
            <input type="file" multiple accept="image/*" onChange={handlePaysheetSelect} style={{ display: 'none' }} id="paysheets-upload" disabled={paysheetFiles.length >= 3 || loadingPaysheets} />
            <label htmlFor="paysheets-upload" className="btn btn-primary" style={{ width: '100%', opacity: (paysheetFiles.length >= 3 || loadingPaysheets) ? 0.5 : 1, cursor: (paysheetFiles.length >= 3 || loadingPaysheets) ? 'not-allowed' : 'pointer' }}>
              <UploadCloud size={18} style={{ marginRight: '0.5rem' }} /> {paysheetFiles.length < 3 ? `Select Paysheet (${paysheetFiles.length}/3)` : '3 Paysheets Selected'}
            </label>
            
            {paysheetFiles.length > 0 && (
              <div style={{ marginTop: '1rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {paysheetFiles.map((file, idx) => (
                  <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                    <CheckCircle size={14} color="var(--success)" /> {file.name} attached
                  </div>
                ))}
              </div>
            )}
            
            {loadingPaysheets && paysheetFiles.length === 3 && !paysheetData && (
              <div style={{ marginTop: '1rem', fontSize: '0.9rem', color: 'var(--accent-primary)' }}>
                Processing OCR extraction...
              </div>
            )}

            {paysheetData && !loadingPaysheets && (
              <div style={{ marginTop: '1rem', fontSize: '0.9rem', color: 'var(--success)' }}>
                <CheckCircle size={16} style={{ display: 'inline', marginRight: '0.25rem', verticalAlign: 'middle' }}/> OCR Validated (Avg: LKR {paysheetData.calculated_avg_salary.toLocaleString(undefined, {minimumFractionDigits: 2})})
                <div style={{ marginTop: '0.25rem', color: 'var(--text-secondary)', fontSize: '0.8rem' }}>Detected: {paysheetData.months_detected}</div>
                {!paysheetData.is_consecutive && <div style={{ color: 'var(--warning)', marginTop: '0.25rem' }}>⚠️ Warning: Months appear non-consecutive</div>}
              </div>
            )}
          </div>

          <div style={{ padding: '1.5rem', background: 'rgba(255,255,255,0.02)', border: '1px dashed var(--glass-border)', borderRadius: '12px' }}>
            <h4 style={{ marginBottom: '1rem' }}><FileText size={18} style={{ display: 'inline', marginRight: '0.5rem', verticalAlign: 'middle' }}/> CRIB Report (PDF)</h4>
            <input type="file" accept="application/pdf" onChange={handleCribUpload} style={{ display: 'none' }} id="crib-upload" disabled={cribFile !== null || loadingCrib} />
            <label htmlFor="crib-upload" className="btn btn-primary" style={{ width: '100%', opacity: (cribFile !== null || loadingCrib) ? 0.5 : 1, cursor: (cribFile !== null || loadingCrib) ? 'not-allowed' : 'pointer' }}>
              <UploadCloud size={18} style={{ marginRight: '0.5rem' }} /> {cribFile ? '1 CRIB Report Selected' : 'Select CRIB Report'}
            </label>

            {cribFile && (
              <div style={{ marginTop: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                <CheckCircle size={14} color="var(--success)" /> {cribFile.name} attached
              </div>
            )}

            {loadingCrib && cribFile && !cribData && (
              <div style={{ marginTop: '1rem', fontSize: '0.9rem', color: 'var(--accent-primary)' }}>
                Processing PDF extraction...
              </div>
            )}

            {cribData && !loadingCrib && (
              <div style={{ marginTop: '1rem', fontSize: '0.9rem', color: 'var(--success)' }}>
                <CheckCircle size={16} style={{ display: 'inline', marginRight: '0.25rem', verticalAlign: 'middle' }}/> PDF Processed (Grade: {cribData.risk_grade})
              </div>
            )}
          </div>
        </div>

        <h3 style={{ borderLeft: '4px solid var(--accent-primary)', paddingLeft: '0.75rem', marginBottom: '1.5rem' }}>Employment & Income</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>Self Employed</label>
            <select name="Self_Employed" value={formData.Self_Employed} onChange={handleInputChange} className="input-field">
              <option>No</option><option>Yes</option>
            </select>
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>Employment Sector</label>
            <select name="Employment_Sector" value={formData.Employment_Sector} onChange={handleInputChange} className="input-field">
              {EMPLOYMENT_SECTORS.map(sec => <option key={sec}>{sec}</option>)}
            </select>
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>Applicant Income (LKR)</label>
            <input type="number" name="ApplicantIncome_LKR" value={formData.ApplicantIncome_LKR} onChange={handleInputChange} className="input-field" />
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>Co-applicant Income (LKR)</label>
            <input type="number" name="CoapplicantIncome_LKR" value={formData.CoapplicantIncome_LKR} onChange={handleInputChange} className="input-field" />
          </div>
        </div>

        <h3 style={{ borderLeft: '4px solid var(--accent-primary)', paddingLeft: '0.75rem', marginBottom: '1.5rem' }}>Loan & Property</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>Loan Type</label>
            <select name="Loan_Type" value={formData.Loan_Type} onChange={handleInputChange} className="input-field">
              {LOAN_TYPES.map(type => <option key={type}>{type}</option>)}
            </select>
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>Loan Amount (LKR)</label>
            <input type="number" name="LoanAmount_LKR" value={formData.LoanAmount_LKR} onChange={handleInputChange} className="input-field" style={{ borderColor: !isMinAmountValid ? 'var(--danger)' : '' }} />
            {!isMinAmountValid && (
              <div style={{ fontSize: '0.8rem', color: 'var(--danger)', marginTop: '0.3rem' }}>
                Minimum: {minAmount.toLocaleString()} LKR
              </div>
            )}
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>Loan Term (Months)</label>
            <input type="number" name="Loan_Amount_Term" value={formData.Loan_Amount_Term} onChange={handleInputChange} className="input-field" />
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>Property Region</label>
            <select name="Property_Region_SL" value={formData.Property_Region_SL} onChange={handleInputChange} className="input-field">
              {SL_REGIONS.map(reg => <option key={reg}>{reg}</option>)}
            </select>
          </div>
        </div>

        {isMinAmountValid && (
          <div style={{ padding: '1rem', background: isEmiValid ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)', borderRadius: '8px', marginBottom: '2rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <strong>Estimated EMI:</strong> LKR {emi.toLocaleString(undefined, {maximumFractionDigits: 2})} / month
              </div>
              <div>
                <strong>Max Deductible (60%):</strong> LKR {maxEMI.toLocaleString(undefined, {maximumFractionDigits: 2})}
              </div>
            </div>
            {!isEmiValid && (
              <div style={{ marginTop: '0.5rem', color: 'var(--danger)', fontSize: '0.9rem' }}>
                ⚠️ EMI exceeds 60% of income. Please increase term or reduce loan amount.
              </div>
            )}
          </div>
        )}

        <button type="submit" className="btn btn-primary" style={{ width: '100%', padding: '1rem', fontSize: '1.1rem' }} disabled={submitting || !paysheetData || !cribData || !isEmiValid || !isMinAmountValid}>
          {submitting ? 'Processing...' : '🔮 Predict Loan Eligibility'}
        </button>
      </form>
    </div>
  );
};

export default LoanApplication;
