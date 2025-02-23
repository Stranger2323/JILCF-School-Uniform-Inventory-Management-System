from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_cors import CORS
import sqlite3
import hashlib
import re
import os
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app)

# Database initialization
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    last_login = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.username}>'

with app.app_context():
    db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
@login_required
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user, remember=remember)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('home'))
        
        flash('Invalid email or password')
    
    return render_template('login.html')

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    remember = data.get('remember', False)
    
    if not email or not password:
        return jsonify({
            "message": "Email and password are required"
        }), 400
    
    try:
        with sqlite3.connect('users.db') as conn:
            c = conn.cursor()
            c.execute('SELECT id, name, password FROM users WHERE email = ?', (email,))
            user = c.fetchone()
            
            if user and user[2] == hash_password(password):
                return jsonify({
                    "message": "Login successful",
                    "name": user[1]
                })
            else:
                return jsonify({
                    "message": "Invalid email or password"
                }), 401
                
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({
            "message": "An error occurred during login"
        }), 500

@app.route('/forgot-password')
def forgot_password():
    return render_template('forgot-password.html')

@app.route('/api/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({
            "message": "Email is required"
        }), 400
    
    try:
        with sqlite3.connect('users.db') as conn:
            c = conn.cursor()
            c.execute('SELECT id FROM users WHERE email = ?', (email,))
            user = c.fetchone()
            
            if user:
                # In a real application, send a password reset email
                return jsonify({
                    "message": "Password reset instructions have been sent to your email"
                })
            else:
                return jsonify({
                    "message": "No account found with this email address"
                }), 404
                
    except Exception as e:
        print(f"Reset password error: {e}")
        return jsonify({
            "message": "An error occurred while processing your request"
        }), 500

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/api/signup', methods=['POST'])
def signup_api():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    
    if not all([name, email, password]):
        return jsonify({
            "message": "All fields are required"
        }), 400
    
    # Check password strength
    strength_check = check_password_strength(password)
    if strength_check['score'] < 3:
        return jsonify({
            "message": "Please choose a stronger password",
            "feedback": strength_check['feedback']
        }), 400
    
    try:
        with sqlite3.connect('users.db') as conn:
            c = conn.cursor()
            c.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)',
                     (name, email, hash_password(password)))
            conn.commit()
            
            return jsonify({
                "message": "Account created successfully"
            })
            
    except sqlite3.IntegrityError:
        return jsonify({
            "message": "An account with this email already exists"
        }), 409
        
    except Exception as e:
        print(f"Signup error: {e}")
        return jsonify({
            "message": "An error occurred while creating your account"
        }), 500

@app.route('/api/check-password-strength', methods=['POST'])
def check_strength():
    data = request.get_json()
    password = data.get('password')
    return jsonify(check_password_strength(password))

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_password_strength(password):
    # Initialize score and feedback
    score = 0
    feedback = []
    
    # Length check
    if len(password) >= 8:
        score += 1
    else:
        feedback.append("Password should be at least 8 characters long")
    
    # Check for uppercase
    if re.search(r"[A-Z]", password):
        score += 1
    else:
        feedback.append("Include at least one uppercase letter")
    
    # Check for lowercase
    if re.search(r"[a-z]", password):
        score += 1
    else:
        feedback.append("Include at least one lowercase letter")
    
    # Check for numbers
    if re.search(r"\d", password):
        score += 1
    else:
        feedback.append("Include at least one number")
    
    # Check for special characters
    if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        score += 1
    else:
        feedback.append("Include at least one special character")
    
    strength = {
        0: "Very Weak",
        1: "Weak",
        2: "Fair",
        3: "Good",
        4: "Strong",
        5: "Very Strong"
    }
    
    return {
        "score": score,
        "strength": strength[score],
        "feedback": feedback
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
