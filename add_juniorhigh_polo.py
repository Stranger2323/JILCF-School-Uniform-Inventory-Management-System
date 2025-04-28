from app import app, db
from models import Item, Stock

def add_juniorhigh_polo():
    """Add the missing Junior High polo shirt item to the database"""
    with app.app_context():
        # Check if the polo shirt already exists
        existing_polo = Item.query.filter_by(
            category='juniorhigh',
            gender='male',
            item_type='polo_shirt'
        ).first()
        
        if existing_polo:
            print(f"Junior High polo shirt already exists with ID: {existing_polo.id}")
            print("Checking if it has all required sizes...")
            
            # Get current stocks
            existing_sizes = [stock.size for stock in existing_polo.stocks]
            print(f"Existing sizes: {existing_sizes}")
            
            # Define expected sizes
            expected_sizes = ['XS', 'S', 'M', 'L', 'XL', '2XL', '3XL', '4XL']
            
            # Check for missing sizes
            missing_sizes = [size for size in expected_sizes if size not in existing_sizes]
            
            if missing_sizes:
                print(f"Adding missing sizes: {missing_sizes}")
                for size in missing_sizes:
                    # Determine price based on size
                    if size == 'XS':
                        price = 375
                    elif size == 'S':
                        price = 390
                    elif size == 'M':
                        price = 400
                    elif size == 'L':
                        price = 415
                    elif size == 'XL':
                        price = 440
                    elif size == '2XL':
                        price = 460
                    elif size == '3XL':
                        price = 490
                    else:  # '4XL'
                        price = 520
                    
                    # Add stock for missing size
                    stock = Stock(
                        item_id=existing_polo.id,
                        size=size,
                        quantity=10,
                        price=price,
                        threshold=3
                    )
                    db.session.add(stock)
                
                db.session.commit()
                print("Added missing sizes successfully!")
            else:
                print("All expected sizes already exist.")
            
            return
        
        # Create new polo shirt item
        print("Creating new Junior High polo shirt item...")
        polo = Item(
            name='Polo Shirt w/ Patch',
            category='juniorhigh',
            gender='male',
            item_type='polo_shirt'
        )
        db.session.add(polo)
        db.session.flush()  # Get ID before adding stocks
        
        # Add stocks with appropriate sizes and prices
        size_prices = {
            'XS': 375, 'S': 390, 'M': 400, 'L': 415, 
            'XL': 440, '2XL': 460, '3XL': 490, '4XL': 520
        }
        
        for size, price in size_prices.items():
            stock = Stock(
                item_id=polo.id,
                size=size,
                quantity=10,  # Default starting quantity
                price=price,
                threshold=3   # Default low stock threshold
            )
            db.session.add(stock)
        
        db.session.commit()
        print(f"Junior High polo shirt successfully added with ID: {polo.id}")

if __name__ == "__main__":
    add_juniorhigh_polo() 