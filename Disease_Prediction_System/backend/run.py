from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import joblib
import numpy as np
import pandas as pd
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'Disease Prediction API'
    })

# Heart disease prediction endpoint
@app.route('/api/predict/heart', methods=['POST'])
def predict_heart():
    try:
        data = request.get_json()
        
        # Mock prediction (replace with actual model later)
        prediction = 1 if data.get('age', 50) > 50 else 0
        probability = 0.85 if prediction == 1 else 0.25
        
        risk_level = 'High' if probability > 0.7 else 'Medium' if probability > 0.4 else 'Low'
        
        return jsonify({
            'success': True,
            'prediction': prediction,
            'probability': probability,
            'risk_level': risk_level,
            'message': 'Prediction completed successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Diabetes prediction endpoint
@app.route('/api/predict/diabetes', methods=['POST'])
def predict_diabetes():
    try:
        data = request.get_json()
        
        # Mock prediction
        glucose = data.get('glucose', 100)
        prediction = 1 if glucose > 140 else 0
        probability = 0.82 if prediction == 1 else 0.18
        
        risk_level = 'High' if probability > 0.7 else 'Medium' if probability > 0.4 else 'Low'
        
        return jsonify({
            'success': True,
            'prediction': prediction,
            'probability': probability,
            'risk_level': risk_level
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Cancer prediction endpoint
@app.route('/api/predict/cancer', methods=['POST'])
def predict_cancer():
    try:
        data = request.get_json()
        
        # Mock prediction
        radius = data.get('radius_mean', 15)
        prediction = 1 if radius > 18 else 0
        probability = 0.91 if prediction == 1 else 0.09
        
        risk_level = 'High' if probability > 0.7 else 'Medium' if probability > 0.4 else 'Low'
        
        return jsonify({
            'success': True,
            'prediction': prediction,
            'probability': probability,
            'risk_level': risk_level,
            'tumor_type': 'Malignant' if prediction == 1 else 'Benign'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)