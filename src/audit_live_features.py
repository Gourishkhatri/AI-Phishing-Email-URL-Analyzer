import pandas as pd

from pathlib import Path

from url_feature_extractor import (
    extract_features,
    FEATURE_NAMES,
)


DATASET_PATH = Path(
    "dataset/raw/PhiUSIIL_Phishing_URL_Dataset.csv"
)


def main():

    print("Loading dataset...")

    df = pd.read_csv(DATASET_PATH)

    # Generate live features
    test_url = "https://www.google.com"

    live_values = extract_features(
        test_url
    )

    live_features = dict(
        zip(
            FEATURE_NAMES,
            live_values
        )
    )

    print("\n========== LIVE URL FEATURES ==========")
    print(f"URL: {test_url}")

    for feature in FEATURE_NAMES:

        print(
            f"{feature:<30} "
            f"{live_features[feature]}"
        )

    print(
        "\n========== TRAINING FEATURE "
        "DISTRIBUTION =========="
    )

    for feature in FEATURE_NAMES:

        values = df[feature]

        print(
            f"\n{feature}"
        )

        print(
            f"  Live value : "
            f"{live_features[feature]}"
        )

        print(
            f"  Min        : "
            f"{values.min()}"
        )

        print(
            f"  Mean       : "
            f"{values.mean():.4f}"
        )

        print(
            f"  Median     : "
            f"{values.median()}"
        )

        print(
            f"  Max        : "
            f"{values.max()}"
        )

        print(
            f"  Q25        : "
            f"{values.quantile(0.25):.4f}"
        )

        print(
            f"  Q75        : "
            f"{values.quantile(0.75):.4f}"
        )


if __name__ == "__main__":
    main()