import sqlite3
from utils import decrypt_secret  # Импортируем функцию decrypt_secret
import json

# Функция для создания таблицы секретов
def create_table():
    conn = sqlite3.connect('secrets.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS secrets
                 (id INTEGER PRIMARY KEY, username TEXT, name TEXT, encrypted_secret BLOB)''')
    conn.commit()
    conn.close()

# Функция для сохранения секрета
def store_secret(username, name, encrypted_secret):
    try:
        conn = sqlite3.connect('secrets.db')
        c = conn.cursor()
        c.execute("INSERT INTO secrets (username, name, encrypted_secret) VALUES (?, ?, ?)", (username, name, encrypted_secret))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error storing secret: {e}")
    finally:
        conn.close()

# Функция для получения секретов пользователя
def get_secrets_by_user(username, key):
    try:
        conn = sqlite3.connect('secrets.db')
        c = conn.cursor()
        c.execute("SELECT name, encrypted_secret FROM secrets WHERE username=?", (username,))
        rows = c.fetchall()
        secrets = []
        for row in rows:
            try:
                decrypted_secret = decrypt_secret(key, row[1])
                secret_data = json.loads(decrypted_secret)
                secrets.append({
                    'name': row[0],
                    'service_login': secret_data.get('login', ''),
                    'service_password': secret_data.get('password', '')
                })
            except Exception as e:
                print(f"Error decrypting secret: {e}")
                continue
        return secrets
    except Exception as e:
        print(f"Error retrieving secrets: {e}")
        return []
    finally:
        if 'conn' in locals():
            conn.close()

# Функция для создания таблицы простых секретов
def create_simple_secrets_table():
    conn = sqlite3.connect('secrets.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS simple_secrets
                 (id INTEGER PRIMARY KEY, username TEXT, name TEXT, secret TEXT)''')
    conn.commit()
    conn.close()

# Функция для сохранения простого секрета
def store_simple_secret(username, name, secret):
    try:
        conn = sqlite3.connect('secrets.db')
        c = conn.cursor()
        c.execute("INSERT INTO simple_secrets (username, name, secret) VALUES (?, ?, ?)", (username, name, secret))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error storing simple secret: {e}")
    finally:
        conn.close()

# Функция для получения простых секретов пользователя
def get_simple_secrets_by_user(username):
    try:
        conn = sqlite3.connect('secrets.db')
        c = conn.cursor()
        c.execute("SELECT name, secret FROM simple_secrets WHERE username=?", (username,))
        rows = c.fetchall()
        return [{'name': row[0], 'secret': row[1]} for row in rows]
    except Exception as e:
        print(f"Error retrieving simple secrets: {e}")
        return []
    finally:
        if 'conn' in locals():
            conn.close()

# Функция для создания таблицы пользователей
def create_users_table():
    conn = sqlite3.connect('secrets.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password_hash TEXT)''')
    conn.commit()
    conn.close()

# Функция для сохранения пользователя
def store_user(username, password_hash):
    conn = None
    try:
        conn = sqlite3.connect('secrets.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", 
                 (username, password_hash))
        conn.commit()
        print(f"Successfully stored user in database: {username}")  # Debug log
        return True
    except sqlite3.IntegrityError:
        print(f"User already exists in database: {username}")  # Debug log
        return False
    except Exception as e:
        print(f"Database error in store_user: {e}")  # Error log
        return False
    finally:
        if conn:
            conn.close()

# Функция для получения пользователя по имени пользователя
def get_user_by_username(username):
    conn = None
    try:
        conn = sqlite3.connect('secrets.db')
        c = conn.cursor()
        c.execute("SELECT id, username, password_hash FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        if user:
            print(f"Found user in database: {username}")  # Debug log
            return {'id': user[0], 'username': user[1], 'password_hash': user[2]}
        print(f"User not found in database: {username}")  # Debug log
        return None
    except Exception as e:
        print(f"Database error in get_user_by_username: {e}")  # Error log
        return None
    finally:
        if conn:
            conn.close()

# Функция для получения пользователя по ID
def get_user_by_id(user_id):
    conn = None
    try:
        conn = sqlite3.connect('secrets.db')
        c = conn.cursor()
        c.execute("SELECT id, username, password_hash FROM users WHERE id = ?", (user_id,))
        user = c.fetchone()
        if user:
            print(f"Found user by ID in database: {user_id}")  # Debug log
            return {'id': user[0], 'username': user[1], 'password_hash': user[2]}
        print(f"User not found by ID in database: {user_id}")  # Debug log
        return None
    except Exception as e:
        print(f"Database error in get_user_by_id: {e}")  # Error log
        return None
    finally:
        if conn:
            conn.close()

# Функция для создания базы данных
def create_database():
    conn = None
    try:
        conn = sqlite3.connect('secrets.db')
        c = conn.cursor()
        
        # Создаем таблицу пользователей
        c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  password_hash TEXT NOT NULL)''')
        
        # Создаем таблицу секретов
        c.execute('''CREATE TABLE IF NOT EXISTS secrets
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT NOT NULL,
                  name TEXT NOT NULL,
                  encrypted_secret BLOB NOT NULL,
                  FOREIGN KEY (username) REFERENCES users(username))''')
        
        # Создаем таблицу простых секретов
        c.execute('''CREATE TABLE IF NOT EXISTS simple_secrets
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT NOT NULL,
                  name TEXT NOT NULL,
                  secret TEXT NOT NULL,
                  FOREIGN KEY (username) REFERENCES users(username))''')
        
        conn.commit()
        print("Database successfully created")  # Debug log
    except Exception as e:
        print(f"Error creating database: {e}")  # Error log
        raise
    finally:
        if conn:
            conn.close()
