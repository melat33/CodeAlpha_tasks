"""
Machine Learning service for model inference
"""

import joblib
import numpy as np
import pandas as pd
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class MLService:
    """Service for loading ML models and making predictions"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.features = {}
        self.load_models()
    
    def load_models(self):
        """Load all saved models"""
        model_path = Path(__file__).parent.parent / 'ml_models'
        
        # Load heart disease models
        try:
            self.models['heart'] = joblib.load(model_path / 'heart' / 'model.pkl')
            self.scalers['heart'] = joblib.load(model_path / 'heart' / 'scaler.pkl')
            self.features['heart'] = joblib.load(model_path / 'heart' / 'features.pkl')
            logger.info("✅ Heart disease model loaded")
        except Exception as e:
            logger.error(f"Failed to load heart model: {e}")
        
        # Load diabetes models
        try:
            self.models['diabetes'] = joblib.load(model_path / 'diabetes' / 'model.pkl')
            self.scalers['diabetes'] = joblib.load(model_path / 'diabetes' / 'scaler.pkl')
            self.features['diabetes'] = joblib.load(model_path / 'diabetes' / 'features.pkl')
            logger.info("✅ Diabetes model loaded")
        except Exception as e:
            logger.error(f"Failed to load diabetes model: {e}")
        
        # Load cancer models
        try:
            self.models['cancer'] = joblib.load(model_path / 'cancer' / 'model.pkl')
            self.scalers['cancer'] = joblib.load(model_path / 'cancer' / 'scaler.pkl')
            self.features['cancer'] = joblib.load(model_path / 'cancer' / 'features.pkl')
            logger.info("✅ Cancer model loaded")
        except Exception as e:
            logger.error(f"Failed to load cancer model: {e}")
    
    def predict_heart(self, data):
        """Predict heart disease"""
        try:
            # Convert to DataFrame
            df = pd.DataFrame([data])
            df = df[self.features['heart']]  # Ensure correct order
            
            # Scale features
            scaled = self.scalers['heart'].transform(df)
            
            # Make prediction
            pred = self.models['heart'].predict(scaled)[0]
            proba = self.models['heart'].predict_proba(scaled)[0]
            
            # Determine risk level
            risk_prob = proba[1] if pred == 1 else proba[0]
            if risk_prob >= 0.7:
                risk_level = "High"
            elif risk_prob >= 0.4:
                risk_level = "Medium"
            else:
                risk_level = "Low"
            
            return {
                'prediction': int(pred),
                'probability': float(risk_prob),
                'risk_level': risk_level,
                'probabilities': {
                    'no_disease': float(proba[0]),
                    'disease': float(proba[1])
                }
            }
        except Exception as e:
            logger.error(f"Heart prediction error: {e}")
            raise
    
    def predict_diabetes(self, data):
        """Predict diabetes"""
        try:
            df = pd.DataFrame([data])
            df = df[self.features['diabetes']]
            scaled = self.scalers['diabetes'].transform(df)
            pred = self.models['diabetes'].predict(scaled)[0]
            proba = self.models['diabetes'].predict_proba(scaled)[0]
            
            risk_prob = proba[1] if pred == 1 else proba[0]
            risk_level = "High" if risk_prob >= 0.7 else "Medium" if risk_prob >= 0.4 else "Low"
            
            return {
                'prediction': int(pred),
                'probability': float(risk_prob),
                'risk_level': risk_level,
                'probabilities': {
                    'no_diabetes': float(proba[0]),
                    'diabetes': float(proba[1])
                }
            }
        except Exception as e:
            logger.error(f"Diabetes prediction error: {e}")
            raise
    
    def predict_cancer(self, data):
        """Predict breast cancer"""
        try:
            df = pd.DataFrame([data])
            df = df[self.features['cancer']]
            scaled = self.scalers['cancer'].transform(df)
            pred = self.models['cancer'].predict(scaled)[0]
            proba = self.models['cancer'].predict_proba(scaled)[0]
            
            risk_prob = proba[1] if pred == 1 else proba[0]
            risk_level = "High" if risk_prob >= 0.7 else "Medium" if risk_prob >= 0.4 else "Low"
            
            return {
                'prediction': int(pred),
                'probability': float(risk_prob),
                'risk_level': risk_level,
                'probabilities': {
                    'benign': float(proba[0]),
                    'malignant': float(proba[1])
                }
            }
        except Exception as e:
            logger.error(f"Cancer prediction error: {e}")
            raise
    
    def get_model_info(self, disease_type):
        """Get model information"""
        if disease_type not in self.models:
            return None
        
        model = self.models[disease_type]
        return {
            'type': type(model).__name__,
            'features': self.features[disease_type],
            'n_features': len(self.features[disease_type])
        }