# backend/ml/train_model.py
import os
import joblib
import argparse
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from feature_extract import load_cicddos, honeypot_logs_to_features, FEATURE_COLS
import pandas as pd

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'ddos_rf.joblib')

def train(cic_csv, honeypot_json=None, save_path=MODEL_PATH):
    print("Loading CICDDoS2019 from:", cic_csv)
    df_cic = load_cicddos(cic_csv)
    print("CICDDoS shape:", df_cic.shape)

    if honeypot_json:
        print("Loading honeypot raw logs to augment training:", honeypot_json)
        honeypot_logs = pd.read_json(honeypot_json)
        df_hp = honeypot_logs_to_features(honeypot_logs)
        print("honeypot converted flows:", df_hp.shape)
        df = pd.concat([df_cic, df_hp[FEATURE_COLS + ['Attack']]], ignore_index=True, sort=False).fillna(0)
    else:
        df = df_cic.fillna(0)

    X = df[FEATURE_COLS]
    y = df['Attack']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    clf = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
    print("Training RandomForest...")
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    print("Classification report:")
    print(classification_report(y_test, y_pred))

    print("Saving model to:", save_path)
    joblib.dump({'model': clf, 'features': FEATURE_COLS}, save_path)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument('--cic', required=True, help='Path to CICDDoS2019 csv')
    p.add_argument('--honeypot', required=False, help='Optional honeypot raw logs JSON to augment training')
    p.add_argument('--out', required=False, help='Model output path')
    args = p.parse_args()
    train(args.cic, args.honeypot, args.out or MODEL_PATH)
