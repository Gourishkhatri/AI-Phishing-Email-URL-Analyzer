import pandas as pd
import joblib

from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
)


DATASET_PATH = Path(
    "dataset/processed/phishing_url_features.csv"
)

RANDOM_FOREST_PATH = Path(
    "model/phishing_url_random_forest.joblib"
)


def evaluate_model(name, model, X_train, X_test, y_train, y_test):
    print(f"\nTraining {name}...")

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    accuracy = accuracy_score(y_test, predictions)
    precision = precision_score(y_test, predictions)
    recall = recall_score(y_test, predictions)
    f1 = f1_score(y_test, predictions)

    print(f"\n{name}")
    print("-" * 45)
    print(f"Accuracy : {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall   : {recall:.4f}")
    print(f"F1 Score : {f1:.4f}")

    return {
        "Model": name,
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1 Score": f1,
    }


def main():

    print("Loading dataset...")

    df = pd.read_csv(DATASET_PATH)

    X = df.drop(columns=["label"])
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )

    results = []

    # Random Forest
    random_forest = joblib.load(
        RANDOM_FOREST_PATH
    )

    rf_result = evaluate_model(
        "Random Forest",
        random_forest,
        X_train,
        X_test,
        y_train,
        y_test,
    )

    results.append(rf_result)

    # Logistic Regression
    logistic_regression = Pipeline([
        (
            "scaler",
            StandardScaler()
        ),
        (
            "classifier",
            LogisticRegression(
                max_iter=1000,
                random_state=42,
            )
        ),
    ])

    lr_result = evaluate_model(
        "Logistic Regression",
        logistic_regression,
        X_train,
        X_test,
        y_train,
        y_test,
    )

    results.append(lr_result)

    # Comparison
    comparison = pd.DataFrame(results)

    print("\n========== MODEL COMPARISON ==========")
    print(
        comparison.to_string(
            index=False
        )
    )

    output_path = Path(
        "reports/model_comparison.csv"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    comparison.to_csv(
        output_path,
        index=False
    )

    print("\nComparison saved:")
    print(output_path)


if __name__ == "__main__":
    main()