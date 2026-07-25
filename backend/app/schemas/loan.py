from pydantic import BaseModel, Field
from typing import List, Dict, Any

class LoanApplicationInput(BaseModel):
    """Input schema for loan application"""
    Loan_ID: str = Field(..., description="Unique loan application ID")
    Gender: str = Field(..., description="Gender: Male/Female")
    Married: str = Field(..., description="Marital status: Yes/No")
    Dependents: Any = Field(..., description="Number of dependents (0, 1, 2, or 3+)")
    Education: str = Field(..., description="Education: Graduate/Not Graduate")
    Self_Employed: str = Field(..., description="Self employed: Yes/No")
    ApplicantIncome_LKR: float = Field(..., description="Applicant income in LKR", gt=0)
    CoapplicantIncome_LKR: float = Field(..., description="Co-applicant income in LKR", ge=0)
    LoanAmount_LKR: float = Field(..., description="Loan amount requested in LKR", gt=0)
    Loan_Amount_Term: int = Field(..., description="Loan amount term in months", gt=0)
    Loan_Type: str = Field(..., description="Type of loan requested")
    Property_Region_SL: str = Field(..., description="Sri Lanka property region")
    Employment_Sector: str = Field(..., description="Employment sector of the applicant")
    CRIB_Clearance: str = Field(..., description="CRIB bureau clearance status")

    class Config:
        example = {
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
                {"factor": "CRIB_Clearance", "impact": "Positive", "value": 0, "shap_contribution": 0.25},
                {"factor": "ApplicantIncome_LKR", "impact": "Positive", "value": 184500.0, "shap_contribution": 0.15}
            ],
            "reasoning_summary": "Loan approved due to clear CRIB status and sufficient income",
            "timestamp": "2026-07-21T10:30:00"
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
