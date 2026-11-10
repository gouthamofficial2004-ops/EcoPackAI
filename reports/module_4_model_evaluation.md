# Module 4 – AI Recommendation Model

## 1. Overview

This module develops an AI-based sustainable packaging recommendation engine. It predicts packaging cost and CO2 emissions for different product-material combinations and ranks eligible materials based on environmental and cost performance.

## 2. Machine Learning Models

Two regression models were developed.

| Model           | Purpose                         | Algorithm               |
| --------------- | ------------------------------- | ----------------------- |
| Cost Prediction | Predict packaging cost per pack | Random Forest Regressor |
| CO2 Prediction  | Predict packaging CO2 emissions | XGBoost Regressor       |

## 3. Model Evaluation

The models were evaluated using an 80:20 train-test split.

### Random Forest – Cost Prediction

| Metric |   Result |
| ------ | -------: |
| RMSE   | 0.062252 |
| MAE    | 0.038075 |
| R²     | 0.999982 |

### XGBoost – CO2 Prediction

| Metric |     Result |
| ------ | ---------: |
| RMSE   | 0.00407390 |
| MAE    | 0.00232776 |
| R²     | 0.99998104 |

## 4. Recommendation Engine

The recommendation engine evaluates product-material combinations and identifies suitable packaging materials.

### Eligibility Conditions

A material must satisfy:

1. Required material strength must be met.
2. Maximum weight capacity must support the product.
3. Moisture resistance must be at least 60 for moisture-sensitive products.
4. Predicted packaging cost must not exceed the product budget.

### Ranking Methodology

Eligible materials are ranked using the following weighted scoring system.

| Parameter        |   Weight |
| ---------------- | -------: |
| CO2 performance  |      40% |
| Biodegradability |      25% |
| Recyclability    |      20% |
| Cost performance |      15% |
| **Total**        | **100%** |

Lower predicted CO2 emissions and lower predicted costs receive higher relative scores.

## 5. Technical Implementation

- Python and Pandas for data processing.
- Scikit-learn for preprocessing and Random Forest.
- XGBoost for CO2 prediction.
- Joblib for saving and loading trained models.
- NumPy for numerical validation.

### Model Artifacts

The following files are stored in the models directory:

- preprocessor.pkl
- cost_random_forest.pkl
- co2_xgboost.pkl

The standalone recommendation engine is implemented in:

`src/recommendation_engine.py`

## 6. Validation and Testing

The standalone recommendation engine was tested successfully.

| Test                             | Result |
| -------------------------------- | ------ |
| Python syntax compilation        | Passed |
| Standalone module import         | Passed |
| P0002 – 10 recommendations       | Passed |
| P0003 – Zero recommendations     | Passed |
| Empty result – 12 output columns | Passed |
| Strength eligibility             | Passed |
| Weight capacity eligibility      | Passed |
| Moisture resistance eligibility  | Passed |
| Budget eligibility               | Passed |
| Non-negative CO2 predictions     | Passed |
| Recommendation ranking           | Passed |

## 7. Limitations

The training targets are generated using synthetic dataset formulas. Therefore, the high evaluation scores indicate that the models reproduce patterns in this dataset; they do not establish real-world predictive accuracy.

The recommendation weights and minimum moisture-resistance threshold are project design assumptions and require validation against real packaging requirements.

The recommendation ranking is relative to the eligible materials for each product.

## 8. Outcome

The AI recommendation engine has been implemented, evaluated and tested independently. It can load the trained models and datasets without depending on notebook variables.

The engine is ready for integration with the Flask backend in Module 5.
