from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from models import (create_database, store_user, get_user_by_username, get_user_by_id,
                   store_secret, get_secrets_by_user, store_simple_secret, get_simple_secrets_by_user)
from utils import generate_key, encrypt_secret, decrypt_secret
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-key-123'  # Фиксированный ключ для отладки
app.config['SESSION_TYPE'] = 'filesystem'
key = generate_key()  # Генерируем ключ для шифрования

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Пожалуйста, войдите, чтобы получить доступ к этой странице.'

class User(UserMixin):
    def __init__(self, user_id, username, password_hash):
        self.id = str(user_id)
        self.username = username
        self.password_hash = password_hash

@login_manager.user_loader
def load_user(user_id):
    if not user_id:
        return None
    user = get_user_by_id(int(user_id))
    if user:
        return User(user['id'], user['username'], user['password_hash'])
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        logout_user()
        session.clear()
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = get_user_by_username(username)
        if user and check_password_hash(user['password_hash'], password):
            user_obj = User(user['id'], user['username'], user['password_hash'])
            login_user(user_obj)
            session['user_id'] = user['id']
            return redirect(url_for('index'))
        flash('Неверное имя пользователя или пароль')
    return render_template('login.html')

@app.route('/')
@app.route('/index')
@login_required
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if get_user_by_username(username):
            flash('Такой пользователь уже существует')
            return redirect(url_for('register'))
        
        password_hash = generate_password_hash(password)
        if store_user(username, password_hash):
            flash('Регистрация успешна! Теперь вы можете войти.')
            return redirect(url_for('login'))
        else:
            flash('Ошибка при регистрации')
    
    return render_template('register.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if current_user.is_authenticated:
        logout_user()
    session.clear()
    return redirect(url_for('login'))

@app.route('/store', methods=['POST'])
@login_required
def store():
    if request.is_json:
        data = request.json
    else:
        data = request.form

    try:
        name = data.get('name')
        service_login = data.get('service-login')
        service_password = data.get('service-password')
        
        secret_data = json.dumps({
            'login': service_login,
            'password': service_password
        })
        encrypted_secret = encrypt_secret(key, secret_data)
        store_secret(current_user.username, name, encrypted_secret)
        return jsonify({"status": "успех"})
    except Exception as e:
        print(f"Error storing secret: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/store_simple', methods=['POST'])
@login_required
def store_simple():
    if request.is_json:
        data = request.json
    else:
        data = request.form
        
    try:
        name = data.get('simple-name')
        secret = data.get('simple-secret')
        store_simple_secret(current_user.username, name, secret)
        return jsonify({"status": "успех"})
    except Exception as e:
        print(f"Error storing simple secret: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/generate_credentials', methods=['GET'])
@login_required
def generate_credentials():
    import random
    import string
    
    def generate_password(length=12):
        characters = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choice(characters) for _ in range(length))
    
    return jsonify({
        'login': 'user_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6)),
        'password': generate_password()
    })

@app.route('/get_secrets')
@login_required
def get_secrets():
    try:
        secrets = get_secrets_by_user(current_user.username, key)
        return jsonify(secrets)
    except Exception as e:
        print(f"Error getting secrets: {e}")
        return jsonify([])

@app.route('/get_simple_secrets')
@login_required
def get_simple_secrets():
    try:
        secrets = get_simple_secrets_by_user(current_user.username)
        return jsonify(secrets)
    except Exception as e:
        print(f"Error getting simple secrets: {e}")
        return jsonify([])

if __name__ == '__main__':
    app.run(debug=True)
