# Bias-Free Loan Eligibility & Risk Explainability System

**AI-Powered Loan Prediction with SHAP Explainability and Fairness Analysis — Sri Lanka**

---

## 🎯 Overview

A complete end-to-end machine learning system for loan eligibility prediction tailored to the Sri Lankan banking context. The system combines:

- **Explainability**: SHAP (SHapley Additive Explanations) values for per-applicant decision breakdowns
- **Local AI**: Natural language decision summaries via an offline Small Language Model (Qwen2.5-0.5B)
- **Fairness**: Bias detection using demographic parity, equal opportunity, and disparate impact metrics
- **Performance**: XGBoost classifier trained on Sri Lanka loan data with 1,000 records
- **Full-Stack**: FastAPI backend + Streamlit frontend — pure Python, no Node.js required
- **Transparency**: Detailed reasoning reports for every prediction decision

---

## 📊 Key Features

### 🤖 Machine Learning
- **Model**: XGBoost Classifier (binary:logistic)
- **Evaluation**: Accuracy, Precision, Recall, F1-Score, ROC-AUC, Confusion Matrix
- **Feature Engineering**: Automated preprocessing with label encoding, standard scaling, and missing value imputation

### 🔍 Explainability (SHAP)
- Local interpretability — per-prediction top-K contributing factors
- Global feature importance across the whole test set
- Horizontal bar charts showing positive (approval-boosting) vs negative (rejection-boosting) contributions

### 🤖 Local AI (Offline SLM)
- **Model**: Qwen2.5-0.5B-Instruct (downloaded on first run, ~900 MB)
- Generates empathetic, natural language summaries for every loan decision
- Runs 100% locally — no internet required after initial download

### ⚖️ Fairness & Bias Analysis
- **Demographic Parity**: Equal approval rates across protected groups
- **Equal Opportunity**: Equal true positive rates across protected groups
- **Disparate Impact Ratio**: 80% rule compliance check
- Sensitive attributes monitored: **Gender**, **Married**

### 🌐 Full-Stack Application
- **Backend**: FastAPI (port 8000) with automatic Swagger docs at `/docs`
- **Frontend**: Streamlit (port 8501) — 5-page interactive UI, pure Python
- **Smart Data Entry**: Automated CRIB Report PDF upload and Risk Grade extraction
- **API Endpoints**:
  - `POST /predict` — prediction + SHAP + LLM explanation
  - `POST /report`  — detailed reasoning report
  - `GET /health`   — system health check

---

## 🏗️ System Architecture

```
┌────────────────────────────────────────────────┐
│            Streamlit Frontend :8501            │
│  Loan Form → Results → SHAP → Fairness → About │
└───────────────────┬────────────────────────────┘
                    │  HTTP POST /predict
┌───────────────────▼────────────────────────────┐
│            FastAPI Backend :8000               │
│         /predict   /report   /health           │
└───────────────────┬────────────────────────────┘
                    │
        ┌───────────┼──────────────┐
        ▼           ▼              ▼
  XGBoost Model  SHAP Explainer  Qwen2.5 SLM
  (xgboost_      (shap_          (ml/llm_models/)
   model.joblib)  explainer.pkl)
```

---

## 📁 Project Structure

```
Bias-Free-Loan-Eligibility-Explainability-System-version_2/
│
├── backend/                        # FastAPI backend
│   ├── app/
│   │   ├── main.py                 # FastAPI app entry point
│   │   ├── routes/
│   │   │   ├── predictions.py      # POST /predict, POST /report
│   │   │   └── health.py           # GET /health
│   │   ├── schemas/
│   │   │   └── loan.py             # Pydantic request/response models
│   │   ├── services/
│   │   │   ├── model_manager.py    # Loads XGBoost + SHAP artifacts
│   │   │   └── llm_explainer.py    # Loads & runs Qwen2.5 locally
│   │   └── utils/
│   │       └── processing.py       # Input preprocessing helpers
│   ├── requirements.txt
│   ├── .env.example
│   └── venv/                       # Python virtual environment
│
├── streamlit_app/                  # Streamlit frontend (replaces React)
│   ├── app.py                      # Single-file multi-page Streamlit UI
│   └── requirements.txt            # Streamlit-specific deps (including PyPDF2)
│
├── ml/                             # Machine learning pipeline
│   ├── data/
│   │   └── sri_lanka_loan_data.csv # 1,000-row Sri Lanka loan dataset
│   ├── models/
│   │   ├── preprocessing.py        # DataPreprocessor class
│   │   ├── xgboost_model.py        # XGBoostLoanClassifier + SHAP
│   │   ├── fairness.py             # FairnessAnalyzer class
│   │   ├── xgboost_model.joblib    # Trained model artifact
│   │   ├── shap_explainer.pkl      # Fitted SHAP TreeExplainer
│   │   ├── scaler.joblib           # StandardScaler
│   │   └── label_encoders.joblib   # Category encoders
│   ├── results/
│   │   └── fairness_report.json    # Post-training fairness metrics
│   ├── llm_models/                 # Qwen2.5 weights (downloaded on first run)
│   ├── notebooks/
│   │   └── 01_data_exploration.ipynb
│   └── training_pipeline.py        # End-to-end training script
│
├── docs/
│   ├── API_DOCUMENTATION.md
│   ├── FAIRNESS_ANALYSIS.md
│   └── DEPLOYMENT_GUIDE.md
│
├── Dockerfile.backend
├── docker-compose.yml
├── .gitignore
└── README.md
```

