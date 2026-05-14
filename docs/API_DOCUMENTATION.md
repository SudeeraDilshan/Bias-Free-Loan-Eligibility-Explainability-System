# API Documentation

## Overview

This document provides comprehensive documentation for the Loan Eligibility Prediction API. All endpoints follow RESTful conventions and return JSON responses.

**Base URL**: `http://localhost:8000`  
**API Version**: 1.0.0

---

## Health Check

### GET `/health`

Check if the API and ML model are ready.

**Response**:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "timestamp": "2026-04-17T10:30:00Z"
}
```

**Status Codes**:
- `200`: Healthy, model loaded
- `503`: Model not loaded

---

## Prediction Endpoint

### POST `/predict`

Get loan eligibility prediction with SHAP explanation and top contributing factors.

**Request Body**:
```json
{
  "Loan_ID": "LP001",
  "Gender": "Male",
  "Married": "Yes",
  "Dependents": 0,
  "Education": "Graduate",
  "Self_Employed": "No",
  "ApplicantIncome": 5500.0,
  "CoapplicantIncome": 2500.0,
  "LoanAmount": 150,
  "Loan_Amount_Term": 360,
  "Credit_History": 1,
  "Property_Area": "Urban"
}
```

**Field Descriptions**:

| Field | Type | Values | Notes |
|-------|------|--------|-------|
| Loan_ID | string | Any unique ID | Required, must be unique |
| Gender | string | Male, Female | Required |
| Married | string | Yes, No | Required |
| Dependents | integer | 0, 1, 2, 3+ | Required |
| Education | string | Graduate, Undergraduate | Required |
| Self_Employed | string | Yes, No | Required |
| ApplicantIncome | float | > 0 | Monthly income in rupees |
| CoapplicantIncome | float | >= 0 | Co-applicant income |
| LoanAmount | float | > 0 | Loan amount in thousands |
| Loan_Amount_Term | integer | > 0 | Tenure in months |
| Credit_History | integer | 0, 1 | 1=Good, 0=Bad |
| Property_Area | string | Urban, Semiurban, Rural | Required |

**Response**:
```json
{
  "loan_id": "LP001",
  "prediction": "Approved",
  "approval_probability": 0.87,
  "rejection_probability": 0.13,
  "confidence_score": 0.87,
  "risk_level": "Low",
  "top_factors": [
    {
      "factor": "Credit_History",
      "impact": "Positive",
      "value": 1.0,
      "shap_contribution": 0.25
    },
    {
      "factor": "ApplicantIncome",
      "impact": "Positive",
      "value": 5500.0,
      "shap_contribution": 0.15
    },
    {
      "factor": "LoanAmount",
      "impact": "Negative",
      "value": 150.0,
      "shap_contribution": -0.08
    }
  ],
  "reasoning_summary": "Loan rejected mainly due to low income...",
  "llm_explanation": "Based on our analysis, your loan application has been rejected. The primary factor was your applicant income, which is currently below the threshold required for the requested loan amount.",
  "timestamp": "2026-04-17T10:30:00Z"
}
```

**Response Fields**:

| Field | Type | Description |
|-------|------|-------------|
| loan_id | string | Echoed loan application ID |
| prediction | string | "Approved" or "Rejected" |
| approval_probability | float | Probability of approval (0-1) |
| rejection_probability | float | Probability of rejection (0-1) |
| confidence_score | float | Model confidence (0-1) |
| risk_level | string | "Low", "Medium", or "High" |
| top_factors | array | Top 5 contributing factors |
| reasoning_summary | string | Technical reasoning summary |
| llm_explanation | string | **[NEW]** Natural language AI summary (Offline SLM) |
| timestamp | string | ISO 8601 timestamp |

**SHAP Factor Explanation**:

Each factor in `top_factors` contains:
- **factor**: Feature name
- **impact**: "Positive" (increases approval) or "Negative" (decreases approval)
- **value**: Actual feature value in application
- **shap_contribution**: SHAP value (magnitude of contribution)

**Examples**:

```bash
# Using curl
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "Loan_ID": "LP001",
    "Gender": "Male",
    "Married": "Yes",
    "Dependents": 2,
    "Education": "Graduate",
    "Self_Employed": "No",
    "ApplicantIncome": 5500,
    "CoapplicantIncome": 2500,
    "LoanAmount": 150,
    "Loan_Amount_Term": 360,
    "Credit_History": 1,
    "Property_Area": "Urban"
  }'
