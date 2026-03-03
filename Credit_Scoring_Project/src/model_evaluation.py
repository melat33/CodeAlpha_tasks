"""Model evaluation functions for credit scoring project"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (accuracy_score, precision_score, recall_score, 
                           f1_score, roc_auc_score, confusion_matrix,
                           classification_report, roc_curve, auc)
import warnings
warnings.filterwarnings('ignore')

def evaluate_model(model, X_test, y_test, model_name):
    """Comprehensive model evaluation"""
    
    # Predictions
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    # Metrics
    metrics = {
        'Model': model_name,
        'Accuracy': accuracy_score(y_test, y_pred),
        'Precision': precision_score(y_test, y_pred),
        'Recall': recall_score(y_test, y_pred),
        'F1-Score': f1_score(y_test, y_pred),
        'ROC-AUC': roc_auc_score(y_test, y_pred_proba)
    }
    
    # Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    
    return metrics, cm, y_pred, y_pred_proba

def plot_confusion_matrix(cm, model_name):
    """Plot confusion matrix"""
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=['Predicted Good', 'Predicted Bad'],
                yticklabels=['Actual Good', 'Actual Bad'])
    plt.title(f'Confusion Matrix - {model_name}')
    plt.ylabel('Actual')
    plt.xlabel('Predicted')
    plt.show()

def plot_roc_curves(models_dict, X_test, y_test):
    """Plot ROC curves for multiple models"""
    plt.figure(figsize=(10, 8))
    
    for model_name, model in models_dict.items():
        y_pred_proba = model.predict_proba(X_test)[:, 1]
        fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
        roc_auc = auc(fpr, tpr)
        
        plt.plot(fpr, tpr, label=f'{model_name} (AUC = {roc_auc:.3f})', linewidth=2)
    
    plt.plot([0, 1], [0, 1], 'k--', label='Random Classifier')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curves Comparison')
    plt.legend(loc='lower right')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

def plot_feature_importance(model, feature_names, model_name):
    """Plot feature importance for tree-based models"""
    if hasattr(model, 'feature_importances_'):
        importances = model.feature_importances_
        indices = np.argsort(importances)[::-1]
        
        plt.figure(figsize=(10, 6))
        plt.title(f'Feature Importance - {model_name}')
        plt.bar(range(len(importances)), importances[indices])
        plt.xticks(range(len(importances)), 
                  [feature_names[i] for i in indices], 
                  rotation=45, ha='right')
        plt.xlabel('Features')
        plt.ylabel('Importance')
        plt.tight_layout()
        plt.show()
        
        # Print feature importance
        print(f"\nTop 10 Important Features - {model_name}:")
        for i, idx in enumerate(indices[:10]):
            print(f"{i+1}. {feature_names[idx]}: {importances[idx]:.4f}")
    else:
        print(f"Model {model_name} doesn't have feature_importances_ attribute")

def generate_credit_score(model, X, scaler, feature_names):
    """Generate credit scores from model probabilities"""
    # Get probability of being good credit
    proba = model.predict_proba(X)[:, 1]
    
    # Convert to credit score (300-850 range)
    # Higher probability of good credit = higher score
    credit_scores = 300 + (proba * 550)
    
    # Risk categories
    risk_categories = pd.cut(credit_scores, 
                             bins=[0, 580, 670, 740, 800, 851],
                             labels=['Very Poor', 'Fair', 'Good', 'Very Good', 'Excellent'])
    
    return credit_scores, risk_categories

def print_classification_report(model, X_test, y_test, model_name):
    """Print detailed classification report"""
    y_pred = model.predict(X_test)
    print(f"\nClassification Report - {model_name}")
    print("="*50)
    print(classification_report(y_test, y_pred, 
                               target_names=['Good Credit', 'Bad Credit']))