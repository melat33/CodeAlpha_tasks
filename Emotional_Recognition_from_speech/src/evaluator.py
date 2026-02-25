import numpy as np
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

class ModelEvaluator:
    def evaluate(self, model, X_test, y_test, emotion_names):
        y_pred = model.predict(X_test)
        y_pred_classes = np.argmax(y_pred, axis=1)
        y_true_classes = np.argmax(y_test, axis=1)
        
        report = classification_report(y_true_classes, y_pred_classes, 
                                      target_names=emotion_names, digits=4)
        cm = confusion_matrix(y_true_classes, y_pred_classes)
        
        # Plot confusion matrix
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                   xticklabels=emotion_names, yticklabels=emotion_names)
        plt.title('Confusion Matrix')
        plt.tight_layout()
        plt.show()
        
        return report, cm