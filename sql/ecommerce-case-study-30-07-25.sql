-- Ensure we're on the correct DB
IF DB_ID(N'EcomDB') IS NULL
BEGIN
    CREATE DATABASE EcomDB;
END
GO
USE EcomDB;
GO

-- Drop if they exist (safe to re-run)
IF OBJECT_ID('dbo.order_items', 'U') IS NOT NULL DROP TABLE dbo.order_items;
IF OBJECT_ID('dbo.orders', 'U')       IS NOT NULL DROP TABLE dbo.orders;
IF OBJECT_ID('dbo.cart', 'U')         IS NOT NULL DROP TABLE dbo.cart;
IF OBJECT_ID('dbo.products', 'U')     IS NOT NULL DROP TABLE dbo.products;
IF OBJECT_ID('dbo.customers', 'U')    IS NOT NULL DROP TABLE dbo.customers;
GO

-- 1) customers
CREATE TABLE dbo.customers (
    customer_id      INT IDENTITY(1,1) PRIMARY KEY,
    name             NVARCHAR(100)  NOT NULL,
    email            NVARCHAR(255)  NOT NULL UNIQUE,
    [password]       NVARCHAR(255)  NOT NULL
);
GO

-- 2) products
CREATE TABLE dbo.products (
    product_id     INT IDENTITY(1,1) PRIMARY KEY,
    name           NVARCHAR(150)   NOT NULL,
    price          DECIMAL(10,2)   NOT NULL CHECK (price >= 0),
    [description]  NVARCHAR(1000)  NULL,
    stockQuantity  INT             NOT NULL CHECK (stockQuantity >= 0)
);
GO

-- 3) cart
CREATE TABLE dbo.cart (
    cart_id      INT IDENTITY(1,1) PRIMARY KEY,
    customer_id  INT NOT NULL,
    product_id   INT NOT NULL,
    quantity     INT NOT NULL CHECK (quantity > 0),
    CONSTRAINT FK_cart_customer FOREIGN KEY (customer_id) REFERENCES dbo.customers(customer_id),
    CONSTRAINT FK_cart_product  FOREIGN KEY (product_id)  REFERENCES dbo.products(product_id),
    CONSTRAINT UQ_cart_customer_product UNIQUE (customer_id, product_id)
);
GO

-- 4) orders
CREATE TABLE dbo.orders (
    order_id          INT IDENTITY(1,1) PRIMARY KEY,
    customer_id       INT           NOT NULL,
    order_date        DATETIME2(0)  NOT NULL CONSTRAINT DF_orders_order_date DEFAULT (SYSUTCDATETIME()),
    total_price       DECIMAL(12,2) NOT NULL CHECK (total_price >= 0),
    shipping_address  NVARCHAR(500) NOT NULL,
    CONSTRAINT FK_orders_customer FOREIGN KEY (customer_id) REFERENCES dbo.customers(customer_id)
);
GO

-- 5) order_items
CREATE TABLE dbo.order_items (
    order_item_id INT IDENTITY(1,1) PRIMARY KEY,
    order_id      INT NOT NULL,
    product_id    INT NOT NULL,
    quantity      INT NOT NULL CHECK (quantity > 0),
    CONSTRAINT FK_order_items_order   FOREIGN KEY (order_id)   REFERENCES dbo.orders(order_id) ON DELETE CASCADE,
    CONSTRAINT FK_order_items_product FOREIGN KEY (product_id)  REFERENCES dbo.products(product_id)
);
GO

-- Optional indexes
CREATE INDEX IX_cart_customer            ON dbo.cart(customer_id);
CREATE INDEX IX_order_items_order        ON dbo.order_items(order_id);
CREATE INDEX IX_orders_customer_date     ON dbo.orders(customer_id, order_date DESC);
GO

-- Seed data (optional for quick testing)
INSERT INTO dbo.customers (name, email, [password]) VALUES
('Alice Sharma', 'alice@example.com', 'alice@123'),
('Bob Kumar',    'bob@example.com',   'bob@123');

INSERT INTO dbo.products (name, price, [description], stockQuantity) VALUES
('Bluetooth Earbuds', 1999.00, 'TWS earbuds with charging case', 50),
('Smartwatch',        4999.00, 'Heart-rate monitor, GPS',        35),
('USB-C Charger 30W',  899.00, 'Fast charging adapter',          100),
('Mechanical Keyboard',3999.00,'RGB, blue switches',             20);

INSERT INTO dbo.cart (customer_id, product_id, quantity)
SELECT c.customer_id, p.product_id, 2
FROM dbo.customers c
JOIN dbo.products p ON p.name='USB-C Charger 30W'
WHERE c.email='alice@example.com';
GO

-- Verify
SELECT DB_NAME() AS now_in_db;
SELECT name FROM sys.tables ORDER BY name;