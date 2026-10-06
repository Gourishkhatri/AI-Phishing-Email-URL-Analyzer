import pandas as pd

from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
)
import joblib


DATASET_PATH = Path(
    "dataset/processed/phishing_url_features.csv"
)

MODEL_PATH = Path(
    "model/phishing_url_random_forest.joblib"
)


def main():
    print("Loading processed dataset...")

    df = pd.read_csv(DATASET_PATH)

    print(f"Dataset shape: {df.shape}")

    # Separate features and target
    X = df.drop(columns=["label"])
    y = df["label"]

    print(f"Features: {X.shape[1]}")
    print(f"Samples : {X.shape[0]:,}")

    # Train/Test split
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )

    print("\n========== TRAIN / TEST SPLIT ==========")
    print(f"Training samples: {len(X_train):,}")
    print(f"Testing samples : {len(X_test):,}")

    # Random Forest model
    print("\nTraining Random Forest...")

    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        n_jobs=-1,
        class_weight="balanced",
    )

    model.fit(X_train, y_train)

    # Predictions
    y_pred = model.predict(X_test)

    # Evaluation
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)

    print("\n========== MODEL PERFORMANCE ==========")
    print(f"Accuracy : {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall   : {recall:.4f}")
    print(f"F1 Score : {f1:.4f}")

    print("\n========== CLASSIFICATION REPORT ==========")
    print(
        classification_report(
            y_test,
            y_pred,
            target_names=[
                "Phishing",
                "Legitimate",
            ],
        )
    )

    print("\n========== CONFUSION MATRIX ==========")
    print(confusion_matrix(y_test, y_pred))

    # Save model
    MODEL_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    joblib.dump(model, MODEL_PATH)

    print("\n========== MODEL SAVED ==========")
    print(f"Model: {MODEL_PATH}")


if __name__ == "__main__":
    main()