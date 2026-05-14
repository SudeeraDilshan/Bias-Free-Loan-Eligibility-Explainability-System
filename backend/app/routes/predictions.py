from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from datetime import datetime
import numpy as np

from app.schemas.loan import LoanApplicationInput, PredictionResponse, ReportResponse
from app.services.model_manager import model_manager
from app.services.llm_explainer import llm_explainer
from app.utils.processing import preprocess_application, generate_reasoning_text

router = APIRouter()

@router.post("/predict", response_model=PredictionResponse)
async def predict_loan_eligibility(application: LoanApplicationInput) -> PredictionResponse:
    """
    Predict loan eligibility and generate SHAP explanation
    
    Returns prediction, probabilities, top contributing factors, and reasoning
    """
    
    if not model_manager.is_loaded:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Preprocess application
        X, loan_id = preprocess_application(application)
        
        # Predict
        prediction = model_manager.model.predict(X)[0]
        probabilities = model_manager.model.predict_proba(X)[0]
        
        # Determine confidence and risk
        approval_prob = probabilities[1]
        confidence = max(probabilities)
        risk_level = "Low" if approval_prob > 0.7 else "Medium" if approval_prob > 0.4 else "High"
        
        # Get SHAP explanation if available
        top_factors = []
        if model_manager.explainer is not None:
            try:
                shap_values = model_manager.explainer.shap_values(X)[0]
                feature_names = X.columns.tolist()
                
                # Get top 5 contributing factors
                abs_shap = np.abs(shap_values)
                top_indices = np.argsort(abs_shap)[-5:][::-1]
                
                for idx in top_indices:
                    top_factors.append({
                        "factor": feature_names[idx],
                        "impact": "Positive" if shap_values[idx] > 0 else "Negative",
                        "value": round(X.iloc[0, idx], 4),
                        "shap_contribution": round(float(shap_values[idx]), 4)
                    })
            except Exception as e:
                print(f"SHAP explanation error: {e}")
        
        # Generate reasoning
        explanation = {
            'prediction': 'Approved' if prediction == 1 else 'Rejected',
            'approval_probability': approval_prob,
            'top_factors': top_factors
        }
        reasoning_summary = generate_reasoning_text(explanation)
        
        # Generate LLM explanation
        llm_explanation = llm_explainer.generate_explanation(
            prediction='Approved' if prediction == 1 else 'Rejected',
            probability=float(approval_prob),
            top_factors=top_factors
        )
        
        return PredictionResponse(
            loan_id=loan_id,
            prediction='Approved' if prediction == 1 else 'Rejected',
            approval_probability=float(approval_prob),
            rejection_probability=float(probabilities[0]),
            confidence_score=float(confidence),
            risk_level=risk_level,
            top_factors=top_factors,
            reasoning_summary=reasoning_summary,
            llm_explanation=llm_explanation,
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        print(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/report", response_model=ReportResponse)
async def generate_detailed_report(application: LoanApplicationInput) -> ReportResponse:
    """
    Generate comprehensive reasoning report with fairness assessment
    """
    
    if not model_manager.is_loaded:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Get prediction first
        prediction_response = await predict_loan_eligibility(application)
        
        # Build detailed report
        report_text = f"""
╔══════════════════════════════════════════════════════════╗
║            LOAN ELIGIBILITY DECISION REPORT              ║
╚══════════════════════════════════════════════════════════╝

Application ID: {prediction_response.loan_id}
Decision: {prediction_response.prediction}
Approval Probability: {prediction_response.approval_probability:.2%}
Confidence Score: {prediction_response.confidence_score:.2%}
Risk Level: {prediction_response.risk_level}
Timestamp: {prediction_response.timestamp}

"""
        
        report_text += "TOP CONTRIBUTING FACTORS:\n"
        report_text += "─" * 60 + "\n"
        for i, factor in enumerate(prediction_response.top_factors, 1):
            report_text += f"{i}. {factor['factor']} ({factor['impact']})\n"
            report_text += f"   Value: {factor['value']}\n"
            report_text += f"   SHAP Contribution: {factor['shap_contribution']}\n"
        
        report_text += "\n" + prediction_response.reasoning_summary
        
        return ReportResponse(
            loan_id=prediction_response.loan_id,
            prediction=prediction_response.prediction,
            approval_probability=prediction_response.approval_probability,
            confidence_score=prediction_response.confidence_score,
            decision_factors={factor['factor']: factor for factor in prediction_response.top_factors},
            fairness_assessment={
                "status": "Under review",
                "notes": "Fairness metrics computed during model training phase"
            },
            recommendations=[
                "Review application for manual verification" if prediction_response.risk_level == "High" else "Standard processing applicable",
                "Monitor similar applications for consistency"
            ],
            report_text=report_text
        )
    
    except Exception as e:
        print(f"Report generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
