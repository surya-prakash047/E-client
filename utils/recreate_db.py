from src.database import EmailDatabase
import os

def recreate_database():
    if os.path.exists('src/database/emails.db'):
        os.remove('src/database/emails.db')
        print("Old database removed")
    
    # Create new database with updated schema
    db = EmailDatabase()
    print("New database created with updated schema")
    db.close()

if __name__ == "__main__":
    recreate_database()