
"""
Model Training Script — UniPay FraudX
Generates synthetic dataset (if not found) and trains a Random Forest classifier.

Run from the project root:
    python models/model.py
"""

import os
import pickle
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_DIR = os.path.join(BASE_DIR, "dataset")
DATASET_PATH = os.path.join(DATASET_DIR, "data.xlsx")
MODEL_PATH   = os.path.join(BASE_DIR, "models", "fraud_model.pkl")

# ── Dataset Generation ─────────────────────────────────────────────────────────
def generate_dataset(n=1000, seed=42):
    """Generate a synthetic, realistic fraud detection dataset."""
    rng = np.random.default_rng(seed)

    sender_types   = ["individual", "business", "government", "unknown"]
    receiver_types = ["individual", "business", "merchant", "unknown"]
    location_types = ["domestic", "international", "unknown"]

    records = []
    for i in range(n):
        hour             = int(rng.integers(0, 24))
        amount           = float(round(rng.exponential(scale=3000) + 50, 2))
        txn_count_1hr    = int(rng.integers(1, 25))
        sender_type      = rng.choice(sender_types)
        receiver_type    = rng.choice(receiver_types)
        location_type    = rng.choice(location_types)

        # Derived boolean features (also used by rule engine)
        is_odd_hour      = 1 if hour < 6 or hour > 22 else 0
        is_high_amount   = 1 if amount > 10000 else 0
        is_high_velocity = 1 if txn_count_1hr > 10 else 0

        # Label: fraud if 2+ risk flags or international + high amount
        fraud_score = is_odd_hour + is_high_amount + is_high_velocity
        if location_type == "international" and amount > 5000:
            fraud_score += 1
        if sender_type == "unknown" or receiver_type == "unknown":
            fraud_score += 1

        label = "Suspicious" if fraud_score >= 2 else "Normal"

        # Inject some noise (10 %)
        if rng.random() < 0.10:
            label = "Suspicious" if label == "Normal" else "Normal"

        records.append({
            "transaction_id"  : f"TXN{i+1:05d}",
            "amount"          : amount,
            "hour"            : hour,
            "txn_count_1hr"   : txn_count_1hr,
            "sender_type"     : sender_type,
            "receiver_type"   : receiver_type,
            "location_type"   : location_type,
            "is_odd_hour"     : is_odd_hour,
            "is_high_amount"  : is_high_amount,
            "is_high_velocity": is_high_velocity,
            "label"           : label,
        })

    return pd.DataFrame(records)


# ── Training ───────────────────────────────────────────────────────────────────
def train_and_save():
    # 1. Dataset
    os.makedirs(DATASET_DIR, exist_ok=True)
    if not os.path.exists(DATASET_PATH):
        print("[INFO] Dataset not found -- generating synthetic dataset ...")
        df = generate_dataset(n=1000)
        df.to_excel(DATASET_PATH, index=False)
        print(f"   [OK] Saved -> {DATASET_PATH}  ({len(df)} rows)")
    else:
        print(f"[INFO] Loading existing dataset: {DATASET_PATH}")
        df = pd.read_excel(DATASET_PATH)

    print(f"   Fraud distribution:\n{df['label'].value_counts().to_string()}\n")

    # 2. Features
    FEATURE_COLS = ["amount", "txn_count_1hr", "hour",
                    "is_odd_hour", "is_high_amount", "is_high_velocity"]
    X = df[FEATURE_COLS]
    y = (df["label"] == "Suspicious").astype(int)

    # 3. Train / test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # 4. Model
    clf = RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        min_samples_leaf=5,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )
    clf.fit(X_train, y_train)

    # 5. Evaluation
    y_pred  = clf.predict(X_test)
    y_proba = clf.predict_proba(X_test)[:, 1]
    print(f"[INFO] Model Evaluation:")
    print(classification_report(y_test, y_pred, target_names=["Normal", "Suspicious"]))
    print(f"   ROC-AUC : {roc_auc_score(y_test, y_proba):.4f}\n")

    # 6. Save
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(clf, f)
    print(f"[OK] Model saved -> {MODEL_PATH}")


if __name__ == "__main__":
    train_and_save()