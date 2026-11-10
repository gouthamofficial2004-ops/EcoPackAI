
-- ==========================================
-- ECOPACKAI DATABASE SCHEMA
-- Based on finalized CSV dataset attributes
-- ==========================================

-- 1. MATERIALS TABLE
CREATE TABLE IF NOT EXISTS materials (
    material_id VARCHAR(20) PRIMARY KEY,
    material_name VARCHAR(150),
    material_category VARCHAR(50),
    strength_score NUMERIC(10,2),
    max_weight_capacity_kg NUMERIC(10,3),
    biodegradability_score NUMERIC(10,2),
    recyclability_percent NUMERIC(10,2),
    co2_kg_per_kg_material NUMERIC(12,4),
    cost_inr_per_kg NUMERIC(12,4),
    moisture_resistance_score NUMERIC(10,2),
    durability_score NUMERIC(10,2)
);

-- 2. PRODUCTS TABLE
CREATE TABLE IF NOT EXISTS products (
    product_id VARCHAR(20) PRIMARY KEY,
    industry VARCHAR(100),
    product_type VARCHAR(100),
    product_weight_kg NUMERIC(10,3),
    fragility_score NUMERIC(10,2),
    moisture_sensitive BOOLEAN,
    required_strength_score NUMERIC(10,2),
    budget_per_pack_inr NUMERIC(12,2)
);

-- 3. TRAINING DATA TABLE
CREATE TABLE IF NOT EXISTS training_data (
    training_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id VARCHAR(20) REFERENCES products(product_id),
    material_id VARCHAR(20) REFERENCES materials(material_id),
    industry VARCHAR(100),
    product_weight_kg NUMERIC(10,3),
    fragility_score NUMERIC(10,2),
    moisture_sensitive BOOLEAN,
    required_strength_score NUMERIC(10,2),
    budget_per_pack_inr NUMERIC(12,2),
    material_category VARCHAR(50),
    strength_score NUMERIC(10,2),
    max_weight_capacity_kg NUMERIC(10,3),
    biodegradability_score NUMERIC(10,2),
    recyclability_percent NUMERIC(10,2),
    co2_kg_per_kg_material NUMERIC(12,4),
    cost_inr_per_kg NUMERIC(12,4),
    moisture_resistance_score NUMERIC(10,2),
    durability_score NUMERIC(10,2),
    packaging_mass_kg_synthetic NUMERIC(12,5),
    cost_target_inr_per_pack NUMERIC(12,4),
    co2_target_kgco2e_per_pack NUMERIC(12,5),
    suitability_score NUMERIC(10,2),
    suitable_label SMALLINT
);
