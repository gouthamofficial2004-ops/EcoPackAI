# Module 6 – Frontend UI

## 1. Objective

Develop a user-friendly web interface for EcoPackAI to allow users to select products, receive AI-based sustainable packaging recommendations, view environmental performance and compare packaging materials.

## 2. Technologies Used

- HTML5
- CSS3
- Bootstrap 5.3.3
- JavaScript
- Flask REST APIs
- Google Fonts – Outfit and DM Sans

## 3. Frontend Features Implemented

### 3.1 Product Selection

- Retrieves product information from the Flask `/api/products` endpoint.
- Displays available products in a dropdown.
- Allows users to select the required number of recommendations.

### 3.2 AI Material Recommendations

- Connects to the `/api/recommendations` endpoint.
- Displays ranked packaging materials.
- Shows material category, predicted cost, predicted CO₂ emissions and recommendation score.

### 3.3 Environmental Performance Dashboard

- Connects to the `/api/environmental-score` endpoint.
- Displays environmental score, CO₂ performance, biodegradability and recyclability.
- Identifies the best environmental recommendation.

### 3.4 Material Comparison

- Allows users to select two recommended materials.
- Compares material category, predicted cost, predicted CO₂ emissions and recommendation score.
- Displays the comparison results in a table.

### 3.5 User Interface Design

- Implemented an Eco-Tech theme.
- Used forest green, mint green and cream colours.
- Added responsive layouts, styled buttons, dropdowns and tables.
- Integrated Outfit and DM Sans typography.

## 4. Testing and Validation

| Test Case                                | Result |
| ---------------------------------------- | ------ |
| Product loading                          | Passed |
| Product P0004 recommendations            | Passed |
| Environmental score display              | Passed |
| Material comparison                      | Passed |
| Product P0003 with no eligible materials | Passed |
| No-recommendation warning                | Passed |

## 5. Result

The EcoPackAI frontend successfully integrates with the Flask backend and displays AI-generated packaging recommendations, environmental performance indicators and material comparison results.

The interface also handles products without eligible materials by displaying appropriate warning messages.

## 6. Conclusion

Module 6 successfully implements the frontend interface for the EcoPackAI project. The application provides an interactive interface for sustainable packaging selection and material evaluation.
