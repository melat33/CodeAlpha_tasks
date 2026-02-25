import tensorflow as tf
from tensorflow.keras import layers, models

class EmotionRecognitionModel:
    def __init__(self, config):
        self.config = config
    
    def build(self, input_shape, num_classes=8):
        model = models.Sequential([
             # ✅ CNN LAYERS 
            layers.Reshape((input_shape[0]//4, 4, 1), input_shape=input_shape),
            
            layers.Conv2D(32, (3, 3), padding='same', activation='relu'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.25),
            
            layers.Conv2D(64, (3, 3), padding='same', activation='relu'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.25),
            
            # ✅ PREPARE FOR LSTM
            layers.Reshape((-1, 64)),
            layers.LSTM(64, return_sequences=True, dropout=0.2),
            layers.LSTM(32, dropout=0.2),
            
            layers.Dense(64, activation='relu'),
            layers.Dropout(0.3),
            layers.Dense(32, activation='relu'),
            layers.Dense(num_classes, activation='softmax')
        ])
        
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=self.config.LEARNING_RATE),
            loss='categorical_crossentropy',
            metrics=['accuracy', 'precision', 'recall']
        )
        
        return model