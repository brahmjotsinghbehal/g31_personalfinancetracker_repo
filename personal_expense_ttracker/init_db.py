import sqlite3

DATABASE = "expense_tracker.db"

# Connect to the database
conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

# Create tables
cursor.executescript("""
CREATE TABLE IF NOT EXISTS register (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    email TEXT NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    userid INTEGER NOT NULL,
    date TEXT NOT NULL,
    expensename TEXT NOT NULL,
    amount REAL NOT NULL,
    paymode TEXT NOT NULL,
    category TEXT NOT NULL,
    FOREIGN KEY (userid) REFERENCES register (id)
);


CREATE TABLE IF NOT EXISTS limits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    userid INTEGER NOT NULL,
    limitss REAL NOT NULL,
    FOREIGN KEY (userid) REFERENCES register (id)
);

""")







# Commit and close
conn.commit()
conn.close()

print("Database initialized successfully!")
