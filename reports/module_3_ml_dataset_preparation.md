# Module 3 – Machine Learning Dataset Preparation

## 1. Introduction

Module 3 focuses on preparing the feature-engineered datasets for machine learning model development.

The processed data is transformed into suitable input features and target variables. The dataset is then divided into training and testing sets, and a preprocessing pipeline is developed to handle numerical and categorical features.

## 2. Objectives

- Prepare the feature-engineered training dataset.
- Select relevant input features.
- Define target variables for cost and CO₂ prediction.
- Split the dataset into training and testing sets.
- Apply numerical scaling and categorical encoding.
- Save the prepared datasets and preprocessing pipeline.

## 3. Dataset Preparation

The feature-engineered dataset generated in Module 2 was used as the input for this module.

**Input file:**

`data/processed/training_data_feature_engineered.csv`

The dataset contains 36,000 records.

Before selecting the model features and targets, the prepared dataset contained 36,000 rows and 25 columns.

## 4. Feature Selection

Relevant product and material attributes were selected as input features for the machine learning models.

The following 16 features were selected:

### Product-related features

1. Industry
2. Product Weight
3. Fragility Score
4. Moisture Sensitive
5. Required Strength Score
6. Budget per Pack
7. Estimated Packaging Mass

### Material-related features

8. Material Category
9. Strength Score
10. Maximum Weight Capacity
11. Biodegradability Score
12. Recyclability Percentage
13. CO₂ per kg of Material
14. Cost per kg of Material
15. Moisture Resistance Score
16. Durability Score

These features provide information about product requirements and packaging material characteristics.

## 5. Target Variable Selection

Two regression targets were selected for the machine learning tasks.

| Target Variable              | Prediction Objective   |
| ---------------------------- | ---------------------- |
| `cost_target_inr_per_pack`   | Predict packaging cost |
| `co2_target_kgco2e_per_pack` | Predict CO₂ emissions  |

The cost target is intended for the Random Forest Regressor model.

The CO₂ target is intended for the XGBoost Regressor model.

## 6. Data Leakage Prevention

Target-related information and diagnostic columns were excluded from the model input features.

The following columns were not used as model inputs:

- Material Suitability Score.
- Suitable Label.
- Target-derived diagnostic indices.

This helps prevent target leakage during model training.

## 7. Train-Test Split

The prepared dataset was divided into training and testing subsets using an 80:20 ratio.

The splitting process used `random_state=42` to ensure reproducibility.

| Dataset          | Records |
| ---------------- | ------: |
| Training Dataset |  28,800 |
| Testing Dataset  |   7,200 |
| Total            |  36,000 |

The training dataset is used to train the machine learning models, while the testing dataset is used to evaluate their predictive performance.

## 8. Data Preprocessing

A preprocessing pipeline was created to transform the selected input features.

### 8.1 Numerical Feature Scaling

StandardScaler was applied to numerical features to standardize their values.

### 8.2 Categorical Feature Encoding

OneHotEncoder was applied to categorical features to convert categorical values into numerical representations.

### 8.3 Binary Feature Handling

Binary features were passed through without additional transformation.

### 8.4 Preprocessing Pipeline

The preprocessing operations were combined using a ColumnTransformer.

This ensures that the same preprocessing steps can be applied consistently during model training and future predictions.

## 9. Preprocessing Results

After preprocessing, the feature dimensions changed as follows:

| Dataset       | Before Transformation | After Transformation |
| ------------- | --------------------: | -------------------: |
| Training Data |           28,800 × 16 |          28,800 × 30 |
| Testing Data  |            7,200 × 16 |           7,200 × 30 |

The transformed datasets contain 30 numerical features after categorical encoding and numerical preprocessing.

## 10. Model Preparation Files

The following files were generated and saved in the `models/` directory:

| File               | Purpose                      |
| ------------------ | ---------------------------- |
| `preprocessor.pkl` | Saved preprocessing pipeline |
| `X_train.pkl`      | Training input features      |
| `X_test.pkl`       | Testing input features       |
| `y_cost_train.pkl` | Training cost targets        |
| `y_cost_test.pkl`  | Testing cost targets         |
| `y_co2_train.pkl`  | Training CO₂ targets         |
| `y_co2_test.pkl`   | Testing CO₂ targets          |

The saved preprocessing pipeline can be reused during model prediction to maintain consistency.

## 11. Result

The feature-engineered dataset was successfully converted into machine-learning-ready inputs.

The 36,000 records were divided into training and testing sets using an 80:20 ratio. Numerical scaling and categorical encoding were applied through a reusable preprocessing pipeline.

The prepared datasets and preprocessing pipeline were saved for subsequent model development.

## 12. Conclusion

Module 3 successfully completed the machine learning dataset preparation process for the EcoPackAI project.

The selected features, target variables, training and testing datasets, and preprocessing pipeline provide the required foundation for developing the AI-based cost and CO₂ prediction models in Module 4.
