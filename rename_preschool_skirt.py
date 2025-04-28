from app import app, db, Item

def rename_preschool_skirt():
    """Rename preschool skirt to jumper dress"""
    with app.app_context():
        # Find the skirt item in preschool category
        skirt_items = Item.query.filter(
            Item.category == 'preschool',
            Item.item_type.like('%skirt%')
        ).all()
        
        if skirt_items:
            print(f"Found {len(skirt_items)} skirt items in preschool category:")
            for item in skirt_items:
                old_name = item.name
                old_type = item.item_type
                
                # Update the name to "Jumper Dress"
                item.name = "Jumper Dress"
                
                # Update the item_type from skirt to jumper_dress
                item.item_type = item.item_type.replace('skirt', 'jumper_dress')
                
                # Log the changes
                print(f"Renamed: '{old_name}' → '{item.name}'")
                print(f"Item type: '{old_type}' → '{item.item_type}'")
            
            # Commit the changes
            db.session.commit()
            print("Preschool skirt successfully renamed to jumper dress.")
        else:
            print("No skirt items found in preschool category.")

if __name__ == "__main__":
    rename_preschool_skirt() 