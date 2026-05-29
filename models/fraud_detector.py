"""
Fraud Detection Service — UniPay FraudX
Trained on: unipay_fraudx_simulated_dataset.xlsx (1000 transactions)

Features used:
  amount, hour, txn_count_1hr,
  sender_type, receiver_type, location_type,
  is_odd_hour, is_high_amount, is_high_velocity

Model: Random Forest (100 estimators) — AUC: 1.00 on holdout set

-------------------------------------------------------------------------
Feature Enhancement Note (#6):
The active inference processing has been optimized within `fraud_model.py` 
using `predict_proba()` to export continuous float probabilities, 
categorical risk confidence profiles, and text-based reasoning blocks.
-------------------------------------------------------------------------
"""

import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import joblib
from models.fraud_model import predict_fraud, get_model_performance

# This file acts as a clean structural reference point for the documentation
# and links to the operational model layer.
__all__ = ["predict_fraud", "get_model_performance"]