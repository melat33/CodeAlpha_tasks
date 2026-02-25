import tensorflow as tf
import numpy as np

class ModelTrainer:
    def __init__(self, config):
        self.config = config
    
    def train(self, model, X_train, y_train, X_val, y_val):
        callbacks = [
            tf.keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=self.config.PATIENCE,
                restore_best_weights=True
            ),
            tf.keras.callbacks.ModelCheckpoint(
                'models/best_model.h5',
                monitor='val_accuracy',
                save_best_only=True
            )
        ]
        
        history = model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=self.config.EPOCHS,
            batch_size=self.config.BATCH_SIZE,
            callbacks=callbacks,
            verbose=1
        )
        
        return history