---

## 🚀 Quick Start

Follow these steps sequentially to run the full pipeline locally from scratch.

### Prerequisites
- Python 3.11+
- Git

### Step 1 — Clone & Create Virtual Environment

```powershell
git clone <repo-url>
cd Bias-Free-Loan-Eligibility-Explainability-System-version_2

# Create the virtual environment
python -m venv backend/venv

# Activate the virtual environment (Windows PowerShell)
.\backend\venv\Scripts\activate

# If using Linux/Mac, use: source backend/venv/bin/activate
```

### Step 2 — Install All Dependencies

With the virtual environment activated, install both the backend and frontend dependencies:

```powershell
# Install Backend Dependencies (FastAPI, ML, etc.)
pip install -r backend/requirements.txt

# Install Frontend Dependencies (Streamlit, PyPDF2, etc.)
pip install -r streamlit_app/requirements.txt
```

### Step 3 — Train the ML Model

The machine learning models must be trained before the backend can serve predictions.

> ⚠️ Must be run **from the `ml/` directory** so relative paths resolve correctly.

```powershell
cd ml
python training_pipeline.py --data-path data/sri_lanka_loan_data.csv --output-dir models
cd ..
```

This produces the necessary model artifacts in the `ml/models/` and `ml/results/` directories.

### Step 4 — Start the FastAPI Backend

Keep your virtual environment activated and run the backend server:

```powershell
cd backend
uvicorn app.main:app --reload --port 8000
```

> ⚠️ **First run**: The backend downloads the Qwen2.5-0.5B model (~900 MB). Wait for the message:
> `✓ Local LLM Ready (CPU)` before proceeding to the next step.

### Step 5 — Start the Streamlit Frontend

Open a **second, new terminal** window, navigate to the project root, activate the environment, and start the frontend:

```powershell
cd Bias-Free-Loan-Eligibility-Explainability-System-version_2

# Activate the virtual environment again in this new terminal
.\backend\venv\Scripts\activate

# Run the Streamlit application
streamlit run streamlit_app/app.py --server.port 8501
```

Then open **http://localhost:8501** in your browser.

| Service | URL |
|---------|-----|
| Streamlit UI | http://localhost:8501 |
| FastAPI Backend | http://localhost:8000 |
| API Swagger Docs | http://localhost:8000/docs |

---

## 🧠 Model Training & Retraining

To train or retrain the machine learning model (XGBoost) with your latest data, you use the provided training pipeline. This is required before the backend can serve predictions.

1. **Prepare your data**: Ensure your data is in CSV format (e.g., `ml/data/sri_lanka_loan_data.csv`). It must include the target column `Loan_Status` and all necessary features (including the 5 categorical risk values for `CRIB_Clearance`).
2. **Run the training script**:
   Make sure your virtual environment is activated and you are in the `ml/` directory.

   ```powershell
   cd ml
   python training_pipeline.py --data-path data/sri_lanka_loan_data.csv --output-dir models
   ```

### Available Training Arguments:
- `--data-path` (default: `./data/sri_lanka_loan_data.csv`): Path to the training dataset.
- `--output-dir` (default: `./models`): Directory where the trained artifacts will be saved.

### Generated Artifacts:
Running the pipeline will automatically generate and overwrite the following files which the backend relies on:
- `xgboost_model.joblib`: The trained classifier.
- `shap_explainer.pkl`: SHAP TreeExplainer for feature importance.
- `scaler.joblib`: Standard scaler fitted to your numerical features.
- `label_encoders.joblib`: Encoders for categorical features.
- `../results/fairness_report.json`: Automatically generated bias analysis report.

---

## 🖥️ Streamlit UI Pages

| Page | Description |
|------|-------------|
| 🏠 **Loan Application** | Submit applicant details (13 fields) and get instant prediction |
| 📊 **Prediction Results** | Decision banner, gauge chart, probability split, LLM explanation |
| 🔍 **SHAP Explainability** | Horizontal SHAP bar chart + factor details table |
| ⚖️ **Fairness Report** | Model-level fairness metrics for Gender & Married attributes |
| ℹ️ **About** | System overview, architecture, model performance |

---

## 📋 API Usage

### Predict Loan Eligibility

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "Loan_ID": "LP001",
    "Gender": "Male",
    "Married": "Yes",
    "Dependents": "1",
    "Education": "Graduate",
    "Self_Employed": "No",
    "ApplicantIncome_LKR": 184500.0,
    "CoapplicantIncome_LKR": 61940.0,
    "LoanAmount_LKR": 1180000.0,
    "Loan_Amount_Term": 48,
    "Loan_Type": "Personal Loan",
    "Property_Region_SL": "Kandy",
    "Employment_Sector": "Informal/Self-Employed",
    "CRIB_Clearance": "Very Low Risk"
  }'
