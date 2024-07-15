import sqlite3
import bcrypt

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            name TEXT,
            password TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_user(username, name, password):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('INSERT INTO users (username, name, password) VALUES (?, ?, ?)', (username, name, hashed_password))
    conn.commit()
    conn.close()

def get_user(username):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    conn.close()
    return user

def verify_password(username, password):
    user = get_user(username)
    if user and bcrypt.checkpw(password.encode('utf-8'), user[2]):
        return True
    return False
