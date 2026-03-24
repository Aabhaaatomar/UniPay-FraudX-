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
    
    # Admin user
    admin = User(username="admin", email="admin@example.com", role="admin")
    admin.set_password("admin123")
    db.session.add(admin)
    
    # Regular user
    user = User(username="johndoe", email="john@example.com", role="user")
    user.set_password("user123")
    db.session.add(user)
    db.session.flush()

    # Sample transactions
    merchants = ["Amazon", "Flipkart", "Zomato", "Swiggy", "Uber", "Netflix", "Unknown Vendor"]
    locations = ["Delhi", "Mumbai", "Bangalore", "Overseas", "Unknown"]
    methods = ["card", "upi", "netbanking", "wallet"]

    for i in range(20):
        amount = round(random.uniform(50, 15000), 2)
        tx = Transaction(
            user_id=user.id,
            transaction_id=str(uuid.uuid4()),
            amount=amount,
            currency="INR",
            merchant=random.choice(merchants),
            location=random.choice(locations),
            ip_address=f"192.168.1.{random.randint(1,254)}",
            device_id=f"device_{random.randint(1,5)}",
            payment_method=random.choice(methods),
            status="approved",
            created_at=datetime.utcnow() - timedelta(days=random.randint(0, 30)),
        )
        db.session.add(tx)

    db.session.commit()
    print("✅ Seed complete!")
    print("   Admin → email: admin@example.com  password: admin123")
    print("   User  → email: john@example.com   password: user123")