```

```python
# Using Python requests
import requests

response = requests.post(
    "http://localhost:8000/predict",
    json={
        "Loan_ID": "LP001",
        "Gender": "Male",
        "Married": "Yes",
        "Dependents": 2,
        "Education": "Graduate",
        "Self_Employed": "No",
        "ApplicantIncome": 5500,
        "CoapplicantIncome": 2500,
        "LoanAmount": 150,
        "Loan_Amount_Term": 360,
        "Credit_History": 1,
        "Property_Area": "Urban"
    }
)

result = response.json()
print(f"Decision: {result['prediction']}")
print(f"Confidence: {result['confidence_score']:.0%}")
```

**Status Codes**:
- `200`: Successful prediction
- `422`: Validation error (missing/invalid fields)
- `503`: Model not loaded
- `500`: Server error

---

## Report Endpoint

### POST `/report`

Generate a detailed reasoning report with fairness assessment.

**Request**: Same as `/predict` endpoint

**Response**:
```json
{
  "loan_id": "LP001",
  "prediction": "Approved",
  "approval_probability": 0.87,
  "confidence_score": 0.87,
  "decision_factors": {
    "Credit_History": {
      "factor": "Credit_History",
      "impact": "Positive",
      "value": 1.0,
      "shap_contribution": 0.25
    }
  },
  "fairness_assessment": {
    "status": "Under review",
    "notes": "Fairness metrics computed during model training phase"
  },
  "recommendations": [
    "Standard processing applicable",
    "Monitor similar applications for consistency"
  ],
  "report_text": "╔══════════════════════════════════════════════════════════╗..."
}
```

---

## Features Endpoint

### GET `/features`

Get information about expected features and their types.

**Response**:
```json
{
  "features": [
    "Gender", "Married", "Dependents", "Education", "Self_Employed",
    "ApplicantIncome", "CoapplicantIncome", "LoanAmount",
    "Loan_Amount_Term", "Credit_History", "Property_Area"
  ],
  "categorical_features": [
    "Gender", "Married", "Dependents", "Education", "Self_Employed", "Property_Area"
  ],
  "numerical_features": [
    "ApplicantIncome", "CoapplicantIncome", "LoanAmount",
    "Loan_Amount_Term", "Credit_History"
  ]
}
```

---

## Error Handling

### Validation Error (422)

```json
{
  "detail": [
    {
      "loc": ["body", "ApplicantIncome"],
      "msg": "ensure this value is greater than 0",
      "type": "value_error.number.not_gt",
      "ctx": {"limit_value": 0}
    }
  ]
}
```

### Server Error (500)

```json
{
  "detail": "Internal server error: [error details]"
}
```

---

## Rate Limiting

API rate limits (recommended for production):
- **Tier 1**: 100 requests per minute
- **Tier 2**: 1,000 requests per minute
- **Tier 3**: Unlimited (enterprise)

---

## Authentication

For production deployment, implement JWT authentication:

```python
# Add to request headers
Authorization: Bearer <JWT_TOKEN>
```

---

## CORS Configuration

**Allowed Origins** (configurable):
- http://localhost:3000
- http://localhost:8080
- https://yourdomain.com

---

## Response Time

**Typical Response Times**:
- Prediction endpoint: ~200-500ms
- Report endpoint: ~300-700ms
- Includes preprocessing, model inference, SHAP computation

---

## Best Practices

1. **Batch Processing**: For multiple applications, submit sequentially
2. **Caching**: Cache results for identical applications
3. **Error Handling**: Always check for `detail` field in error responses
4. **Logging**: Keep detailed logs of all predictions for audit
5. **Feedback**: Store user feedback to improve fairness metrics

---

## Interactive API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These provide interactive testing and detailed documentation.

---

## Integration Examples

### Excel/Google Sheets Integration

Use Google Apps Script or Power Query:
```javascript
const response = UrlFetchApp.fetch('http://localhost:8000/predict', {
  method: 'post',
  contentType: 'application/json',
  payload: JSON.stringify(applicationData)
});
```

### Analytics Platform Integration

Send predictions to BI tools:
```python
# Send to PowerBI, Tableau, etc.
import requests
import pandas as pd

applications = pd.read_csv('applications.csv')

for _, app in applications.iterrows():
    prediction = requests.post('http://localhost:8000/predict', json=app.to_dict())
    # Store results in BI tool
```

---

**API Version**: 1.0.0  
**Last Updated**: April 2026  
**Support**: See README.md for support channels
