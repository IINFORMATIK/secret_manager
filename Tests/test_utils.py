import unittest
import sys
import os

# Добавляем путь к родительской директории, чтобы импортировать utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import generate_key, encrypt_secret, decrypt_secret

class UtilsTestCase(unittest.TestCase):
    def setUp(self):
        self.key = generate_key()

    def test_encrypt_decrypt_secret(self):
        secret = 'mysecret'
        encrypted_secret = encrypt_secret(self.key, secret)
        decrypted_secret = decrypt_secret(self.key, encrypted_secret)
        assert secret == decrypted_secret

if __name__ == '__main__':
    unittest.main()
