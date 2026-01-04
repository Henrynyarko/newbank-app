-- Create tables for demo banking app

-- Users / Auth table
CREATE TABLE IF NOT EXISTS users (
    username VARCHAR(50) PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    disabled BOOLEAN DEFAULT FALSE
);

-- Accounts table
CREATE TABLE IF NOT EXISTS accounts (
    account_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    balance NUMERIC(12,2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'USD',
    created_at DATE DEFAULT CURRENT_DATE
);

-- Transactions table
CREATE TABLE IF NOT EXISTS transactions (
    id VARCHAR(20) PRIMARY KEY,
    account_id VARCHAR(20) REFERENCES accounts(account_id),
    amount NUMERIC(12,2) NOT NULL,
    type VARCHAR(10) CHECK (type IN ('debit', 'credit')),
    date DATE DEFAULT CURRENT_DATE,
    description VARCHAR(255)
);

-- Insert mock users
INSERT INTO users (username, full_name, email, hashed_password, disabled) VALUES
('johndoe', 'John Doe', 'john.doe@example.com', '$2b$12$examplehashedpassword', FALSE),
('janesmith', 'Jane Smith', 'jane.smith@example.com', '$2b$12$examplehashedpassword', FALSE);

-- Insert mock accounts
INSERT INTO accounts (account_id, name, balance, currency, created_at) VALUES
('acct-001', 'John Doe', 1250.75, 'USD', '2020-05-17'),
('acct-002', 'Jane Smith', 3475.60, 'USD', '2021-09-20');

-- Insert mock transactions
INSERT INTO transactions (id, account_id, amount, type, date, description) VALUES
('tx1001','acct-001',-50.00,'debit','2026-01-02','Grocery Store'),
('tx1002','acct-001',200.00,'credit','2026-01-01','Salary'),
('tx2001','acct-002',-150.00,'debit','2026-01-01','Utilities'),
('tx2002','acct-002',500.00,'credit','2025-12-30','Freelance Payment');
