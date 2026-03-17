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
    cursor.execute("DESCRIBE register")
    columns = cursor.fetchall()
    print("DESCRIBE register:")
    for col in columns:
        print(col)
    
    cursor.execute("DESCRIBE medications")
    columns = cursor.fetchall()
    print("\nDESCRIBE medications:")
    for col in columns:
        print(col)

    cursor.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
