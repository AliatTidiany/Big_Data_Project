-- =====================================================
-- STRUCTURE DES TABLES DU PROFESSEUR
-- =====================================================

-- 1. Table category
CREATE TABLE IF NOT EXISTS category (
    id SERIAL PRIMARY KEY,
    intitule VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Table books
CREATE TABLE IF NOT EXISTS books (
    id SERIAL PRIMARY KEY,
    category_id INTEGER,
    code VARCHAR(50),
    intitule VARCHAR(200),
    isbn_10 VARCHAR(20),
    isbn_13 VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Table customers
CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Table factures
CREATE TABLE IF NOT EXISTS factures (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50),
    date_edit VARCHAR(8),
    customers_id INTEGER,
    qte_totale INTEGER,
    total_amount DECIMAL(10,2),
    total_paid DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Table ventes
CREATE TABLE IF NOT EXISTS ventes (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50),
    date_edit VARCHAR(8),
    factures_id INTEGER,
    books_id INTEGER,
    pu DECIMAL(10,2),
    qte INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- DONNÉES DE TEST
-- =====================================================

INSERT INTO category (id, intitule) VALUES
(1, 'Roman'),
(2, 'Science-Fiction'),
(3, 'Policier'),
(4, 'Fantasy'),
(5, 'Biographie')
ON CONFLICT (id) DO NOTHING;

INSERT INTO books (id, category_id, code, intitule, isbn_10, isbn_13) VALUES
(1, 1, 'BK001', 'Le Petit Prince', '1234567890', '9781234567890'),
(2, 2, 'BK002', '1984', '0987654321', '9780987654321'),
(3, 3, 'BK003', 'Crime et Châtiment', '1122334455', '9781122334455'),
(4, 4, 'BK004', 'Harry Potter', '2233445566', '9782233445566'),
(5, 5, 'BK005', 'Steve Jobs', '3344556677', '9783344556677')
ON CONFLICT (id) DO NOTHING;

INSERT INTO customers (id, code, first_name, last_name) VALUES
(1, 'C001', 'Jean', 'Dupont'),
(2, 'C002', 'Marie', 'Martin'),
(3, 'C003', 'Pierre', 'Durand'),
(4, 'C004', 'Sophie', 'Lambert'),
(5, 'C005', 'Lucas', 'Moreau')
ON CONFLICT (id) DO NOTHING;

INSERT INTO factures (id, code, date_edit, customers_id, qte_totale, total_amount, total_paid) VALUES
(1, 'F001', '20250315', 1, 2, 25.00, 25.00),
(2, 'F002', '20250316', 2, 1, 15.00, 15.00),
(3, 'F003', '20250317', 1, 3, 37.50, 37.50),
(4, 'F004', '20250318', 3, 2, 29.00, 29.00),
(5, 'F005', '20250319', 4, 1, 22.00, 22.00)
ON CONFLICT (id) DO NOTHING;

INSERT INTO ventes (id, code, date_edit, factures_id, books_id, pu, qte) VALUES
(1, 'V001', '20250315', 1, 1, 12.50, 2),
(2, 'V002', '20250316', 2, 2, 15.00, 1),
(3, 'V003', '20250317', 3, 1, 12.50, 3),
(4, 'V004', '20250318', 4, 3, 18.00, 1),
(5, 'V005', '20250318', 4, 4, 14.50, 1),
(6, 'V006', '20250319', 5, 5, 22.00, 1)
ON CONFLICT (id) DO NOTHING;