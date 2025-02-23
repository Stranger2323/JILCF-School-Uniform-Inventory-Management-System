from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_cors import CORS
from flask_mail import Mail, Message
import os
import re
from datetime import datetime, timedelta
import requests
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from oauthlib.oauth2 import WebApplicationClient
import json
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import random
import string
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app)

# Load environment variables
IS_PRODUCTION = bool(os.getenv('RENDER', False))

# OAuth 2 client setup
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
    app.logger.error("Google OAuth credentials not found! Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables.")

# Configure HTTPS for OAuth
if not IS_PRODUCTION:
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# OAuth configuration
app.config['OAUTH_CREDENTIALS'] = {
    'google': {
        'id': GOOGLE_CLIENT_ID,
        'secret': GOOGLE_CLIENT_SECRET
    }
}

client = WebApplicationClient(GOOGLE_CLIENT_ID)

def get_google_provider_cfg():
    try:
        return requests.get(GOOGLE_DISCOVERY_URL, timeout=5).json()
    except Exception as e:
        app.logger.error(f"Failed to get Google provider config: {e}")
        return None

mail = Mail(app)
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    last_login = db.Column(db.DateTime, default=datetime.utcnow)
    name = db.Column(db.String(1000))
    is_verified = db.Column(db.Boolean, default=False)
    otp = db.Column(db.String(6))
    otp_created_at = db.Column(db.DateTime)

    def __repr__(self):
        return f'<User {self.username}>'

    def get_id(self):
        return str(self.id)

    def is_active(self):
        return True

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

def send_otp_email(email, otp):
    msg = Message('Email Verification Code',
                sender=app.config['MAIL_USERNAME'],
                recipients=[email])
    msg.body = f'Your verification code is: {otp}'
    mail.send(msg)

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route('/home')
@login_required
def home():
    return render_template('home.html')

@app.route("/login/google")
def google_login():
    try:
        if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
            app.logger.error("Google OAuth credentials not configured")
            flash("Google login is not configured properly. Please contact the administrator.", "error")
            return redirect(url_for('login'))

        # Find out what URL to hit for Google login
        google_provider_cfg = get_google_provider_cfg()
        if not google_provider_cfg:
            flash("Error connecting to Google services", "error")
            return redirect(url_for('login'))

        authorization_endpoint = google_provider_cfg["authorization_endpoint"]
        
        # Use the correct redirect URI based on environment
        if IS_PRODUCTION:
            redirect_uri = "https://jilcf-school-uniform-inventory.onrender.com/login/google/callback"
            app.logger.info("Using production redirect URI")
        else:
            redirect_uri = url_for('google_callback', _external=True, _scheme='http')
            app.logger.info("Using development redirect URI")

        app.logger.info(f"Using redirect URI: {redirect_uri}")

        # Construct the request for Google login
        request_uri = client.prepare_request_uri(
            authorization_endpoint,
            redirect_uri=redirect_uri,
            scope=["openid", "email", "profile"],
            prompt="select_account"
        )
        
        app.logger.info(f"Redirecting to Google auth: {request_uri}")
        return redirect(request_uri)
    except Exception as e:
        app.logger.error(f"Error in google_login: {str(e)}")
        flash("Failed to initiate Google login. Please try again.", "error")
        return redirect(url_for('login'))

