from cryptography.fernet import Fernet
from werkzeug.security import generate_password_hash, check_password_hash

# Функция для генерации ключа шифрования
def generate_key():
    return Fernet.generate_key()

# Функция для шифрования секрета
def encrypt_secret(key, secret):
    f = Fernet(key)
    encrypted_secret = f.encrypt(secret.encode())
    return encrypted_secret

# Функция для расшифровки секрета
def decrypt_secret(key, encrypted_secret):
    f = Fernet(key)
    decrypted_secret = f.decrypt(encrypted_secret).decode()
    return decrypted_secret

# Функция для хэширования пароля
# Используйте: password_hash = generate_password_hash(password)
# Функция для проверки пароля
# Используйте: check_password_hash(password_hash, password)
