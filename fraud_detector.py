"""
Fraud Detection Service — UniPay FraudX
Trained on: unipay_fraudx_simulated_dataset.xlsx (1000 transactions)

Features used:
  amount, hour, txn_count_1hr,
  sender_type, receiver_type, location_type,
  is_odd_hour, is_high_amount, is_high_velocity

Model: Random Forest (100 estimators) — AUC: 1.00 on holdout set
"""

import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import joblib

MODEL_PATH = os.path.join(os.path.dirname(__file__), "fraud_model.pkl")

# Dataset-derived thresholds
# Normal transactions: amount <= 4990, txn_count <= 10, hour 5-23
# Hours 0-4 are 100% Suspicious in the dataset
AMOUNT_THRESHOLD = int(os.getenv("FRAUD_AMOUNT_THRESHOLD", 5000))
VELOCITY_LIMIT = int(os.getenv("FRAUD_VELOCITY_LIMIT", 10))
ODD_HOUR_MAX = 4


# Supported categorical values from training data
SENDER_TYPES   = ["Student", "Vendor"]
RECEIVER_TYPES = ["Canteen", "Hostel", "Library", "Local_Shop"]
LOCATION_TYPES = ["Community", "University"]

_bundle = None


def _get_bundle():
    global _bundle
    if _bundle is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"ML model not found at {MODEL_PATH}. "
                "Run seed.py or the training script first."
            )
        _bundle = joblib.load(MODEL_PATH)
    return _bundle


def _safe_encode(encoder, value, fallback=0):
    try:
        return int(encoder.transform([value])[0])
    except Exception:
        return fallback


def _normalize_sender(payment_method):
    """Map transaction payment_method to dataset sender_type vocabulary."""
    mapping = {
        "upi": "Student", "wallet": "Student",
        "card": "Vendor", "netbanking": "Vendor",
    }
    return mapping.get(str(payment_method).lower(), "Vendor")


def _normalize_receiver(merchant_category):
    """Map merchant_category to dataset receiver_type vocabulary."""
    if not merchant_category:
        return "Local_Shop"
    v = str(merchant_category).strip().title().replace(" ", "_")
    return v if v in RECEIVER_TYPES else "Local_Shop"


def _normalize_location(location):
    """Map location to dataset location_type vocabulary."""
    if not location:
        return "Community"
    loc = str(location).strip().lower()
    if any(k in loc for k in ["university", "campus", "college"]):
        return "University"
    return "Community"

# ─── Rule-Based Engine ────────────────────────────────────────────────────────

def run_rule_engine(transaction, recent_transactions, blocklist_values):
    """
    8 rules derived from dataset analysis.
    Returns: (triggered_rules: list[str], rule_score: float 0-1)
    """
    triggered = []

# Rule 1: High amount (all Normal transactions are <= 4990)
    if transaction.amount > AMOUNT_THRESHOLD:
        triggered.append("HIGH_AMOUNT")

    # Rule 2: Odd hour (hours 0-4 are 100% Suspicious in dataset)
    if transaction.created_at.hour <= ODD_HOUR_MAX:
        triggered.append("ODD_HOUR_TRANSACTION")

    # Rule 3: High velocity (>= 10 txns/hr mirrors dataset feature)
    txn_count_1hr = len([
        t for t in recent_transactions
        if t.created_at >= datetime.utcnow() - timedelta(hours=1)
        and t.id != transaction.id
    ])
    if txn_count_1hr >= VELOCITY_LIMIT:
        triggered.append("HIGH_VELOCITY")

    # Rule 4: Compound risk — high amount AND high velocity
    if "HIGH_AMOUNT" in triggered and "HIGH_VELOCITY" in triggered:
        triggered.append("HIGH_AMOUNT_AND_VELOCITY")


# Rule 5: Blocked IP
    if transaction.ip_address and transaction.ip_address in blocklist_values:
        triggered.append("BLOCKED_IP")

    # Rule 6: Blocked device
    if transaction.device_id and transaction.device_id in blocklist_values:
        triggered.append("BLOCKED_DEVICE")

    # Rule 7: Round large amount (structuring)
    if transaction.amount >= 1000 and transaction.amount % 1000 == 0:
        triggered.append("ROUND_LARGE_AMOUNT")

    # Rule 8: Duplicate amounts in short window
    dup_count = sum(
        1 for t in recent_transactions
        if t.amount == transaction.amount and t.id != transaction.id
    )
    if dup_count >= 2:
        triggered.append("DUPLICATE_AMOUNT")

    rule_weights = {
        "HIGH_AMOUNT":              0.55,
        "ODD_HOUR_TRANSACTION":     0.70,
        "HIGH_VELOCITY":            0.50,
        "HIGH_AMOUNT_AND_VELOCITY": 0.80,
        "BLOCKED_IP":               1.00,
        "BLOCKED_DEVICE":           1.00,
        "ROUND_LARGE_AMOUNT":       0.20,
        "DUPLICATE_AMOUNT":         0.30,
    }
    rule_score = min(1.0, sum(rule_weights.get(r, 0.1) for r in set(triggered)))
    return triggered, round(rule_score, 4)


