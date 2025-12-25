import joblib
import numpy as np

class Predictor:
    def __init__(self, model_path):
        self.model = joblib.load(model_path)

    def predict_proba(self, X):
        if hasattr(self.model, "predict_proba"):
            return self.model.predict_proba(X)
        else:
            scores = self.model.decision_function(X)
            scores = (scores - scores.min()) / (scores.max() - scores.min() + 1e-6)
            return np.vstack([1 - scores, scores]).T
