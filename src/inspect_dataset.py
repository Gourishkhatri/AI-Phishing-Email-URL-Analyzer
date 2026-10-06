import pandas as pd
from pathlib import Path

# Dataset path
dataset_path = Path(
    "dataset/raw/PhiUSIIL_Phishing_URL_Dataset.csv"
)

# Load dataset
df = pd.read_csv(dataset_path)

print("\n========== DATASET OVERVIEW ==========")
print(f"Rows    : {df.shape[0]:,}")
print(f"Columns : {df.shape[1]:,}")

print("\n========== COLUMN NAMES ==========")
for i, column in enumerate(df.columns, start=1):
    print(f"{i:02d}. {column}")

print("\n========== FIRST 5 ROWS ==========")
print(df.head())

print("\n========== DATA TYPES ==========")
print(df.dtypes)

print("\n========== MISSING VALUES ==========")
missing = df.isnull().sum()
print(missing[missing > 0])

print("\n========== DUPLICATE ROWS ==========")
print(df.duplicated().sum())

print("\n========== UNIQUE VALUES ==========")
print(df.nunique())

print("\n========== DATASET INFO ==========")
df.info()