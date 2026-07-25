from fastapi import APIRouter
from typing import Dict, Any
from datetime import datetime

from app.services.model_manager import model_manager

router = APIRouter()

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": model_manager.is_loaded,
        "timestamp": datetime.now().isoformat()
    }

@router.get("/features")
async def get_feature_info() -> Dict[str, Any]:
    """Get information about expected features"""
    return {
        "features": [
            "Gender", "Married", "Dependents", "Education", "Self_Employed",
            "ApplicantIncome_LKR", "CoapplicantIncome_LKR", "LoanAmount_LKR",
            "Loan_Amount_Term", "Loan_Type", "Property_Region_SL",
            "Employment_Sector", "CRIB_Clearance"
        ],
        "categorical_features": [
            "Gender", "Married", "Dependents", "Education", "Self_Employed",
            "Loan_Type", "Property_Region_SL", "Employment_Sector", "CRIB_Clearance"
        ],
        "numerical_features": [
            "ApplicantIncome_LKR", "CoapplicantIncome_LKR", "LoanAmount_LKR", "Loan_Amount_Term"
        ]
    }
