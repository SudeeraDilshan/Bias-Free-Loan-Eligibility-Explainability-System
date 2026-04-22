import pandas as pd
from typing import Dict, Any

from app.schemas.loan import LoanApplicationInput
from app.services.model_manager import model_manager

def preprocess_application(application: LoanApplicationInput) -> pd.DataFrame:
    """Convert input to preprocessed features"""
    
    # Create DataFrame
    df = pd.DataFrame([{
        'Loan_ID': application.Loan_ID,
        'Gender': application.Gender,
        'Married': application.Married,
        'Dependents': str(application.Dependents),
        'Education': application.Education,
        'Self_Employed': application.Self_Employed,
        'ApplicantIncome': application.ApplicantIncome,
        'CoapplicantIncome': application.CoapplicantIncome,
        'LoanAmount': application.LoanAmount,
        'Loan_Amount_Term': application.Loan_Amount_Term,
        'Credit_History': application.Credit_History,
        'Property_Area': application.Property_Area
    }])
    
    # Store Loan_ID for later
    loan_id = df['Loan_ID'].iloc[0]
    df = df.drop('Loan_ID', axis=1)
    
    # Encode categorical features
    categorical_cols = ['Gender', 'Married', 'Dependents', 'Education', 
                       'Self_Employed', 'Property_Area']
    
    for col in categorical_cols:
        if col in model_manager.label_encoders:
            df[col] = model_manager.label_encoders[col].transform(df[col])
    
    # Scale features
    df_scaled = pd.DataFrame(
        model_manager.scaler.transform(df),
        columns=df.columns
    )
    
    return df_scaled, loan_id

def generate_reasoning_text(explanation: Dict[str, Any]) -> str:
    """Generate human-readable reasoning for decision"""
    
    top_factors = explanation['top_factors']
    pred = explanation['prediction']
    prob = explanation['approval_probability']
    
    # Build reasoning text
    positive_factors = [f for f in top_factors if f['impact'] == 'Positive']
    negative_factors = [f for f in top_factors if f['impact'] == 'Negative']
    
    reasoning = f"Loan decision: {pred} with {prob:.0%} approval probability.\n"
    
    if positive_factors:
        reasoning += f"\nPositive factors:\n"
        for factor in positive_factors[:3]:
            reasoning += f"  • {factor['factor']}: Increases approval chances\n"
    
    if negative_factors:
        reasoning += f"\nConcerns:\n"
        for factor in negative_factors[:3]:
            reasoning += f"  • {factor['factor']}: Decreases approval chances\n"
    
    return reasoning
