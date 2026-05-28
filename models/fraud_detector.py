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


