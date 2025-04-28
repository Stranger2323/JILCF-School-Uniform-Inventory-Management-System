from app import app, db, Item, Stock

def remove_shs_generic_patch():
    """Remove generic patch from Senior High School category"""
    with app.app_context():
        # Find the generic patch (not the strand-specific ones)
        generic_patch = Item.query.filter_by(
            category='seniorhigh',
            item_type='patch'  # Generic patch, not patch_abm, patch_stem, etc.
        ).first()
        
        if generic_patch:
            print(f"Found generic patch: {generic_patch.name} (ID: {generic_patch.id})")
            
            # Find all stocks for this patch
            stocks = Stock.query.filter_by(item_id=generic_patch.id).all()
            print(f"Removing {len(stocks)} stock entries...")
            
            # Delete all stocks first
            for stock in stocks:
                db.session.delete(stock)
            
            # Delete the patch item
            db.session.delete(generic_patch)
            db.session.commit()
            
            print("Generic SHS patch successfully removed.")
        else:
            print("No generic SHS patch found. Only strand-specific patches exist.")

if __name__ == "__main__":
    remove_shs_generic_patch() 