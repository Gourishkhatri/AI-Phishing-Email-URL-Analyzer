import os
import pandas as pd
import joblib

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)

from url_feature_extractor import (
    extract_features,
    FEATURE_NAMES,
)


# =========================================================
# PATHS
# =========================================================

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DATASET_PATH = os.path.join(
    BASE_DIR,
    "dataset",
    "raw",
    "PhiUSIIL_Phishing_URL_Dataset.csv",
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "model",
)

REPORT_DIR = os.path.join(
    BASE_DIR,
    "reports",
)

os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)


# =========================================================
# LOAD DATASET
# =========================================================

print("Loading PhiUSIIL dataset...")

df = pd.read_csv(DATASET_PATH)

print(f"Original rows: {len(df)}")


# =========================================================
# REMOVE ONLY EXACT DUPLICATE URLs
# =========================================================

before = len(df)

df = df.drop_duplicates(
    subset=["URL"]
).reset_index(drop=True)

removed = before - len(df)

print(f"Duplicate URLs removed: {removed}")
print(f"Remaining rows: {len(df)}")


# =========================================================
# EXTRACT URL-ONLY FEATURES
# =========================================================

print("\nExtracting URL-only features...")

feature_rows = []

for index, url in enumerate(df["URL"]):

    if index % 25000 == 0:
        print(
            f"Processed {index}/{len(df)} URLs..."
        )

    try:
        features = extract_features(url)

        feature_rows.append(
            [
                features[name]
                for name in FEATURE_NAMES
            ]
        )

    except Exception as e:

        print(
            f"Skipping row {index}: {e}"
        )


X = pd.DataFrame(
    feature_rows,
    columns=FEATURE_NAMES,
)

# Keep labels aligned with successfully processed rows.
# Since the extractor is deterministic, rebuild labels
# from the same valid URL rows.

valid_urls = []

for url in df["URL"]:

    try:
        extract_features(url)
        valid_urls.append(url)

    except Exception:
        pass


valid_df = df[
    df["URL"].isin(valid_urls)
].copy()

y = valid_df["label"].reset_index(
    drop=True
)

X = X.reset_index(drop=True)


# =========================================================
# DATASET INFORMATION
# =========================================================

print("\n========== DATASET ==========")

print(
    f"Features: {X.shape[1]}"
)

print(
    f"Samples : {X.shape[0]}"
)

print("\nLabel distribution:")

print(
    y.value_counts().sort_index()
)


# =========================================================
# TRAIN / TEST SPLIT
# =========================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y,
)

print("\n========== SPLIT ==========")

print(
    f"Training samples: {len(X_train)}"
)

print(
    f"Testing samples : {len(X_test)}"
)


# =========================================================
# RANDOM FOREST
# =========================================================

print("\nTraining Random Forest...")

model = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    class_weight="balanced",
    n_jobs=-1,
)

model.fit(
    X_train,
    y_train,
)


# =========================================================
# PREDICTION
# =========================================================

y_pred = model.predict(X_test)


# =========================================================
# METRICS
# =========================================================

accuracy = accuracy_score(
    y_test,
    y_pred,
)

precision = precision_score(
    y_test,
    y_pred,
    pos_label=0,
)

recall = recall_score(
    y_test,
    y_pred,
    pos_label=0,
)

f1 = f1_score(
    y_test,
    y_pred,
    pos_label=0,
)

cm = confusion_matrix(
    y_test,
    y_pred,
    labels=[0, 1],
)


# =========================================================
# RESULTS
# =========================================================

print("\n========== RESULTS ==========")

print(
    f"Accuracy  : {accuracy:.6f}"
)

print(
    f"Precision : {precision:.6f}"
)

print(
    f"Recall    : {recall:.6f}"
)

print(
    f"F1 Score  : {f1:.6f}"
)

print("\nConfusion Matrix:")

print(cm)

print("\nClassification Report:")

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


# =========================================================
# FEATURE IMPORTANCE
# =========================================================

importance_df = pd.DataFrame(
    {
        "feature": FEATURE_NAMES,
        "importance": model.feature_importances_,
    }
).sort_values(
    "importance",
    ascending=False,
)

print("\n========== TOP FEATURES ==========")

print(
    importance_df.head(15).to_string(
        index=False
    )
)


# =========================================================
# SAVE MODEL
# =========================================================

model_path = os.path.join(
    MODEL_DIR,
    "url_only_random_forest.joblib",
)

joblib.dump(
    model,
    model_path,
)


# Save feature names
features_path = os.path.join(
    MODEL_DIR,
    "url_only_features.txt",
)

with open(
    features_path,
    "w",
    encoding="utf-8",
) as f:

    for feature in FEATURE_NAMES:
        f.write(
            feature + "\n"
        )


# Save comparison report
report_path = os.path.join(
    REPORT_DIR,
    "url_only_model_results.csv",
)

pd.DataFrame(
    [
        {
            "model": "Random Forest URL-only",
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
        }
    ]
).to_csv(
    report_path,
    index=False,
)


print("\n========== SAVED ==========")

print(
    f"Model: {model_path}"
)

print(
    f"Features: {features_path}"
)

print(
    f"Report: {report_path}"
)