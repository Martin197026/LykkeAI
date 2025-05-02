# manualchat/auth.py
import sqlite3
from passlib.hash import bcrypt

DB_FILE = "users.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def register_user(email, password):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        hashed_password = bcrypt.hash(password)
        c.execute('INSERT INTO users (email, password) VALUES (?, ?)', (email, hashed_password))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False  # Email allerede brugt

def login_user(email, password):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT password FROM users WHERE email = ?', (email,))
    result = c.fetchone()
    conn.close()

    if result:
        stored_password = result[0]
        return bcrypt.verify(password, stored_password)
    else:
        return False
