from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_cors import CORS
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
if os.environ.get('FLASK_ENV') == 'production':
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///users.db')
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
    
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
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
    if current_user.is_authenticated:
        return redirect(url_for('home'))
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
        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            flash('Invalid email or password. Please try again.', 'error')
            return redirect(url_for('login'))

        login_user(user)
        user.last_login = datetime.utcnow()
        db.session.commit()
        return redirect(url_for('home'))

    return render_template('login.html')

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400
    
    user = User.query.filter_by(email=email).first()
    
    if user and check_password_hash(user.password, password):
        user.last_login = datetime.utcnow()
        db.session.commit()
        return jsonify({
            "message": "Login successful",
            "username": user.username,
            "email": user.email
        })
    return jsonify({"message": "Invalid email or password"}), 401

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        terms = request.form.get('terms')

        if not username or not email or not password or not confirm_password:
            flash('All fields are required.', 'error')
            return redirect(url_for('signup'))

        if not terms:
            flash('You must agree to the Terms and Privacy Policy.', 'error')
            return redirect(url_for('signup'))

        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose a different username.', 'error')
            return redirect(url_for('signup'))

        if User.query.filter_by(email=email).first():
            flash('Email already exists. Please login or use a different email.', 'error')
            return redirect(url_for('signup'))

        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('signup'))

        # Password strength validation
        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'error')
            return redirect(url_for('signup'))

        if not any(c.isupper() for c in password):
            flash('Password must contain at least one uppercase letter.', 'error')
            return redirect(url_for('signup'))

        if not any(c.islower() for c in password):
            flash('Password must contain at least one lowercase letter.', 'error')
            return redirect(url_for('signup'))

        if not any(c.isdigit() for c in password):
            flash('Password must contain at least one number.', 'error')
            return redirect(url_for('signup'))

        if not any(c in '!@#$%^&*(),.?":{}|<>' for c in password):
            flash('Password must contain at least one special character.', 'error')
            return redirect(url_for('signup'))

        try:
            hashed_password = generate_password_hash(password)
            new_user = User(username=username, email=email, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('Error creating account. Please try again.', 'error')
            return redirect(url_for('signup'))

    return render_template('signup.html')

@app.route('/api/signup', methods=['POST'])
def signup_api():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not username or not email or not password:
        return jsonify({"message": "Username, email and password are required"}), 400
    
    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username already exists"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already exists"}), 400
    
    try:
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User created successfully"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error creating user"}), 500

@app.route('/api/check-password', methods=['POST'])
def check_strength():
    data = request.get_json()
    password = data.get('password')
    return jsonify(check_password_strength(password))

def check_password_strength(password):
    score = 0
    feedback = []
    
    if len(password) >= 8:
        score += 1
    else:
        feedback.append("Password should be at least 8 characters long")
    
    if re.search(r"[A-Z]", password):
        score += 1
    else:
        feedback.append("Include at least one uppercase letter")
    
    if re.search(r"[a-z]", password):
        score += 1
    else:
        feedback.append("Include at least one lowercase letter")
    
    if re.search(r"\d", password):
        score += 1
    else:
        feedback.append("Include at least one number")
    
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

@app.route('/forgot-password')
def forgot_password():
    return render_template('forgot-password.html')

@app.route('/api/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({"message": "Email is required"}), 400
    
    user = User.query.filter_by(email=email).first()
    
    if user:
        # In a real application, send a password reset email
        return jsonify({
            "message": "If an account exists with this email, password reset instructions have been sent."
        })
    else:
        # For security, don't reveal if the email exists or not
        return jsonify({
            "message": "If an account exists with this email, password reset instructions have been sent."
        }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
