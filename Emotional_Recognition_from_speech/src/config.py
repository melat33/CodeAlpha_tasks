# src/config.py
class Config:
    # Data paths
    RAVDESS_PATH = "data/raw/audio_speech_actors_01-24/"
    
    # Audio processing
    SAMPLE_RATE = 22050
    DURATION = 3
    MONO = True  # ADD THIS LINE
    
    # Feature extraction
    N_MFCC = 40
    N_MELS = 128
    HOP_LENGTH = 512
    
    # Model parameters
    BATCH_SIZE = 32
    EPOCHS = 100
    LEARNING_RATE = 0.001
    PATIENCE = 15
    
    # Emotions mapping
    EMOTION_MAP = {
        '01': 'neutral', '02': 'calm', '03': 'happy',
        '04': 'sad', '05': 'angry', '06': 'fearful',
        '07': 'disgust', '08': 'surprised'
    }