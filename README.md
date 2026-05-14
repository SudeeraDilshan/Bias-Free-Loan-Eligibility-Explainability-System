# Bias-Free Loan Eligibility & Risk Explainability System

**AI-Powered Loan Prediction with Explainability (SHAP) and Fairness Analysis**

## 🎯 Overview

This is a complete end-to-end machine learning system for loan eligibility prediction that combines:

- **Explainability**: SHAP (Shapley Additive Explanations) values to explain individual predictions
- **Local AI**: Natural language decision summaries powered by an offline Small Language Model (Qwen2.5-0.5B)
- **Fairness**: Bias detection and mitigation using demographic parity, equal opportunity metrics
- **Performance**: XGBoost classification with rigorous hyperparameter tuning
- **Production-Ready**: FastAPI backend + React frontend + Docker deployment
- **Transparency**: Detailed reasoning reports for every prediction decision

## 📊 Key Features

### 🤖 Machine Learning
- **Model**: XGBoost Classifier with GridSearchCV hyperparameter optimization
- **Evaluation Metrics**:
  - Accuracy, Precision, Recall, F1-Score
  - ROC-AUC Score
  - Confusion Matrix & ROC Curve
- **Feature Engineering**: Automated preprocessing with intelligent missing value handling

### 🔍 Explainability
- **SHAP Analysis**:
  - Local interpretability (individual predictions)
  - Global feature importance
  - Top-K contributing factors for each prediction
- **Reasoning Reports**: Human-readable explanations for every decision

### 🤖 Local AI (Offline SLM)
- **Model**: Qwen2.5-0.5B-Instruct
- **Feature**: Generates empathetic, natural language summaries for every loan decision
- **Privacy**: Runs 100% locally with no internet connection required after setup

### ⚖️ Fairness & Bias
- **Demographic Parity**: Equal selection rates across protected groups
- **Equal Opportunity**: Equal true positive rates for positive labels
- **Disparate Impact Ratio**: Checks 80% rule compliance
- **Bias Mitigation**: Actionable recommendations for fairness

### 🌐 Full-Stack Application
- **Backend**: FastAPI with automatic API documentation
- **Frontend**: React with interactive UI
- **API Endpoints**:
  - `/predict` - Get prediction + SHAP explanation
  - `/report` - Generate detailed reasoning report
  - `/health` - System health check
  - `/features` - Feature information

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   User Interface                         │
│                   (React Frontend)                       │
│            Loan Form → Results → Explanations            │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/REST
┌────────────────────▼────────────────────────────────────┐
│                   API Layer                              │
│                 (FastAPI Server)                         │
│            /predict  /report  /features                 │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              ML Pipeline Layer                           │
│   ┌──────────────┐  ┌──────────────┐ ┌─────────────┐   │
│   │  Preprocess  │→ │ XGBoost Mdl  │→│ Prediction  │   │
│   └──────────────┘  └──────────────┘ └─────────────┘   │
│                            │                             │
│                    ┌───────▼────────┐                   │
│                    │  SHAP Explainer│                   │
│                    │  Fairness Check│                   │
│                    └────────────────┘                   │
└─────────────────────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│              Data Layer                                  │
│  Training Data  →  Models  →  Results/Logs              │
└─────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
loan-eligibility-system/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── routes/              # API endpoints
│   │   ├── models/              # Database models
│   │   └── utils/               # Helper functions
│   ├── requirements.txt          # Python dependencies
│   └── .env.example              # Environment variables
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # Main React component
│   │   ├── components/
│   │   │   ├── LoanApplicationForm.jsx
│   │   │   ├── PredictionResult.jsx
│   │   │   ├── SHAPExplanation.jsx
│   │   │   └── LoadingSpinner.jsx
│   │   └── styles/              # CSS files
│   ├── package.json
│   └── Dockerfile.frontend
│
├── ml/
│   ├── models/
│   │   ├── preprocessing.py     # Data preprocessing
│   │   ├── xgboost_model.py     # Model training & SHAP
│   │   └── fairness.py          # Bias detection
│   ├── notebooks/               # Jupyter notebooks
│   │   └── 01_data_exploration.ipynb
│   └── training_pipeline.py     # Complete ML pipeline
│
├── docs/
│   ├── API_DOCUMENTATION.md
│   ├── FAIRNESS_ANALYSIS.md
│   └── DEPLOYMENT_GUIDE.md
│
├── Dockerfile.backend
├── Dockerfile.frontend
├── docker-compose.yml
├── .gitignore
└── README.md
```

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Clone and navigate to project
cd loan-eligibility-system

# Start all services
docker-compose up --build

# Access applications
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Local Development (Windows)

#### 1. ML Model Training
Before running the app, you must train the model to generate the necessary artifacts.
```powershell
# Navigate to project root
cd "Bias-Free Loan Eligibility & Explainability System"

