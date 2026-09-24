create database eshop;

use eshop;
USE eshop;

DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    two_step_verification BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DESCRIBE users;

select * from users;


create table products (
        id int primary key auto_increment,
        name varchar(150) NOT null,
        category varchar(100) NOT NULL,
        description TEXT,
        price DECIMAL(10,2) NOT NULL,
        stock INT NOT NUll default 0,
        image varchar(255),
        rating decimal(2,1) DEFAULT 0,
        created_at timestamp DEFAULT current_timestamp,
        check (price >= 0),
        check (stock >= 0),
        check (rating >= 0 AND rating <=5)
        );
        
        
USE eshop;

SHOW TABLES;

USE eshop;

SELECT
    id,
    name,
    email,
    phone,
    two_step_verification,
    created_at
FROM users;






create table addresses(
id INT PRIMARY KEY auto_increment,
user_id INT NOT NuLL,
full_name VARCHAR(100) NOT NULL,
phone VARCHAR(20) NOT NULL,
address TEXT NOT NULL,
city VARCHAR(100) NOT NULL,
state VARCHAR(100) NOT NULL,
pincode VARCHAR(10) NOT NULL,
is_default BOOLEAN NOT NULL DEFAULT FALSE,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
CONSTRAINT fk_addresses_user
foreign key (user_id)
references users(id)
ON DELETE cascade
);




select * from addresses;


USE eshop;

INSERT INTO products
(name, category, description, price, stock, image, rating)
VALUES
(
    'Wireless Headphones',
    'Electronics',
    'High-quality wireless headphones with excellent sound, comfortable design and long battery life.',
    2499.00,
    25,
    'headphones.jpg',
    4.8
),
(
    'Smart Watch',
    'Electronics',
    'Smart watch with fitness tracking, heart rate monitoring and multiple smart features.',
    3999.00,
    15,
    'smartwatch.jpg',
    4.7
),
(
    'Running Shoes',
    'Footwear',
    'Comfortable lightweight running shoes suitable for daily workouts and running.',
    2199.00,
    30,
    'running-shoes.jpg',
    4.6
),
(
    'Laptop Backpack',
    'Bags',
    'Durable laptop backpack with multiple compartments and water-resistant material.',
    1499.00,
    40,
    'backpack.jpg',
    4.5
),
(
    'Bluetooth Speaker',
    'Electronics',
    'Portable Bluetooth speaker with powerful audio and long battery backup.',
    1799.00,
    20,
    'speaker.jpg',
    4.4
),
(
    'Mechanical Keyboard',
    'Electronics',
    'RGB mechanical keyboard designed for gaming and professional use.',
    3299.00,
    18,
    'keyboard.jpg',
    4.7
),
(
    'Cotton T-Shirt',
    'Fashion',
    'Premium cotton regular-fit T-shirt suitable for everyday wear.',
    799.00,
    50,
    'tshirt.jpg',
    4.3
),
(
    'Denim Jeans',
    'Fashion',
    'Comfortable slim-fit denim jeans with premium stitching.',
    1899.00,
    35,
    'jeans.jpg',
    4.5
),
(
    'Sunglasses',
    'Fashion',
    'Stylish UV-protected sunglasses for everyday outdoor use.',
    999.00,
    25,
    'sunglasses.jpg',
    4.2
),
(
    'Water Bottle',
    'Accessories',
    'Stainless steel insulated water bottle with leak-proof design.',
    699.00,
    60,
    'water-bottle.jpg',
    4.4
);



SELECT * FROM products;