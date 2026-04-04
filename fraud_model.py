import pickle

# Load model
with open("fraud_model.pkl", "rb") as f:
    model = pickle.load(f)

def predict_fraud(amount, txn_count, hour):
    data = [[amount, txn_count, hour]]
    prediction = model.predict(data)[0]
    
    if prediction == 1:
        return "🚨 Fraud Transaction"
    else:
        return "✅ Normal Transaction"