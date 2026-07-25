"""
XGBoost Model Training & SHAP Explainability Module
Handles model training, hyperparameter tuning, evaluation, and SHAP explanations
"""
import torch  # Fix for WinError 1114 DLL load failed (OpenMP conflict)
import pandas as pd
import numpy as np
import shap
import xgboost as xgb
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import (accuracy_score, precision_score, recall_score, 
                             f1_score, roc_auc_score, confusion_matrix, roc_curve, auc)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import warnings
warnings.filterwarnings('ignore')
from typing import Dict, Any, Tuple

class XGBoostLoanClassifier:
    """XGBoost classifier for loan eligibility with hyperparameter optimization"""
    
    def __init__(self, random_state: int = 42):
        self.model = None
        self.explainer = None
        self.shap_values = None
        self.random_state = random_state
        self.best_params = None
        self.cv_results = None
        
    def train(self, X_train: pd.DataFrame, y_train: np.ndarray, 
              use_hyperparameter_tuning: bool = True) -> Dict[str, Any]:
        """Train XGBoost model with optional hyperparameter tuning"""
        print("="*60)
        print("XGBOOST MODEL TRAINING")
        print("="*60)
        
        if use_hyperparameter_tuning:
            self.model, self.best_params, self.cv_results = self._hyperparameter_tuning(X_train, y_train)
        else:
            # Train with default parameters
            params = {
                'max_depth': 6,
                'learning_rate': 0.1,
                'n_estimators': 100,
                'subsample': 0.8,
                'colsample_bytree': 0.8,
                'objective': 'binary:logistic',
                'random_state': self.random_state,
                'n_jobs': -1
            }
            self.model = xgb.XGBClassifier(**params)
            self.model.fit(X_train, y_train, verbose=True)
            self.best_params = params
            print("✓ Model trained with default parameters")
        
        return {
            'model': self.model,
            'best_params': self.best_params,
            'cv_results': self.cv_results
        }
    
    def _hyperparameter_tuning(self, X_train: pd.DataFrame, 
                               y_train: np.ndarray) -> Tuple[Any, Dict, Dict]:
        """Perform GridSearchCV for hyperparameter optimization"""
        print("\nPerforming hyperparameter tuning...")
        
        param_grid = {
            'max_depth': [5, 6, 7],
            'learning_rate': [0.05, 0.1, 0.15],
            'n_estimators': [100, 150],
            'subsample': [0.7, 0.8],
            'colsample_bytree': [0.7, 0.8]
        }
        
        base_model = xgb.XGBClassifier(
            objective='binary:logistic',
            random_state=self.random_state,
            n_jobs=-1
        )
        
        grid_search = GridSearchCV(
            base_model, param_grid, cv=5, scoring='roc_auc', 
            n_jobs=-1, verbose=1
        )
        
        grid_search.fit(X_train, y_train)
        
        print(f"\nBest parameters: {grid_search.best_params_}")
        print(f"Best CV AUC Score: {grid_search.best_score_:.4f}")
        
        return grid_search.best_estimator_, grid_search.best_params_, grid_search.cv_results_
    
    def evaluate(self, X_test: pd.DataFrame, y_test: np.ndarray) -> Dict[str, float]:
        """Evaluate model performance on test set"""
        print("\n" + "="*60)
        print("MODEL EVALUATION")
        print("="*60)
        
        y_pred = self.model.predict(X_test)
        y_pred_proba = self.model.predict_proba(X_test)[:, 1]
        
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred),
            'recall': recall_score(y_test, y_pred),
            'f1_score': f1_score(y_test, y_pred),
            'roc_auc': roc_auc_score(y_test, y_pred_proba),
            'confusion_matrix': confusion_matrix(y_test, y_pred)
        }
        
        print(f"\nAccuracy:  {metrics['accuracy']:.4f}")
        print(f"Precision: {metrics['precision']:.4f}")
        print(f"Recall:    {metrics['recall']:.4f}")
        print(f"F1-Score:  {metrics['f1_score']:.4f}")
        print(f"ROC-AUC:   {metrics['roc_auc']:.4f}")
        print(f"\nConfusion Matrix:")
        print(metrics['confusion_matrix'])
        
        return metrics
    
    def plot_feature_importance(self, feature_names: list, top_n: int = 20):
        """Plot feature importance from XGBoost model"""
        importance_df = pd.DataFrame({
            'feature': feature_names,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False).head(top_n)
        
        plt.figure(figsize=(10, 8))
        sns.barplot(data=importance_df, x='importance', y='feature', palette='viridis')
        plt.title('Top 20 Feature Importance (XGBoost)', fontsize=14, fontweight='bold')
        plt.xlabel('Importance Score')
        plt.tight_layout()
        import os
        os.makedirs('results', exist_ok=True)
        plt.savefig('results/feature_importance_xgboost.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        return importance_df
    
    def initialize_explainer(self, X_train: pd.DataFrame):
        """Initialize SHAP Explainer for model interpretation"""
        print("\n" + "="*60)
        print("INITIALIZING SHAP EXPLAINER")
        print("="*60)
        
        # Use TreeExplainer for XGBoost
        self.explainer = shap.TreeExplainer(self.model)
        print("✓ SHAP TreeExplainer initialized for XGBoost")
        
        # Compute base value
        base_val = self.explainer.expected_value
        if isinstance(base_val, np.ndarray):
            base_val = base_val[0]
        print(f"Base value (expected model output): {float(base_val):.4f}")
        
        return self.explainer
    
    def explain_prediction(self, instance: pd.DataFrame, feature_names: list) -> Dict[str, Any]:
        """Generate SHAP explanation for a single prediction"""
        shap_values = self.explainer.shap_values(instance)
        prediction = self.model.predict(instance)[0]
        prediction_proba = self.model.predict_proba(instance)[0]
        
        explanation = {
            'prediction': 'Approved' if prediction == 1 else 'Rejected',
            'approval_probability': prediction_proba[1],
            'rejection_probability': prediction_proba[0],
            'shap_values': shap_values[0],
            'feature_names': feature_names,
            'feature_values': instance.values[0]
        }
        
        return explanation
    
    def generate_reasoning_report(self, explanation: Dict[str, Any], 
                                 top_factors: int = 5) -> str:
        """Generate human-readable reasoning report for loan decision"""
        
        # Get feature contributions (SHAP values)
        feature_contributions = pd.DataFrame({
            'feature': explanation['feature_names'],
            'shap_value': explanation['shap_values'],
            'feature_value': explanation['feature_values']
        })
        
        # Sort by absolute SHAP value to get top contributing factors
        feature_contributions['abs_shap'] = np.abs(feature_contributions['shap_value'])
        top_factors_df = feature_contributions.nlargest(top_factors, 'abs_shap')
        
        # Build report
        report = f"""
╔══════════════════════════════════════════════════════════╗
║            LOAN ELIGIBILITY DECISION REPORT              ║
╚══════════════════════════════════════════════════════════╝

PREDICTION: {explanation['prediction'].upper()}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Approval Probability: {explanation['approval_probability']:.2%}
Rejection Probability: {explanation['rejection_probability']:.2%}

TOP CONTRIBUTING FACTORS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        for idx, (_, row) in enumerate(top_factors_df.iterrows(), 1):
            contribution = "Positive" if row['shap_value'] > 0 else "Negative"
            impact = "INCREASES" if row['shap_value'] > 0 else "DECREASES"
            
            report += f"\n{idx}. {row['feature']} (Value: {row['feature_value']:.4f})\n"
            report += f"   Impact: {impact} approval chances\n"
            report += f"   SHAP Contribution: {row['shap_value']:.4f}\n"
        
        report += "\n" + "="*60 + "\n"
        report += "EXPLANATION:\n"
        report += "This decision is based on factors that historically correlate\n"
        report += "with loan approval/rejection. The SHAP values indicate the\n"
        report += "magnitude and direction of each factor's contribution.\n"
        report += "="*60 + "\n"
        
        return report
    
    def plot_shap_summary(self, X_test: pd.DataFrame, plot_type: str = 'bar'):
        """Plot SHAP summary (global interpretability)"""
        if self.explainer is None:
            print("Error: SHAP Explainer not initialized. Call initialize_explainer first.")
            return
        
        shap_values = self.explainer.shap_values(X_test)
        
        plt.figure(figsize=(12, 8))
        shap.summary_plot(shap_values, X_test, plot_type=plot_type, show=False)
        plt.title(f'SHAP {plot_type.capitalize()} Plot - Global Feature Importance', 
                 fontsize=14, fontweight='bold')
        plt.tight_layout()
        import os
        os.makedirs('results', exist_ok=True)
        plt.savefig(f'results/shap_summary_{plot_type}.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_shap_force_plot(self, instance: pd.DataFrame, idx: int = 0):
        """Plot SHAP force plot for individual prediction"""
        if self.explainer is None:
            print("Error: SHAP Explainer not initialized. Call initialize_explainer first.")
            return
        
        shap_value = self.explainer.shap_values(instance)[idx]
        shap.force_plot(self.explainer.expected_value, shap_value, 
                       instance.iloc[idx], show=False).save_html(
                       f'results/shap_force_plot_{idx}.html')
        print(f"✓ SHAP force plot saved")
    
    def save_model(self, filepath: str):
        """Save trained model"""
        joblib.dump(self.model, filepath)
        print(f"✓ Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load trained model"""
        self.model = joblib.load(filepath)
        print(f"✓ Model loaded from {filepath}")


def train_loan_classifier(X_train: pd.DataFrame, y_train: np.ndarray,
                         X_test: pd.DataFrame, y_test: np.ndarray,
                         feature_names: list) -> Dict[str, Any]:
    """Complete training pipeline"""
    clf = XGBoostLoanClassifier()
    clf.train(X_train, y_train, use_hyperparameter_tuning=True)
    metrics = clf.evaluate(X_test, y_test)
    clf.initialize_explainer(X_train)
    clf.plot_feature_importance(feature_names)
    clf.plot_shap_summary(X_test, plot_type='bar')
    
    return {
        'classifier': clf,
        'metrics': metrics,
        'explainer': clf.explainer
    }
