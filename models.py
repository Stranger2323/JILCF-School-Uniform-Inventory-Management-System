from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # preschool, elementary, juniorhigh, seniorhigh
    gender = db.Column(db.String(10), nullable=False)    # male, female
    item_type = db.Column(db.String(50), nullable=False) # polo_shirt, blouse, pants, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with Stock
    stocks = db.relationship('Stock', backref='item', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Item {self.name} ({self.category}-{self.gender})>"

class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    size = db.Column(db.String(20), nullable=False)      # XS, S, M, L, XL, etc.
    quantity = db.Column(db.Integer, default=0)
    price = db.Column(db.Float, nullable=False)
    threshold = db.Column(db.Integer, default=5)         # Low stock threshold
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Stock {self.item_id} Size:{self.size} Qty:{self.quantity}>"
    
    @property
    def status(self):
        if self.quantity <= 0:
            return "out_of_stock"
        elif self.quantity <= self.threshold:
            return "low_stock"
        else:
            return "in_stock"

class StockTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stock.id'), nullable=False)
    quantity_change = db.Column(db.Integer, nullable=False)  # Positive for additions, negative for reductions
    transaction_type = db.Column(db.String(20), nullable=False)  # 'add', 'remove', 'adjustment'
    receipt_number = db.Column(db.String(50))  # For sales
    notes = db.Column(db.Text)
    created_by = db.Column(db.String(100))  # User who made the transaction
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with Stock
    stock = db.relationship('Stock', backref='transactions')
    
    def __repr__(self):
        return f"<Transaction {self.id} Stock:{self.stock_id} Change:{self.quantity_change}>" 