"""
Fairness & Bias Detection Module
Analyzes potential bias in loan predictions and suggests mitigation strategies
"""
import pandas as pd
import numpy as np
from fairlearn.metrics import demographic_parity_difference, equalized_odds_difference
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Tuple, Any

class FairnessAnalyzer:
    """Analyzes and detects bias in loan predictions"""
    
    def __init__(self):
        self.fairness_metrics = {}
        self.bias_report = {}
        
    def demographic_parity(self, y_true: np.ndarray, y_pred: np.ndarray, 
                          sensitive_attr: pd.Series) -> Dict[str, float]:
        """
        Calculate demographic parity across sensitive attributes
        
        Demographic Parity: P(ŷ=1|A=0) = P(ŷ=1|A=1)
        Perfect fairness when difference = 0
        """
        groups = sensitive_attr.unique()
        approval_rates = {}
        
        print("\n" + "="*60)
        print("DEMOGRAPHIC PARITY ANALYSIS")
        print("="*60)
        
        for group in groups:
            mask = sensitive_attr == group
            group_approval_rate = np.mean(y_pred[mask])
            approval_rates[str(group)] = group_approval_rate
            print(f"Group '{group}': {group_approval_rate:.4f} approval rate")
        
        # Calculate demographic parity difference
        rates = list(approval_rates.values())
        dp_difference = max(rates) - min(rates)
        print(f"\nDemographic Parity Difference: {dp_difference:.4f}")
        print(f"Status: {'✓ FAIR' if dp_difference < 0.1 else '✗ BIAS DETECTED' if dp_difference > 0.2 else '⚠ CAUTION'}")
        
        return {
            'approval_rates': approval_rates,
            'dp_difference': dp_difference,
            'is_fair': dp_difference < 0.1
        }
    
    def equal_opportunity(self, y_true: np.ndarray, y_pred: np.ndarray,
                         sensitive_attr: pd.Series) -> Dict[str, float]:
        """
        Calculate Equal Opportunity across sensitive attributes
        
        Equal Opportunity: For positive labels, P(ŷ=1|y=1, A=0) = P(ŷ=1|y=1, A=1)
        """
        groups = sensitive_attr.unique()
        tpr_rates = {}
        
        print("\n" + "="*60)
        print("EQUAL OPPORTUNITY ANALYSIS")
        print("="*60)
        
        for group in groups:
            mask = (sensitive_attr == group) & (y_true == 1)
            if mask.sum() > 0:
                tpr = np.mean(y_pred[mask])
                tpr_rates[str(group)] = tpr
                print(f"Group '{group}': {tpr:.4f} TPR (True Positive Rate)")
            else:
                tpr_rates[str(group)] = np.nan
                print(f"Group '{group}': No positive samples")
        
        # Calculate EOD difference
        valid_rates = [v for v in tpr_rates.values() if not np.isnan(v)]
        if len(valid_rates) >= 2:
            eod_difference = max(valid_rates) - min(valid_rates)
            print(f"\nEqual Opportunity Difference: {eod_difference:.4f}")
            print(f"Status: {'✓ FAIR' if eod_difference < 0.1 else '✗ BIAS DETECTED' if eod_difference > 0.2 else '⚠ CAUTION'}")
        else:
            eod_difference = np.nan
            print("\nCannot calculate EOD (insufficient positive samples)")
        
        return {
            'tpr_rates': tpr_rates,
            'eod_difference': eod_difference,
            'is_fair': eod_difference < 0.1 if not np.isnan(eod_difference) else None
        }
    
    def disparate_impact_ratio(self, y_pred: np.ndarray, 
                              sensitive_attr: pd.Series) -> Dict[str, Any]:
        """
        Calculate Disparate Impact Ratio (80% Rule)
        
        Selection Rate Ratio: SR_unprivileged / SR_privileged
        Fair when ratio >= 0.8
        """
        groups = sorted(sensitive_attr.unique())
        selection_rates = {}
        
        print("\n" + "="*60)
        print("DISPARATE IMPACT RATIO (80% RULE)")
        print("="*60)
        
        for group in groups:
            mask = sensitive_attr == group
            sr = np.mean(y_pred[mask])
            selection_rates[str(group)] = sr
            print(f"Group '{group}': {sr:.4f} selection rate")
        
        rates = list(selection_rates.values())
        if len(rates) >= 2:
            di_ratio = min(rates) / max(rates)
            print(f"\nDisparate Impact Ratio: {di_ratio:.4f}")
            print(f"Status: {'✓ FAIR (≥0.8)' if di_ratio >= 0.80 else '✗ VIOLATION (<0.8)'}")
        else:
            di_ratio = np.nan
        
        return {
            'selection_rates': selection_rates,
            'di_ratio': di_ratio,
            'is_fair': di_ratio >= 0.80 if not np.isnan(di_ratio) else None
        }
    
    def analyze_fairness(self, y_true: np.ndarray, y_pred: np.ndarray,
                        sensitive_attr: pd.Series, attr_name: str) -> Dict[str, Any]:
        """Comprehensive fairness analysis across sensitive attribute"""
        
        print(f"\n{'#'*60}")
        print(f"FAIRNESS ANALYSIS: {attr_name}")
        print(f"{'#'*60}")
        
        dp_results = self.demographic_parity(y_true, y_pred, sensitive_attr)
        eop_results = self.equal_opportunity(y_true, y_pred, sensitive_attr)
        di_results = self.disparate_impact_ratio(y_pred, sensitive_attr)
        
        fairness_summary = {
            'attribute': attr_name,
            'demographic_parity': dp_results,
            'equal_opportunity': eop_results,
            'disparate_impact': di_results,
            'overall_bias_level': self._calculate_overall_bias(dp_results, eop_results, di_results)
        }
        
        return fairness_summary
    
    def _calculate_overall_bias(self, dp: Dict, eop: Dict, di: Dict) -> str:
        """Calculate overall bias level based on multiple metrics"""
        bias_flags = 0
        
        if not dp['is_fair']:
            bias_flags += 1
        if eop['is_fair'] is False:
            bias_flags += 1
        if di['is_fair'] is False:
            bias_flags += 1
        
        if bias_flags == 0:
            return "✓ FAIR"
        elif bias_flags == 1:
            return "⚠ CAUTION"
        else:
            return "✗ SIGNIFICANT BIAS"
    
    def plot_fairness_comparison(self, fairness_results: Dict[str, Any], 
                                save_path: str = None):
        """Visualize fairness metrics across sensitive attributes"""
        
        attributes = []
        dp_diffs = []
        eop_diffs = []
        di_ratios = []
        
        for attr, results in fairness_results.items():
            attributes.append(attr)
            dp_diffs.append(results['demographic_parity']['dp_difference'])
            eop_diffs.append(results['equal_opportunity'].get('eod_difference', 0))
            di_ratios.append(results['disparate_impact'].get('di_ratio', 0))
        
        fig, axes = plt.subplots(1, 3, figsize=(16, 5))
        
        # Demographic Parity
        axes[0].barh(attributes, dp_diffs, color=['green' if x < 0.1 else 'orange' if x < 0.2 else 'red' for x in dp_diffs])
        axes[0].axvline(x=0.1, color='red', linestyle='--', label='Fair threshold')
        axes[0].set_xlabel('DP Difference')
        axes[0].set_title('Demographic Parity Difference')
        axes[0].legend()
        
        # Equal Opportunity
        valid_eop = [(attr, val) for attr, val in zip(attributes, eop_diffs) if not np.isnan(val)]
        if valid_eop:
            attrs, vals = zip(*valid_eop)
            axes[1].barh(attrs, vals, color=['green' if x < 0.1 else 'orange' if x < 0.2 else 'red' for x in vals])
            axes[1].axvline(x=0.1, color='red', linestyle='--', label='Fair threshold')
            axes[1].set_xlabel('EOD Difference')
            axes[1].set_title('Equal Opportunity Difference')
            axes[1].legend()
        
        # Disparate Impact
        valid_di = [(attr, val) for attr, val in zip(attributes, di_ratios) if not np.isnan(val)]
        if valid_di:
            attrs, vals = zip(*valid_di)
            axes[2].barh(attrs, vals, color=['green' if x >= 0.80 else 'red' for x in vals])
            axes[2].axvline(x=0.80, color='red', linestyle='--', label='Fair threshold (0.80)')
            axes[2].set_xlabel('Disparate Impact Ratio')
            axes[2].set_title('Disparate Impact (80% Rule)')
            axes[2].legend()
        
        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def generate_bias_mitigation_report(self, fairness_results: Dict[str, Any]) -> str:
        """Generate recommendations for bias mitigation"""
        
        report = """
╔══════════════════════════════════════════════════════════╗
║            BIAS MITIGATION RECOMMENDATIONS               ║
╚══════════════════════════════════════════════════════════╝

"""
        
        for attr, results in fairness_results.items():
            report += f"\n{'─'*60}\n"
            report += f"Sensitive Attribute: {attr}\n"
            report += f"Overall Bias Level: {results['overall_bias_level']}\n"
            report += f"{'─'*60}\n"
            
            # DP Recommendations
            dp_diff = results['demographic_parity']['dp_difference']
            if dp_diff > 0.2:
                report += f"\n⚠ DEMOGRAPHIC PARITY VIOLATION (Difference: {dp_diff:.4f})\n"
                report += "  Recommendations:\n"
                report += "  • Re-examine feature engineering for hidden proxies of sensitive attributes\n"
                report += "  • Consider fairness-aware preprocessing techniques\n"
                report += "  • Adjust decision threshold for disadvantaged groups\n"
            
            # EOD Recommendations
            eod_diff = results['equal_opportunity'].get('eod_difference')
            if eod_diff and eod_diff > 0.2:
                report += f"\n⚠ EQUAL OPPORTUNITY VIOLATION (Difference: {eod_diff:.4f})\n"
                report += "  Recommendations:\n"
                report += "  • Ensure accurate labeling in training data\n"
                report += "  • Balance representation of positive outcomes across groups\n"
            
            # DI Recommendations
            di_ratio = results['disparate_impact'].get('di_ratio')
            if di_ratio and di_ratio < 0.80:
                report += f"\n⚠ DISPARATE IMPACT VIOLATION (Ratio: {di_ratio:.4f})\n"
                report += "  Recommendations:\n"
                report += "  • Apply fairness constraints in model optimization\n"
                report += "  • Use reweighting or resampling techniques\n"
                report += f"  • Target approval rate difference < {0.25:.0%}\n"
        
        report += "\n" + "="*60 + "\n"
        report += "GENERAL MITIGATION STRATEGIES:\n"
        report += "="*60 + "\n"
        report += """
1. DATA PREPROCESSING:
   • Remove sensitive attributes (if not needed for fairness analysis)
   • Remove correlated proxy variables
   • Balance underrepresented groups in training data

2. ALGORITHM LEVEL:
   • Use fairness-aware ML libraries (FairLearn, AI Fairness 360)
   • Adjust decision thresholds per group
   • Use group-aware decision boundaries

3. POST-PROCESSING:
   • Adjust predictions to meet fairness constraints
   • Set different acceptance thresholds by group
   • Monitor predictions for drift in fairness metrics

4. MONITORING & GOVERNANCE:
   • Continuously monitor fairness metrics in production
   • Create fairness dashboards for stakeholders
   • Establish appeal processes for rejected applications
   • Regular audits by external parties
"""
        
        return report
    
    def save_fairness_report(self, fairness_results: Dict, 
                            save_dir: str = '../results/'):
        """Save fairness analysis results"""
        import json
        import os
        
        os.makedirs(save_dir, exist_ok=True)
        
        # Convert to serializable format
        results_serialized = {}
        for attr, metrics in fairness_results.items():
            results_serialized[attr] = {
                'demographic_parity': {
                    'approval_rates': {k: float(v) for k, v in metrics['demographic_parity']['approval_rates'].items()},
                    'dp_difference': float(metrics['demographic_parity']['dp_difference']),
                    'is_fair': bool(metrics['demographic_parity']['is_fair'])
                },
                'equal_opportunity': {
                    'tpr_rates': {k: float(v) if not np.isnan(v) else None 
                                 for k, v in metrics['equal_opportunity']['tpr_rates'].items()},
                    'eod_difference': float(metrics['equal_opportunity'].get('eod_difference', np.nan)) if not np.isnan(metrics['equal_opportunity'].get('eod_difference', np.nan)) else None,
                    'is_fair': bool(metrics['equal_opportunity']['is_fair']) if metrics['equal_opportunity']['is_fair'] is not None else None
                },
                'disparate_impact': {
                    'selection_rates': {k: float(v) for k, v in metrics['disparate_impact']['selection_rates'].items()},
                    'di_ratio': float(metrics['disparate_impact'].get('di_ratio', np.nan)) if not np.isnan(metrics['disparate_impact'].get('di_ratio', np.nan)) else None,
                    'is_fair': bool(metrics['disparate_impact']['is_fair']) if metrics['disparate_impact']['is_fair'] is not None else None
                },
                'overall_bias_level': metrics['overall_bias_level']
            }
        
        with open(f'{save_dir}fairness_report.json', 'w') as f:
            json.dump(results_serialized, f, indent=2)
        
        print(f"✓ Fairness report saved to {save_dir}fairness_report.json")


def analyze_model_fairness(y_true: np.ndarray, y_pred: np.ndarray,
                          sensitive_attributes: pd.DataFrame) -> Dict[str, Any]:
    """Complete fairness analysis pipeline"""
    
    analyzer = FairnessAnalyzer()
    fairness_results = {}
    
    for attr_name in sensitive_attributes.columns:
        fairness_results[attr_name] = analyzer.analyze_fairness(
            y_true, y_pred, sensitive_attributes[attr_name], attr_name
        )
    
    print("\n" + "="*60)
    print("FAIRNESS ANALYSIS SUMMARY")
    print("="*60)
    for attr, results in fairness_results.items():
        print(f"\n{attr}: {results['overall_bias_level']}")
    
    return fairness_results
