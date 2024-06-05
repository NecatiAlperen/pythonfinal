import sqlite3
from werkzeug.security import generate_password_hash

connection = sqlite3.connect("database.db")

with open("scheme.sql") as f:
    connection.executescript(f.read())

cur = connection.cursor()

# Add admin user
cur.execute(
    "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
    ("admin", "admin@blog.com", generate_password_hash("123456")),
)

cur.execute(
    "INSERT INTO posts (user_id, title, content) VALUES (?, ?, ?)",
    (1, "First Post", "Content for the first post"),
)

cur.execute(
    "INSERT INTO posts (user_id, title, content) VALUES (?, ?, ?)",
    (1, "Second Post", "Content for the second post"),
)

connection.commit()
connection.close()
