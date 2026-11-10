
from pathlib import Path

import joblib
import numpy as np
import pandas as pd


# --------------------------------------------------
# 1. PROJECT PATHS AND CONFIGURATION
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data" / "processed"
MODEL_DIR = PROJECT_ROOT / "models"

MATERIALS_FILE = DATA_DIR / "materials_feature_engineered.csv"
PRODUCTS_FILE = DATA_DIR / "products_cleaned.csv"

PREPROCESSOR_FILE = MODEL_DIR / "preprocessor.pkl"

# Verified compressed cost model
COST_MODEL_FILE = MODEL_DIR / "cost_random_forest_compressed.pkl"

# Original CO2 model (not compressed)
CO2_MODEL_FILE = MODEL_DIR / "co2_xgboost.pkl"

MIN_MOISTURE_RESISTANCE = 60

RANKING_WEIGHTS = {
    "co2": 0.40,
    "biodegradability": 0.25,
    "recyclability": 0.20,
    "cost": 0.15,
}


# --------------------------------------------------
# 2. MODEL FEATURES
# --------------------------------------------------

MODEL_FEATURES = [
    "industry",
    "product_weight_kg",
    "fragility_score",
    "moisture_sensitive",
    "required_strength_score",
    "budget_per_pack_inr",
    "material_category",
    "strength_score",
    "max_weight_capacity_kg",
    "biodegradability_score",
    "recyclability_percent",
    "co2_kg_per_kg_material",
    "cost_inr_per_kg",
    "moisture_resistance_score",
    "durability_score",
    "estimated_packaging_mass",
]


CUSTOM_PRODUCT_FIELDS = [
    "industry",
    "product_weight_kg",
    "fragility_score",
    "moisture_sensitive",
    "required_strength_score",
    "budget_per_pack_inr",
]


# --------------------------------------------------
# 3. LOAD DATASETS AND TRAINED MODELS
# --------------------------------------------------

materials_df = pd.read_csv(MATERIALS_FILE)
products_df = pd.read_csv(PRODUCTS_FILE)

preprocessor = joblib.load(PREPROCESSOR_FILE)
cost_model = joblib.load(COST_MODEL_FILE)
co2_model = joblib.load(CO2_MODEL_FILE)


# --------------------------------------------------
# 4. VALIDATE CONFIGURATION
# --------------------------------------------------

if not np.isclose(sum(RANKING_WEIGHTS.values()), 1.0):
    raise ValueError("Recommendation weights must sum to 1.")

if materials_df["material_id"].duplicated().any():
    raise ValueError("Duplicate material IDs found.")

if products_df["product_id"].duplicated().any():
    raise ValueError("Duplicate product IDs found.")

if materials_df.empty or products_df.empty:
    raise ValueError("Product or material dataset is empty.")

if not set(MODEL_FEATURES).issubset(
    set(products_df.columns).union(set(materials_df.columns))
    | {"estimated_packaging_mass"}
):
    raise ValueError("Required model features are missing.")


# --------------------------------------------------
# 5. RESULT COLUMNS
# --------------------------------------------------

RESULT_COLUMNS = [
    "rank",
    "material_id",
    "material_name",
    "material_category",
    "predicted_cost_inr",
    "predicted_co2_kg",
    "biodegradability_score",
    "recyclability_percent",
    "co2_score",
    "cost_score",
    "final_score",
    "recommendation_reason",
]


# --------------------------------------------------
# 6. INPUT VALIDATION
# --------------------------------------------------

def validate_top_n(top_n):

    if (
        not isinstance(top_n, (int, np.integer))
        or isinstance(top_n, (bool, np.bool_))
        or top_n < 1
        or top_n > len(materials_df)
    ):
        raise ValueError(
            f"top_n must be between 1 and {len(materials_df)}."
        )


