import tensorflow as tf
import numpy as np
import joblib

class EmotionPredictor:
    def __init__(self, model_path, scaler_path, config):
        self.model = tf.keras.models.load_model(model_path)
        self.scaler = joblib.load(scaler_path)
        self.config = config
        
        from .preprocessor import AudioPreprocessor
        from .feature_extractor import FeatureExtractor
        
        self.preprocessor = AudioPreprocessor(config)
        self.feature_extractor = FeatureExtractor(config)
        self.emotion_names = list(config.EMOTION_MAP.values())
    
    def predict(self, audio_file):
        audio = self.preprocessor.process(audio_file)
        features = self.feature_extractor.extract_all(audio)
        features_scaled = self.scaler.transform([features])
        
        predictions = self.model.predict(features_scaled, verbose=0)[0]
        emotion_idx = np.argmax(predictions)
        
        return {
            'emotion': self.emotion_names[emotion_idx],
            'confidence': float(predictions[emotion_idx]),
            'all_predictions': {self.emotion_names[i]: float(predictions[i]) 
                               for i in range(len(predictions))}
        }