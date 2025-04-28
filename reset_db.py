from app import app, db
from initialize_db import initialize_database
import os

def reset_database():
    """Remove the existing database and reinitialize it"""
    with app.app_context():
        # Get the database file path
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        
        # Print what we're about to do
        print(f"This will delete your existing database at {db_path}")
        print("All existing data will be lost and replaced with the initialization data.")
        
        # Ask for confirmation
        confirmation = input("Are you sure you want to proceed? (yes/no): ")
        if confirmation.lower() != 'yes':
            print("Operation cancelled.")
            return
        
        # Drop all tables
        print("Dropping all tables...")
        db.drop_all()
        
        # Alternative: delete the database file completely
        if os.path.exists(db_path):
            try:
                os.remove(db_path)
                print(f"Deleted database file: {db_path}")
            except Exception as e:
                print(f"Warning: Could not delete database file: {e}")
        
        # Initialize new database
        print("Initializing new database...")
        initialize_database()
        
        print("Database reset complete! The necktie items for preschool and elementary categories have been removed.")

if __name__ == "__main__":
    reset_database() 