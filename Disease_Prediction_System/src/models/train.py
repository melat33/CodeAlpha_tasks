import numpy as np
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb
from src.utils.logger import setup_logger
from src.utils.metrics import calculate_metrics

logger = setup_logger('model_trainer')

def get_model_configs():
    """Get model configurations for training"""
    return {
        'Logistic Regression': {
            'model': LogisticRegression(random_state=42, max_iter=1000),
            'params': {
                'C': [0.01, 0.1, 1, 10],
                'solver': ['lbfgs', 'liblinear'],
                'class_weight': ['balanced', None]
            }
        },
        'SVM': {
            'model': SVC(probability=True, random_state=42),
            'params': {
                'C': [0.1, 1, 10],
                'gamma': ['scale', 'auto', 0.1, 1],
                'kernel': ['rbf', 'poly']
            }
        },
        'Random Forest': {
            'model': RandomForestClassifier(random_state=42),
            'params': {
                'n_estimators': [50, 100, 200],
                'max_depth': [5, 10, None],
                'min_samples_split': [2, 5, 10],
                'class_weight': ['balanced', None]
            }
        },
        'XGBoost': {
            'model': xgb.XGBClassifier(random_state=42, eval_metric='logloss'),
            'params': {
                'n_estimators': [50, 100, 200],
                'max_depth': [3, 5, 7],
                'learning_rate': [0.01, 0.1, 0.3],
                'subsample': [0.8, 1.0]
            }
        }
    }

def train_models(X_train, y_train, X_test, y_test, cv_folds=5):
    """Train multiple models with hyperparameter tuning"""
    
    models = get_model_configs()
    results = {}
    best_models = {}
    
    for name, config in models.items():
        logger.info(f"Training {name}...")
        
        # Grid search with cross-validation
        grid_search = GridSearchCV(
            config['model'],
            config['params'],
            cv=StratifiedKFold(cv_folds, shuffle=True, random_state=42),
            scoring='f1',
            n_jobs=-1,
            verbose=0
        )
        
        grid_search.fit(X_train, y_train)
        
        # Best model
        best_model = grid_search.best_estimator_
        best_models[name] = best_model
        
        # Predictions
        y_pred = best_model.predict(X_test)
        y_pred_proba = best_model.predict_proba(X_test)[:, 1]
        
        # Calculate metrics
        metrics = calculate_metrics(y_test, y_pred, y_pred_proba)
        metrics['best_params'] = grid_search.best_params_
        metrics['best_cv_score'] = grid_search.best_score_
        
        results[name] = metrics
        
        logger.info(f"{name} - F1: {metrics['f1']:.4f}, Accuracy: {metrics['accuracy']:.4f}")
    
    return best_models, results