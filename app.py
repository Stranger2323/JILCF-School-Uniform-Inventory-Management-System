from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from functools import wraps
import os
from models import db, Item, Stock, StockTransaction
from sqlalchemy import or_
import random
import string
from datetime import datetime
import click
from flask.cli import with_appcontext
from flask_socketio import SocketIO, emit
import json

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Generate a secure secret key

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Initialize SocketIO with the app - use threading instead of eventlet
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Hardcoded credentials (in production, use a secure database)
VALID_EMAIL = "jilcfadministratoruser@jilcf.com"
VALID_PASSWORD = "JILCF2025"

# Admin role check
def is_admin():
    return 'user' in session and session['user'] == VALID_EMAIL

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_admin():
            flash('Admin access required', 'error')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def login():
    if 'user' in session:
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/verify', methods=['POST'])
def verify():
    email = request.form.get('email')
    password = request.form.get('password')
    
    if email == VALID_EMAIL and password == VALID_PASSWORD:
        session['user'] = email
        session.permanent = True  # Make session persistent
        return jsonify({'success': True})
    return jsonify({'success': False})

@app.route('/home')
@login_required
def home():
    return render_template('home.html', active_page='home')

@app.route('/inventory')
@login_required
def inventory():
    # Query all items with their stock information grouped by category
    inventory_data = {}
    
    # Get all items from the database
    items = Item.query.all()
    
    # Organize items by category and gender
    for item in items:
        # Create category entry if it doesn't exist
        if item.category not in inventory_data:
            inventory_data[item.category] = {
                'male': {},
                'female': {},
                'unisex': {}
            }
        
        # Get all stock entries for this item
        stocks = Stock.query.filter_by(item_id=item.id).all()
        
        # Skip items with no stock entries
        if not stocks:
            continue
        
        # Skip patch items in Junior High category
        if item.item_type == 'patch' and item.category.lower() == 'juniorhigh':
            continue
        
        # Prepare item data with sizes and prices
        item_data = {
            'name': item.name,
            'sizes': {stock.size: {'price': stock.price, 'quantity': stock.quantity, 'status': stock.status} for stock in stocks}
        }
        
        # Add item to the appropriate gender category
        if item.gender == 'unisex':
            # All unisex items go to unisex category
            inventory_data[item.category]['unisex'][item.item_type] = item_data
        # Check if item is a Patch (should be moved to unisex/both gender)
        elif item.item_type == 'patch' or item.item_type.endswith('_patch'):
            # Move patches to unisex category
            inventory_data[item.category]['unisex'][item.item_type] = item_data
        else:
            # Regular gender-specific items
            inventory_data[item.category][item.gender][item.item_type] = item_data
    
    # You can change template here if needed: 'inventory.html', 'inventory_current.html', or keep 'db_inventory.html'
    return render_template('db_inventory.html', categories=inventory_data, is_admin=is_admin(), active_page='inventory')

@app.route('/admin/inventory')
@login_required
@admin_required
def admin_inventory():
    return render_template('admin_inventory.html', active_page='admin_inventory')

@app.route('/api/items', methods=['GET'])
@login_required
def get_items():
    category = request.args.get('category')
    gender = request.args.get('gender')
    
    query = Item.query
    if category:
        query = query.filter_by(category=category)
    if gender:
        query = query.filter_by(gender=gender)
        
    items = query.all()
    result = []
    
    for item in items:
        item_data = {
            'id': item.id,
            'name': item.name,
            'category': item.category,
            'gender': item.gender,
            'item_type': item.item_type,
            'stocks': []
        }
        
        for stock in item.stocks:
            item_data['stocks'].append({
                'id': stock.id,
                'size': stock.size,
                'quantity': stock.quantity,
                'price': stock.price,
                'status': stock.status,
                'threshold': stock.threshold
            })
            
        result.append(item_data)
        
    return jsonify(result)

