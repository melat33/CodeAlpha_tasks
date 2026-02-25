import shap
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from src.utils.logger import setup_logger

logger = setup_logger('model_explainer')

def explain_with_shap(model, X_test, feature_names, model_type='tree'):
    """Generate SHAP explanations for model predictions"""
    
    logger.info("Generating SHAP explanations...")
    
    if model_type == 'tree':
        explainer = shap.TreeExplainer(model)
    else:
        explainer = shap.KernelExplainer(model.predict_proba, X_test[:100])
    
    shap_values = explainer.shap_values(X_test[:100])
    
    # Summary plot
    plt.figure(figsize=(12, 8))
    shap.summary_plot(shap_values, X_test[:100], 
                     feature_names=feature_names,
                     show=False)
    plt.title('SHAP Feature Impact', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig('reports/shap_summary.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Individual prediction explanation
    shap.force_plot(explainer.expected_value, 
                   shap_values[0] if isinstance(shap_values, list) else shap_values[0,:],
                   X_test[0,:],
                   feature_names=feature_names,
                   matplotlib=True,
                   show=False)
    plt.savefig('reports/shap_force.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    logger.info("SHAP explanations saved")
    return explainer, shap_values