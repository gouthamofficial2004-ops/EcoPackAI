# Module 2 – Data Cleaning & Feature Engineering

## 1. Introduction

Module 2 focuses on preparing the collected datasets for machine learning by performing data auditing, data cleaning, exploratory data analysis (EDA) and feature engineering.

The objective is to improve data quality and generate meaningful features that help evaluate packaging materials based on their cost, environmental impact and physical properties.

## 2. Objectives

- Audit the collected datasets.
- Identify missing values and duplicate records.
- Clean and prepare the datasets.
- Perform exploratory data analysis.
- Generate meaningful features from existing attributes.
- Calculate sustainability-related indices.
- Prepare the processed datasets for machine learning.

## 3. Data Auditing

Data auditing was performed using the Python script:

`src/audit_data.py`

The following datasets were examined:

| Dataset       |   Rows | Columns |
| ------------- | -----: | ------: |
| Materials     |    120 |      11 |
| Products      |    300 |       8 |
| Training Data | 36,000 |      22 |

### Data quality verification

The audit checked:

- Missing values.
- Duplicate rows.
- Duplicate identifiers in the base datasets.
- Dataset dimensions and structure.

**Audit results:**

- No missing values were identified.
- No duplicate rows were identified.
- No duplicate identifiers were found in the materials and products base datasets.

Repeated material identifiers in the training dataset are expected because multiple training records can refer to the same material.

## 4. Data Cleaning

Data cleaning was performed using:

`src/clean_data.py`

The cleaning process was applied to the collected datasets, and the cleaned files were saved in the `data/processed/` directory.

### Cleaning activities

1. Loaded the original CSV datasets.
2. Checked the structure and data types.
3. Audited missing values.
4. Checked duplicate records.
5. Generated cleaned datasets.
6. Verified the resulting record counts.

### Cleaned dataset verification

| Dataset       | Cleaned Records |
| ------------- | --------------: |
| Materials     |             120 |
| Products      |             300 |
| Training Data |          36,000 |

The record counts remained unchanged after cleaning because the audit did not identify missing or duplicate records requiring removal.

## 5. Exploratory Data Analysis (EDA)

Exploratory Data Analysis was performed using:

`notebooks/01_exploratory_data_analysis.ipynb`

The analysis examined the structure, distribution and characteristics of the collected datasets.

### 5.1 Material Category Distribution

The materials dataset contains the following categories:

| Material Category |   Count |
| ----------------- | ------: |
| Paper             |      40 |
| Plastic           |      30 |
| Plant Fiber       |      20 |
| Bioplastic        |      10 |
| Glass             |      10 |
| Metal             |      10 |
| **Total**         | **120** |

### 5.2 Product Distribution

- Total industries: 10.
- Products per industry: 30.
- Total products: 300.
- Product types: 30.
- Records per product type: 10.

### 5.3 Suitability Label Distribution

The training dataset contains two suitability classes:

| Suitability Label |    Records |
| ----------------- | ---------: |
| 0 – Not Suitable  |     29,466 |
| 1 – Suitable      |      6,534 |
| **Total**         | **36,000** |

Approximately 18.15% of the records belong to the suitable class. This indicates an imbalance in the suitability labels.

## 6. Feature Engineering

Feature engineering was performed using:

`notebooks/02_feature_engineering.ipynb`

New features were derived from existing material properties to support sustainability evaluation.

### 6.1 Material Suitability Score

A suitability score was calculated using the average of five material attributes:

- Strength Score.
- Biodegradability Score.
- Recyclability Percentage.
- Moisture Resistance Score.
- Durability Score.

The equal-weight average was used to generate a combined material suitability indicator.

### 6.2 CO₂ Impact Index

The CO₂ Impact Index represents the relative carbon emission impact of a material.

Formula:

CO₂ Impact Index = (Material CO₂ Emission / Maximum Material CO₂ Emission) × 100

A lower index indicates a lower relative carbon emission impact.

### 6.3 Cost Efficiency Index

The Cost Efficiency Index represents the relative cost efficiency of a material.

Formula:

Cost Efficiency Index = (Minimum Material Cost / Material Cost) × 100

A higher index indicates better relative cost efficiency.

### 6.4 Estimated Packaging Mass

An estimated packaging mass feature was derived from the product weight.

The dataset-observed calculation rule was:

Estimated Packaging Mass = Maximum of (0.075 × Product Weight, 0.025 kg)

This rule was derived from the synthetic dataset used in the project and should not be treated as a universal packaging standard.

## 7. Feature Engineering Results

The feature-engineered materials dataset was saved as:

`data/processed/materials_feature_engineered.csv`

- Records: 120.
- Columns: 14.

The merged feature-engineered training dataset was saved as:

`data/processed/training_data_feature_engineered.csv`

The resulting model preparation dataset contained 36,000 records and 25 columns before selecting the final model features and targets.

### Important observations

- Material properties were combined to generate a suitability indicator.
- Relative CO₂ impact and cost efficiency indices were calculated.
- Estimated packaging mass was derived from product weight.
- The engineered datasets were prepared for machine learning.

## 8. Data Leakage Prevention

During feature selection, target-related and diagnostic columns were excluded from the model input features.

The suitability score and suitability label were not included as model input features for the cost and CO₂ prediction tasks.

This helps prevent target-related information from unintentionally entering the prediction inputs.

## 9. Project Files Created

The following files support Module 2:

- `src/audit_data.py` – Data quality auditing.
- `src/clean_data.py` – Data cleaning.
- `notebooks/01_exploratory_data_analysis.ipynb` – Exploratory data analysis.
- `notebooks/02_feature_engineering.ipynb` – Feature engineering.
- `data/processed/materials_feature_engineered.csv` – Engineered materials dataset.
- `data/processed/training_data_feature_engineered.csv` – Engineered training dataset.

## 10. Result

The collected datasets were audited and cleaned successfully. Exploratory data analysis was performed to understand material categories, product distribution and suitability labels.

Additional sustainability-related features were generated to support the next stage of machine learning dataset preparation.

## 11. Conclusion

Module 2 successfully completed the data auditing, cleaning, exploratory data analysis and feature engineering activities for the EcoPackAI project.

The processed and feature-engineered datasets provide the foundation for preparing machine learning inputs and target variables in Module 3.
