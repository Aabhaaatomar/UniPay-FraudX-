"""
Seed script — creates an admin user and sample transactions.
Run: python seed.py
"""

from app import create_app, db
from app.models import User, Transaction
import uuid
from datetime import datetime, timedelta
import random

