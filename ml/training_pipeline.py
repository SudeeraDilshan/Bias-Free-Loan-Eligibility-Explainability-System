"""
Complete ML Training Pipeline
Trains XGBoost model with SHAP explanations and fairness analysis
"""

import torch  # Fix for WinError 1114 DLL load failed (OpenMP conflict)
import os
import sys
import pandas as pd
import numpy as np
import warnings
from datetime import datetime
import json

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.preprocessing import DataPreprocessor
from models.xgboost_model import XGBoostLoanClassifier
from models.fairness import FairnessAnalyzer

warnings.filterwarnings('ignore')


class LoanModelPipeline:
    """Complete pipeline for training loan eligibility model"""
    
    def __init__(self, data_path: str, output_dir: str = './models'):
        self.data_path = data_path
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        self.preprocessor = None
        self.classifier = None
        self.fairness_analyzer = None
        self.results = {}
        
    def run(self):
        """Execute complete training pipeline"""
        print("\n" + "="*70)
        print("LOAN ELIGIBILITY MODEL TRAINING PIPELINE")
        print("="*70)
        print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        try:
            # Step 1: Data Preparation
            self._step_data_preparation()
            
            # Step 2: Model Training
            self._step_model_training()
            
            # Step 3: Model Evaluation
            self._step_model_evaluation()
            
            # Step 4: Fairness Analysis
            self._step_fairness_analysis()
            
            # Step 5: Save Results
            self._step_save_results()
            
            print("\n" + "="*70)
            print("✓ PIPELINE COMPLETED SUCCESSFULLY")
            print("="*70)
            print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
        except Exception as e:
            print(f"\n✗ PIPELINE FAILED: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    def _step_data_preparation(self):
        """Step 1: Data Preparation"""
        print("\n📊 STEP 1: DATA PREPARATION")
        print("-" * 70)
        
        self.preprocessor = DataPreprocessor()
        self.data = self.preprocessor.prepare_data(
            self.data_path, 
            test_size=0.2, 
            random_state=42
        )
        
        print(f"\n✓ Data prepared successfully")
        print(f"  Training set: {self.data['X_train'].shape}")
        print(f"  Test set: {self.data['X_test'].shape}")
    
    def _step_model_training(self):
        """Step 2: Model Training"""
        print("\n🤖 STEP 2: MODEL TRAINING & HYPERPARAMETER TUNING")
        print("-" * 70)
        
        self.classifier = XGBoostLoanClassifier(random_state=42)
        self.classifier.train(
            self.data['X_train'],
            self.data['y_train'],
            use_hyperparameter_tuning=False
        )
        
        self.classifier.initialize_explainer(self.data['X_train'])
        
        print(f"\n✓ Model trained successfully")
        print(f"  Best parameters: {self.classifier.best_params}")
    
    def _step_model_evaluation(self):
        """Step 3: Model Evaluation"""
        print("\n📈 STEP 3: MODEL EVALUATION")
        print("-" * 70)
        
        metrics = self.classifier.evaluate(
            self.data['X_test'],
            self.data['y_test']
        )
        
        self.results['metrics'] = {
            'accuracy': float(metrics['accuracy']),
            'precision': float(metrics['precision']),
            'recall': float(metrics['recall']),
            'f1_score': float(metrics['f1_score']),
            'roc_auc': float(metrics['roc_auc'])
        }
        
        # Generate visualizations
        print("\nGenerating visualizations...")
        self.classifier.plot_feature_importance(self.data['feature_names'])
        self.classifier.plot_shap_summary(self.data['X_test'], plot_type='bar')
        
        print("✓ Visualizations saved")
    
    def _step_fairness_analysis(self):
        """Step 4: Fairness Analysis"""
        print("\n⚖️ STEP 4: FAIRNESS & BIAS ANALYSIS")
        print("-" * 70)
        
        y_pred = self.classifier.model.predict(self.data['X_test'])
        
        self.fairness_analyzer = FairnessAnalyzer()
        
        fairness_results = {}
        for attr_name in self.data['sensitive_attributes']:
            if self.data['sensitive_test'] is not None and attr_name in self.data['sensitive_test'].columns:
                fairness_results[attr_name] = self.fairness_analyzer.analyze_fairness(
                    self.data['y_test'],
                    y_pred,
                    self.data['sensitive_test'][attr_name],
                    attr_name
                )
        
        self.results['fairness'] = fairness_results
        
        # Generate bias mitigation report
        print("\nGenerating fairness report...")
        report = self.fairness_analyzer.generate_bias_mitigation_report(fairness_results)
        
        print("✓ Fairness analysis complete")
    
    def _step_save_results(self):
        """Step 5: Save Results & Artifacts"""
        print("\n💾 STEP 5: SAVING MODELS & RESULTS")
        print("-" * 70)
        
        # Save model
        model_path = os.path.join(self.output_dir, 'xgboost_model.joblib')
        self.classifier.save_model(model_path)
        
        # Save preprocessing artifacts
        self.preprocessor.save_preprocessing_artifacts(self.output_dir)
        
        # Save explainer
        explainer_path = os.path.join(self.output_dir, 'shap_explainer.pkl')
        import joblib
        joblib.dump(self.classifier.explainer, explainer_path)
        print(f"✓ SHAP Explainer saved to {explainer_path}")
        
        # Save results
        results_path = os.path.join(self.output_dir, 'training_results.json')
        with open(results_path, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'metrics': self.results.get('metrics', {}),
                'best_params': self.classifier.best_params
            }, f, indent=2)
        print(f"✓ Results saved to {results_path}")
        
        # Save fairness report
        fairness_path = os.path.join(self.output_dir, '../results')
        os.makedirs(fairness_path, exist_ok=True)
        self.fairness_analyzer.save_fairness_report(self.results['fairness'], fairness_path)
        
        print(f"\n✓ All artifacts saved to {self.output_dir}/")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Train Loan Eligibility Model with SHAP & Fairness'
    )
    parser.add_argument(
        '--data-path',
        type=str,
        default='./data/loan_data.csv',
        help='Path to loan dataset CSV'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='./models',
        help='Directory to save trained models'
    )
    
    args = parser.parse_args()
    
    # Run pipeline
    pipeline = LoanModelPipeline(
        data_path=args.data_path,
        output_dir=args.output_dir
    )
    pipeline.run()


if __name__ == '__main__':
    main()
