import joblib
import os
import sys

# Add project paths to avoid import issues
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if base_dir not in sys.path:
    sys.path.append(base_dir)

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
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            models_dir = os.path.join(base_dir, 'ml', 'models')
            
            model_path = os.path.join(models_dir, 'xgboost_model.joblib')
            explainer_path = os.path.join(models_dir, 'shap_explainer.pkl')
            scaler_path = os.path.join(models_dir, 'scaler.joblib')
            encoders_path = os.path.join(models_dir, 'label_encoders.joblib')
            
            # Load model
            self.model = joblib.load(model_path)
            print(f"✓ Model loaded from {model_path}")
            
            # Load explainer
            if os.path.exists(explainer_path):
                self.explainer = joblib.load(explainer_path)
                print(f"✓ SHAP Explainer loaded from {explainer_path}")
            
            # Load preprocessing artifacts
            self.scaler = joblib.load(scaler_path)
            self.label_encoders = joblib.load(encoders_path)
            print(f"✓ Scaler and encoders loaded")
            
            self.is_loaded = True
            return True
        except Exception as e:
            print(f"✗ Error loading models: {e}")
            return False

# Global instance
model_manager = ModelManager()
