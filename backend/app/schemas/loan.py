from pydantic import BaseModel, Field
from typing import List, Dict, Any

class LoanApplicationInput(BaseModel):
    """Input schema for loan application"""
    Loan_ID: str = Field(..., description="Unique loan application ID")
    Gender: str = Field(..., description="Gender: Male/Female")
    Married: str = Field(..., description="Marital status: Yes/No")
    Dependents: int = Field(..., description="Number of dependents (0-3+)")
    Education: str = Field(..., description="Education: Graduate/Undergraduate")
    Self_Employed: str = Field(..., description="Self employed: Yes/No")
    ApplicantIncome: float = Field(..., description="Monthly income in rupees", gt=0)
    CoapplicantIncome: float = Field(..., description="Co-applicant income in rupees", ge=0)
    LoanAmount: float = Field(..., description="Loan amount requested (in 000s)", gt=0)
    Loan_Amount_Term: int = Field(..., description="Loan amount term in months", gt=0)
    Credit_History: int = Field(..., description="Credit history: 1 (good) or 0 (bad)")
    Property_Area: str = Field(..., description="Property area: Urban/Semiurban/Rural")

    class Config:
        example = {
            "Loan_ID": "LP001",
            "Gender": "Male",
            "Married": "Yes",
            "Dependents": 2,
            "Education": "Graduate",
            "Self_Employed": "No",
            "ApplicantIncome": 5500.0,
            "CoapplicantIncome": 2500.0,
            "LoanAmount": 150,
            "Loan_Amount_Term": 360,
            "Credit_History": 1,
            "Property_Area": "Urban"
        }

class PredictionResponse(BaseModel):
    """Response schema for predictions"""
    loan_id: str
    prediction: str  # "Approved" or "Rejected"
    approval_probability: float
    rejection_probability: float
    confidence_score: float
    risk_level: str  # "Low", "Medium", "High"
    top_factors: List[Dict[str, Any]]
    reasoning_summary: str
    llm_explanation: str | None = None
    timestamp: str

    class Config:
        example = {
            "loan_id": "LP001",
            "prediction": "Approved",
            "approval_probability": 0.87,
            "rejection_probability": 0.13,
            "confidence_score": 0.87,
            "risk_level": "Low",
            "top_factors": [
                {"factor": "Credit_History", "impact": "Positive", "value": 1, "shap_contribution": 0.25},
                {"factor": "ApplicantIncome", "impact": "Positive", "value": 5500, "shap_contribution": 0.15}
            ],
            "reasoning_summary": "Loan approved due to strong credit history and sufficient income",
            "timestamp": "2026-04-17T10:30:00"
        }

class ReportResponse(BaseModel):
    """Response schema for detailed reasoning reports"""
    loan_id: str
    prediction: str
    approval_probability: float
    confidence_score: float
    decision_factors: Dict[str, Any]
    fairness_assessment: Dict[str, Any]
    recommendations: List[str]
    report_text: str
