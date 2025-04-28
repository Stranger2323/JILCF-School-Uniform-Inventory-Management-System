from app import app, db
from models import Item, Stock

def remove_necktie_items():
    """Remove necktie items from preschool and elementary categories"""
    with app.app_context():
        # Find all necktie items for preschool and elementary
        necktie_items = Item.query.filter(
            Item.item_type == 'necktie',
            Item.gender == 'female',
            Item.category.in_(['preschool', 'elementary'])
        ).all()
        
        # Print what we found
        print(f"Found {len(necktie_items)} necktie items to remove:")
        for item in necktie_items:
            print(f"- {item.category} {item.gender} {item.name} (ID: {item.id})")
        
        if not necktie_items:
            print("No necktie items found in preschool or elementary categories.")
            return
            
        # Ask for confirmation
        confirmation = input("Do you want to delete these items? (yes/no): ")
        if confirmation.lower() != 'yes':
            print("Operation cancelled.")
            return
        
        # Delete the items and their associated stocks
        for item in necktie_items:
            # Delete associated stocks first
            stocks = Stock.query.filter_by(item_id=item.id).all()
            print(f"Deleting {len(stocks)} stock entries for {item.category} {item.name}")
            for stock in stocks:
                db.session.delete(stock)
            
            # Then delete the item
            print(f"Deleting {item.category} {item.name}")
            db.session.delete(item)
        
        # Commit the changes
        db.session.commit()
        print("Necktie items successfully removed from the database!")

if __name__ == "__main__":
    remove_necktie_items() 