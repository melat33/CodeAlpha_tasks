from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import GridSearchCV, cross_val_score
import joblib
import numpy as np
import logging

logger = logging.getLogger(__name__)

def train_logistic_regression(X_train, y_train):
    """Train Logistic Regression with hyperparameter tuning"""
    param_grid = {
        'C': [0.01, 0.1, 1, 10],
        'penalty': ['l1', 'l2'],
        'solver': ['liblinear']
    }
    
    lr = LogisticRegression(random_state=42, max_iter=1000)
    grid_search = GridSearchCV(lr, param_grid, cv=5, scoring='roc_auc', n_jobs=-1)
    grid_search.fit(X_train, y_train)
    
    logger.info(f"Best Logistic Regression parameters: {grid_search.best_params_}")
    logger.info(f"Best CV Score: {grid_search.best_score_:.4f}")
    
    return grid_search.best_estimator_

def train_decision_tree(X_train, y_train):
    """Train Decision Tree with hyperparameter tuning"""
    param_grid = {
        'max_depth': [3, 5, 7, 10, 15],
        'min_samples_split': [2, 5, 10, 20],
        'min_samples_leaf': [1, 2, 5, 10],
        'criterion': ['gini', 'entropy']
    }
    
    dt = DecisionTreeClassifier(random_state=42)
    grid_search = GridSearchCV(dt, param_grid, cv=5, scoring='roc_auc', n_jobs=-1)
    grid_search.fit(X_train, y_train)
    
    logger.info(f"Best Decision Tree parameters: {grid_search.best_params_}")
    logger.info(f"Best CV Score: {grid_search.best_score_:.4f}")
    
    return grid_search.best_estimator_

def train_random_forest(X_train, y_train):
    """Train Random Forest with hyperparameter tuning"""
    param_grid = {
        'n_estimators': [100, 200, 300],
        'max_depth': [5, 10, 15, None],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4],
        'max_features': ['sqrt', 'log2']
    }
    
    rf = RandomForestClassifier(random_state=42, n_jobs=-1)
    grid_search = GridSearchCV(rf, param_grid, cv=5, scoring='roc_auc', n_jobs=-1, verbose=1)
    grid_search.fit(X_train, y_train)
    
    logger.info(f"Best Random Forest parameters: {grid_search.best_params_}")
    logger.info(f"Best CV Score: {grid_search.best_score_:.4f}")
    
    return grid_search.best_estimator_

def train_gradient_boosting(X_train, y_train):
    """Train Gradient Boosting with hyperparameter tuning"""
    param_grid = {
        'n_estimators': [100, 200],
        'max_depth': [3, 5, 7],
        'learning_rate': [0.01, 0.1, 0.2],
        'subsample': [0.8, 1.0]
    }
    
    gb = GradientBoostingClassifier(random_state=42)
    grid_search = GridSearchCV(gb, param_grid, cv=5, scoring='roc_auc', n_jobs=-1)
    grid_search.fit(X_train, y_train)
    
    logger.info(f"Best Gradient Boosting parameters: {grid_search.best_params_}")
    logger.info(f"Best CV Score: {grid_search.best_score_:.4f}")
    
    return grid_search.best_estimator_

def save_model(model, filepath):
    """Save trained model"""
    joblib.dump(model, filepath)
    logger.info(f"Model saved to {filepath}")

def load_model(filepath):
    """Load trained model"""
    return joblib.load(filepath)