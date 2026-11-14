# EcoPackAI – AI-Powered Sustainable Packaging Recommendation System

**EcoPackAI** is an AI-powered sustainable packaging recommendation system designed to help users identify and compare eco-friendly packaging alternatives based on product requirements, estimated cost, material properties and environmental impact.

The project integrates Machine Learning, data analytics, a Flask backend, PostgreSQL database and an interactive web-based dashboard to support sustainable packaging decisions.

## 🌱 Project Overview

Traditional packaging materials can contribute to environmental pollution and increased carbon emissions. Selecting sustainable alternatives requires evaluating several factors, including cost, recyclability, biodegradability and material suitability.

EcoPackAI addresses this challenge through an intelligent recommendation system that evaluates available packaging alternatives and provides data-driven recommendations.

## 🎯 Project Objectives

- Recommend suitable sustainable packaging alternatives.
- Predict the estimated cost of packaging materials.
- Estimate the CO₂ footprint of packaging alternatives.
- Evaluate material suitability using relevant product requirements.
- Compare packaging alternatives based on sustainability parameters.
- Provide interactive visualizations through a BI dashboard.
- Support informed and environmentally responsible packaging decisions.

## ✨ Key Features

- **AI-Based Recommendations:** Suggests suitable sustainable packaging alternatives.
- **Cost Prediction:** Estimates packaging costs using Machine Learning.
- **CO₂ Prediction:** Predicts the estimated carbon footprint of packaging materials.
- **Material Evaluation:** Evaluates packaging materials based on sustainability characteristics.
- **Alternative Comparison:** Helps compare available packaging options.
- **PostgreSQL Integration:** Stores and manages application data.
- **Interactive Dashboard:** Displays sustainability analytics and visual insights.
- **Report Generation:** Supports available PDF and Excel analytics exports.

## 🛠️ Technology Stack

| Category | Technologies |
|---|---|
| Programming Language | Python |
| Backend Framework | Flask |
| Data Processing | Pandas, NumPy |
| Machine Learning | Scikit-learn, Random Forest, XGBoost |
| Model Persistence | Joblib |
| Database | PostgreSQL |
| Database Connectivity | SQLAlchemy, Psycopg |
| Frontend | HTML, CSS, Bootstrap, JavaScript |
| Data Visualization | Plotly, Matplotlib |
| Deployment | Render |

## 🏗️ System Architecture

The EcoPackAI system follows an integrated architecture:

1. **Data Collection:** Collects product and packaging material information.
2. **Data Preprocessing:** Cleans and prepares the collected data.
3. **Feature Engineering:** Extracts relevant features for recommendation and prediction.
4. **Machine Learning:** Uses trained models to estimate packaging cost and CO₂ footprint.
5. **Recommendation Engine:** Evaluates candidate materials and identifies suitable alternatives.
6. **Backend Integration:** Processes application requests through Flask APIs.
7. **Database Management:** Connects to PostgreSQL for data storage and retrieval.
8. **Dashboard & Visualization:** Presents analytics and sustainability insights through an interactive interface.

## 🤖 Machine Learning Models

EcoPackAI integrates Machine Learning models to support packaging evaluation.

| Model | Purpose |
|---|---|
| Random Forest | Packaging cost prediction |
| XGBoost | CO₂ footprint prediction |
| Preprocessing Pipeline | Prepares input features for model prediction |

The trained models and preprocessing artifacts are maintained in the `models/` directory.

## ♻️ Sustainable Packaging Recommendation

The recommendation engine evaluates packaging alternatives using sustainability-related parameters, including:

- CO₂ footprint
- Biodegradability
- Recyclability
- Cost
- Material suitability

The system uses these criteria to evaluate and rank eligible packaging alternatives.

## 📊 Business Intelligence Dashboard

The EcoPackAI dashboard provides visual insights into packaging materials, product information and sustainability-related analytics.

Dashboard capabilities include:

- Summary metrics
- Product and material analysis
- Sustainability comparisons
- Interactive data visualizations
- Available filters
- PDF and Excel report exports

For more information, refer to:

**[Dashboard Documentation](docs/DASHBOARD.md)**

## 📂 Project Structure

```text
EcoPackAI/
│
├── backend/          # Flask backend and API integration
├── dashboard/        # Business Intelligence dashboard
├── data/             # Project datasets
├── database/         # Database-related files
├── docs/             # Project documentation
│   ├── DASHBOARD.md
│   └── VIDEO_DEMO.md
├── frontend/         # User interface
├── models/           # Trained ML models and preprocessing artifacts
├── notebooks/        # Data analysis and experimentation
├── reports/          # Project reports and analysis
├── src/              # Source code
│
├── requirements.txt  # Python dependencies
├── .gitignore
└── README.md
```

## 📦 Installation and Setup

### Prerequisites

- Python
- PostgreSQL
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/gouthamofficial2004-ops/EcoPackAI.git
```

### 2. Navigate to the Project Directory

```bash
cd EcoPackAI
```

### 3. Create a Virtual Environment

```bash
python -m venv .venv
```

### 4. Activate the Virtual Environment

**Windows:**

```powershell
.venv\Scripts\activate
```

**Linux / macOS:**

```bash
source .venv/bin/activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Configure the Database

Configure PostgreSQL using the environment variables expected by the project.

Make sure the database is running and the required configuration is available before starting the application.

**Important:** Do not upload database passwords, API keys or other sensitive credentials to GitHub.

### 7. Run the Application

Use the Flask application entry point and start command configured in the project.

## 🌐 Live Deployment

**Live Application:**  
https://ecopackai-green-intelligence.onrender.com

**GitHub Repository:**  
https://github.com/gouthamofficial2004-ops/EcoPackAI

EcoPackAI is deployed using Render.

## 📚 Project Documentation

Additional documentation is maintained separately to keep the main README focused on the overall project.

- **Dashboard Documentation:** `docs/DASHBOARD.md`
- **Video Demonstration Guide:** `docs/VIDEO_DEMO.md`

## 🔮 Future Enhancements

- Improve recommendation accuracy with additional packaging datasets.
- Integrate more sustainable packaging materials.
- Enhance prediction performance through model optimization.
- Introduce advanced sustainability analytics.
- Improve the user experience and dashboard functionality.
- Expand the recommendation engine with additional environmental parameters.

## ⚠️ Project Limitations

- Prediction accuracy depends on the quality and availability of training data.
- Cost and CO₂ outputs are model-based estimates.
- Actual environmental impact may vary depending on manufacturing, transportation and disposal conditions.
- Recommendations depend on the configured eligibility criteria and available material information.

## 👨‍💻 Project Information

**Project Name:** EcoPackAI – AI-Powered Sustainable Packaging Recommendation System

**Developer:** Goutham G

**Department:** Artificial Intelligence and Data Science

**Degree:** B.Tech

---

*EcoPackAI – Making sustainable packaging decisions smarter through Artificial Intelligence.*
