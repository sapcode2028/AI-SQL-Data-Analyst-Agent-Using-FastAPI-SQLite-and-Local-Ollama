CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name TEXT,
    category TEXT,
    price NUMERIC
);

CREATE TABLE sales (
    id SERIAL PRIMARY KEY,
    product_id INT REFERENCES products(id),
    quantity INT,
    sale_date DATE
);

INSERT INTO products (name, category, price) VALUES
('Keyboard', 'Electronics', 4500),
('Mouse', 'Electronics', 1400),
('Lamp', 'Home', 2200);

INSERT INTO sales (product_id, quantity, sale_date) VALUES
(1, 3, '2026-10-01'),
(2, 5, '2026-10-05'),
(3, 2, '2026-10-10');