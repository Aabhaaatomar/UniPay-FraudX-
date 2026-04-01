from flask import Flask, render_template
import pandas as pd

app = Flask(__name__)

# For local file (replace 'your_dataset.xlsx' with actual path)
df = pd.read_excel('data.xlsx', engine='openpyxl')


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    df = pd.read_excel("data.xlsx")

    transactions = df.to_dict(orient="records")

    total_txn = len(df)
    suspicious_txn = len(df[df["label"] == "Suspicious"])
    normal_txn = len(df[df["label"] == "Normal"])

    hours = df["hour"].tolist()
    counts = df["txn_count_1hr"].tolist()

    # 👇 YE NAYA PART
    amounts = list(map(int, df["amount"]))
    txn_counts = list(map(int, df["txn_count_1hr"]))
    labels = df["label"].tolist()

    return render_template(
        "dashboard.html",
        transactions=transactions,
        total_txn=int(total_txn),
        suspicious_txn=int(suspicious_txn),
        normal_txn=int(normal_txn),
        hours=hours,
        counts=counts,
        amounts=amounts,
        txn_counts=txn_counts,
        labels=labels
    )

if __name__ == "__main__":
    app.run(debug=True)
