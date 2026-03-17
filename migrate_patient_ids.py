import mysql.connector
import os

# Database configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "", 
    "database": "smile_ai",
    "port": 3307
}

def generate_patient_id(numeric_id):
    return f"P{numeric_id:04d}"

def migrate():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        # 1. Find patients without patient_id
        cursor.execute("SELECT id, full_name FROM register WHERE role = 'patient' AND (patient_id IS NULL OR patient_id = '')")
        patients = cursor.fetchall()
        
        if not patients:
            print("No patients found needing ID migration.")
        else:
            print(f"Found {len(patients)} patients needing Clinical IDs. Migrating...")
            for p in patients:
                new_id = generate_patient_id(p['id'])
                cursor.execute("UPDATE register SET patient_id = %s WHERE id = %s", (new_id, p['id']))
                print(f"Migrated {p['full_name']} -> {new_id}")
            
        # 2. Sync cases that might have old patient IDs or be missing them
        # (Optional but good for data integrity if case creation was inconsistent)
        
        conn.commit()
        conn.close()
        print("Migration complete!")
    except mysql.connector.Error as err:
        print(f"Error: {err}")

if __name__ == "__main__":
    migrate()
