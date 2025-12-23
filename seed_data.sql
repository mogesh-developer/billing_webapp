-- Database Schema and Seed Data for Grocery Billing App

-- 1. Create Tables (If they don't exist, though app.py handles this)
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    barcode VARCHAR(50) UNIQUE NOT NULL,
    price FLOAT NOT NULL,
    stock_quantity INT DEFAULT 0,
    category VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS bills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    bill_number VARCHAR(50) UNIQUE NOT NULL,
    date DATETIME DEFAULT CURRENT_TIMESTAMP,
    customer_name VARCHAR(100),
    total_amount FLOAT NOT NULL
);

CREATE TABLE IF NOT EXISTS bill_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    bill_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    price_at_sale FLOAT NOT NULL,
    subtotal FLOAT NOT NULL,
    FOREIGN KEY (bill_id) REFERENCES bills(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- 2. Insert Sample Products (Groceries)
INSERT INTO products (name, barcode, price, stock_quantity, category) VALUES
('Fresh Milk 1L', '1001', 2.50, 50, 'Dairy'),
('Whole Wheat Bread', '1002', 1.80, 30, 'Bakery'),
('Eggs (Dozen)', '1003', 3.00, 40, 'Dairy'),
('Coca Cola 1.5L', '1004', 2.20, 100, 'Beverages'),
('Lay\'s Classic Chips', '1005', 1.50, 60, 'Snacks'),
('Basmati Rice 5kg', '1006', 12.00, 20, 'Grains'),
('Sunflower Oil 1L', '1007', 4.50, 25, 'Pantry'),
('Apple (Red Delicious) /kg', '1008', 3.20, 45, 'Fruits'),
('Banana /kg', '1009', 1.10, 50, 'Fruits'),
('Colgate Toothpaste', '1010', 2.80, 35, 'Personal Care');

-- 3. Insert a Sample Bill (Historical Data)
INSERT INTO bills (bill_number, customer_name, total_amount, date) VALUES
('INV-DEMO-001', 'John Doe', 7.50, NOW());

-- 4. Insert Bill Items for the Sample Bill
-- Assuming the IDs match the order above (1=Milk, 3=Eggs)
INSERT INTO bill_items (bill_id, product_id, quantity, price_at_sale, subtotal) VALUES
(1, 1, 1, 2.50, 2.50), -- 1x Milk
(1, 3, 1, 3.00, 3.00), -- 1x Eggs (Dozen)
(1, 4, 1, 2.00, 2.00); -- 1x Coke (Price might vary)

-- 5. Decrease Stock for sold items (Manual simulation)
UPDATE products SET stock_quantity = stock_quantity - 1 WHERE id IN (1, 3, 4);
