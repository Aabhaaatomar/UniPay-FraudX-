import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import pickle

# Load dataset
df = pd.read_excel("data.xlsx")

# Features (input)
X = df[["amount", "txn_count_1hr", "hour"]]

# Target (output)
y = df["label"]   # 0 = normal, 1 = fraud

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

# Save model
with open("fraud_model.pkl", "wb") as f:
    pickle.dump(model, f)

print("Model trained & saved successfully")
