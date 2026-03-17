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
    cursor = conn.cursor(dictionary=True)
    
    print("--- Users in 'register' table ---")
    cursor.execute("SELECT id, full_name, email, role, patient_id FROM register LIMIT 20")
    users = cursor.fetchall()
    for user in users:
        print(user)
        
    print("\n--- Rows in 'dentist_profiles' table ---")
    cursor.execute("SELECT * FROM dentist_profiles LIMIT 20")
    profiles = cursor.fetchall()
    for p in profiles:
        print(p)
        
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
