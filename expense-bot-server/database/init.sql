-- Create the database
CREATE DATABASE expense_tracker;

-- Switch to the new database
\c expense_tracker;

-- Create user_info table
CREATE TABLE user_info (
    user_id UUID PRIMARY KEY ,
    email_id TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    fullname TEXT NOT NULL
);

-- Create sessions table
CREATE TABLE sessions (
    session_id UUID PRIMARY KEY,
    session_name TEXT NOT NULL,
    user_id UUID NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user_info(user_id) ON DELETE CASCADE
);

-- Create events table
CREATE TABLE transaction (
    transaction_id UUID PRIMARY KEY ,
    session_id UUID REFERENCES sessions(session_id),
    operation TEXT NOT NULL,
    amount NUMERIC(10, 2) NOT NULL,
    category TEXT,
    sub_category TEXT,
    date_of_transaction DATE,
    created_date DATE DEFAULT CURRENT_DATE,
    updated_date DATE DEFAULT CURRENT_DATE
);

CREATE TABLE events (
    event_id UUID PRIMARY KEY ,
    session_id UUID NOT NULL,
    prompt_req TEXT NOT NULL,
    prompt_res TEXT NOT NULL,
    transaction_id UUID ,
    created_date DATE DEFAULT CURRENT_DATE,
    updated_date DATE DEFAULT CURRENT_DATE,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
);