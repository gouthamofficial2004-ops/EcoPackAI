# Module 1 – Data Collection & Management

## 1. Introduction

The first module of the EcoPackAI project focuses on collecting, organizing and managing the datasets required for AI-powered sustainable packaging material recommendations.

The collected data contains information about packaging materials, products and historical training records. PostgreSQL is used to store and manage the structured datasets.

## 2. Objectives

- Collect packaging material and product-related datasets.
- Organize datasets in CSV format.
- Create a structured PostgreSQL database.
- Design database tables using SQL.
- Import CSV datasets into PostgreSQL.
- Validate the imported records.

## 3. Dataset Collection

Three primary datasets were used in this project.

| Dataset       | Description                                       | Records |
| ------------- | ------------------------------------------------- | ------: |
| Materials     | Packaging material properties and characteristics |     120 |
| Products      | Product details and packaging requirements        |     300 |
| Training Data | Historical records used for machine learning      |  36,000 |

The datasets are maintained in the project's `data` directory.

### Dataset storage structure

- `data/raw/` – Original collected datasets.
- `data/processed/` – Processed datasets.
- `data/data_dictionary.csv` – Dataset field descriptions.

## 4. Database Setup

PostgreSQL was selected as the relational database management system.

**Database name:** `ecopackai_db`

**Database version:** PostgreSQL 17.11

Three primary tables were created:

1. `materials`
2. `products`
3. `training_data`

The database schema was defined using SQL and stored in:

`database/schema.sql`

The tables contain structured information about packaging materials, product requirements and machine learning training records.

## 5. Data Import and Integration

The collected CSV datasets were imported into their corresponding PostgreSQL tables.

The following activities were completed:

- Created the PostgreSQL database.
- Created the required database tables.
- Imported the materials dataset.
- Imported the products dataset.
- Imported the training dataset.
- Verified the imported records.

The database connection and related operations are handled through the project's backend database configuration.

## 6. Data Validation

After importing the datasets, the following record counts were verified:

| Database Table | Expected Records | Verified Records |
| -------------- | ---------------: | ---------------: |
| materials      |              120 |              120 |
| products       |              300 |              300 |
| training_data  |           36,000 |           36,000 |

All three datasets were successfully imported, and their record counts were verified against the source CSV files.

## 7. Project Files Created

The following project files support Module 1:

- `data/raw/` – Original datasets.
- `data/processed/` – Processed dataset storage.
- `data/data_dictionary.csv` – Data dictionary.
- `database/schema.sql` – PostgreSQL table definitions.
- `backend/db.py` – Database connection implementation.

## 8. Result

The materials, products and training datasets were successfully organized and integrated into the PostgreSQL database.

A structured database environment was established for subsequent data cleaning, feature engineering and machine learning activities.

## 9. Conclusion

Module 1 successfully established the data collection and database management foundation for the EcoPackAI project. The three primary datasets were imported and validated in PostgreSQL, making the data available for the next stages of the AI-based sustainable packaging system.
