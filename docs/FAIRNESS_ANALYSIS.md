# Fairness & Bias Analysis Guide

## Overview

This guide explains the fairness metrics used in the Loan Eligibility System and how to interpret bias detection results.

---

## Why Fairness Matters

Financial institutions can inadvertently discriminate based on protected attributes (gender, race, marital status, etc.). This system detects such bias using scientific fairness metrics and suggests mitigation strategies.

---

## Key Fairness Metrics

### 1. Demographic Parity

**Definition**: Selection rate should be approximately equal across all demographic groups.

**Formula**:
```
Demographic Parity Difference = |P(ŷ=1|A=0) - P(ŷ=1|A=1)|
```

Where:
- `ŷ` = predicted label (approved=1, rejected=0)
- `A` = protected attribute value

**Interpretation**:

| Difference | Status | Action |
|-----------|--------|--------|
| < 0.10 | ✓ Fair | No intervention needed |
| 0.10-0.20 | ⚠ Caution | Monitor closely |
| > 0.20 | ✗ Bias Detected | Mitigation required |

**Example**:
```
Gender=Male approval rate:   78%
Gender=Female approval rate: 62%
Difference: 16% → CAUTION (significant imbalance)
```

**Mitigation**:
- Review feature engineering for hidden proxies
- Apply fairness-aware preprocessing
- Adjust decision thresholds per gender
- Collect more diverse training data

---

### 2. Equal Opportunity Difference

**Definition**: For positive cases, true positive rate (TPR) should be equal across groups.

**Formula**:
```
Equal Opportunity Diff = |TPR₀ - TPR₁|
where TPR = P(ŷ=1|y=1, A)
```

This measures: "Among qualified applicants (y=1), is each group equally likely to be approved?"

**Interpretation**:

| Difference | Status |
|-----------|--------|
| < 0.10 | ✓ Fair |
| 0.10-0.20 | ⚠ Caution |
| > 0.20 | ✗ Violation |

**Example**: 
```
Among actually creditworthy applicants (y=1):
- 95% of men are approved
- 75% of women are approved
- Difference: 20% → EQUAL OPPORTUNITY VIOLATION
```

**Mitigation**:
- Ensure balanced positive samples in training
- Investigate feature engineering quality
- Use fairness-aware ML algorithms
- Set group-specific decision thresholds

---

### 3. Disparate Impact Ratio (80% Rule)

**Definition**: Selection rate for disadvantaged group should be ≥80% of privileged group.

**Formula**:
```
DI Ratio = min_group_rate / max_group_rate ≥ 0.80
```

**Interpretation**:

| Ratio | Status | Compliance |
|-------|--------|-----------|
| ≥ 0.80 | ✓ Fair | Passes 80% rule |
| 0.60-0.80 | ✗ Violation | Legally risky |
| < 0.60 | ✗ Severe | Clear discrimination |

**Example**:
```
Approval rates:
- Urban: 80%
- Rural: 60%
DI Ratio: 60/80 = 0.75 → VIOLATION (below 0.80)
```

**Mitigation**:
- Balance training data representation
- Use stratified sampling
- Apply fairness constraints in optimization
- Monitor and adjust thresholds

---

## Sensitive Attributes Analyzed

The system checks fairness across these protected attributes:

1. **Gender**: Male, Female
2. **Marital Status**: Married, Single
3. **Age Groups** (if available): Young, Middle-aged, Senior
4. **Geographic Location**: Urban, Semi-urban, Rural

---

## Reading Fairness Reports

### Sample Fairness Report

```
╔══════════════════════════════════════════════════════════╗
║            FAIRNESS ANALYSIS SUMMARY                     ║
╚══════════════════════════════════════════════════════════╝

GENDER Analysis:
────────────────
✓ Demographic Parity: Difference = 0.08 (FAIR)
✓ Equal Opportunity: Difference = 0.12 (CAUTION)
⚠ Disparate Impact: Ratio = 0.78 (VIOLATION)
Overall: ⚠ CAUTION - Monitor gender disparities

MARITAL_STATUS Analysis:
─────────────────────────
✓ Demographic Parity: Difference = 0.05 (FAIR)
✓ Equal Opportunity: Difference = 0.06 (FAIR)
✓ Disparate Impact: Ratio = 0.92 (FAIR)
Overall: ✓ FAIR - No significant bias detected

PROPERTY_AREA Analysis:
───────────────────────
✗ Demographic Parity: Difference = 0.32 (BIAS DETECTED)
✗ Equal Opportunity: Difference = 0.28 (BIAS DETECTED)
✗ Disparate Impact: Ratio = 0.55 (VIOLATION)
Overall: ✗ SIGNIFICANT BIAS - Urgent action needed
```

---

## Bias Mitigation Strategies

### Level 1: Data-level Approaches

**1. Balanced Sampling**
```python
# Stratified sampling ensures equal representation
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y, 
    stratify=sensitive_attr,  # Balance by protected attribute
    test_size=0.2
)
```

**2. Fairness-aware Preprocessing**
```python
# Remove sensitive attributes from features (if possible)
X_processed = X.drop(['Gender', 'Marital_Status'], axis=1)

# Use carefully to avoid proxy variables
```

**3. Oversampling/Undersampling**
```python
from imblearn.over_sampling import RandomOverSampler
from imblearn.under_sampling import RandomUnderSampler

# Balance underrepresented groups
oversample = RandomOverSampler(sampling_strategy='auto')
X_balanced, y_balanced = oversample.fit_resample(X, y)
```

### Level 2: Algorithm-level Approaches

**1. Fairness-aware Optimization**
```python
from fairlearn.reductions import ExponentiatedGradient
from fairlearn.metrics import demographic_parity_difference

# Optimize for both accuracy and fairness
constraint = demographic_parity_difference()
mitigator = ExponentiatedGradient(estimator, constraints=constraint)
mitigator.fit(X_train, y_train, sensitive_features=protected_attr)
```

