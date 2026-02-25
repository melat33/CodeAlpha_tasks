# app/app.py
import os
import sys
import numpy as np
from flask import Flask, render_template, request, jsonify
import joblib
import librosa
import warnings
warnings.filterwarnings('ignore')

# IMPORTANT: Add the src folder to Python path
# Go up one level from app/ to project root, then into src/
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, src_path)
print(f"✅ Added src to path: {src_path}")

# Now import from src
from config import Config
from preprocessor import AudioPreprocessor
from feature_extractor import FeatureExtractor

import tensorflow as tf

app = Flask(__name__)

# Load model and components
config = Config()

# Update model paths - go up one level from app/ to project root
model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'models', 'emotion_model.h5'))
scaler_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'models', 'scaler.pkl'))

print(f"📂 Looking for model at: {model_path}")
print(f"📂 Looking for scaler at: {scaler_path}")

# Check if files exist
if not os.path.exists(model_path):
    print(f"❌ Model not found at: {model_path}")
    print("Please train the model first or check the path")
    exit(1)

if not os.path.exists(scaler_path):
    print(f"❌ Scaler not found at: {scaler_path}")
    print("Please train the model first or check the path")
    exit(1)

# Load model and scaler
model = tf.keras.models.load_model(model_path)
scaler = joblib.load(scaler_path)
preprocessor = AudioPreprocessor(config)
extractor = FeatureExtractor(config)

emotion_names = ['neutral', 'calm', 'happy', 'sad', 
                 'angry', 'fearful', 'disgust', 'surprised']
emotion_colors = {
    'neutral': '#95a5a6',
    'calm': '#3498db',
    'happy': '#f1c40f',
    'sad': '#9b59b6',
    'angry': '#e74c3c',
    'fearful': '#e67e22',
    'disgust': '#27ae60',
    'surprised': '#1abc9c'
}

@app.route('/')
def index():
    return render_template('index.html', emotions=emotion_names)

@app.route('/predict', methods=['POST'])
def predict():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file'}), 400
    
    audio_file = request.files['audio']
    temp_path = os.path.join(os.path.dirname(__file__), 'temp_audio.wav')
    audio_file.save(temp_path)
    
    try:
        # Process audio
        audio = preprocessor.process(temp_path)
        features = extractor.extract_all(audio)
        features_scaled = scaler.transform([features])
        
        # Predict
        predictions = model.predict(features_scaled, verbose=0)[0]
        
        # Get top 3 predictions
        top_3_idx = np.argsort(predictions)[-3:][::-1]
        top_3 = [{
            'emotion': emotion_names[i],
            'confidence': float(predictions[i]),
            'color': emotion_colors[emotion_names[i]]
        } for i in top_3_idx]
        
        # Main prediction
        main_emotion = emotion_names[np.argmax(predictions)]
        main_confidence = float(np.max(predictions))
        
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        return jsonify({
            'success': True,
            'main_emotion': main_emotion,
            'main_confidence': main_confidence,
            'main_color': emotion_colors[main_emotion],
            'top_3': top_3,
            'all_predictions': [{
                'emotion': emotion_names[i],
                'confidence': float(predictions[i]),
                'color': emotion_colors[emotion_names[i]]
            } for i in range(len(emotion_names))]
        })
        
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting Emotion Recognition Dashboard...")
    print(f"🌐 Open http://localhost:5000 in your browser")
    app.run(debug=True, port=5000)