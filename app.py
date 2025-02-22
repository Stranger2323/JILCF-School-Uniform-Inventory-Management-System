from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3
import hashlib
import re
import os

app = Flask(__name__)
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

@app.route('/signup')
def signup_page():
    return render_template('signup.html')

@app.route('/forgot-password')
def forgot_password_page():
    return render_template('forgot-password.html')

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    
    # Check password strength
    strength_check = check_password_strength(password)
    if strength_check['score'] < 3:  # Require at least "Good" strength
        return jsonify({
            "success": False,
            "message": "Password not strong enough",
            "feedback": strength_check
        }), 400
    
    try:
        with sqlite3.connect('users.db') as conn:
            c = conn.cursor()
            c.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)',
                     (name, email, hash_password(password)))
            conn.commit()
        return jsonify({"success": True, "message": "User registered successfully"})
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "message": "Email already exists"}), 400
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    try:
        with sqlite3.connect('users.db') as conn:
            c = conn.cursor()
            c.execute('SELECT name, password FROM users WHERE email = ?', (email,))
            user = c.fetchone()
            
            if user and user[1] == hash_password(password):
                return jsonify({
                    "success": True,
                    "message": "Login successful",
                    "name": user[0]
                })
            return jsonify({
                "success": False,
                "message": "Invalid email or password"
            }), 401
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/check-password-strength', methods=['POST'])
def check_strength():
    data = request.json
    password = data.get('password')
    return jsonify(check_password_strength(password))

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8080, debug=True)