@app.route('/login/google/callback')
def google_callback():
    try:
        # Get authorization code Google sent back
        code = request.args.get("code")
        if not code:
            app.logger.error("No code received from Google")
            flash("Authentication failed - No code received", "error")
            return redirect(url_for('login'))

        # Get the correct redirect URI based on environment
        if IS_PRODUCTION:
            redirect_uri = "https://jilcf-school-uniform-inventory.onrender.com/login/google/callback"
        else:
            redirect_uri = url_for('google_callback', _external=True, _scheme='http')

        app.logger.info(f"Using callback redirect URI: {redirect_uri}")

        # Get token endpoint
        google_provider_cfg = get_google_provider_cfg()
        if not google_provider_cfg:
            app.logger.error("Failed to get Google provider configuration")
            raise Exception("Failed to get Google provider configuration")
            
        token_endpoint = google_provider_cfg["token_endpoint"]
        app.logger.info(f"Token endpoint: {token_endpoint}")

        # Prepare token request
        token_url, headers, body = client.prepare_token_request(
            token_endpoint,
            authorization_response=request.url,
            redirect_url=redirect_uri,
            code=code
        )
        app.logger.info(f"Preparing token request to: {token_url}")

        # Add client authentication
        token_response = requests.post(
            token_url,
            headers=headers,
            data=body,
            auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
            timeout=5
        )

        app.logger.info(f"Token response status: {token_response.status_code}")
        if token_response.status_code != 200:
            app.logger.error(f"Token response error: {token_response.text}")
            raise Exception(f"Failed to get token: {token_response.text}")

        # Parse the token response
        client.parse_request_body_response(token_response.text)

        # Get user info from Google
        userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
        app.logger.info(f"Getting user info from: {userinfo_endpoint}")
        
        uri, headers, body = client.add_token(userinfo_endpoint)
        userinfo_response = requests.get(uri, headers=headers, data=body, timeout=5)

        app.logger.info(f"Userinfo response status: {userinfo_response.status_code}")
        if userinfo_response.status_code != 200:
            app.logger.error(f"Userinfo response error: {userinfo_response.text}")
            raise Exception(f"Failed to get user info: {userinfo_response.text}")

        if userinfo_response.json().get("email_verified"):
            unique_id = userinfo_response.json()["sub"]
            users_email = userinfo_response.json()["email"]
            users_name = userinfo_response.json().get("name", users_email.split('@')[0])
            
            app.logger.info(f"Authenticated user: {users_email}")
            
            # Only allow specific test users
            allowed_users = ['josiahdeasis009@gmail.com', 'urbanninvidz2@gmail.com']
            if users_email not in allowed_users:
                app.logger.error(f"User not in allowed list: {users_email}")
                flash("Access denied. Only test users are allowed.", "error")
                return redirect(url_for('login'))
            
            # Create or update user
            user = User.query.filter_by(email=users_email).first()
            if not user:
                user = User(
                    username=users_email,
                    email=users_email,
                    name=users_name,
                    password=generate_password_hash(unique_id),
                    is_verified=True
                )
                db.session.add(user)
                db.session.commit()
                app.logger.info(f"Created new user: {users_email}")
            
            # Log in the user
            login_user(user)
            app.logger.info(f"Logged in user: {users_email}")
            return redirect(url_for('home'))
        else:
            app.logger.error("Email not verified by Google")
            flash("Google login failed - Email not verified", "error")
            return redirect(url_for('login'))

    except Exception as e:
        app.logger.error(f"Error in Google callback: {str(e)}")
        flash("Failed to complete Google authentication. Please try again.", "error")
        return redirect(url_for('login'))

@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if 'email' not in session:
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        entered_otp = request.form.get('otp')
        user = User.query.filter_by(email=session['email']).first()
        
        if user and user.otp == entered_otp:
            # Check if OTP is not expired (15 minutes validity)
            if (datetime.utcnow() - user.otp_created_at).total_seconds() <= 900:
                user.is_verified = True
                user.otp = None  # Clear the OTP
                db.session.commit()
                login_user(user)
                flash('Email verified successfully!', 'success')
                return redirect(url_for('home'))
            else:
                flash('OTP has expired. Please request a new one.', 'error')
                return redirect(url_for('login'))
        else:
            flash('Invalid OTP. Please try again.', 'error')
            
    return render_template('verify_otp.html')

@app.route('/resend-otp')
def resend_otp():
    if 'email' not in session:
        return redirect(url_for('login'))
        
    user = User.query.filter_by(email=session['email']).first()
    if user:
        otp = generate_otp()
        user.otp = otp
        user.otp_created_at = datetime.utcnow()
        db.session.commit()
        
        send_otp_email(session['email'], otp)
        flash('New OTP has been sent to your email.', 'success')
    else:
        flash('User not found.', 'error')
        
    return redirect(url_for('verify_otp'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not check_password_hash(user.password, password):
            flash('Please check your login details and try again.', 'error')
            return redirect(url_for('login'))
            
        login_user(user, remember=remember)
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        return redirect(url_for('home'))
        
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Check if user already exists
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email address already exists', 'error')
            return redirect(url_for('signup'))
            
        # Create new user
        new_user = User(
            username=username,
            email=email,
            password=generate_password_hash(password, method='sha256')
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Successfully registered! Please log in.', 'success')
        return redirect(url_for('login'))
        
    return render_template('signup.html')

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
    import logging
    logging.basicConfig(level=logging.INFO)
    app.logger.setLevel(logging.INFO)
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=True)
