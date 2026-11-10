
from pathlib import Path
import pandas as pd

# Project root directory
ROOT = Path(__file__).resolve().parent.parent

# Dataset locations
files = {
    "Materials": ROOT / "data" / "raw" / "materials.csv",
    "Products": ROOT / "data" / "raw" / "products.csv",
    "Training Data": ROOT / "data" / "processed" / "training_data.csv",
    "Data Dictionary": ROOT / "data" / "data_dictionary.csv"}

for name, path in files.items():
    print("\n" + "=" * 60)
    print(f"DATASET: {name}")
    print("=" * 60)

    if not path.exists():
        print(f"FILE NOT FOUND: {path}")
        continue

    df = pd.read_csv(path)

    print("Rows and columns:", df.shape)
    print("\nColumn names:")
    print(df.columns.tolist())

    print("\nMissing values:")
    print(df.isnull().sum())

    print("\nDuplicate rows:", df.duplicated().sum())

    print("\nData types:")
    print(df.dtypes)

    if "material_id" in df.columns:
        print(
            "Duplicate material IDs:",
            df["material_id"].duplicated().sum()
        )

    if "product_id" in df.columns and name == "Products":
        print(
            "Duplicate product IDs:",
            df["product_id"].duplicated().sum()
        )

print("\nDATA AUDIT COMPLETED")
