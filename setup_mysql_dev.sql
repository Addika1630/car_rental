-- Setup Database (development)
CREATE DATABASE IF NOT EXISTS car_rental_db;
CREATE USER IF NOT EXISTS 'car_rental'@'localhost' IDENTIFIED BY 'car_rental_pwd';
GRANT ALL PRIVILEGES ON hbnb_dev_db.* TO 'car_rental'@'localhost';
GRANT SELECT ON performance_schema.* to 'car_rental'@'localhost';
