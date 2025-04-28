from app import app, db
from models import Item, Stock

def add_juniorhigh_blouse():
    """Add the missing Junior High blouse item to the database"""
    with app.app_context():
        # Check if the blouse already exists
        existing_blouse = Item.query.filter_by(
            category='juniorhigh',
            gender='female',
            item_type='blouse'
        ).first()
        
        if existing_blouse:
            print(f"Junior High blouse already exists with ID: {existing_blouse.id}")
            print("Checking if it has all required sizes...")
            
            # Get current stocks
            existing_sizes = [stock.size for stock in existing_blouse.stocks]
            print(f"Existing sizes: {existing_sizes}")
            
            # Define expected sizes
            expected_sizes = ['XS', 'S', 'M', 'L', 'XL', '2XL', '3XL', '4XL']
            
            # Check for missing sizes
            missing_sizes = [size for size in expected_sizes if size not in existing_sizes]
            
            if missing_sizes:
                print(f"Adding missing sizes: {missing_sizes}")
                for size in missing_sizes:
                    # Determine price based on size
                    if size in ['XS', 'S', 'M', 'L']:
                        price = 295
                    elif size in ['XL', '2XL']:
                        price = 325
                    elif size == '3XL':
                        price = 385
                    else:  # '4XL'
                        price = 345
                    
                    # Add stock for missing size
                    stock = Stock(
                        item_id=existing_blouse.id,
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
        
        # Create new blouse item
        print("Creating new Junior High blouse item...")
        blouse = Item(
            name='Blouse w/ Patch',
            category='juniorhigh',
            gender='female',
            item_type='blouse'
        )
        db.session.add(blouse)
        db.session.flush()  # Get ID before adding stocks
        
        # Add stocks with appropriate sizes and prices
        size_prices = {
            'XS': 295, 'S': 295, 'M': 295, 'L': 295, 
            'XL': 325, '2XL': 325, '3XL': 385, '4XL': 345
        }
        
        for size, price in size_prices.items():
            stock = Stock(
                item_id=blouse.id,
                size=size,
                quantity=10,  # Default starting quantity
                price=price,
                threshold=3   # Default low stock threshold
            )
            db.session.add(stock)
        
        db.session.commit()
        print(f"Junior High blouse successfully added with ID: {blouse.id}")

if __name__ == "__main__":
    add_juniorhigh_blouse() 