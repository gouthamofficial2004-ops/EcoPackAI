
import pandas as pd
from functools import lru_cache

from src.recommendation_engine import (
    products_df,
    materials_df,
    recommend_materials,
)


# --------------------------------------------------
# 1. DASHBOARD FILTER OPTIONS
# --------------------------------------------------

def get_dashboard_filter_options():
    """Return available industry and material category filters."""

    return {
        "industries": sorted(
            products_df["industry"].dropna().astype(str).unique().tolist()
        ),
        "material_categories": sorted(
            materials_df["material_category"].dropna().astype(str).unique().tolist()
        ),
    }


# --------------------------------------------------
# 2. CACHED DASHBOARD ANALYTICS
# --------------------------------------------------

@lru_cache(maxsize=8)
def _calculate_dashboard_data_cached(
    industry=None,
    material_category=None,
    product_search=None,
):
    """
    Calculate dashboard analytics.

    Cache up to eight filter combinations to avoid
    repeating expensive model predictions.
    """

    selected_products = products_df.copy()

    if industry:
        selected_products = selected_products[
            selected_products["industry"].astype(str) == str(industry)
        ]

    if product_search:
        search_value = str(product_search).strip().lower()

        selected_products = selected_products[
            selected_products["product_id"].astype(str).str.lower().str.contains(
                search_value, regex=False
            )
        ]

    product_results = []
    material_usage = []

    # Process products sequentially to control temporary memory use.
    for _, product in selected_products.iterrows():

        product_id = product["product_id"]

        recommendations = recommend_materials(
            product_id,
            top_n=len(materials_df),
        )

        if recommendations.empty:
            continue

        if material_category:
            recommendations = recommendations[
                recommendations["material_category"].astype(str)
                == str(material_category)
            ]

        if recommendations.empty:
            continue

        best = recommendations.iloc[0]

        average_cost = recommendations["predicted_cost_inr"].mean()
        average_co2 = recommendations["predicted_co2_kg"].mean()

        recommended_cost = best["predicted_cost_inr"]
        recommended_co2 = best["predicted_co2_kg"]

        cost_difference = average_cost - recommended_cost
        co2_reduction = average_co2 - recommended_co2

        cost_difference_percent = (
            cost_difference / average_cost * 100
            if average_cost > 0 else 0
        )

        co2_reduction_percent = (
            co2_reduction / average_co2 * 100
            if average_co2 > 0 else 0
        )

        product_results.append({
            "product_id": product_id,
            "product_type": product["product_type"],
            "industry": product["industry"],
            "material_name": best["material_name"],
            "material_category": best["material_category"],
            "predicted_cost_inr": recommended_cost,
            "predicted_co2_kg": recommended_co2,
            "average_eligible_cost_inr": average_cost,
            "average_eligible_co2_kg": average_co2,
            "potential_cost_saving_inr": cost_difference,
            "potential_co2_reduction_kg": co2_reduction,
            "potential_cost_saving_percent": cost_difference_percent,
            "potential_co2_reduction_percent": co2_reduction_percent,
            "eligible_material_count": len(recommendations),
        })

        material_usage.append({
            "material_name": best["material_name"],
            "material_category": best["material_category"],
            "industry": product["industry"],
        })

    # --------------------------------------------------
    # 3. PRODUCT ANALYTICS DATAFRAME
    # --------------------------------------------------

    product_columns = [
        "product_id",
        "product_type",
        "industry",
        "material_name",
        "material_category",
        "predicted_cost_inr",
        "predicted_co2_kg",
        "average_eligible_cost_inr",
        "average_eligible_co2_kg",
        "potential_cost_saving_inr",
        "potential_co2_reduction_kg",
        "potential_cost_saving_percent",
        "potential_co2_reduction_percent",
        "eligible_material_count",
    ]

    product_analytics = pd.DataFrame(
        product_results,
        columns=product_columns,
    )

    usage_data = pd.DataFrame(
        material_usage,
        columns=[
            "material_name",
            "material_category",
            "industry",
        ],
    )

    # --------------------------------------------------
    # 4. KPI CALCULATIONS
    # --------------------------------------------------

    total_products = len(selected_products)
    eligible_products = len(product_analytics)

    if product_analytics.empty:

        kpis = {
            "total_products_in_dataset": total_products,
            "eligible_products": 0,
            "products_without_recommendations": total_products,
            "average_potential_co2_reduction_percent": 0.0,
            "average_potential_cost_difference_inr": 0.0,
            "average_potential_cost_difference_percent": 0.0,
            "average_recommended_cost_inr": 0.0,
            "average_recommended_co2_kg": 0.0,
        }

    else:

        kpis = {
            "total_products_in_dataset": total_products,
            "eligible_products": eligible_products,
            "products_without_recommendations": (
                total_products - eligible_products
            ),
            "average_potential_co2_reduction_percent": (
                product_analytics["potential_co2_reduction_percent"].mean()
            ),
            "average_potential_cost_difference_inr": (
                product_analytics["potential_cost_saving_inr"].mean()
            ),
            "average_potential_cost_difference_percent": (
                product_analytics["potential_cost_saving_percent"].mean()
            ),
            "average_recommended_cost_inr": (
                product_analytics["predicted_cost_inr"].mean()
            ),
            "average_recommended_co2_kg": (
                product_analytics["predicted_co2_kg"].mean()
            ),
        }

    # --------------------------------------------------
    # 5. MATERIAL TRENDS
    # --------------------------------------------------

    material_trends = (
        usage_data
        .groupby(
            ["material_name", "material_category"],
            as_index=False,
        )
        .size()
        .rename(columns={"size": "recommendation_count"})
        .sort_values("recommendation_count", ascending=False)
    )

    # --------------------------------------------------
    # 6. INDUSTRY TRENDS
    # --------------------------------------------------

    industry_trends = (
        usage_data
        .groupby(
            ["industry", "material_category"],
            as_index=False,
        )
        .size()
        .rename(columns={"size": "recommendation_count"})
    )

    return {
        "kpis": kpis,
        "product_analytics": product_analytics,
        "material_trends": material_trends,
        "industry_trends": industry_trends,
    }


# --------------------------------------------------
# 7. PUBLIC DASHBOARD ANALYTICS FUNCTION
# --------------------------------------------------

def calculate_dashboard_data(
    industry=None,
    material_category=None,
    product_search=None,
):
    """
    Return cached analytics for the requested filters.

    Identical filter combinations reuse previous results.
    """

    industry = str(industry).strip() if industry else None

    material_category = (
        str(material_category).strip()
        if material_category else None
    )

    product_search = (
        str(product_search).strip()
        if product_search else None
    )

    return _calculate_dashboard_data_cached(
        industry,
        material_category,
        product_search,
    )
