import mysql.connector

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'smile_ai',
    'port': 3307
}

try:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    # Add dentist_id to register table
    cursor.execute("DESCRIBE register")
    cols = [col[0] for col in cursor.fetchall()]
    
    if 'dentist_id' not in cols:
        print("Adding 'dentist_id' column to 'register' table...")
        cursor.execute("ALTER TABLE register ADD COLUMN dentist_id VARCHAR(50) UNIQUE AFTER role")
        print("Success!")
    else:
        print("'dentist_id' column already exists.")

    conn.commit()
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
