import pandas as pd
import joblib

from pathlib import Path


DATASET_PATH = Path(
    "dataset/processed/phishing_url_features.csv"
)

MODEL_PATH = Path(
    "model/phishing_url_random_forest.joblib"
)


def main():
    print("Loading dataset and model...")

    df = pd.read_csv(DATASET_PATH)
    model = joblib.load(MODEL_PATH)

    X = df.drop(columns=["label"])

    importance = pd.DataFrame({
        "feature": X.columns,
        "importance": model.feature_importances_
    })

    importance = importance.sort_values(
        by="importance",
        ascending=False
    )

    print("\n========== FEATURE IMPORTANCE ==========")

    for index, row in importance.iterrows():
        print(
            f"{row['feature']:<30} "
            f"{row['importance']:.6f}"
        )

    # Save feature importance
    output_path = Path(
        "reports/feature_importance.csv"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    importance.to_csv(
        output_path,
        index=False
    )

    print("\n========== TOP 10 FEATURES ==========")

    print(
        importance.head(10).to_string(
            index=False
        )
    )

    print("\nSaved:")
    print(output_path)


if __name__ == "__main__":
    main()