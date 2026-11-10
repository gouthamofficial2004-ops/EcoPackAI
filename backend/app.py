import os
from flask import Flask, jsonify, render_template, request
from sqlalchemy import text

from src.recommendation_engine import (
    recommend_materials,
    recommend_materials_for_custom_product,
    diagnose_custom_product,
    get_custom_product_warnings,
    RANKING_WEIGHTS
)
from backend.db import get_db_connection
from dashboard.app import dashboard_bp


# --------------------------------------------------
# Initialize Main EcoPackAI Flask Application
# --------------------------------------------------

app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static"
)

# Register BI Dashboard inside the SAME Flask application
app.register_blueprint(
    dashboard_bp,
    url_prefix="/dashboard"
)


# --------------------------------------------------
# Shared Helpers
# --------------------------------------------------

def dataframe_to_records(dataframe):
    """Convert a DataFrame into JSON-safe records."""
    return dataframe.astype(object).where(
        dataframe.notna(), None
    ).to_dict(orient="records")


def calculate_environmental_score(recommendations):
    """
    Calculate the best environmental score.
    Cost is intentionally excluded.
    """

    if recommendations.empty:
        return None

    environmental_weight = (
        RANKING_WEIGHTS["co2"]
        + RANKING_WEIGHTS["biodegradability"]
        + RANKING_WEIGHTS["recyclability"]
    )

    scored = recommendations.copy()

    scored["environmental_score"] = (
        scored["co2_score"] * RANKING_WEIGHTS["co2"]
        + scored["biodegradability_score"]
        * RANKING_WEIGHTS["biodegradability"]
        + scored["recyclability_percent"]
        * RANKING_WEIGHTS["recyclability"]
    ) / environmental_weight

    best = scored.sort_values(
        by="environmental_score",
        ascending=False
    ).iloc[0]

    return {
        "best_material": str(best["material_name"]),
        "environmental_score": float(best["environmental_score"]),
        "co2_score": float(best["co2_score"]),
        "biodegradability_score": float(
            best["biodegradability_score"]
        ),
        "recyclability_percent": float(
            best["recyclability_percent"]
        ),
        "score_method": "Weighted environmental score excluding cost"
    }


def validate_top_n(top_n):
    return (
        isinstance(top_n, int)
        and not isinstance(top_n, bool)
        and 1 <= top_n <= 120
    )


# --------------------------------------------------
# Home Route
# --------------------------------------------------

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


# --------------------------------------------------
# Health Check API
# --------------------------------------------------

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "module": "EcoPackAI Integrated Flask Application"
    }), 200


# --------------------------------------------------
# Database Health Check API
# --------------------------------------------------

@app.route("/api/database-status", methods=["GET"])
def database_status():
    try:
        with get_db_connection() as connection:

            material_count = connection.execute(
                text("SELECT COUNT(*) FROM materials")
            ).scalar()

            product_count = connection.execute(
                text("SELECT COUNT(*) FROM products")
            ).scalar()

            training_count = connection.execute(
                text("SELECT COUNT(*) FROM training_data")
            ).scalar()

        return jsonify({
            "status": "success",
            "database": "PostgreSQL",
            "connection": "connected",
            "tables": {
                "materials": material_count,
                "products": product_count,
                "training_data": training_count
            }
        }), 200

    except Exception:
        app.logger.exception("Database health check failed")

        return jsonify({
            "status": "error",
            "connection": "failed",
            "message": "Unable to connect to the database."
        }), 500


# --------------------------------------------------
# Get Available Products API
# --------------------------------------------------

@app.route("/api/products", methods=["GET"])
def get_products():
    try:
        with get_db_connection() as connection:

            result = connection.execute(
                text("""
                    SELECT product_id, product_type, industry
                    FROM products
                    ORDER BY product_id
                """)
            )

            products = [
                {
                    "product_id": row.product_id,
                    "product_type": row.product_type,
                    "industry": row.industry
                }
                for row in result
            ]

        return jsonify({
            "status": "success",
            "total_products": len(products),
            "products": products
        }), 200

    except Exception:
        app.logger.exception("Product retrieval failed")

        return jsonify({
            "status": "error",
            "message": "Unable to retrieve products."
        }), 500


# --------------------------------------------------
# Existing Product Recommendation API
# --------------------------------------------------

