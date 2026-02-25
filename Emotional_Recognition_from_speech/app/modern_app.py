# app/modern_app.py
import os
import sys
import numpy as np
from flask import Flask, render_template, request, jsonify, send_from_directory
import joblib
import librosa
import warnings
warnings.filterwarnings('ignore')

# Add src to path
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

try:
    from config import Config
    from preprocessor import AudioPreprocessor
    from feature_extractor import FeatureExtractor
except:
    class Config:
        SAMPLE_RATE = 22050
        DURATION = 3
        N_MFCC = 40
        MONO = True
    Config = Config()

import tensorflow as tf

app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')

config = Config()
if not hasattr(config, 'MONO'):
    config.MONO = True

# Load emotion model
model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'models', 'emotion_model.h5'))
scaler_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'models', 'scaler.pkl'))

model = None
scaler = None
preprocessor = None
extractor = None

if os.path.exists(model_path) and os.path.exists(scaler_path):
    try:
        model = tf.keras.models.load_model(model_path)
        scaler = joblib.load(scaler_path)
        preprocessor = AudioPreprocessor(config)
        extractor = FeatureExtractor(config)
        print("✅ Emotion model loaded successfully")
    except Exception as e:
        print(f"❌ Error loading emotion model: {e}")

# Gender detection function
def detect_gender(audio, sr=22050):
    """
    Detect gender from audio features
    Returns: 'male', 'female', or 'unknown'
    """
    try:
        # Extract pitch-related features
        pitches, magnitudes = librosa.piptrack(y=audio, sr=sr)
        pitches = pitches[pitches > 0]
        
        if len(pitches) == 0:
            return 'unknown'
        
        # Average pitch (fundamental frequency)
        avg_pitch = np.mean(pitches)
        
        # Extract spectral features
        spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(y=audio, sr=sr))
        spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=audio, sr=sr))
        
        # Gender classification logic
        # Male voices typically: lower pitch (85-180 Hz), lower spectral centroid
        # Female voices typically: higher pitch (165-255 Hz), higher spectral centroid
        
        if avg_pitch < 165 and spectral_centroid < 2000:
            return 'male'
        elif avg_pitch > 165 and spectral_centroid > 2000:
            return 'female'
        else:
            # Use additional features for borderline cases
            zero_crossings = np.mean(librosa.feature.zero_crossing_rate(audio))
            if avg_pitch < 180 and zero_crossings < 0.05:
                return 'male'
            elif avg_pitch > 160 and zero_crossings > 0.03:
                return 'female'
            else:
                return 'unknown'
    except:
        return 'unknown'

emotion_names = ['neutral', 'calm', 'happy', 'sad', 'angry', 'fearful', 'disgust', 'surprised']
emotion_colors = {
    'neutral': '#94A3B8',
    'calm': '#3B82F6',
    'happy': '#FBBF24',
    'sad': '#8B5CF6',
    'angry': '#EF4444',
    'fearful': '#F97316',
    'disgust': '#10B981',
    'surprised': '#06B6D4'
}

emotion_emojis = {
    'neutral': '😐',
    'calm': '😌',
    'happy': '😊',
    'sad': '😢',
    'angry': '😠',
    'fearful': '😨',
    'disgust': '🤢',
    'surprised': '😲'
}

gender_icons = {
    'male': '👨',
    'female': '👩',
    'unknown': '🤖'
}

gender_colors = {
    'male': '#3B82F6',  # Blue
    'female': '#EC4899', # Pink
    'unknown': '#94A3B8' # Gray
}

@app.route('/')
def index():
    return render_template('modern_index.html')

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'emotions': emotion_names
    })

@app.route('/predict', methods=['POST'])
def predict():
    if model is None:
        return jsonify({'error': 'Model not loaded'}), 500
    
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file'}), 400
    
    audio_file = request.files['audio']
    temp_path = os.path.join(os.path.dirname(__file__), 'temp.wav')
    audio_file.save(temp_path)
    
    try:
        # Load audio for both emotion and gender detection
        audio, sr = librosa.load(temp_path, sr=config.SAMPLE_RATE)
        
        # Gender detection
        gender = detect_gender(audio, sr)
        
        # Emotion detection
        processed_audio = preprocessor.process(temp_path)
        features = extractor.extract_all(processed_audio)
        features_scaled = scaler.transform([features])
        predictions = model.predict(features_scaled, verbose=0)[0]
        
        # Get all emotion predictions
        all_preds = []
        for i, name in enumerate(emotion_names):
            all_preds.append({
                'emotion': name,
                'confidence': float(predictions[i]),
                'color': emotion_colors[name],
                'emoji': emotion_emojis[name]
            })
        
        # Sort by confidence
        all_preds.sort(key=lambda x: x['confidence'], reverse=True)
        
        # Main prediction
        main = all_preds[0]
        
        # Calculate audio features for display
        audio_features = {
            'duration': len(audio) / sr,
            'sample_rate': sr,
            'pitch': float(np.mean(librosa.piptrack(y=audio, sr=sr)[0][librosa.piptrack(y=audio, sr=sr)[0] > 0]) or 0)
        }
        
        os.remove(temp_path)
        
        return jsonify({
            'success': True,
            'main': main,
            'all_predictions': all_preds,
            'gender': {
                'label': gender,
                'icon': gender_icons[gender],
                'color': gender_colors[gender]
            },
            'audio_features': audio_features
        })
        
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 EMOTION + GENDER DETECTION DASHBOARD")
    print("="*50)
    print(f"📍 URL: http://localhost:5000")
    print("="*50 + "\n")
    app.run(debug=True, port=5000, host='127.0.0.1')