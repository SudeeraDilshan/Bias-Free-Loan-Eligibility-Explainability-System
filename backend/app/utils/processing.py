import pandas as pd
from typing import Dict, Any

from app.schemas.loan import LoanApplicationInput
from app.services.model_manager import model_manager

def preprocess_application(application: LoanApplicationInput) -> pd.DataFrame:
    """Convert input to preprocessed features"""
    
    df = pd.DataFrame([{
        'Loan_ID': application.Loan_ID,
        'Gender': application.Gender,
        'Married': application.Married,
        'Dependents': '3+' if str(application.Dependents) == '3+' or (str(application.Dependents).isdigit() and int(application.Dependents) >= 3) else str(application.Dependents),
        'Education': application.Education,
        'Self_Employed': application.Self_Employed,
        'ApplicantIncome_LKR': application.ApplicantIncome_LKR,
        'CoapplicantIncome_LKR': application.CoapplicantIncome_LKR,
        'LoanAmount_LKR': application.LoanAmount_LKR,
        'Loan_Amount_Term': application.Loan_Amount_Term,
        'Loan_Type': application.Loan_Type,
        'Property_Region_SL': application.Property_Region_SL,
        'Employment_Sector': application.Employment_Sector,
        'CRIB_Clearance': application.CRIB_Clearance
    }])
    
    loan_id = df['Loan_ID'].iloc[0]
    df = df.drop('Loan_ID', axis=1)
    
    categorical_cols = [
        'Gender', 'Married', 'Dependents', 'Education', 'Self_Employed',
        'Loan_Type', 'Property_Region_SL', 'Employment_Sector', 'CRIB_Clearance'
    ]
    
    for col in categorical_cols:
        if col in model_manager.label_encoders:
            df[col] = model_manager.label_encoders[col].transform(df[col])

    feature_order = model_manager.preprocessor_config.get('feature_order', list(df.columns))
    df = df[feature_order]
    
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
