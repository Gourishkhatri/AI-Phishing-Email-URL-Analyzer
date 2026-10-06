import pandas as pd
from pathlib import Path

RAW_DATASET = Path(
    "dataset/raw/PhiUSIIL_Phishing_URL_Dataset.csv"
)

PROCESSED_DATASET = Path(
    "dataset/processed/phishing_url_features.csv"
)

FEATURES = [
    "URLLength",
    "DomainLength",
    "IsDomainIP",
    "URLSimilarityIndex",
    "CharContinuationRate",
    "TLDLegitimateProb",
    "URLCharProb",
    "TLDLength",
    "NoOfSubDomain",
    "HasObfuscation",
    "NoOfObfuscatedChar",
    "ObfuscationRatio",
    "NoOfLettersInURL",
    "LetterRatioInURL",
    "NoOfDegitsInURL",
    "DegitRatioInURL",
    "NoOfEqualsInURL",
    "NoOfQMarkInURL",
    "NoOfAmpersandInURL",
    "NoOfOtherSpecialCharsInURL",
    "SpacialCharRatioInURL",
    "IsHTTPS",
    "NoOfURLRedirect",
    "NoOfSelfRedirect",
    "HasExternalFormSubmit",
    "HasPasswordField",
    "Bank",
    "Pay",
    "Crypto",
    "NoOfSelfRef",
    "NoOfEmptyRef",
    "NoOfExternalRef",
]

TARGET = "label"


def main():
    print("Loading dataset...")
    df = pd.read_csv(RAW_DATASET)

    print(f"Original shape: {df.shape}")

    # Select ML features + target
    selected_columns = FEATURES + [TARGET]
    processed_df = df[selected_columns].copy()

    # Remove rows containing missing values
    before = len(processed_df)
    processed_df = processed_df.dropna()
    removed = before - len(processed_df)

    # Remove duplicate rows
    before = len(processed_df)
    processed_df = processed_df.drop_duplicates()
    duplicates_removed = before - len(processed_df)

    # Ensure target is integer
    processed_df[TARGET] = processed_df[TARGET].astype(int)

    # Save processed dataset
    PROCESSED_DATASET.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    processed_df.to_csv(
        PROCESSED_DATASET,
        index=False
    )

    print("\n========== PREPROCESSING COMPLETE ==========")
    print(f"Original rows       : {len(df):,}")
    print(f"Missing rows removed: {removed:,}")
    print(f"Duplicates removed  : {duplicates_removed:,}")
    print(f"Final rows          : {len(processed_df):,}")
    print(f"Features            : {len(FEATURES)}")
    print(f"Output              : {PROCESSED_DATASET}")

    print("\n========== LABEL DISTRIBUTION ==========")
    print(processed_df[TARGET].value_counts())

    print("\n========== FINAL SHAPE ==========")
    print(processed_df.shape)


if __name__ == "__main__":
    main()