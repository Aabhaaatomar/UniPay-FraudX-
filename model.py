import pandas as pd
import pickle

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report


def load_data(file_path):
    try:
        df = pd.read_excel(file_path)
        print("Dataset loaded successfully")
        return df
    except Exception as e:
        print("Error loading dataset:", e)
        return None


def preprocess_data(df):
    # Remove missing values
    df = df.dropna()

    # Features and target
    X = df[["amount", "txn_count_1hr", "hour"]]
    y = df["label"]

    return X, y


def train_model(X_train, y_train):
    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42
    )
    model.fit(X_train, y_train)
    return model


def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)

    print("\nModel Evaluation:")
    print("Accuracy:", accuracy_score(y_test, y_pred))
    print("\nClassification Report:\n", classification_report(y_test, y_pred))


def show_feature_importance(model, feature_names):
    importance = pd.Series(model.feature_importances_, index=feature_names)
    print("\nFeature Importance:\n", importance.sort_values(ascending=False))


def save_model(model, feature_names, file_name="fraud_model.pkl"):
    model_data = {
        "model": model,
        "features": feature_names
    }

    with open(file_name, "wb") as f:
        pickle.dump(model_data, f)

    print(f"\nModel saved successfully as {file_name}")


def main():
    # Step 1: Load data
    df = load_data("data.xlsx")
    if df is None:
        return

    # Step 2: Preprocess
    X, y = preprocess_data(df)

    # Step 3: Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Step 4: Train model
    model = train_model(X_train, y_train)

    # Step 5: Evaluate
    evaluate_model(model, X_test, y_test)

    # Step 6: Feature importance
    show_feature_importance(model, X.columns)

    # Step 7: Save model
    save_model(model, list(X.columns))


if __name__ == "__main__":
    main()
