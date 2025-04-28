from app import app, db, Item, Stock

def add_shs_patches():
    """Add SHS strand patches to the database"""
    with app.app_context():
        # Strands to add
        strands = ['ABM', 'STEM', 'HUMSS', 'TVL']
        
        # Check if any strands already exist
        for strand in strands:
            item_type = f"patch_{strand.lower()}"
            existing = Item.query.filter_by(category='seniorhigh', item_type=item_type).first()
            
            if existing:
                print(f"Patch for {strand} already exists, skipping...")
                continue
            
            print(f"Adding {strand} patch to database...")
            # Create new item
            new_patch = Item(
                name=f"Patch - {strand}",
                category='seniorhigh',
                gender='unisex',  # Make it available for both genders
                item_type=item_type
            )
            db.session.add(new_patch)
            db.session.flush()  # Get ID for stock creation
            
            # Add stock for the patch
            stock = Stock(
                item_id=new_patch.id,
                size='Regular',  # Patches usually have a standard size
                quantity=10,     # Initial quantity
                price=120.0,     # Standard price for patches
                threshold=3      # Low stock threshold
            )
            db.session.add(stock)
        
        # Commit changes
        db.session.commit()
        print("SHS strand patches added successfully!")

if __name__ == "__main__":
    add_shs_patches() 