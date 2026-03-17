import mysql.connector

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'smile_ai',
    'port': 3307
}

def fix_schema():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Check current columns in reports
        cursor.execute("DESCRIBE reports")
        columns = [col[0] for col in cursor.fetchall()]
        
        print(f"Current columns in 'reports': {columns}")
        
        if 'medications' not in columns:
            print("Adding 'medications' column to 'reports' table...")
            cursor.execute("ALTER TABLE reports ADD COLUMN medications TEXT AFTER missing_teeth_status")
            
        if 'care_instructions' not in columns:
            print("Adding 'care_instructions' column to 'reports' table...")
            cursor.execute("ALTER TABLE reports ADD COLUMN care_instructions TEXT AFTER medications")
            
        conn.commit()
        print("Schema update completed successfully.")
        
    except Exception as e:
        print(f"Error updating schema: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    fix_schema()
