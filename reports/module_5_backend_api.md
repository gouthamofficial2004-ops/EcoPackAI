# Module 5 – Flask Backend API Integration

## 1. Introduction

The Flask Backend API Integration module connects the EcoPackAI machine learning recommendation engine with a REST API. It allows users to submit product details, receive suitable sustainable packaging material recommendations, and retrieve environmental scores.

The backend also integrates with PostgreSQL to access product, material, and training data.

## 2. Technology Stack

| Component                          | Technology                                       |
| ---------------------------------- | ------------------------------------------------ |
| Backend framework                  | Python Flask                                     |
| Database                           | PostgreSQL 17                                    |
| Database connectivity              | SQLAlchemy                                       |
| Machine Learning – Cost Prediction | Random Forest Regressor                          |
| CO₂ Prediction                     | XGBoost Regressor                                |
| Data processing                    | Pandas, NumPy                                    |
| Model loading                      | Joblib                                           |
| API communication                  | REST API / JSON                                  |
| API testing                        | Python Requests and PowerShell Invoke-RestMethod |

## 3. Backend Project Structure

```text
EcoPackAI_Project/
│
├── backend/
│   ├── app.py
│   └── db.py
│
├── src/
│   └── recommendation_engine.py
│
├── models/
│   ├── preprocessor.pkl
│   ├── cost_random_forest.pkl
│   └── co2_xgboost.pkl
│
├── database/
│   └── schema.sql
│
└── reports/
    └── module_5_backend_api.md
```

## 4. Backend Implementation

The Flask application is implemented in `backend/app.py`.

The following endpoints have been implemented.

### 4.1 Home Route

**Endpoint:** `GET /`

Purpose:

- Display the EcoPackAI homepage.
- Render the frontend HTML template using Flask.

### 4.2 Health Check API

**Endpoint:** `GET /health`

Purpose:

- Check the health status of the Flask backend.
- Return the backend service status in JSON format.

### 4.3 Database Status API

**Endpoint:** `GET /api/database-status`

Purpose:

- Establish a connection with PostgreSQL.
- Retrieve the number of records in database tables.
- Verify database connectivity.

Verified database records:

| Database table | Number of records |
| -------------- | ----------------: |
| Materials      |               120 |
| Products       |               300 |
| Training Data  |            36,000 |

### 4.4 Product Listing API

**Endpoint:** `GET /api/products`

Purpose:

- Retrieve available products from PostgreSQL.
- Return product ID, product type, and industry.
- Populate the product selection dropdown in the frontend.

The API successfully retrieves all 300 product records.

### 4.5 AI Material Recommendation API

**Endpoint:** `POST /api/recommendations`

Purpose:

- Accept a product ID and the requested number of recommendations.
- Call the existing machine learning recommendation engine.
- Return eligible packaging materials in JSON format.

Sample request:

```json
{
  "product_id": "P0002",
  "top_n": 3
}
```

The API returns:

- Material ID and material name.
- Material category.
- Predicted packaging cost.
- Predicted CO₂ emissions.
- Biodegradability score.
- Recyclability percentage.
- CO₂ score and cost score.
- Overall recommendation score.
- Recommendation rank and reason.

The recommendation engine checks technical strength, material capacity, moisture resistance, and budget before ranking eligible materials.

### 4.6 Environmental Score API

**Endpoint:** `POST /api/environmental-score`

Purpose:

- Calculate an environmental score for a given product.
- Identify the highest-scoring eligible material.
- Return environmental performance indicators in JSON format.

Sample request:

```json
{
  "product_id": "P0002"
}
```

The environmental score uses three factors from the existing recommendation engine:

| Environmental parameter | Weight |
| ----------------------- | -----: |
| CO₂ score               |    40% |
| Biodegradability        |    25% |
| Recyclability           |    20% |

The environmental score is calculated by normalizing the environmental weights:

\[
Environmental\ Score =
\frac{
(CO_2\ Score \times 0.40)
+(Biodegradability \times 0.25)
+(Recyclability \times 0.20)
}{0.85}
\]

The cost component is excluded from this environmental score.

The API evaluates eligible materials and selects the material with the highest environmental score.

The API returns:

- Product ID.
- Best recommended material.
- Environmental score.
- CO₂ score.
- Biodegradability score.
- Recyclability percentage.
- Score calculation method.

**Note:** The environmental score is a comparative, project-specific score based on eligible materials for a product. It is not a certified environmental rating.

## 5. PostgreSQL Database Integration

Database connectivity is implemented in `backend/db.py` using SQLAlchemy.

The database connection is configured through the `DATABASE_URL` environment variable.

The backend verifies connectivity and retrieves record counts from:

- `materials`
- `products`
- `training_data`

The database connection was successfully tested with PostgreSQL.

## 6. API Testing and Validation

The backend APIs were tested locally using Python Requests and PowerShell Invoke-RestMethod.

### 6.1 Environmental Score API Tests

| Test case                                | Expected HTTP status | Actual HTTP status | Result |
| ---------------------------------------- | -------------------: | -----------------: | ------ |
| Valid product P0002                      |                  200 |                200 | Passed |
| Product P0003 with no eligible materials |                  200 |                200 | Passed |
| Invalid product ID (INVALID999)          |                  400 |                400 | Passed |

Verified result for P0002:

- Best material: Glass - Variant 07
- CO₂ score: 100
- Biodegradability score: 0
- Recyclability: 100%
- Environmental score: Approximately 70.59/100

### 6.2 Existing API Regression Tests

| API endpoint                | HTTP status | Result |
| --------------------------- | ----------: | ------ |
| Home route                  |         200 | Passed |
| Health Check API            |         200 | Passed |
| Database Status API         |         200 | Passed |
| Product Listing API         |         200 | Passed |
| Material Recommendation API |         200 | Passed |

### 6.3 Additional Validation

The following validations are implemented:

- Invalid or missing JSON request bodies are rejected.
- Missing or invalid product IDs are rejected.
- Invalid recommendation limits are rejected.
- Products without eligible materials receive a separate response.
- Unexpected backend errors are logged and handled with an error response.

## 7. Running the Flask Backend

The backend is started from the project root using:

```powershell
python -m backend.app
```

The local development server runs at:

```text
http://127.0.0.1:5000
```

The database connection must be configured in the same terminal session before starting the backend.

## 8. Module 5 Deliverables

The following components have been implemented:

1. Flask REST API application.
2. PostgreSQL database connectivity.
3. Product listing API.
4. Product-based material recommendation API.
5. Environmental score API.
6. JSON request and response handling.
7. Input validation and error handling.
8. API testing and regression validation.
9. Module 5 technical documentation.

## 9. Conclusion

The Flask Backend API Integration module connects the EcoPackAI machine learning recommendation engine with the PostgreSQL database and exposes its functionality through REST APIs.

The homepage, health check, database status, product listing, material recommendation, and environmental score endpoints have been implemented and tested in the local development environment.

The backend provides the required foundation for integrating the EcoPackAI system with the frontend interface in Module 6.