# Activate your virtual environment
.\backend\venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Run training (MUST be run from /ml directory for correct paths)
cd ml
python training_pipeline.py --data-path data/loan_data.csv --output-dir models
cd ..
```

#### 2. Backend Setup (FastAPI)
```powershell
cd backend
# Ensure venv is active
uvicorn app.main:app --reload --port 8000
```
*Note: On first run, the backend will download the 900MB Qwen model. Wait for "✓ Local LLM Ready".*

#### 3. Frontend Setup (React)
```powershell
cd frontend
npm install
npm run dev
```
*Access at: http://localhost:5173*

## 📚 Usage Guide

### 1. Training the Model

```python
from ml.models.preprocessing import preprocess_loan_data
from ml.models.xgboost_model import train_loan_classifier
from ml.models.fairness import analyze_model_fairness

# Prepare data
data = preprocess_loan_data('data/loan_data.csv')

# Train model
results = train_loan_classifier(
    data['X_train'], data['y_train'],
    data['X_test'], data['y_test'],
    data['feature_names']
)

# Analyze fairness
fairness_results = analyze_model_fairness(
    data['y_test'],
    results['classifier'].model.predict(data['X_test']),
    data['sensitive_test']
)
```

### 2. Making Predictions via API

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "Loan_ID": "LP001",
    "Gender": "Male",
    "Married": "Yes",
    "Dependents": 2,
    "Education": "Graduate",
    "Self_Employed": "No",
    "ApplicantIncome": 5500,
    "CoapplicantIncome": 2500,
    "LoanAmount": 150,
    "Loan_Amount_Term": 360,
    "Credit_History": 1,
    "Property_Area": "Urban"
  }'
```

### 3. API Response Example

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
      "factor": "Credit_History",
      "impact": "Positive",
      "value": 1.0,
      "shap_contribution": 0.25
    },
    {
      "factor": "ApplicantIncome",
      "impact": "Positive",
      "value": 5500.0,
      "shap_contribution": 0.15
    }
  ],
  "reasoning_summary": "Loan approved due to strong credit history and sufficient income",
  "llm_explanation": "Based on our analysis, your loan application has been approved! Your excellent credit history and stable income were the primary reasons for this positive decision.",
  "timestamp": "2026-04-17T10:30:00"
}
```

## 🔍 Understanding SHAP Explanations

### What is SHAP?

SHAP (SHapley Additive exPlanations) uses game theory to determine each feature's contribution to the prediction:

- **Positive SHAP Value**: Feature increases loan approval chances
- **Negative SHAP Value**: Feature decreases loan approval chances
- **SHAP Value Magnitude**: How strongly the feature influences the decision

### Example Interpretation

```
Application: Rejected with 25% approval probability

Top Contributing Factors:
1. Low_Income (-0.35 SHAP)      ← Strongest negative impact
2. High_Loan_Amount (-0.20)    ← Secondary concern
3. Good_Credit_History (+0.10) ← Some positive factor
```

**Reasoning**: "Loan rejected primarily due to low applicant income relative to requested loan amount. While credit history is acceptable, insufficient income to support loan repayment is the main concern."

## ⚖️ Fairness Metrics Explained

### 1. Demographic Parity

- **Definition**: Selection rate should be equal across protected groups
- **Formula**: |P(ŷ=1|A=0) - P(ŷ=1|A=1)| ≈ 0
- **Threshold**: < 0.1 (Fair), > 0.2 (Bias Detected)

### 2. Equal Opportunity Difference

- **Definition**: True positive rate should be equal given positive labels
- **Formula**: |P(ŷ=1|y=1, A=0) - P(ŷ=1|y=1, A=1)| ≈ 0
- **Threshold**: < 0.1 (Fair), > 0.2 (Bias Detected)

### 3. Disparate Impact Ratio (80% Rule)

- **Definition**: Selection rate ratio ≥ 0.80
- **Formula**: min_group_rate / max_group_rate ≥ 0.80
- **Status**: ✓ Fair if ≥ 0.80, ✗ Violation if < 0.80

## 🛠️ Configuration

### Backend Environment Variables

```env
# API Configuration
API_TITLE=Bias-Free Loan Eligibility System
PORT=8000
DEBUG=False

