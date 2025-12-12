# backend/ml/predictor.py
import os
import joblib
import numpy as np
from feature_extract import FEATURE_COLS
MODEL_FILE = os.path.join(os.path.dirname(__file__), 'ddos_rf.joblib')

class Predictor:
    def __init__(self, model_path=MODEL_FILE):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model missing at {model_path}. Train first.")
        data = joblib.load(model_path)
        self.model = data['model']
        self.features = data['features']

    def predict_proba(self, df_features):
        """
        df_features: pandas DataFrame with columns matching self.features
        returns: probability of attack (0..1) for each row
        """
        X = df_features[self.features].fillna(0)
        probs = self.model.predict_proba(X)[:,1]
        return probs

# convenience single row prediction
def single_predict(feats_dict, predictor=None):
    import pandas as pd
    if predictor is None:
        predictor = Predictor()
    df = pd.DataFrame([feats_dict])
    df = df.reindex(columns=predictor.features, fill_value=0)
    return predictor.predict_proba(df)[0]
