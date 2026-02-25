import librosa
import numpy as np

class FeatureExtractor:
    def __init__(self, config):
        self.config = config
    
    def extract_mfcc(self, audio):
        mfccs = librosa.feature.mfcc(y=audio, sr=self.config.SAMPLE_RATE, 
                                    n_mfcc=self.config.N_MFCC,
                                    hop_length=self.config.HOP_LENGTH)
        return np.mean(mfccs.T, axis=0)
    
    def extract_all(self, audio):
        features = []
        features.extend(self.extract_mfcc(audio))
        
        # Add more features if needed
        zcr = librosa.feature.zero_crossing_rate(audio)
        features.append(np.mean(zcr))
        
        rms = librosa.feature.rms(y=audio)
        features.append(np.mean(rms))
        
        return np.array(features)