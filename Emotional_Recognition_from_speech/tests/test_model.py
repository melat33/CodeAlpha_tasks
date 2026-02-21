import pytest
import numpy as np
import tensorflow as tf
import joblib
import os
import sys
sys.path.append('src')
from config import Config
from preprocessor import AudioPreprocessor
from feature_extractor import FeatureExtractor

class TestEmotionModel:
    @pytest.fixture
    def setup(self):
        self.config = Config()
        self.model = tf.keras.models.load_model('models/emotion_model.h5')
        self.scaler = joblib.load('models/scaler.pkl')
        self.preprocessor = AudioPreprocessor(self.config)
        self.extractor = FeatureExtractor(self.config)
        
    def test_model_loading(self, setup):
        """Test if model loads correctly"""
        assert self.model is not None
        assert self.model.input_shape[-1] == 42
        
    def test_prediction_shape(self, setup):
        """Test prediction output shape"""
        dummy_audio = np.zeros(22050 * 3)
        features = self.extractor.extract_all(dummy_audio)
        features_scaled = self.scaler.transform([features])
        predictions = self.model.predict(features_scaled)
        
        assert predictions.shape == (1, 8)
        
    def test_prediction_range(self, setup):
        """Test if predictions sum to 1"""
        dummy_audio = np.random.randn(22050 * 3)
        features = self.extractor.extract_all(dummy_audio)
        features_scaled = self.scaler.transform([features])
        predictions = self.model.predict(features_scaled)[0]
        
        assert np.isclose(np.sum(predictions), 1.0, rtol=1e-3)
        
    @pytest.mark.parametrize("emotion", ['happy', 'sad', 'angry'])
    def test_emotion_detection(self, setup, emotion):
        """Test emotion detection on synthetic audio"""
        # Create synthetic audio with specific emotion
        audio = create_synthetic_audio(emotion)
        features = self.extractor.extract_all(audio)
        features_scaled = self.scaler.transform([features])
        predictions = self.model.predict(features_scaled)[0]
        
        emotion_idx = np.argmax(predictions)
        emotion_names = self.config.EMOTIONS
        
        assert predictions[emotion_idx] > 0.3

def create_synthetic_audio(emotion):
    """Create synthetic audio for testing"""
    sr = 22050
    duration = 3
    t = np.linspace(0, duration, int(sr * duration))
    
    if emotion == 'happy':
        return 0.3 * np.sin(2 * np.pi * 440 * t)
    elif emotion == 'sad':
        return 0.2 * np.sin(2 * np.pi * 220 * t)
    elif emotion == 'angry':
        return 0.5 * np.random.randn(len(t))
    else:
        return 0.2 * np.sin(2 * np.pi * 261.63 * t)