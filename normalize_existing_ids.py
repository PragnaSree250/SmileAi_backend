import mysql.connector

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'smile_ai',
    'port': 3307
}

def normalize_id(pid):
    if not pid: return pid
    return str(pid).strip().upper().replace("-", "")

def normalize_db_ids():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        print("Standardizing patient IDs in 'register' table...")
        cursor.execute("SELECT id, patient_id FROM register WHERE role = 'patient' AND patient_id IS NOT NULL")
        users = cursor.fetchall()
        for user in users:
            old_id = user['patient_id']
            new_id = normalize_id(old_id)
            if old_id != new_id:
                print(f"  Updating user {user['id']}: {old_id} -> {new_id}")
                cursor.execute("UPDATE register SET patient_id = %s WHERE id = %s", (new_id, user['id']))
        
        print("Standardizing patient IDs in 'cases' table...")
        cursor.execute("SELECT id, patient_id FROM cases WHERE patient_id IS NOT NULL")
        cases = cursor.fetchall()
        for case in cases:
            old_id = case['patient_id']
            new_id = normalize_id(old_id)
            if old_id != new_id:
                print(f"  Updating case {case['id']}: {old_id} -> {new_id}")
                cursor.execute("UPDATE cases SET patient_id = %s WHERE id = %s", (new_id, case['id']))
        
        conn.commit()
        print("ID standardization completed successfully.")
        
    except Exception as e:
        print(f"Error standardizing IDs: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    normalize_db_ids()