@app.route("/api/recommendations", methods=["POST"])
def get_recommendations():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "status": "error",
            "message": "Request body must be a valid JSON object."
        }), 400

    product_id = data.get("product_id")
    top_n = data.get("top_n", 10)

    if not isinstance(product_id, str) or not product_id.strip():
        return jsonify({
            "status": "error",
            "message": "A valid product_id is required."
        }), 400

    if not validate_top_n(top_n):
        return jsonify({
            "status": "error",
            "message": "top_n must be an integer between 1 and 120."
        }), 400

    try:
        recommendations = recommend_materials(
            product_id=product_id.strip(),
            top_n=top_n
        )

        if recommendations.empty:
            return jsonify({
                "status": "no_recommendations",
                "product_id": product_id.strip(),
                "message": "No eligible packaging materials found.",
                "recommendations": []
            }), 200

        return jsonify({
            "status": "success",
            "product_id": product_id.strip(),
            "total_recommendations": len(recommendations),
            "recommendations": dataframe_to_records(recommendations)
        }), 200

    except ValueError as error:
        return jsonify({
            "status": "error",
            "message": str(error)
        }), 400

    except Exception:
        app.logger.exception("Recommendation API failed")

        return jsonify({
            "status": "error",
            "message": "Internal recommendation error."
        }), 500


# --------------------------------------------------
# Custom Product Recommendation API
# --------------------------------------------------

@app.route("/api/custom-recommendations", methods=["POST"])
def custom_recommendations():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "status": "error",
            "message": "Request body must be a valid JSON object."
        }), 400

    custom_product = {
        "industry": data.get("industry"),
        "product_weight_kg": data.get("product_weight_kg"),
        "fragility_score": data.get("fragility_score"),
        "moisture_sensitive": data.get("moisture_sensitive"),
        "required_strength_score": data.get(
            "required_strength_score"
        ),
        "budget_per_pack_inr": data.get("budget_per_pack_inr")
    }

    top_n = data.get("top_n", 10)

    if not validate_top_n(top_n):
        return jsonify({
            "status": "error",
            "message": "top_n must be an integer between 1 and 120."
        }), 400

    try:
        # Validate and generate recommendations.
        # Evaluate all materials so environmental scoring
        # considers the complete eligible set.
        all_recommendations = recommend_materials_for_custom_product(
            custom_product,
            top_n=120
        )

        # Generate diagnostics and input warnings.
        diagnosis = diagnose_custom_product(custom_product)

        warnings = get_custom_product_warnings(custom_product)

        if all_recommendations.empty:
            return jsonify({
                "status": "no_recommendations",
                "message": (
                    "No packaging materials satisfy all "
                    "the specified product requirements."
                ),
                "diagnostics": diagnosis,
                "warnings": warnings,
                "total_recommendations": 0,
                "recommendations": [],
                "environmental_score": None
            }), 200

        # Calculate environmental score across all eligible materials.
        environmental_score = calculate_environmental_score(
            all_recommendations
        )

        # Return only the requested number of recommendations.
        displayed_recommendations = all_recommendations.head(top_n)

        return jsonify({
            "status": "success",
            "message": "Custom product recommendations generated.",
            "total_eligible_materials": len(all_recommendations),
            "total_recommendations": len(displayed_recommendations),
            "diagnostics": diagnosis,
            "warnings": warnings,
            "environmental_score": environmental_score,
            "recommendations": dataframe_to_records(
                displayed_recommendations
            )
        }), 200

    except ValueError as error:
        return jsonify({
            "status": "error",
            "message": str(error)
        }), 400

    except Exception:
        app.logger.exception("Custom recommendation API failed")

        return jsonify({
            "status": "error",
            "message": "Internal custom recommendation error."
        }), 500


# --------------------------------------------------
# Existing Product Environmental Score API
# --------------------------------------------------

@app.route("/api/environmental-score", methods=["POST"])
def environmental_score():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "status": "error",
            "message": "Request body must be valid JSON."
        }), 400

    product_id = data.get("product_id")

    if not isinstance(product_id, str) or not product_id.strip():
        return jsonify({
            "status": "error",
            "message": "A valid product_id is required."
        }), 400

    try:
        recommendations = recommend_materials(
            product_id.strip(),
            top_n=120
        )

        if recommendations.empty:
            return jsonify({
                "status": "no_recommendations",
                "product_id": product_id.strip(),
                "message": "No eligible materials found."
            }), 200

        score = calculate_environmental_score(recommendations)

        return jsonify({
            "status": "success",
            "product_id": product_id.strip(),
            **score
        }), 200

    except ValueError as error:
        return jsonify({
            "status": "error",
            "message": str(error)
        }), 400

    except Exception:
        app.logger.exception("Environmental Score API failed")

        return jsonify({
            "status": "error",
            "message": "Internal environmental score error."
        }), 500


# --------------------------------------------------
# Run ONE Integrated EcoPackAI Application
# --------------------------------------------------

if __name__ == "__main__":
    app.run(
        debug=os.getenv("FLASK_DEBUG", "false").lower() == "true",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "5000"))
    )