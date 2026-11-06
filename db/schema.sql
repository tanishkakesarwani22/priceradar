CREATE DATABASE IF NOT EXISTS priceradar;
USE priceradar;

CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    url VARCHAR(500) NOT NULL UNIQUE,
    name VARCHAR(255),
    current_price DECIMAL(10,2),
    lowest_price DECIMAL(10,2),
    target_price DECIMAL(10,2),
    last_checked DATETIME,
    alert_sent TINYINT DEFAULT 0
);

CREATE TABLE price_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    checked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id),
    INDEX idx_product_time (product_id, checked_at)
);