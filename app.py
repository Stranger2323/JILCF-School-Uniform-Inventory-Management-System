from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_cors import CORS
import sqlite3
import hashlib
import re
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app)

# Database initialization
def init_db():
    with sqlite3.connect('users.db') as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/login', methods=['POST'])
def login():
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

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8080, debug=True)