# Model Paths
MODEL_PATH=../ml/models/xgboost_model.joblib
SCALER_PATH=../ml/models/scaler.joblib

# CORS
CORS_ORIGINS=["http://localhost:3000"]

# Database (optional)
DATABASE_URL=sqlite:///./app.db
```

## 🧪 Testing

```python
# Test prediction
from backend.app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

response = client.post(
    "/predict",
    json={
        "Loan_ID": "TEST001",
        "Gender": "Male",
        "Married": "Yes",
        # ... other fields
    }
)

assert response.status_code == 200
assert "prediction" in response.json()
```

## 📊 Model Performance

Expected performance on test set:
- **Accuracy**: ~81-82%
- **Precision**: ~82-84%  
- **Recall**: ~95-97%
- **F1-Score**: ~88-90%
- **ROC-AUC**: ~0.85-0.87%

## 🚢 Deployment on Cloud

### AWS Deployment

```bash
# Prerequisites: AWS CLI configured

# Push images to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin $AWS_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com

docker tag loan-backend:latest $AWS_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/loan-backend:latest
docker push $AWS_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/loan-backend:latest

# Use ECS or EKS for orchestration
```

### Google Cloud Deployment

```bash
# Configure gcloud
gcloud config set project PROJECT_ID

# Build and push
gcloud builds submit --tag gcr.io/PROJECT_ID/loan-backend

# Deploy to Cloud Run
gcloud run deploy loan-backend \
  --image gcr.io/PROJECT_ID/loan-backend \
  --platform managed
```

## 🔐 Security Best Practices

1. **Environment Variables**: Never commit `.env` files
2. **API Keys**: Use JWT authentication for production
3. **HTTPS**: Enable SSL/TLS in production
4. **CORS**: Restrict origins to trusted domains
5. **Input Validation**: Pydantic validates all inputs
6. **Rate Limiting**: Implement rate limiting for public APIs
7. **Logging**: Monitor and log all predictions for audit trails

## 📈 Model Monitoring & Drift Detection

Track these metrics in production:

```python
# Data Drift
- Feature distributions vs training data
- Statistical tests (KS test, Kolmogorov-Smirnov)

# Prediction Drift  
- Approval rate trends
- Prediction confidence distributions

# Fairness Drift
- Demographic parity change
- Equal opportunity change
```

## 🤝 Contributing

1. Create feature branch: `git checkout -b feature/new-feature`
2. Commit changes: `git commit -am 'Add new feature'`
3. Push to branch: `git push origin feature/new-feature`
4. Submit pull request

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

## 👨‍🎓 Author

Created as a comprehensive ML system demonstrating:
- Explainable AI (XAI) principles
- Fairness in machine learning
- Production-ready deployment
- Best practices in data science

## 🙏 Acknowledgments

- Dataset: [Kaggle Loan Prediction Problem](https://kaggle.com/altruistdelhitiger/loan-prediction-problem-dataset)
- Libraries: XGBoost, SHAP, FastAPI, React, FairLearn
- Fairness Metrics: Inspired by research in algorithmic fairness

## 📞 Support

For issues and questions:
1. Check [API Documentation](docs/API_DOCUMENTATION.md)
2. Review [Fairness Analysis Guide](docs/FAIRNESS_ANALYSIS.md)
3. Create GitHub issue for bug reports

---

**Last Updated**: April 2026  
**Version**: 1.0.0  
**Status**: Production-Ready ✓
