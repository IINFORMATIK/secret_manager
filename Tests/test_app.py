import unittest
import sys
import os

# Добавляем путь к родительской директории, чтобы импортировать app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, User, generate_key, encrypt_secret, decrypt_secret

class SecretManagerTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()
        self.key = generate_key()

    def tearDown(self):
        pass

    def register(self, username, password):
        return self.app.post('/register', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def login(self, username, password):
        return self.app.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.app.post('/logout', follow_redirects=True)

    def test_register_login_logout(self):
        rv = self.register('testuser', 'testpassword')
        assert 'Регистрация успешна! Теперь вы можете войти.'.encode('utf-8') in rv.data

        rv = self.login('testuser', 'testpassword')
        assert 'Добро пожаловать!'.encode('utf-8') in rv.data

        rv = self.logout()
        assert 'Войти'.encode('utf-8') in rv.data

    def test_store_and_get_secret(self):
        self.register('testuser', 'testpassword')
        self.login('testuser', 'testpassword')

        secret = encrypt_secret(self.key, 'mysecret')
        # Test with JSON payload
        rv = self.app.post('/store', json=dict(
            name='testsecret',
            secret='mysecret'
        ))
        assert 'успех'.encode('utf-8') in rv.data

        # Test with form data
        rv = self.app.post('/store', data=dict(
            name='testsecret2',
            secret='mysecret2'
        ))
        assert 'успех'.encode('utf-8') in rv.data

        rv = self.app.get('/get_secrets')
        assert 'testsecret'.encode('utf-8') in rv.data
        assert 'mysecret'.encode('utf-8') in rv.data
        assert 'testsecret2'.encode('utf-8') in rv.data
        assert 'mysecret2'.encode('utf-8') in rv.data

    def test_store_and_get_simple_secret(self):
        self.register('testuser', 'testpassword')
        self.login('testuser', 'testpassword')

        # Test with JSON payload
        rv = self.app.post('/store_simple', json=dict(
            name='simpletest',
            secret='simplemysecret'
        ))
        assert 'успех'.encode('utf-8') in rv.data

        # Test with form data
        rv = self.app.post('/store_simple', data=dict(
            name='simpletest2',
            secret='simplemysecret2'
        ))
        assert 'успех'.encode('utf-8') in rv.data

        rv = self.app.get('/get_simple_secrets')
        assert 'simpletest'.encode('utf-8') in rv.data
        assert 'simplemysecret'.encode('utf-8') in rv.data
        assert 'simpletest2'.encode('utf-8') in rv.data
        assert 'simplemysecret2'.encode('utf-8') in rv.data

    def test_generate_credentials(self):
        self.register('testuser', 'testpassword')
        self.login('testuser', 'testpassword')

        rv = self.app.get('/generate_credentials')
        data = rv.get_json()
        assert 'login' in data
        assert 'password' in data

if __name__ == '__main__':
    unittest.main()