def validate_custom_product(product_data):

    if not isinstance(product_data, dict):
        raise ValueError("Product details must be a JSON object.")

    missing_fields = [
        field for field in CUSTOM_PRODUCT_FIELDS
        if field not in product_data
    ]

    if missing_fields:
        raise ValueError(
            "Missing required fields: "
            + ", ".join(missing_fields)
        )

    industry = product_data["industry"]

    if not isinstance(industry, str) or not industry.strip():
        raise ValueError("A valid industry is required.")

    valid_industries = products_df["industry"].dropna().unique()

    if industry.strip() not in valid_industries:
        raise ValueError(
            "Unsupported industry. Available industries: "
            + ", ".join(sorted(valid_industries))
        )

    numeric_fields = [
        "product_weight_kg",
        "fragility_score",
        "required_strength_score",
        "budget_per_pack_inr",
    ]

    validated = {
        "industry": industry.strip()
    }

    for field in numeric_fields:

        value = product_data[field]

        if isinstance(value, (bool, np.bool_)):
            raise ValueError(f"{field} must be numeric.")

        try:
            number = float(value)
        except (TypeError, ValueError):
            raise ValueError(f"{field} must be numeric.")

        if not np.isfinite(number):
            raise ValueError(f"{field} must be finite.")

        validated[field] = number

    if validated["product_weight_kg"] <= 0:
        raise ValueError("Product weight must be greater than zero.")

    if not 1 <= validated["fragility_score"] <= 100:
        raise ValueError("Fragility score must be between 1 and 100.")

    if not 1 <= validated["required_strength_score"] <= 100:
        raise ValueError(
            "Required strength score must be between 1 and 100."
        )

    if validated["budget_per_pack_inr"] <= 0:
        raise ValueError("Budget must be greater than zero.")

    moisture = product_data["moisture_sensitive"]

    if isinstance(moisture, (bool, np.bool_)):
        validated["moisture_sensitive"] = int(moisture)

    elif moisture in (0, 1, "0", "1"):
        validated["moisture_sensitive"] = int(moisture)

    else:
        raise ValueError(
            "Moisture sensitivity must be 0 or 1."
        )

    return validated


# --------------------------------------------------
# 7. BUILD PRODUCT-MATERIAL CANDIDATES
# --------------------------------------------------

def build_candidates(product_data):

    product_df = pd.DataFrame([product_data])

    candidates = product_df.merge(
        materials_df,
        how="cross"
    )

    # Existing synthetic packaging-mass assumption.
    candidates["estimated_packaging_mass"] = (
        0.075 * candidates["product_weight_kg"]
    ).clip(lower=0.025)

    return candidates


# --------------------------------------------------
# 8. GENERATE MODEL PREDICTIONS
# --------------------------------------------------

def predict_candidates(candidates):

    features = candidates[MODEL_FEATURES].copy()

    processed_features = preprocessor.transform(features)

    candidates = candidates.copy()

    candidates["predicted_cost_inr"] = cost_model.predict(
        processed_features
    )

    candidates["predicted_co2_kg"] = co2_model.predict(
        processed_features
    )

    predictions = candidates[
        ["predicted_cost_inr", "predicted_co2_kg"]
    ].to_numpy()

    if not np.isfinite(predictions).all():
        raise ValueError("Model generated invalid predictions.")

    if (predictions < 0).any():
        raise ValueError("Negative cost or CO2 prediction detected.")

    return candidates


# --------------------------------------------------
# 9. RECOMMENDATION ELIGIBILITY
# --------------------------------------------------

def evaluate_candidates(candidates):

    candidates = candidates.copy()

    candidates["technical_pass"] = (
        (
            candidates["strength_score"]
            >= candidates["required_strength_score"]
        )
        &
        (
            candidates["max_weight_capacity_kg"]
            >= candidates["product_weight_kg"]
        )
    )

    candidates["moisture_pass"] = (
        (candidates["moisture_sensitive"] == 0)
        |
        (
            candidates["moisture_resistance_score"]
            >= MIN_MOISTURE_RESISTANCE
        )
    )

    candidates["budget_pass"] = (
        candidates["predicted_cost_inr"]
        <= candidates["budget_per_pack_inr"]
    )

    candidates["eligible"] = (
        candidates["technical_pass"]
        & candidates["moisture_pass"]
        & candidates["budget_pass"]
    )

    return candidates


# --------------------------------------------------
# 10. RECOMMENDATION RANKING
# --------------------------------------------------

def rank_candidates(candidates, top_n=10):

    validate_top_n(top_n)

    eligible = candidates[
        candidates["eligible"]
    ].copy()

    if eligible.empty:
        return pd.DataFrame(columns=RESULT_COLUMNS)

    def lower_is_better(series):

        minimum = series.min()
        maximum = series.max()

        if maximum == minimum:
            return pd.Series(100.0, index=series.index)

        return (
            (maximum - series) / (maximum - minimum)
        ) * 100

    eligible["co2_score"] = lower_is_better(
        eligible["predicted_co2_kg"]
    )

    eligible["cost_score"] = lower_is_better(
        eligible["predicted_cost_inr"]
    )

    eligible["final_score"] = (
        eligible["co2_score"] * RANKING_WEIGHTS["co2"]
        + eligible["biodegradability_score"]
        * RANKING_WEIGHTS["biodegradability"]
        + eligible["recyclability_percent"]
        * RANKING_WEIGHTS["recyclability"]
        + eligible["cost_score"] * RANKING_WEIGHTS["cost"]
    )

    eligible["recommendation_reason"] = (
        "Passed strength, capacity, moisture and budget checks."
    )

    eligible = eligible.sort_values(
        by=[
            "final_score",
            "predicted_co2_kg",
            "predicted_cost_inr",
        ],
        ascending=[False, True, True],
        kind="stable",
    ).reset_index(drop=True)

    eligible["rank"] = range(1, len(eligible) + 1)

    return eligible[RESULT_COLUMNS].head(top_n)


