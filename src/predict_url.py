import sys
import os
import pandas as pd
import joblib

from url_feature_extractor import (
    extract_features,
    FEATURE_NAMES
)


MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "model",
    "url_only_random_forest.joblib"
)


def predict_url(url):

    model = joblib.load(MODEL_PATH)

    features = extract_features(url)

    X = pd.DataFrame(
        [[features[name] for name in FEATURE_NAMES]],
        columns=FEATURE_NAMES
    )

    prediction = model.predict(X)[0]
    probabilities = model.predict_proba(X)[0]

    class_probabilities = dict(
        zip(model.classes_, probabilities)
    )

    phishing_probability = class_probabilities.get(0, 0)
    legitimate_probability = class_probabilities.get(1, 0)

    if prediction == 0:
        result = "PHISHING"
        confidence = phishing_probability
    else:
        result = "LEGITIMATE"
        confidence = legitimate_probability

    if phishing_probability >= 0.75:
        risk = "HIGH"
    elif phishing_probability >= 0.40:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    print("\n========== AI PHISHING URL ANALYZER ==========")
    print(f"URL        : {url}")
    print(f"Prediction : {result}")
    print(f"Confidence : {confidence * 100:.2f}%")
    print(
        f"Phishing Probability   : "
        f"{phishing_probability * 100:.2f}%"
    )
    print(
        f"Legitimate Probability : "
        f"{legitimate_probability * 100:.2f}%"
    )
    print(f"Risk Level : {risk}")

    print("\n========== EXTRACTED FEATURE VALUES ==========")

    for name in FEATURE_NAMES:
        print(
            f"{name:<30} {features[name]}"
        )

    print("===============================================")


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print(
            'Usage: python src/predict_url.py '
            '"https://example.com"'
        )
        sys.exit(1)

    url = sys.argv[1]

    try:
        predict_url(url)

    except Exception as e:
        print(f"\nError analyzing URL: {e}")
        sys.exit(1)