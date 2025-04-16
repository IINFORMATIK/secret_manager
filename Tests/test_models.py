import unittest
import sys
import os
import json

# Добавляем путь к родительской директории, чтобы импортировать models и utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models import create_table, store_secret, get_secrets_by_user, create_simple_secrets_table, store_simple_secret, get_simple_secrets_by_user, create_users_table, store_user, get_user_by_username
from utils import generate_key, encrypt_secret, decrypt_secret, generate_password_hash, check_password_hash
import sqlite3

class ModelsTestCase(unittest.TestCase):
    def setUp(self):
        self.key = generate_key()
        create_table()
        create_simple_secrets_table()
        create_users_table()

    def tearDown(self):
        conn = sqlite3.connect('secrets.db')
        c = conn.cursor()
        c.execute("DROP TABLE IF EXISTS secrets")
        c.execute("DROP TABLE IF EXISTS simple_secrets")
        c.execute("DROP TABLE IF EXISTS users")
        conn.commit()
        conn.close()

    def test_store_and_get_secret(self):
        secret_data = json.dumps({'login': 'mylogin', 'password': 'mypassword'})
        encrypted_secret = encrypt_secret(self.key, secret_data)
        store_secret('testuser', 'testsecret', encrypted_secret)
        secrets = get_secrets_by_user('testuser', self.key)
        assert len(secrets) == 1, "Ожидается, что количество секретов будет равно 1"
        assert secrets[0]['name'] == 'testsecret', "Ожидается, что имя секрета будет 'testsecret'"
        assert secrets[0]['service_login'] == 'mylogin', "Ожидается, что логин сервиса будет 'mylogin'"
        assert secrets[0]['service_password'] == 'mypassword', "Ожидается, что пароль сервиса будет 'mypassword'"

    def test_store_and_get_simple_secret(self):
        store_simple_secret('testuser', 'testsecret', 'mysecret')
        secrets = get_simple_secrets_by_user('testuser')
        assert len(secrets) == 1, "Ожидается, что количество простых секретов будет равно 1"
        assert secrets[0]['name'] == 'testsecret', "Ожидается, что имя простого секрета будет 'testsecret'"
        assert secrets[0]['secret'] == 'mysecret', "Ожидается, что значение простого секрета будет 'mysecret'"

    def test_store_and_get_user(self):
        password_hash = generate_password_hash('testpassword')
        store_user('testuser', password_hash)
        user = get_user_by_username('testuser')
        assert user is not None, "Ожидается, что пользователь будет найден"
        assert user['username'] == 'testuser', "Ожидается, что имя пользователя будет 'testuser'"
        assert check_password_hash(user['password_hash'], 'testpassword'), "Ожидается, что хэш пароля будет совпадать"

if __name__ == '__main__':
    unittest.main()
