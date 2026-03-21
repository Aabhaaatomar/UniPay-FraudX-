"""
Seed script — creates an admin user and sample transactions.
Run: python seed.py
"""

from app import create_app, db
from app.models import User, Transaction
import uuid
from datetime import datetime, timedelta
import random

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()
