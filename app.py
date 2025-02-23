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
        remember = request.form.get('remember') == 'on'
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user, remember=remember)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('home'))
        
        flash('Invalid email or password')
        return redirect(url_for('index'))
    
    return redirect(url_for('index'))

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400
    
    user = User.query.filter_by(email=email).first()
    
    if user and check_password_hash(user.password, password):
        return jsonify({
            "message": "Login successful",
            "name": user.username
        })
    return jsonify({"message": "Invalid email or password"}), 401

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('signup'))
        
        hashed_password = generate_password_hash(password)
        user = User(username=username, email=email, password=hashed_password)
        
        try:
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('home'))
        except:
            db.session.rollback()
            flash('Error creating account')
            return redirect(url_for('signup'))
            
    return render_template('signup.html')

@app.route('/api/signup', methods=['POST'])
def signup_api():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not all([username, email, password]):
        return jsonify({"message": "All fields are required"}), 400
        
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already registered"}), 400
    
    hashed_password = generate_password_hash(password)
    user = User(username=username, email=email, password=hashed_password)
    
    try:
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "Account created successfully"})
    except:
        db.session.rollback()
        return jsonify({"message": "Error creating account"}), 500

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
