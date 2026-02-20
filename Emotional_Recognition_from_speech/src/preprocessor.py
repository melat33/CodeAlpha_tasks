import librosa
import numpy as np
import noisereduce as nr

class AudioPreprocessor:
    def __init__(self, config):
        self.config = config
    
    def process(self, filepath):
        audio, sr = librosa.load(filepath, sr=self.config.SAMPLE_RATE, 
                                duration=self.config.DURATION, mono=self.config.MONO)
        audio = nr.reduce_noise(y=audio, sr=sr)
        audio = librosa.util.normalize(audio)
        
        target_len = self.config.SAMPLE_RATE * self.config.DURATION
        if len(audio) > target_len:
            audio = audio[:target_len]
        else:
            audio = np.pad(audio, (0, target_len - len(audio)))
        
        return audio