import os
import pandas as pd

class RAVDESSLoader:
    def __init__(self, config):
        self.config = config
    
    def load_metadata(self):
        records = []
        for root, _, files in os.walk(self.config.RAVDESS_PATH):
            for file in files:
                if file.endswith('.wav'):
                    parts = file.split('-')
                    if len(parts) >= 3:
                        records.append({
                            'filepath': os.path.join(root, file),
                            'emotion': self.config.EMOTION_MAP.get(parts[2], 'unknown'),
                            'actor': parts[6] if len(parts) > 6 else 'unknown'
                        })
        
        df = pd.DataFrame(records)
        df['emotion_label'] = pd.Categorical(df['emotion']).codes
        return df