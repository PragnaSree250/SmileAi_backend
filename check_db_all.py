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
    
    tables = ['reports', 'care_tips', 'notifications', 'case_timeline', 'case_files']
    for table in tables:
        try:
            cursor.execute(f"DESCRIBE {table}")
            print(f"\nDESCRIBE {table}:")
            columns = cursor.fetchall()
            for col in columns:
                print(col)
        except Exception as e:
            print(f"\nTable {table} error: {e}")

    cursor.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