@app.route('/api/items/<int:item_id>', methods=['GET'])
@login_required
def get_item(item_id):
    item = Item.query.get_or_404(item_id)
    
    item_data = {
        'id': item.id,
        'name': item.name,
        'category': item.category,
        'gender': item.gender,
        'item_type': item.item_type,
        'stocks': []
    }
    
    for stock in item.stocks:
        item_data['stocks'].append({
            'id': stock.id,
            'size': stock.size,
            'quantity': stock.quantity,
            'price': stock.price,
            'status': stock.status,
            'threshold': stock.threshold
        })
        
    return jsonify(item_data)

@app.route('/api/stock/<int:stock_id>', methods=['PUT'])
@login_required
@admin_required
def update_stock(stock_id):
    stock = Stock.query.get_or_404(stock_id)
    data = request.json
    
    if 'quantity' in data:
        old_quantity = stock.quantity
        new_quantity = int(data['quantity'])
        quantity_change = new_quantity - old_quantity
        
        # Update stock
        stock.quantity = new_quantity
        
        if 'price' in data:
            stock.price = float(data['price'])
        
        if 'threshold' in data:
            stock.threshold = int(data['threshold'])
        
        # Record transaction
        transaction = StockTransaction(
            stock_id=stock.id,
            quantity_change=quantity_change,
            transaction_type='adjustment',
            notes=data.get('notes', 'Stock adjustment'),
            created_by=session['user']
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        # Emit a stock update event via WebSocket
        stock_item = Item.query.get(stock.item_id)
        socketio.emit('stock_update', {
            'item_id': stock.item_id,
            'item_name': stock_item.name,
            'category': stock_item.category,
            'gender': stock_item.gender,
            'item_type': stock_item.item_type,
            'size': stock.size,
            'quantity': stock.quantity,
            'status': stock.status
        })
        
        return jsonify({
            'success': True, 
            'stock': {
                'id': stock.id,
                'quantity': stock.quantity,
                'price': stock.price,
                'status': stock.status,
                'threshold': stock.threshold
            }
        })
    
    return jsonify({'success': False, 'error': 'Missing required data'})

@app.route('/api/stock/<int:stock_id>/sell', methods=['POST'])
@login_required
def sell_stock(stock_id):
    stock = Stock.query.get_or_404(stock_id)
    data = request.json
    
    quantity = int(data.get('quantity', 1))
    
    if quantity <= 0:
        return jsonify({'success': False, 'error': 'Invalid quantity'})
    
    if stock.quantity < quantity:
        return jsonify({'success': False, 'error': 'Not enough stock'})
    
    # Generate receipt number
    receipt_number = generate_receipt_number()
    
    # Update stock
    stock.quantity -= quantity
    
    # Record transaction
    transaction = StockTransaction(
        stock_id=stock.id,
        quantity_change=-quantity,
        transaction_type='sell',
        receipt_number=receipt_number,
        notes=data.get('notes', ''),
        created_by=session['user']
    )
    
    db.session.add(transaction)
    db.session.commit()
    
    # Emit a stock update event via WebSocket
    stock_item = Item.query.get(stock.item_id)
    socketio.emit('stock_update', {
        'item_id': stock.item_id,
        'item_name': stock_item.name,
        'category': stock_item.category,
        'gender': stock_item.gender,
        'item_type': stock_item.item_type,
        'size': stock.size,
        'quantity': stock.quantity,
        'status': stock.status
    })
    
    return jsonify({
        'success': True, 
        'receipt_number': receipt_number,
        'stock': {
            'id': stock.id,
            'quantity': stock.quantity,
            'status': stock.status
        }
    })

@app.route('/api/transactions', methods=['GET'])
@login_required
def get_transactions():
    transaction_type = request.args.get('type')
    
    # Query transactions with optional filters
    query = db.session.query(
        StockTransaction,
        Stock,
        Item
    ).join(
        Stock, StockTransaction.stock_id == Stock.id
    ).join(
        Item, Stock.item_id == Item.id
    ).order_by(StockTransaction.created_at.desc())
    
    # Apply transaction type filter if provided
    if transaction_type:
        query = query.filter(StockTransaction.transaction_type == transaction_type)
    
    # Execute query and format results
    results = []
    for transaction, stock, item in query.all():
        # Ensure created_at is a proper ISO format string
        created_at_iso = transaction.created_at.isoformat() + 'Z' if transaction.created_at.tzinfo is None else transaction.created_at.isoformat()
        
        results.append({
            'id': transaction.id,
            'item_name': item.name,
            'category': item.category,
            'gender': item.gender,
            'size': stock.size,
            'price': stock.price,
            'quantity_change': transaction.quantity_change,
            'transaction_type': transaction.transaction_type,
            'receipt_number': transaction.receipt_number,
            'notes': transaction.notes,
            'created_by': transaction.created_by,
            'created_at': created_at_iso
        })
    
    return jsonify(results)

@app.route('/api/stock/<int:stock_id>/reduce', methods=['POST'])
@login_required
def reduce_stock(stock_id):
    stock = Stock.query.get_or_404(stock_id)
    data = request.json
    
    quantity = int(data.get('quantity', 1))
    
    if quantity <= 0:
        return jsonify({'success': False, 'error': 'Invalid quantity'})
    
    if stock.quantity < quantity:
        return jsonify({'success': False, 'error': 'Not enough stock'})
    
    # Generate receipt number
    receipt_number = generate_receipt_number()
    
    # Update stock
    stock.quantity -= quantity
    
    # Record transaction
    transaction = StockTransaction(
        stock_id=stock.id,
        quantity_change=-quantity,
        transaction_type='reduce',
        receipt_number=receipt_number,
        notes=data.get('notes', 'Stock reduction'),
        created_by=session['user']
    )
    
    db.session.add(transaction)
    db.session.commit()
    
    # Emit a stock update event via WebSocket
    stock_item = Item.query.get(stock.item_id)
    socketio.emit('stock_update', {
        'item_id': stock.item_id,
        'item_name': stock_item.name,
        'category': stock_item.category,
        'gender': stock_item.gender,
        'item_type': stock_item.item_type,
        'size': stock.size,
        'quantity': stock.quantity,
        'status': stock.status
    })
    
    return jsonify({
        'success': True, 
        'receipt_number': receipt_number,
        'stock': {
            'id': stock.id,
            'quantity': stock.quantity,
            'status': stock.status
        }
    })

def generate_receipt_number():
    # Generate a unique receipt number format: JILCF-YYYYMMDD-XXXXX
    date_part = datetime.now().strftime('%Y%m%d')
    random_part = ''.join(random.choices(string.digits, k=5))
    return f"JILCF-{date_part}-{random_part}"

@app.route('/api/initialize-db', methods=['POST'])
@login_required
@admin_required
def initialize_db():
    """Initialize the database with preset uniform data"""
    try:
        # Create database tables if they don't exist
        with app.app_context():
            db.create_all()
            
            # Only add sample data if the database is empty
            if Item.query.count() == 0:
                # Add sample data from your existing priceData structure
                # This would be filled with your data
                initialize_sample_data()
                
            return jsonify({'success': True, 'message': 'Database initialized successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def initialize_sample_data():
    # Sample data structure based on your existing frontend data
    uniform_data = {
        'preschool': {
            'pe_tshirt': {
                'name': 'PE T-shirt',
                'sizes': {
                    '6': 240, '8': 240, '10': 240, '12': 240, '14': 240,
                    '16': 255, '18': 255, '20': 255, 'XS': 255, 'S': 270
                }
            },
            'pe_pants': {
                'name': 'PE Jogging Pants',
                'sizes': {
                    '6': 380, '8': 380, '10': 380, '12': 380, '14': 380,
                    '16': 380, '18': 380, '20': 380
                }
            },
            'male': {
                'polo_shirt': {
                    'name': 'Polo Shirt',
                    'sizes': {
                        '6': 350, '8': 350, '10': 350, '12': 350, '14': 350,
                        '16': 350, '18': 350, '20': 350
                    }
                },
                'short_pants': {
                    'name': 'Short Pants',
                    'sizes': {
                        '6': 360, '8': 360, '10': 360, '12': 360, '14': 360,
                        '16': 360, '18': 360, '20': 360
                    }
                }
            },
            'female': {
                'blouse': {
                    'name': 'Blouse',
                    'sizes': {
                        '6': 370, '8': 370, '10': 370, '12': 370, '14': 370,
                        '16': 370, '18': 370, '20': 370
                    }
                },
                'skirt': {
                    'name': 'Skirt',
                    'sizes': {
                        '6': 360, '8': 360, '10': 360, '12': 360, '14': 360,
                        '16': 360, '18': 360, '20': 360
                    }
                },
                'patch': {
                    'name': 'Patch',
                    'sizes': {
                        'Regular': 120
                    }
                }
            }
        }
        # Other categories would follow the same pattern
    }
    
    # Add items to database
    for category, category_data in uniform_data.items():
        # Handle PE items which are gender-neutral
        if 'pe_tshirt' in category_data:
            # Add PE T-shirt item
            pe_tshirt = Item(
                name=category_data['pe_tshirt']['name'],
                category=category,
                gender='unisex',
                item_type='pe_tshirt'
            )
            db.session.add(pe_tshirt)
            db.session.flush()  # Get ID before adding stocks
            
            # Add PE T-shirt stocks
            for size, price in category_data['pe_tshirt']['sizes'].items():
                stock = Stock(
                    item_id=pe_tshirt.id,
                    size=size,
                    quantity=10,  # Default starting quantity
                    price=price,
                    threshold=3   # Default low stock threshold
                )
                db.session.add(stock)
        
        if 'pe_pants' in category_data:
            # Add PE Pants item
            pe_pants = Item(
                name=category_data['pe_pants']['name'],
                category=category,
                gender='unisex',
                item_type='pe_pants'
            )
            db.session.add(pe_pants)
            db.session.flush()  # Get ID before adding stocks
            
            # Add PE Pants stocks
            for size, price in category_data['pe_pants']['sizes'].items():
                stock = Stock(
                    item_id=pe_pants.id,
                    size=size,
                    quantity=10,  # Default starting quantity
                    price=price,
                    threshold=3   # Default low stock threshold
                )
                db.session.add(stock)
        
        # Handle gender-specific items
        for gender in ['male', 'female']:
            if gender in category_data:
                for item_type, item_data in category_data[gender].items():
                    # Add item
                    item = Item(
                        name=item_data['name'],
                        category=category,
                        gender=gender,
                        item_type=item_type
                    )
                    db.session.add(item)
                    db.session.flush()  # Get ID before adding stocks
                    
                    # Add stocks
                    for size, price in item_data['sizes'].items():
                        stock = Stock(
                            item_id=item.id,
                            size=size,
                            quantity=10,  # Default starting quantity
                            price=price,
                            threshold=3   # Default low stock threshold
                        )
                        db.session.add(stock)
    
    db.session.commit()

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    try:
        session.pop('user', None)
        if request.method == 'POST':
            return jsonify({'success': True})
        return redirect(url_for('login'))
    except Exception as e:
        app.logger.error(f"Logout error: {str(e)}")
        if request.method == 'POST':
            return jsonify({'success': False, 'error': str(e)}), 500
        return redirect(url_for('login'))

# Replace @app.before_first_request with a with_appcontext function
@click.command('create-tables')
@with_appcontext
def create_tables():
    """Create database tables."""
    db.create_all()
    print("Tables created successfully!")

# Add the command to the Flask CLI
app.cli.add_command(create_tables)

# Create app initialization function
def init_app(app):
    # Register the command with Flask CLI
    app.cli.add_command(create_tables)
    
# Remove or comment out the before_first_request decorator
# @app.before_first_request
# def create_tables():
#     db.create_all()

# Add a socket event handler for stock updates
@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

# Update the main function to use socketio.run
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, host='0.0.0.0', port=5000, debug=True) 