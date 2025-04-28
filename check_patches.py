from app import app, db, Item

def check_shs_patches():
    """Check all patch items in the Senior High School category"""
    with app.app_context():
        # Find all patches in SHS category
        patches = Item.query.filter(
            Item.category == 'seniorhigh',
            Item.item_type.like('%patch%')
        ).all()
        
        if patches:
            print(f"Found {len(patches)} patches in SHS category:")
            for patch in patches:
                print(f"- {patch.name} (ID: {patch.id}, Type: {patch.item_type}, Gender: {patch.gender})")
        else:
            print("No patch items found in SHS category.")

if __name__ == "__main__":
    check_shs_patches() 