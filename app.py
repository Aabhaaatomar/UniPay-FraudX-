import os
import logging
from flask import Flask, render_template
import pandas as pd

app = Flask(__name__)

# Configure logging to monitor file read occurrences
logging.basicConfig(level=logging.INFO)

DATA_PATH = "data.xlsx"

# Global cache variables
_cached_df = None
_last_modified_time = 0

def get_dataframe():
    """
    Helper function that reads the Excel file dynamically only if it has 
    been modified on disk. Otherwise, it serves data instantly from memory.
    """
    global _cached_df, _last_modified_time
    
    if not os.path.exists(DATA_PATH):
        logging.error(f"Database file '{DATA_PATH}' not found!")
        # Fallback: return empty dataframe with expected columns to prevent server crash
        return pd.DataFrame(columns=["label", "hour", "txn_count_1hr", "amount"])
    
    try:
        # Check the last modification timestamp of the file
        current_mtime = os.path.getmtime(DATA_PATH)
        
        # If file is updated or cache is completely empty, read from disk
        if _cached_df is None or current_mtime > _last_modified_time:
            logging.info("Reading Excel file from disk (Cache refresh)...")
            _cached_df = pd.read_excel(DATA_PATH, engine="openpyxl")
            _last_modified_time = current_mtime
            
        return _cached_df
    except Exception as e:
        logging.error(f"Error accessing or reading Excel data file: {e}")
        return pd.DataFrame(columns=["label", "hour", "txn_count_1hr", "amount"])


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    # Fetch optimized data through the helper cache function
    df = get_dataframe().copy()

    # Graceful fallback handler if dataframe contains no rows
    if df.empty:
        return render_template(
            "dashboard.html", 
            transactions=[], total_txn=0, suspicious_txn=0, normal_txn=0,
            hours=[], counts=[], amounts=[], txn_counts=[], labels=[]
        )

    # Convert DataFrame records cleanly to dictionaries for HTML rendering
    transactions = df.to_dict(orient="records")

    # Metrics Calculations
    total_txn = len(df)
    suspicious_txn = len(df[df["label"].str.lower() == "suspicious"])
    normal_txn = len(df[df["label"].str.lower() == "normal"])

    # Extract Chart Lists
    hours = df["hour"].tolist()
    counts = df["txn_count_1hr"].tolist()
    labels = df["label"].tolist()

    # FIX: Vectorized safe casting via Pandas to protect against type crashes (NaN strings)
    amounts = df["amount"].fillna(0).astype(int).tolist()
    txn_counts = df["txn_count_1hr"].fillna(0).astype(int).tolist()

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
