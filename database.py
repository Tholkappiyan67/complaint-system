import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT
)
""")

cursor.execute("""
CREATE TABLE complaints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT,
    complaint TEXT,
    status TEXT
)
""")

conn.commit()
conn.close()

print("Database created successfully")