**2. Threshold Adjustment**
```python
# Different decision thresholds per group
thresholds = {
    'Male': 0.5,
    'Female': 0.45,  # Lower threshold for underrepresented group
    'Other': 0.48
}

def fair_predict(X, sensitive_attr, model):
    probabilities = model.predict_proba(X)[:, 1]
    predictions = []
    for prob, attr_val in zip(probabilities, sensitive_attr):
        threshold = thresholds.get(attr_val, 0.5)
        predictions.append(1 if prob > threshold else 0)
    return predictions
```

### Level 3: Post-processing Approaches

**1. Output Adjustment**
```python
# Equalize odds by adjusting predictions
from fairlearn.postprocessing import ThresholdOptimizer

post_processor = ThresholdOptimizer(
    estimator=model,
    constraints='equalized_odds'
)
post_processor.fit(X_train, y_train, sensitive_features=protected_train)
fair_predictions = post_processor.predict(X_test, sensitive_features=protected_test)
```

**2. Calibration per Group**
```python
# Calibrate predictions separately for each group
from sklearn.calibration import CalibratedClassifierCV

calibrators = {}
for group in unique_groups:
    mask = sensitive_attr == group
    calibrator = CalibratedClassifierCV(model, method='sigmoid')
    calibrator.fit(X_train[mask], y_train[mask])
    calibrators[group] = calibrator
```

---

## Implementation in Production

### Continuous Fairness Monitoring

```python
def monitor_fairness(predictions, sensitive_attrs, time_window='daily'):
    """
    Monitor fairness metrics continuously
    Alert if metrics degrade
    """
    
    metrics = {
        'timestamp': datetime.now(),
        'demographic_parity': demographic_parity_difference(
            y_true, predictions, sensitive_features=sensitive_attrs
        ),
        'equal_opportunity': equalized_odds_difference(
            y_true, predictions, sensitive_features=sensitive_attrs
        )
    }
    
    # Check against baseline
    if metrics['demographic_parity'] > THRESHOLD:
        send_alert('Demographic parity degradation detected!')
    
    return metrics
```

### Fairness Dashboard

Track these KPIs per protected group:

```json
{
  "metrics": {
    "approval_rate": 0.75,
    "demographic_parity_diff": 0.12,
    "equal_opportunity_diff": 0.08,
    "disparate_impact_ratio": 0.82,
    "positive_rate": 0.65,
    "negative_rate": 0.35,
    "accuracy": 0.81,
    "precision": 0.83,
    "recall": 0.96
  },
  "flags": ["DP_CAUTION", "DI_VIOLATION"],
  "actions": ["Monitor closely", "Adjust threshold", "Collect more data"]
}
```

---

## Legal & Regulatory Compliance

### US Context

- **Title VII Civil Rights Act**: Disparate impact illegal in employment
- **Fair Housing Act**: Redlining and discrimination in lending illegal
- **Equal Credit Opportunity Act (ECOA)**: Discrimination in credit illegal
- **80% Rule**: Disparate impact presumed if DI ratio < 0.80

### EU Context

- **GDPR Article 22**: Right to human review in automated decisions
- **Recital 71**: Meaningful information about fairness required
- **Algorithmic Accountability**: Document fairness decisions

### Implementation

```python
# Document fairness analysis as per GDPR requirements
fairness_documentation = {
    'analysis_date': datetime.now().isoformat(),
    'model_version': 'XGBoost v1.0',
    'protected_attributes': ['Gender', 'Marital_Status'],
    'metrics': fairness_results,
    'violations': ['DI_RATIO_VIOLATION'],
    'mitigation': 'Applied threshold adjustment',
    'audit_trail': audit_trail_data,
    'responsible_party': 'ML Governance Team'
}

# Store in compliance-auditable format
store_compliance_record(fairness_documentation)
```

---

## Testing & Validation

### Unit Tests for Fairness

```python
import pytest
from ml.models.fairness import FairnessAnalyzer

def test_demographic_parity():
    """Ensure DP difference < 0.15"""
    analyzer = FairnessAnalyzer()
    dp_result = analyzer.demographic_parity(y_true, y_pred, sensitive_attr)
    assert dp_result['dp_difference'] < 0.15, "Demographic Parity violation"

def test_equal_opportunity():
    """Ensure EOD difference < 0.15"""
    eop_result = analyzer.equal_opportunity(y_true, y_pred, sensitive_attr)
    assert eop_result['eod_difference'] < 0.15, "Equal Opportunity violation"

def test_disparate_impact():
    """Ensure 80% rule compliance"""
    di_result = analyzer.disparate_impact_ratio(y_pred, sensitive_attr)
    assert di_result['di_ratio'] >= 0.80, "Disparate Impact rule violation"
```

---

## Resources & References

### Academic Papers

- Bolukbasi et al. (2016): "Man is to Computer Programmer as Woman is to Homemaker?"
- Hardt et al. (2016): "Equality of Opportunity in Supervised Learning"
- Dressel & Farid (2018): "The accuracy, fairness, and limits of predictive algorithms"

### Libraries

- **FairLearn**: Microsoft's fairness toolkit
- **AI Fairness 360**: IBM's toolkit
- **Themis**: Fairness testing framework
- **Fairness Metrics**: TensorFlow fairness metrics

### Tools

- [SHAP Documentation](https://shap.readthedocs.io/)
- [FairLearn Documentation](https://fairlearn.org/)
- [Fairness and ML - Berkeley AI Course](https://fairmlbook.org/)

---

**Last Updated**: April 2026  
**Version**: 1.0.0  
**Reviewed By**: ML Ethics Committee
