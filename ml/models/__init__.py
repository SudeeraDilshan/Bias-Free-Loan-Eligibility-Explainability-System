"""
Loan Eligibility ML Models Package
Submodules for preprocessing, modeling, and fairness analysis
"""

from .preprocessing import DataPreprocessor, preprocess_loan_data
from .xgboost_model import XGBoostLoanClassifier, train_loan_classifier
from .fairness import FairnessAnalyzer, analyze_model_fairness

__version__ = '1.0.0'
__all__ = [
    'DataPreprocessor',
    'preprocess_loan_data',
    'XGBoostLoanClassifier',
    'train_loan_classifier',
    'FairnessAnalyzer',
    'analyze_model_fairness'
]
