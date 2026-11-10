
from io import BytesIO
import math

import numpy as np
import pandas as pd

from flask import (
    Blueprint,
    current_app,
    jsonify,
    render_template_string,
    request,
    send_file,
)

from dashboard.analytics import (
    calculate_dashboard_data,
    get_dashboard_filter_options,
)

dashboard_bp = Blueprint("dashboard", __name__)


# --------------------------------------------------
# JSON CONVERSION
# --------------------------------------------------

def convert_to_json_safe(value):
    """Convert pandas and NumPy values into JSON-compatible values."""

    if isinstance(value, dict):
        return {
            str(key): convert_to_json_safe(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [convert_to_json_safe(item) for item in value]

    if isinstance(value, pd.DataFrame):
        return convert_to_json_safe(value.to_dict(orient="records"))

    if isinstance(value, pd.Series):
        return convert_to_json_safe(value.to_dict())

    if isinstance(value, np.ndarray):
        return convert_to_json_safe(value.tolist())

    if isinstance(value, np.generic):
        return convert_to_json_safe(value.item())

    if isinstance(value, float):
        return value if math.isfinite(value) else None

    if isinstance(value, pd.Timestamp):
        return value.isoformat()

    return value


# --------------------------------------------------
# FILTER HANDLING
# --------------------------------------------------

def get_active_filters():
    """Read selected filters from URL query parameters."""

    industry = request.args.get("industry", "").strip()

    material_category = request.args.get(
        "material_category", ""
    ).strip()

    product_search = request.args.get(
        "product_search", ""
    ).strip()

    return {
        "industry": industry or None,
        "material_category": material_category or None,
        "product_search": product_search or None,
    }


def get_filtered_dashboard_data(filters=None):
    """Calculate dashboard analytics using selected filters."""

    filters = filters or get_active_filters()

    return calculate_dashboard_data(
        industry=filters.get("industry"),
        material_category=filters.get("material_category"),
        product_search=filters.get("product_search"),
    )


# --------------------------------------------------
# CHART PREPARATION
# --------------------------------------------------

def prepare_dashboard(data):

    # Load Plotly only when the dashboard charts are prepared.
    import plotly.express as px

    product_df = data["product_analytics"]
    material_df = data["material_trends"]
    industry_df = data["industry_trends"]

    material_chart = px.bar(
        material_df.head(10),
        x="material_name",
        y="recommendation_count",
        color="material_category",
        labels={
            "material_name": "Material",
            "recommendation_count": "Top-ranked product count",
            "material_category": "Category",
        },
    )

    co2_by_industry = (
        product_df.groupby("industry", as_index=False)
        ["potential_co2_reduction_percent"]
        .mean()
        .sort_values(
            "potential_co2_reduction_percent",
            ascending=False,
        )
    )

    co2_chart = px.bar(
        co2_by_industry,
        x="industry",
        y="potential_co2_reduction_percent",
        labels={
            "industry": "Industry",
            "potential_co2_reduction_percent":
                "Potential CO2 difference (%)",
        },
    )

    cost_by_category = (
        product_df.groupby("material_category", as_index=False)
        ["potential_cost_saving_inr"]
        .mean()
    )

    cost_chart = px.bar(
        cost_by_category,
        x="material_category",
        y="potential_cost_saving_inr",
        color="material_category",
        labels={
            "material_category": "Material category",
            "potential_cost_saving_inr":
                "Average predicted cost difference (INR)",
        },
    )

    industry_chart = px.bar(
        industry_df,
        x="industry",
        y="recommendation_count",
        color="material_category",
        barmode="stack",
        labels={
            "industry": "Industry",
            "recommendation_count": "Top-ranked product count",
            "material_category": "Material category",
        },
    )

    return {
        "material_chart": material_chart.to_json(),
        "co2_chart": co2_chart.to_json(),
        "cost_chart": cost_chart.to_json(),
        "industry_chart": industry_chart.to_json(),
    }


# --------------------------------------------------
# DASHBOARD HTML
# --------------------------------------------------

DASHBOARD_HTML = r"""
<!DOCTYPE html>
<html lang="en">

<head>

<meta charset="UTF-8">

<meta name="viewport"
content="width=device-width, initial-scale=1.0">

<title>EcoPackAI | BI Dashboard</title>

<script src="https://cdn.plot.ly/plotly-3.0.1.min.js"></script>

<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Outfit:wght@500;600;700;800&display=swap"
rel="stylesheet">

<style>

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: 'DM Sans', sans-serif;
    background: #f5faf4;
    color: #24352c;
}

header {
    background: linear-gradient(110deg, #123d2b, #198754);
    color: white;
    padding: 20px 6%;
}

header h1 {
    margin: 0;
    font-family: 'Outfit', sans-serif;
    font-size: 30px;
}

header p {
    margin: 6px 0 0;
    color: #e5f5e9;
}

nav {
    display: flex;
    gap: 22px;
    flex-wrap: wrap;
    margin-top: 15px;
}

nav a {
    color: white;
    text-decoration: none;
    font-weight: 700;
}

main {
    max-width: 1250px;
    margin: 30px auto;
    padding: 0 20px;
}

.intro {
    margin-bottom: 20px;
}

.intro h2 {
    color: #123d2b;
    font-family: 'Outfit', sans-serif;
    font-size: 27px;
}

.muted {
    color: #718075;
}

.filter-card,
.kpi-card,
.chart-card,
.table-card,
.note-card {
    background: white;
    border: 1px solid #e1eee3;
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 5px 20px rgba(31, 75, 49, 0.05);
}

.filter-card {
    margin: 20px 0;
}

.filter-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 15px;
}

label {
    display: block;
    font-weight: 700;
    margin-bottom: 7px;
}

input,
select {
    width: 100%;
    padding: 11px;
    border: 1px solid #d5e5d8;
    border-radius: 9px;
    background: #fbfdfb;
    font: inherit;
}

.actions {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin-top: 16px;
}

.btn {
    display: inline-block;
    border: 0;
    border-radius: 9px;
    padding: 11px 17px;
    background: #198754;
    color: white;
    text-decoration: none;
    font-weight: 700;
    cursor: pointer;
}

.btn.secondary {
    background: #e8f4eb;
    color: #145c39;
}

.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin: 20px 0;
}

.kpi-card p {
    color: #718075;
    font-size: 14px;
    margin: 0 0 8px;
}

.kpi-card h3 {
    font-family: 'Outfit', sans-serif;
    color: #198754;
    font-size: 27px;
    margin: 0;
}

.chart-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 18px;
}

.chart-card {
    min-width: 0;
}

.chart-card h3 {
    font-family: 'Outfit', sans-serif;
    color: #123d2b;
}

.chart {
    width: 100%;
    min-height: 340px;
}

.table-card {
    margin-top: 20px;
    overflow-x: auto;
}

table {
    width: 100%;
    border-collapse: collapse;
    min-width: 760px;
}

th,
td {
    padding: 11px;
    border-bottom: 1px solid #e5eee5;
    text-align: left;
}

th {
    background: #e5f5e9;
    color: #123d2b;
}

.note-card {
    margin-top: 18px;
    background: #fff9e9;
    border-left: 4px solid #e5a000;
    box-shadow: none;
}

footer {
    text-align: center;
    color: #718075;
    padding: 30px;
}

@media (max-width: 900px) {

    .kpi-grid {
        grid-template-columns: repeat(2, 1fr);
    }

    .chart-grid {
        grid-template-columns: 1fr;
    }

    .filter-grid {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 500px) {

    .kpi-grid {
        grid-template-columns: 1fr;
    }

    header h1 {
        font-size: 24px;
    }
}

</style>

</head>

<body>

<header>

    <h1>EcoPackAI</h1>

    <p>Business Intelligence &amp; Sustainability Analytics</p>

    <nav>
        <a href="/">Home</a>
        <a href="/dashboard/">BI Dashboard</a>
    </nav>

</header>


<main>

<section class="intro">

    <h2>Sustainability Analytics Dashboard</h2>

    <p class="muted">
        Explore model-based packaging recommendations and
        potential sustainability differences across the stored product dataset.
    </p>

</section>


<!-- FILTER SECTION -->

<section class="filter-card">

    <h3>Dashboard Filters</h3>

    <p class="muted">
        Filters update dashboard analytics and exported reports.
        They do not create new recommendations or change stored product data.
    </p>

    <form method="GET" action="/dashboard/">

        <div class="filter-grid">

            <div>

                <label for="industry">Industry</label>

                <select id="industry" name="industry">

                    <option value="">All industries</option>

                    {% for item in filter_options.industries %}

                    <option value="{{ item }}"
                    {% if filters.industry == item %}selected{% endif %}>
                        {{ item }}
                    </option>

                    {% endfor %}

                </select>

            </div>


            <div>

                <label for="material_category">
                    Recommended Material Category
                </label>

                <select
                    id="material_category"
                    name="material_category"
                >

                    <option value="">All material categories</option>

                    {% for item in filter_options.material_categories %}

                    <option value="{{ item }}"
                    {% if filters.material_category == item %}selected{% endif %}>
                        {{ item }}
                    </option>

                    {% endfor %}

                </select>

            </div>


            <div>

                <label for="product_search">
                    Product ID / Product Type
                </label>

                <input
                    id="product_search"
                    name="product_search"
                    type="text"
                    value="{{ filters.product_search or '' }}"
                    placeholder="Example: P0002"
                >

            </div>

        </div>


        <div class="actions">

            <button class="btn" type="submit">
                Apply Filters
            </button>

            <a class="btn secondary" href="/dashboard/">
                Clear Filters
            </a>

            <a
                class="btn secondary"
                href="{{ url_for(
                    'dashboard.export_excel',
                    industry=filters.industry or '',
                    material_category=filters.material_category or '',
                    product_search=filters.product_search or ''
                ) }}"
            >
                Export Filtered Excel
            </a>

            <a
                class="btn secondary"
                href="{{ url_for(
                    'dashboard.export_pdf',
                    industry=filters.industry or '',
                    material_category=filters.material_category or '',
                    product_search=filters.product_search or ''
                ) }}"
            >
                Download Filtered PDF
            </a>

        </div>

    </form>

</section>


<!-- KPI CARDS -->

<section class="kpi-grid">

    <div class="kpi-card">

        <p>Products in Filtered Dataset</p>

        <h3>{{ kpis.total_products_in_dataset }}</h3>

    </div>


    <div class="kpi-card">

        <p>Products with Eligible Recommendations</p>

        <h3>{{ kpis.eligible_products }}</h3>

    </div>


    <div class="kpi-card">

        <p>Average Potential CO₂ Difference</p>

        <h3>
            {{ "%.2f"|format(
                kpis.average_potential_co2_reduction_percent
            ) }}%
        </h3>

    </div>


    <div class="kpi-card">

        <p>Average Potential Cost Difference</p>

        <h3>
            ₹{{ "%.2f"|format(
                kpis.average_potential_cost_difference_inr
            ) }}
        </h3>

    </div>

</section>


<!-- METRIC EXPLANATION -->

<section class="note-card">

    <strong>How to interpret these figures:</strong>

    The percentages and cost differences are model-based comparisons
    between the best-ranked eligible material and the average of eligible
    materials for each product. They are not measured savings against
    actual packaging currently in use.

    Material trend counts represent the top-ranked material per eligible product.

</section>


<!-- CHARTS -->

<section class="chart-grid">

    <div class="chart-card">

        <h3>Top-ranked Materials</h3>

        <div id="materialChart" class="chart"></div>

    </div>


    <div class="chart-card">

        <h3>Potential CO₂ Difference by Industry</h3>

        <div id="co2Chart" class="chart"></div>

    </div>


    <div class="chart-card">

        <h3>Cost Difference by Material Category</h3>

        <div id="costChart" class="chart"></div>

    </div>


    <div class="chart-card">

        <h3>Industry-wise Top-ranked Material Trends</h3>

        <div id="industryChart" class="chart"></div>

    </div>

</section>


<!-- PRODUCT ANALYTICS TABLE -->

<section class="table-card">

    <h3>Product-level Analytics</h3>

    <div class="muted">
        Showing {{ products|length }} product(s) with at least
        one eligible material under the selected filters.
    </div>

    <table>

        <thead>

            <tr>
                <th>Product ID</th>
                <th>Product Type</th>
                <th>Industry</th>
                <th>Recommended Material</th>
                <th>Predicted Cost (₹)</th>
                <th>Predicted CO₂ (kg)</th>
                <th>Potential CO₂ Difference (%)</th>
            </tr>

        </thead>


        <tbody>

            {% for item in products %}

            <tr>

                <td>{{ item.product_id }}</td>

                <td>{{ item.product_type }}</td>

                <td>{{ item.industry }}</td>

                <td>{{ item.material_name }}</td>

                <td>
                    {{ "%.2f"|format(item.predicted_cost_inr) }}
                </td>

                <td>
                    {{ "%.4f"|format(item.predicted_co2_kg) }}
                </td>

                <td>
                    {{ "%.2f"|format(
                        item.potential_co2_reduction_percent
                    ) }}%
                </td>

            </tr>

            {% else %}

            <tr>
                <td colspan="7">
                    No products with eligible recommendations
                    match these filters.
                </td>
            </tr>

            {% endfor %}

        </tbody>

    </table>

</section>

</main>


<footer>
    EcoPackAI | AI-Powered Sustainable Packaging
</footer>


<!-- CHART JAVASCRIPT -->

<script>

const materialData = {{ material_chart|safe }};
const co2Data = {{ co2_chart|safe }};
const costData = {{ cost_chart|safe }};
const industryData = {{ industry_chart|safe }};

const layout = {

    autosize: true,

    paper_bgcolor: "white",

    plot_bgcolor: "white",

    font: {
        family: "DM Sans",
        color: "#24352c"
    },

    margin: {
        l: 60,
        r: 20,
        t: 25,
        b: 90
    }

};


function drawChart(id, data) {

    if (data && data.data && data.data.length) {

        Plotly.newPlot(
            id,
            data.data,
            {
                ...layout,
                ...data.layout
            },
            {
                responsive: true,
                displaylogo: false
            }
        );

    } else {

        document.getElementById(id).innerHTML =
            '<p class="muted">No chart data is available for the selected filters.</p>';

    }

}


drawChart("materialChart", materialData);

drawChart("co2Chart", co2Data);

drawChart("costChart", costData);

drawChart("industryChart", industryData);

</script>

</body>
</html>
"""


# --------------------------------------------------
# REPORT DATA
# --------------------------------------------------

def _build_report_data(filters):

    return get_filtered_dashboard_data(filters)


# --------------------------------------------------
# DASHBOARD HOME ROUTE
# --------------------------------------------------

@dashboard_bp.route("/", methods=["GET"], strict_slashes=False)
def dashboard_home():

    try:

        filters = get_active_filters()

        data = _build_report_data(filters)

        charts = prepare_dashboard(data)

        return render_template_string(
            DASHBOARD_HTML,
            kpis=data["kpis"],
            products=data["product_analytics"].to_dict(
                orient="records"
            ),
            filter_options=get_dashboard_filter_options(),
            filters=filters,
            **charts,
        )

    except Exception:

        current_app.logger.exception(
            "BI Dashboard loading failed"
        )

        return (
            "BI Dashboard could not be loaded. "
            "Check the VS Code terminal for the error.",
            500,
        )


# --------------------------------------------------
# DASHBOARD DATA API
# --------------------------------------------------

@dashboard_bp.route("/api/dashboard-data", methods=["GET"])
def dashboard_data():

    try:

        filters = get_active_filters()

        data = _build_report_data(filters)

        response_data = {

            "status": "success",

            "filters": filters,

            "kpis": data["kpis"],

            "material_trends":
                data["material_trends"].to_dict(
                    orient="records"
                ),

            "industry_trends":
                data["industry_trends"].to_dict(
                    orient="records"
                ),

            "product_analytics":
                data["product_analytics"].to_dict(
                    orient="records"
                ),

            "product_count":
                len(data["product_analytics"]),

        }

        return jsonify(
            convert_to_json_safe(response_data)
        ), 200

    except Exception:

        current_app.logger.exception(
            "Dashboard data API failed"
        )

        return jsonify({
            "status": "error",
            "message": "Unable to load dashboard analytics.",
        }), 500


# --------------------------------------------------
# FILTERED EXCEL EXPORT
# --------------------------------------------------

@dashboard_bp.route("/export/excel", methods=["GET"])
def export_excel():

    try:

        filters = get_active_filters()

        data = _build_report_data(filters)

        output = BytesIO()

        with pd.ExcelWriter(
            output,
            engine="openpyxl"
        ) as writer:

            data["product_analytics"].to_excel(
                writer,
                sheet_name="Product Analytics",
                index=False,
            )

            data["material_trends"].to_excel(
                writer,
                sheet_name="Material Trends",
                index=False,
            )

            data["industry_trends"].to_excel(
                writer,
                sheet_name="Industry Trends",
                index=False,
            )

            pd.DataFrame(
                list(data["kpis"].items()),
                columns=["KPI", "Value"],
            ).to_excel(
                writer,
                sheet_name="Dashboard KPIs",
                index=False,
            )

            pd.DataFrame([
                {
                    "Filter": key,
                    "Selected Value": value or "All",
                }
                for key, value in filters.items()
            ]).to_excel(
                writer,
                sheet_name="Applied Filters",
                index=False,
            )

        output.seek(0)

        return send_file(
            output,
            as_attachment=True,
            download_name="EcoPackAI_Filtered_Analytics.xlsx",
            mimetype=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
        )

    except Exception:

        current_app.logger.exception(
            "Excel export failed"
        )

        return jsonify({
            "status": "error",
            "message": "Unable to generate Excel report.",
        }), 500


# --------------------------------------------------
# FILTERED PDF EXPORT
# --------------------------------------------------

@dashboard_bp.route("/export/pdf", methods=["GET"])
def export_pdf():

    # Load Matplotlib only when a PDF report is requested.
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages

    try:

        filters = get_active_filters()

        data = _build_report_data(filters)

        kpis = data["kpis"]

        products = data["product_analytics"]

        materials = data["material_trends"]

        output = BytesIO()

        with PdfPages(output) as pdf:

            # ------------------------------------------
            # PDF PAGE 1: KPI SUMMARY
            # ------------------------------------------

            fig, ax = plt.subplots(
                figsize=(11.7, 8.3)
            )

            ax.axis("off")

            ax.text(
                0.5,
                0.94,
                "EcoPackAI Sustainability Analytics Report",
                ha="center",
                fontsize=19,
                fontweight="bold",
            )

            filter_text = "\n".join(
                f"{key.replace('_', ' ').title()}: {value or 'All'}"
                for key, value in filters.items()
            )

            report_text = (

                f"Applied filters:\n{filter_text}\n\n"

                f"Products in filtered dataset: "
                f"{kpis['total_products_in_dataset']}\n\n"

                f"Products with eligible recommendations: "
                f"{kpis['eligible_products']}\n\n"

                f"Products without recommendations: "
                f"{kpis['products_without_recommendations']}\n\n"

                f"Average potential CO2 difference: "
                f"{kpis['average_potential_co2_reduction_percent']:.2f}%\n\n"

                f"Average potential cost difference: "
                f"Rs. {kpis['average_potential_cost_difference_inr']:.2f}\n\n"

                "Baseline: average predicted values across eligible materials.\n"

                "These are model-based comparisons, not measured real-world savings."

            )

            ax.text(
                0.10,
                0.80,
                report_text,
                fontsize=12,
                va="top",
                linespacing=1.5,
            )

            pdf.savefig(
                fig,
                bbox_inches="tight"
            )

            plt.close(fig)


            # ------------------------------------------
            # PDF PAGE 2: TOP MATERIALS
            # ------------------------------------------

            fig, ax = plt.subplots(
                figsize=(11.7, 8.3)
            )

            top_materials = (
                materials.head(12)
                .sort_values("recommendation_count")
            )

            if not top_materials.empty:

                ax.barh(
                    top_materials["material_name"],
                    top_materials["recommendation_count"],
                )

            ax.set_title("Top-ranked Materials")

            ax.set_xlabel("Number of products")

            fig.tight_layout()

            pdf.savefig(fig)

            plt.close(fig)


            # ------------------------------------------
            # PDF PAGE 3: INDUSTRY CO2 ANALYSIS
            # ------------------------------------------

            fig, ax = plt.subplots(
                figsize=(11.7, 8.3)
            )

            if not products.empty:

                co2_by_industry = (
                    products.groupby(
                        "industry",
                        as_index=False
                    )["potential_co2_reduction_percent"]
                    .mean()
                    .sort_values(
                        "potential_co2_reduction_percent"
                    )
                )

                ax.barh(
                    co2_by_industry["industry"],
                    co2_by_industry[
                        "potential_co2_reduction_percent"
                    ],
                )

            ax.set_title(
                "Potential CO2 Difference by Industry"
            )

            ax.set_xlabel(
                "Potential difference (%)"
            )

            fig.tight_layout()

            pdf.savefig(fig)

            plt.close(fig)


        output.seek(0)

        return send_file(
            output,
            as_attachment=True,
            download_name="EcoPackAI_Filtered_Sustainability_Report.pdf",
            mimetype="application/pdf",
        )

    except Exception:

        current_app.logger.exception(
            "PDF export failed"
        )

        return jsonify({
            "status": "error",
            "message": "Unable to generate PDF report.",
        }), 500