```

### API Response

```json
{
  "loan_id": "LP001",
  "prediction": "Approved",
  "approval_probability": 0.87,
  "rejection_probability": 0.13,
  "confidence_score": 0.87,
  "risk_level": "Low",
  "top_factors": [
    {
      "factor": "CRIB_Clearance",
      "impact": "Positive",
      "value": 0.0,
      "shap_contribution": 0.31
    },
    {
      "factor": "ApplicantIncome_LKR",
      "impact": "Positive",
      "value": 0.42,
      "shap_contribution": 0.12
    }
  ],
  "reasoning_summary": "Loan approved due to clear CRIB status and sufficient income.",
  "llm_explanation": "Your application has been approved! A clear CRIB record and stable income were the primary factors.",
  "timestamp": "2026-07-21T20:39:33"
}
```

---

## 📊 Model Performance (Actual)

Measured on the 200-sample held-out test set:

| Metric | Score |
|--------|-------|
| Accuracy | 72.0% |
| Precision | 75.2% |
| Recall | 89.2% |
| F1-Score | 81.6% |
| ROC-AUC | 64.6% |

---

## ⚖️ Fairness Results (Actual)

All sensitive attributes evaluated as **✓ FAIR** (threshold: DP diff < 0.10, DI ratio ≥ 0.80):

| Attribute | Demographic Parity Diff | Equal Opportunity Diff | Disparate Impact Ratio |
|-----------|------------------------|------------------------|------------------------|
| Gender | 0.0548 ✅ | 0.0154 ✅ | 0.9356 ✅ |
| Married | 0.0384 ✅ | 0.0342 ✅ | 0.9547 ✅ |

---

## 🔍 Understanding SHAP Values

SHAP (SHapley Additive exPlanations) uses game theory to attribute each feature's contribution to the model output:

| SHAP Value | Meaning |
|------------|---------|
| **Positive** | Feature pushed the decision toward *Approved* |
| **Negative** | Feature pushed the decision toward *Rejected* |
| **Magnitude** | Larger absolute value = stronger influence |

---

## ⚖️ Fairness Metrics Explained

| Metric | Definition | Fair Threshold |
|--------|-----------|---------------|
| **Demographic Parity** | Difference in approval rates across groups | < 0.10 |
| **Equal Opportunity** | Difference in True Positive Rates across groups | < 0.10 |
| **Disparate Impact Ratio** | Ratio of approval rates (min / max group) | ≥ 0.80 |

---

## 🛠️ Configuration

### Backend Environment Variables (`backend/.env`)

```env
API_TITLE=Bias-Free Loan Eligibility System
PORT=8000
DEBUG=False
MODEL_PATH=../ml/models/xgboost_model.joblib
SCALER_PATH=../ml/models/scaler.joblib
CORS_ORIGINS=["http://localhost:8501"]
DATABASE_URL=sqlite:///./app.db
```

---

## 🚢 Docker Deployment (Backend Only)

The Streamlit frontend runs as a Python process and does not need Docker. Only the backend is Dockerised:

```bash
# Build and start the backend container
docker-compose up --build

# Backend API available at:
# http://localhost:8000
# http://localhost:8000/docs

# Then run Streamlit locally:
.\backend\venv\Scripts\streamlit.exe run streamlit_app\app.py --server.port 8501
```

---

## 🔐 Security Best Practices

1. **Environment Variables**: Never commit `.env` files (already in `.gitignore`)
2. **CORS**: Restrict origins to `http://localhost:8501` in production
3. **Input Validation**: Pydantic validates all API inputs automatically
4. **HTTPS**: Enable SSL/TLS in production behind a reverse proxy (nginx)
5. **Logging**: All predictions are timestamped for audit trails

---

## 📈 Model Monitoring

Track these in production:

```
# Data Drift
- Feature distributions vs training data (KS test)

# Prediction Drift
- Approval rate trends over time
- Confidence score distributions

# Fairness Drift
- Demographic parity change over rolling windows
- Equal opportunity change per cohort
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [API Documentation](docs/API_DOCUMENTATION.md) | Full endpoint reference |
| [Fairness Analysis Guide](docs/FAIRNESS_ANALYSIS.md) | Deep-dive into bias metrics |
| [Deployment Guide](docs/DEPLOYMENT_GUIDE.md) | Cloud & Docker deployment |

---

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Commit changes: `git commit -am 'Add your feature'`
3. Push: `git push origin feature/your-feature`
4. Open a Pull Request

---

## 📝 License

MIT License — see LICENSE file for details.

---

## 🙏 Acknowledgments

- **Dataset**: Sri Lanka loan application data (1,000 records, 14 features)
- **Libraries**: XGBoost, SHAP, FastAPI, Streamlit, FairLearn, Aequitas, Qwen2.5
- **Fairness Metrics**: Grounded in algorithmic fairness research

---

**Last Updated**: July 2026 &nbsp;|&nbsp; **Version**: 2.0.0 &nbsp;|&nbsp; **Status**: Production-Ready ✓
