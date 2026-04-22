"""
Data Preprocessing Module
Handles data loading, cleaning, feature engineering, and preparation
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
import joblib
import os
from typing import Tuple, Dict, Any

class DataPreprocessor:
    """Comprehensive data preprocessing pipeline for loan eligibility"""
    
    def __init__(self):
        self.label_encoders = {}
        self.scaler = StandardScaler()
        self.preprocessor_config = {}
        
    def load_data(self, filepath: str) -> pd.DataFrame:
        """Load dataset and display basic statistics"""
        df = pd.read_csv(filepath)
        print("Dataset loaded successfully!")
        print(f"Shape: {df.shape}")
        print(f"\nDataset Info:")
        print(df.info())
        print(f"\nFirst few rows:")
        print(df.head())
        print(f"\nMissing values:")
        print(df.isnull().sum())
        print(f"\nTarget variable distribution:")
        print(df['Loan_Status'].value_counts())
        return df
    
    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values using appropriate imputation strategies"""
        df_clean = df.copy()
        
        # Identify columns with missing values
        missing_cols = df_clean.columns[df_clean.isnull().any()].tolist()
        print(f"\nHandling missing values in: {missing_cols}")
        
        # Strategy: For numerical features, use median; for categorical, use mode
        for col in missing_cols:
            if col == 'Loan_Status':
                # Drop rows with missing target
                df_clean = df_clean.dropna(subset=['Loan_Status'])
            elif df_clean[col].dtype == 'object':
                # Categorical: fill with mode
                mode_val = df_clean[col].mode()[0]
                df_clean[col].fillna(mode_val, inplace=True)
                print(f"  {col}: Filled with mode '{mode_val}'")
            else:
                # Numerical: fill with median
                median_val = df_clean[col].median()
                df_clean[col].fillna(median_val, inplace=True)
                print(f"  {col}: Filled with median {median_val:.2f}")
        
        print(f"\nMissing values after handling:")
        print(df_clean.isnull().sum().sum(), "values remaining")
        return df_clean
    
    def identify_features(self, df: pd.DataFrame) -> Tuple[list, list, list]:
        """Identify numerical, categorical, and sensitive attributes"""
        numerical_features = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        categorical_features = df.select_dtypes(include=['object']).columns.tolist()
        
        # Remove target from features
        if 'Loan_Status' in numerical_features:
            numerical_features.remove('Loan_Status')
        if 'Loan_Status' in categorical_features:
            categorical_features.remove('Loan_Status')
        
        # Sensitive attributes for fairness analysis
        sensitive_attributes = [col for col in categorical_features 
                               if col.lower() in ['gender', 'married', 'married_status']]
        
        print(f"\nFeature Identification:")
        print(f"  Numerical features ({len(numerical_features)}): {numerical_features}")
        print(f"  Categorical features ({len(categorical_features)}): {categorical_features}")
        print(f"  Sensitive attributes: {sensitive_attributes}")
        
        self.preprocessor_config['numerical_features'] = numerical_features
        self.preprocessor_config['categorical_features'] = categorical_features
        self.preprocessor_config['sensitive_attributes'] = sensitive_attributes
        
        return numerical_features, categorical_features, sensitive_attributes
    
    def encode_categorical_features(self, df: pd.DataFrame, 
                                   categorical_features: list, 
                                   fit: bool = True) -> pd.DataFrame:
        """Encode categorical variables using LabelEncoder"""
        df_encoded = df.copy()
        
        for col in categorical_features:
            if col == 'Loan_Status':
                # Target variable encoding
                if fit:
                    le = LabelEncoder()
                    df_encoded[col] = le.fit_transform(df_encoded[col])
                    self.label_encoders[col] = le
                    print(f"  {col}: {dict(zip(le.classes_, le.transform(le.classes_)))}")
                else:
                    df_encoded[col] = self.label_encoders[col].transform(df_encoded[col])
            else:
                # Feature encoding
                if fit:
                    le = LabelEncoder()
                    df_encoded[col] = le.fit_transform(df_encoded[col])
                    self.label_encoders[col] = le
                    print(f"  {col}: {dict(zip(le.classes_, le.transform(le.classes_)))}")
                else:
                    df_encoded[col] = self.label_encoders[col].transform(df_encoded[col])
        
        return df_encoded
    
    def scale_features(self, X: pd.DataFrame, fit: bool = True) -> np.ndarray:
        """Scale numerical features using StandardScaler"""
        if fit:
            X_scaled = self.scaler.fit_transform(X)
            print("\nFeatures scaled using StandardScaler")
        else:
            X_scaled = self.scaler.transform(X)
        
        return X_scaled
    
    def prepare_data(self, filepath: str, test_size: float = 0.2, 
                    random_state: int = 42) -> Dict[str, Any]:
        """Complete data preparation pipeline"""
        print("="*60)
        print("DATA PREPROCESSING PIPELINE")
        print("="*60)
        
        # Load and clean
        df = self.load_data(filepath)
        if 'Loan_ID' in df.columns:
            df = df.drop('Loan_ID', axis=1)
            print("Dropped Loan_ID from features.")
            
        df = self.handle_missing_values(df)
        
        # Identify features
        numerical_features, categorical_features, sensitive_attrs = self.identify_features(df)
        
        # Separate target and features
        X = df.drop('Loan_Status', axis=1)
        y = df['Loan_Status']
        
        # Store sensitive attributes for fairness analysis
        sensitive_data = X[sensitive_attrs] if sensitive_attrs else None
        
        # Encode categorical features
        print("\nEncoding categorical features:")
        for col in categorical_features:
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col])
            self.label_encoders[col] = le
            mapping = dict(zip(le.classes_, le.transform(le.classes_)))
            print(f"  {col}: {mapping}")
        
        # Encode target
        le_target = LabelEncoder()
        y = le_target.fit_transform(y)
        self.label_encoders['Loan_Status'] = le_target
        
        # Train-test split
        X_train, X_test, y_train, y_test, sensitive_train, sensitive_test = train_test_split(
            X, y, sensitive_data, test_size=test_size, random_state=random_state, stratify=y
        )
        
        print(f"\nTrain-Test Split:")
        print(f"  Training set: {X_train.shape}")
        print(f"  Test set: {X_test.shape}")
        
        # Scale features
        print("\nScaling features:")
        X_train_scaled = self.scale_features(X_train, fit=True)
        X_test_scaled = self.scale_features(X_test, fit=False)
        
        # Convert back to DataFrame with feature names
        X_train_scaled = pd.DataFrame(X_train_scaled, columns=X_train.columns, 
                                     index=X_train.index)
        X_test_scaled = pd.DataFrame(X_test_scaled, columns=X_test.columns, 
                                    index=X_test.index)
        
        return {
            'X_train': X_train_scaled,
            'X_test': X_test_scaled,
            'y_train': y_train,
            'y_test': y_test,
            'X_original': X,
            'y_original': y,
            'sensitive_train': sensitive_train,
            'sensitive_test': sensitive_test,
            'feature_names': list(X.columns),
            'numerical_features': numerical_features,
            'categorical_features': categorical_features,
            'sensitive_attributes': sensitive_attrs,
            'label_encoders': self.label_encoders,
            'scaler': self.scaler
        }
    
    def save_preprocessing_artifacts(self, save_dir: str):
        """Save encoders and scaler for production use"""
        os.makedirs(save_dir, exist_ok=True)
        joblib.dump(self.label_encoders, f"{save_dir}/label_encoders.joblib")
        joblib.dump(self.scaler, f"{save_dir}/scaler.joblib")
        joblib.dump(self.preprocessor_config, f"{save_dir}/preprocessor_config.joblib")
        print(f"\n✓ Preprocessing artifacts saved to {save_dir}")


def preprocess_loan_data(filepath: str, test_size: float = 0.2) -> Dict[str, Any]:
    """Convenience function for data preprocessing"""
    preprocessor = DataPreprocessor()
    return preprocessor.prepare_data(filepath, test_size=test_size)
