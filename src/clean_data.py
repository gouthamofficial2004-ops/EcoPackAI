
from pathlib import Path
import pandas as pd

# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent

RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# 2. LOAD DATASETS
# --------------------------------------------------

materials = pd.read_csv(RAW_DIR / "materials.csv")
products = pd.read_csv(RAW_DIR / "products.csv")
training = pd.read_csv(PROCESSED_DIR / "training_data.csv")


# --------------------------------------------------
# 3. REMOVE DUPLICATE RECORDS
# --------------------------------------------------

materials = materials.drop_duplicates(subset="material_id")
products = products.drop_duplicates(subset="product_id")

training = training.drop_duplicates(
    subset=["product_id", "material_id"]
)


# --------------------------------------------------
# 4. HANDLE MISSING VALUES
# --------------------------------------------------

# Remove records without essential identifiers
materials = materials.dropna(subset=["material_id", "material_name"])
products = products.dropna(subset=["product_id", "product_type"])

training = training.dropna(
    subset=["product_id", "material_id"]
)

# Fill missing numerical values using median
for df in [materials, products, training]:
    numeric_columns = df.select_dtypes(include="number").columns

    for column in numeric_columns:
        if df[column].isna().any():
            df[column] = df[column].fillna(df[column].median())


# --------------------------------------------------
# 5. VALIDATE NUMERICAL RANGES
# --------------------------------------------------

score_columns = [
    (materials, [
        "biodegradability_score",
        "recyclability_percent",
        "moisture_resistance_score",
        "durability_score"
    ]),
    (products, [
        "fragility_score",
        "required_strength_score"
    ])
]

for df, columns in score_columns:
    for column in columns:
        df[column] = df[column].clip(lower=0, upper=100)

# Product weight and budget must be positive
products = products[
    (products["product_weight_kg"] > 0) &
    (products["budget_per_pack_inr"] > 0)
]


# --------------------------------------------------
# 6. CHECK RELATIONSHIPS BETWEEN DATASETS
# --------------------------------------------------

valid_material_ids = set(materials["material_id"])
valid_product_ids = set(products["product_id"])

training = training[
    training["material_id"].isin(valid_material_ids) &
    training["product_id"].isin(valid_product_ids)
]


# --------------------------------------------------
# 7. SAVE CLEANED DATASETS
# --------------------------------------------------

materials.to_csv(
    PROCESSED_DIR / "materials_cleaned.csv",
    index=False
)

products.to_csv(
    PROCESSED_DIR / "products_cleaned.csv",
    index=False
)

training.to_csv(
    PROCESSED_DIR / "training_data_cleaned.csv",
    index=False
)


# --------------------------------------------------
# 8. DISPLAY FINAL SUMMARY
# --------------------------------------------------

print("\n" + "=" * 55)
print("ECOPACKAI DATA CLEANING SUMMARY")
print("=" * 55)

print("Materials cleaned:", len(materials))
print("Products cleaned:", len(products))
print("Training records cleaned:", len(training))

print("\nRemaining missing values:")
print("Materials:", materials.isna().sum().sum())
print("Products:", products.isna().sum().sum())
print("Training:", training.isna().sum().sum())

print("\nCleaned datasets saved successfully!")
print("=" * 55)