# --------------------------------------------------
# 11. PREPARE EXISTING PRODUCT CANDIDATES
# --------------------------------------------------

candidate_analysis = build_candidates(
    products_df.drop(columns=["product_id", "product_type"]).assign(
        product_id=products_df["product_id"].values,
        product_type=products_df["product_type"].values,
    ).to_dict(orient="records")[0]
) if False else None


# Build the complete existing product-material dataset.
candidate_analysis = products_df.merge(
    materials_df,
    how="cross"
)

candidate_analysis["estimated_packaging_mass"] = (
    0.075 * candidate_analysis["product_weight_kg"]
).clip(lower=0.025)

candidate_analysis = predict_candidates(candidate_analysis)


# --------------------------------------------------
# 12. EXISTING PRODUCT RECOMMENDATIONS
# --------------------------------------------------

def recommend_materials(product_id, top_n=10):

    validate_top_n(top_n)

    product_matches = products_df[
        products_df["product_id"] == product_id
    ]

    if len(product_matches) != 1:
        raise ValueError(
            f"Expected one product for {product_id}, "
            f"but found {len(product_matches)}."
        )

    candidates = candidate_analysis[
        candidate_analysis["product_id"] == product_id
    ].copy()

    candidates = evaluate_candidates(candidates)

    return rank_candidates(candidates, top_n)


# --------------------------------------------------
# 13. CUSTOM PRODUCT RECOMMENDATIONS
# --------------------------------------------------

def recommend_materials_for_custom_product(
    product_data,
    top_n=10
):

    validate_top_n(top_n)

    validated_product = validate_custom_product(
        product_data
    )

    candidates = build_candidates(
        validated_product
    )

    candidates = predict_candidates(candidates)

    candidates = evaluate_candidates(candidates)

    return rank_candidates(candidates, top_n)


# --------------------------------------------------
# 14. RECOMMENDATION FAILURE EXPLANATION
# --------------------------------------------------

def diagnose_candidates(candidates):

    total = len(candidates)

    technical_count = int(
        candidates["technical_pass"].sum()
    )

    technical_moisture_count = int(
        (
            candidates["technical_pass"]
            & candidates["moisture_pass"]
        ).sum()
    )

    technical_budget_count = int(
        (
            candidates["technical_pass"]
            & candidates["budget_pass"]
        ).sum()
    )

    eligible_count = int(
        candidates["eligible"].sum()
    )

    reasons = []

    if technical_count == 0:
        reasons.append(
            "No material satisfies both strength and weight capacity."
        )

    elif technical_moisture_count == 0:
        reasons.append(
            "No technically suitable material satisfies moisture resistance."
        )

    elif technical_budget_count == 0:
        reasons.append(
            "No technically suitable material is within the specified budget."
        )

    elif eligible_count == 0:
        reasons.append(
            "No material satisfies all technical, moisture and budget conditions together."
        )

    else:
        reasons.append(
            "Suitable materials are available."
        )

    return {
        "total_materials_evaluated": total,
        "technical_pass": technical_count,
        "technical_and_moisture_pass": technical_moisture_count,
        "technical_and_budget_pass": technical_budget_count,
        "eligible_materials": eligible_count,
        "failure_reasons": reasons,
    }


def diagnose_product(product_id):

    product_matches = products_df[
        products_df["product_id"] == product_id
    ]

    if len(product_matches) != 1:
        raise ValueError(
            f"Expected one product for {product_id}."
        )

    candidates = candidate_analysis[
        candidate_analysis["product_id"] == product_id
    ].copy()

    candidates = evaluate_candidates(candidates)

    return diagnose_candidates(candidates)


def diagnose_custom_product(product_data):

    validated_product = validate_custom_product(
        product_data
    )

    candidates = build_candidates(
        validated_product
    )

    candidates = predict_candidates(candidates)

    candidates = evaluate_candidates(candidates)

    return diagnose_candidates(candidates)


# --------------------------------------------------
# 15. INPUT RANGE WARNINGS
# --------------------------------------------------

def get_custom_product_warnings(product_data):

    validated = validate_custom_product(product_data)

    warnings = []

    numeric_fields = [
        "product_weight_kg",
        "fragility_score",
        "required_strength_score",
        "budget_per_pack_inr",
    ]

    for field in numeric_fields:

        training_min = float(products_df[field].min())
        training_max = float(products_df[field].max())

        value = validated[field]

        if value < training_min or value > training_max:
            warnings.append(
                f"{field} is outside the observed training-data "
                f"range ({training_min:.2f} to {training_max:.2f}). "
                "Predictions may be less reliable."
            )

    return warnings
