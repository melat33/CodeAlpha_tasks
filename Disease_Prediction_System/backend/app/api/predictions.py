"""
Prediction API endpoints
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.ml_service import MLService
from app.services.prediction_service import PredictionService
from app.services.explanation_service import ExplanationService
from app.models import Prediction, db
from app.utils.validators import validate_heart_data, validate_diabetes_data, validate_cancer_data
from app.utils.decorators import rate_limit
import logging

predictions_bp = Blueprint('predictions', __name__)
logger = logging.getLogger(__name__)

ml_service = MLService()
prediction_service = PredictionService()
explanation_service = ExplanationService()

@predictions_bp.route('/heart', methods=['POST'])
@jwt_required()
@rate_limit(limit=100, period=3600)  # 100 requests per hour
def predict_heart():
    """
    Predict heart disease
    """
    try:
        data = request.get_json()
        
        # Validate input data
        is_valid, errors = validate_heart_data(data)
        if not is_valid:
            return jsonify({'error': 'Validation failed', 'details': errors}), 400
        
        # Make prediction
        prediction = ml_service.predict_heart(data)
        
        # Get SHAP explanation
        explanation = explanation_service.get_shap_values('heart', data)
        
        # Save to database
        user_id = get_jwt_identity()
        prediction_record = Prediction(
            user_id=user_id,
            disease_type='heart',
            input_data=data,
            result=prediction['prediction'],
            probability=prediction['probability'],
            explanation=explanation
        )
        db.session.add(prediction_record)
        db.session.commit()
        
        # Log prediction
        logger.info(f"Heart disease prediction made by user {user_id}: {prediction}")
        
        return jsonify({
            'success': True,
            'prediction': prediction['prediction'],
            'probability': prediction['probability'],
            'risk_level': prediction['risk_level'],
            'explanation': explanation,
            'id': prediction_record.id,
            'timestamp': prediction_record.created_at.isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return jsonify({'error': 'Prediction failed', 'message': str(e)}), 500

@predictions_bp.route('/diabetes', methods=['POST'])
@jwt_required()
@rate_limit(limit=100, period=3600)
def predict_diabetes():
    """
    Predict diabetes
    """
    try:
        data = request.get_json()
        
        # Validate input data
        is_valid, errors = validate_diabetes_data(data)
        if not is_valid:
            return jsonify({'error': 'Validation failed', 'details': errors}), 400
        
        # Make prediction
        prediction = ml_service.predict_diabetes(data)
        
        # Get SHAP explanation
        explanation = explanation_service.get_shap_values('diabetes', data)
        
        # Save to database
        user_id = get_jwt_identity()
        prediction_record = Prediction(
            user_id=user_id,
            disease_type='diabetes',
            input_data=data,
            result=prediction['prediction'],
            probability=prediction['probability'],
            explanation=explanation
        )
        db.session.add(prediction_record)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'prediction': prediction['prediction'],
            'probability': prediction['probability'],
            'risk_level': prediction['risk_level'],
            'explanation': explanation,
            'id': prediction_record.id,
            'timestamp': prediction_record.created_at.isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return jsonify({'error': 'Prediction failed', 'message': str(e)}), 500

@predictions_bp.route('/cancer', methods=['POST'])
@jwt_required()
@rate_limit(limit=100, period=3600)
def predict_cancer():
    """
    Predict breast cancer
    """
    try:
        data = request.get_json()
        
        # Validate input data
        is_valid, errors = validate_cancer_data(data)
        if not is_valid:
            return jsonify({'error': 'Validation failed', 'details': errors}), 400
        
        # Make prediction
        prediction = ml_service.predict_cancer(data)
        
        # Get SHAP explanation
        explanation = explanation_service.get_shap_values('cancer', data)
        
        # Save to database
        user_id = get_jwt_identity()
        prediction_record = Prediction(
            user_id=user_id,
            disease_type='cancer',
            input_data=data,
            result=prediction['prediction'],
            probability=prediction['probability'],
            explanation=explanation
        )
        db.session.add(prediction_record)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'prediction': prediction['prediction'],
            'probability': prediction['probability'],
            'risk_level': prediction['risk_level'],
            'explanation': explanation,
            'id': prediction_record.id,
            'timestamp': prediction_record.created_at.isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return jsonify({'error': 'Prediction failed', 'message': str(e)}), 500

@predictions_bp.route('/history', methods=['GET'])
@jwt_required()
def get_prediction_history():
    """
    Get user's prediction history
    """
    try:
        user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        disease_type = request.args.get('disease_type')
        
        query = Prediction.query.filter_by(user_id=user_id)
        
        if disease_type:
            query = query.filter_by(disease_type=disease_type)
        
        pagination = query.order_by(Prediction.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        predictions = [{
            'id': p.id,
            'disease_type': p.disease_type,
            'input_data': p.input_data,
            'result': p.result,
            'probability': p.probability,
            'risk_level': 'High' if p.probability > 0.7 else 'Medium' if p.probability > 0.4 else 'Low',
            'explanation': p.explanation,
            'created_at': p.created_at.isoformat()
        } for p in pagination.items]
        
        return jsonify({
            'predictions': predictions,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        logger.error(f"History fetch error: {str(e)}")
        return jsonify({'error': 'Failed to fetch history', 'message': str(e)}), 500

@predictions_bp.route('/<int:prediction_id>', methods=['GET'])
@jwt_required()
def get_prediction_detail(prediction_id):
    """
    Get detailed prediction by ID
    """
    try:
        user_id = get_jwt_identity()
        prediction = Prediction.query.filter_by(
            id=prediction_id, user_id=user_id
        ).first_or_404()
        
        return jsonify({
            'id': prediction.id,
            'disease_type': prediction.disease_type,
            'input_data': prediction.input_data,
            'result': prediction.result,
            'probability': prediction.probability,
            'explanation': prediction.explanation,
            'created_at': prediction.created_at.isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Prediction detail fetch error: {str(e)}")
        return jsonify({'error': 'Failed to fetch prediction', 'message': str(e)}), 500