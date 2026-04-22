import pandas as pd
import numpy as np
import os

os.makedirs('data', exist_ok=True)

np.random.seed(42)
n_samples = 500

data = {
    'Loan_ID': [f'LP{i:04d}' for i in range(1, n_samples + 1)],
    'Gender': np.random.choice(['Male', 'Female'], n_samples),
    'Married': np.random.choice(['Yes', 'No'], n_samples),
    'Dependents': np.random.choice(['0', '1', '2', '3+'], n_samples),
    'Education': np.random.choice(['Graduate', 'Not Graduate'], n_samples),
    'Self_Employed': np.random.choice(['Yes', 'No'], n_samples),
    'ApplicantIncome': np.random.randint(1500, 15000, n_samples),
    'CoapplicantIncome': np.random.randint(0, 10000, n_samples),
    'LoanAmount': np.random.randint(50, 500, n_samples),
    'Loan_Amount_Term': np.random.choice([180, 240, 360, 480], n_samples),
    'Credit_History': np.random.choice([1.0, 0.0], n_samples, p=[0.8, 0.2]),
    'Property_Area': np.random.choice(['Urban', 'Semiurban', 'Rural'], n_samples),
}

df = pd.DataFrame(data)
df['Loan_Status'] = np.where(
    (df['Credit_History'] == 1.0) & (df['ApplicantIncome'] + df['CoapplicantIncome'] > 4000), 
    'Y', 
    'N'
)

noise = np.random.choice(n_samples, int(0.15 * n_samples), replace=False)
df.loc[noise, 'Loan_Status'] = np.where(df.loc[noise, 'Loan_Status'] == 'Y', 'N', 'Y')

df.to_csv('data/loan_data.csv', index=False)
print("Generated data/loan_data.csv successfully!")
