CREATE DATABASE support_engine;
USE support_engine;

CREATE TABLE customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    country VARCHAR(60) NULL,
    signup_date DATE NOT NULL
);

CREATE TABLE intents (
    intent_id INT AUTO_INCREMENT PRIMARY KEY,
    intent_name VARCHAR(50) UNIQUE NOT NULL,
    description VARCHAR(255),
    target_resolution_hours INT NOT NULL
);

CREATE TABLE tickets (
    ticket_id INT AUTO_INCREMENT PRIMARY KEY,
    subject VARCHAR(200) NOT NULL,
    channel ENUM('email', 'chat', 'app') NOT NULL,
    status ENUM('open', 'in_progress', 'resolved', 'escalated') NOT NULL DEFAULT 'open',
    created_at DATETIME NOT NULL,
    resolution_due_at DATETIME,
    resolved_at DATETIME,
    customer_id INT NOT NULL,
    intent_id INT,
    FOREIGN KEY (customer_id) REFERENCES customers (customer_id),
    FOREIGN KEY (intent_id) REFERENCES intents (intent_id)
);

CREATE TABLE ticket_events (
    event_id INT AUTO_INCREMENT PRIMARY KEY,
    ticket_id INT NOT NULL,
    event_type ENUM('created', 'classified', 'routed', 'resolved', 'escalated') NOT NULL,
    occurred_at DATETIME NOT NULL,
    FOREIGN KEY (ticket_id) REFERENCES tickets (ticket_id)
);

CREATE TABLE workflows (
    workflow_id INT AUTO_INCREMENT PRIMARY KEY,
    workflow_name VARCHAR(100) NOT NULL,
    config_file VARCHAR(100) NOT NULL,
    is_self_service BOOLEAN NOT NULL DEFAULT TRUE,
    intent_id INT NOT NULL UNIQUE,
    FOREIGN KEY (intent_id) REFERENCES intents (intent_id)
);
