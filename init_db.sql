-- Initialisation de la base de données MySQL pour MLOps
CREATE DATABASE IF NOT EXISTS mlops_db;
USE mlops_db;

-- Table pour stocker les métadonnées des images
CREATE TABLE IF NOT EXISTS plants_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    url_source VARCHAR(500) NOT NULL,
    url_s3 VARCHAR(500),
    label VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_label (label),
    INDEX idx_url_source (url_source(255))
);

-- Table pour le feature store
CREATE TABLE IF NOT EXISTS feature_store (
    id INT AUTO_INCREMENT PRIMARY KEY,
    image_path VARCHAR(500) NOT NULL,
    label VARCHAR(50) NOT NULL,
    features JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_label (label),
    INDEX idx_image_path (image_path(255))
);

