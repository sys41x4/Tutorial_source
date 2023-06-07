
-- Create database if not exist
CREATE DATABASE IF NOT EXISTS user_data;

-- Create table if not exist
CREATE TABLE IF NOT EXISTS user (
    uid VARCHAR(60),
    email VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255)
);

-- Create table if not exist
CREATE TABLE IF NOT EXISTS user_details (
    uid VARCHAR(60),
    gender VARCHAR(10),
    latitude VARCHAR(15),
    longitude VARCHAR(15),
    datetime VARCHAR(30)
);