import torch  # Fix for WinError 1114 DLL load failed (OpenMP conflict)
import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
import joblib
import sys

# Add project paths to avoid import issues
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if base_dir not in sys.path:
    sys.path.append(base_dir)

from ml.models.preprocessing import DataPreprocessor
from ml.models.xgboost_model import XGBoostLoanClassifier

class ModelManager:
    """Manages model and preprocessor loading"""
    def __init__(self):
        self.model = None
        self.explainer = None
        self.preprocessor = None
        self.feature_names = None
        self.scaler = None
        self.label_encoders = None
        self.is_loaded = False
    
    def load_models(self):
        """Load trained model and preprocessor artifacts"""
        try:
            # Build absolute paths to avoid CWD relative path issues
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            models_dir = os.path.join(base_dir, 'ml', 'models')
            data_dir = os.path.join(base_dir, 'ml', 'data')
            primary_data_path = os.path.join(data_dir, 'sri_lanka_loan_data.csv')
            fallback_data_path = os.path.join(data_dir, 'loan_data.csv')
            data_path = primary_data_path if os.path.exists(primary_data_path) else fallback_data_path
            
            model_path = os.path.join(models_dir, 'xgboost_model.joblib')
            explainer_path = os.path.join(models_dir, 'shap_explainer.pkl')
            scaler_path = os.path.join(models_dir, 'scaler.joblib')
            encoders_path = os.path.join(models_dir, 'label_encoders.joblib')
            preprocessor_config_path = os.path.join(models_dir, 'preprocessor_config.joblib')
            
            if not os.path.exists(model_path):
                print(f"⚠️ Model artifact not found at {model_path}")
                if os.path.exists(data_path):
                    data_source = 'sri_lanka_loan_data.csv' if os.path.exists(primary_data_path) else 'loan_data.csv'
                    print(f"⚠️ Training fallback model from ml/data/{data_source}...")
                    self._train_and_save_artifacts(
                        data_path,
                        model_path,
                        explainer_path,
                        scaler_path,
                        encoders_path
                    )
                else:
                    raise FileNotFoundError(
                        f"Model file not found and training data missing: {model_path} / {data_path}"
                    )
            else:
                self.model = joblib.load(model_path)
                print(f"✓ Model loaded from {model_path}")

                if os.path.exists(explainer_path):
                    self.explainer = joblib.load(explainer_path)
                    print(f"✓ SHAP Explainer loaded from {explainer_path}")

                if os.path.exists(preprocessor_config_path):
                    self.preprocessor_config = joblib.load(preprocessor_config_path)
                    print(f"✓ Preprocessor config loaded from {preprocessor_config_path}")

                self.scaler = joblib.load(scaler_path)
                self.label_encoders = joblib.load(encoders_path)
                print(f"✓ Scaler and encoders loaded")
            
            self.is_loaded = True
            return True
        except Exception as e:
            print(f"✗ Error loading models: {e}")
            return False

    def _train_and_save_artifacts(self, data_path, model_path, explainer_path, scaler_path, encoders_path):
        """Train the XGBoost model if artifacts are missing"""
        try:
            preprocessor = DataPreprocessor()
            data = preprocessor.prepare_data(data_path, test_size=0.2, random_state=42)

            classifier = XGBoostLoanClassifier(random_state=42)
            classifier.train(data['X_train'], data['y_train'], use_hyperparameter_tuning=False)
            classifier.initialize_explainer(data['X_train'])

            self.model = classifier.model
            self.explainer = classifier.explainer
            self.scaler = data['scaler']
            self.label_encoders = data['label_encoders']
            self.preprocessor_config = data.get('preprocessor_config', {})

            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            joblib.dump(self.model, model_path)
            print(f"✓ Trained model saved to {model_path}")

            if self.explainer is not None:
                joblib.dump(self.explainer, explainer_path)
                print(f"✓ SHAP explainer saved to {explainer_path}")

            joblib.dump(self.scaler, scaler_path)
            joblib.dump(self.label_encoders, encoders_path)
            if self.preprocessor_config:
                joblib.dump(self.preprocessor_config, preprocessor_config_path)
                print(f"✓ Preprocessor config saved to {preprocessor_config_path}")
            else:
                print("⚠️ Preprocessor config missing, feature order may not be preserved")
            print(f"✓ Preprocessing artifacts saved")
        except Exception:
            raise

# Global instance
model_manager = ModelManager()
